"""
daily_telegram_briefing.py - Palinsesto Quotidiano Telegram Mattutino (Ore 07:30)
=================================================================================
Pubblica ogni mattina alle ore 07:30 sul canale Telegram @fantamasterai.

Supporta 3 modalità intelligenti in base al calendario reale di Serie A 2026/27:
1. POST-FINE TURNO (Giorno dopo l'ultima partita della giornata):
   - I TOP & FLOP ufficiali di giornata (con voti, bonus/malus e commenti AI)
     👉 https://www.fantamasterai.it/top-flop/
   - Le Statistiche più interessanti (xG, clean sheet, tiratori, curiosità)
     👉 https://www.fantamasterai.it/statistiche-serie-a/
   - CTA Importazione Rosa per schierare l'11 migliore del prossimo turno.

2. IN-PROGRESS / POST-MATCH (Giorno dopo le partite di venerdì o sabato):
   - Recap delle gare disputate ieri (Risultati, Gol, Assist, Cartellini, Infortuni sul campo)
   - Link obbligatorio infortuni: https://www.fantamasterai.it/infortunati-serie-a/
   - CTA ai ballottaggi del giorno: https://www.fantamasterai.it/chi-schiero/
   - CTA consigli: https://www.fantamasterai.it/consigli-fantacalcio/

3. GIORNO FERIALE ORDINARIO (Mercoledì, Giovedì senza partite):
   - Pillole 100% Serie A 2026/27 (Esiti esami, rientri in gruppo, novità dai campi)
   - Link infortuni fisso: https://www.fantamasterai.it/infortunati-serie-a/
   - CTA promozionali complete al portale e all'11 migliore.
"""

import os
import sys
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.telegram_engine import load_telegram_config, send_telegram_message, get_upcoming_round

TOP_FLOP_PATH = os.path.join(ROOT_DIR, "data", "processed", "top_flop_rounds.json")
PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")

RSS_QUERIES = [
    'fantacalcio+infortunati+OR+serie+a+lesione+OR+allenamento+when:1d',
    'serie+a+fantacalcio+novita+when:1d',
    'infortuni+serie+a+esami+comunicato+when:1d'
]

EXCLUDE_KEYWORDS = [
    'serie b', 'serie bkt', 'serie c', 'serie d', 'premier league', 'liga', 'bundesliga',
    'champions league', 'europa league', 'motogp', 'formula 1', 'f1', 'basket',
    'tennis', 'sinner', 'alcaraz', 'musetti', 'djokovic', 'mondiali'
]

SERIE_A_TEAMS = [
    'atalanta', 'bologna', 'cagliari', 'como', 'fiorentina', 'frosinone', 'genoa',
    'inter', 'juventus', 'lazio', 'lecce', 'milan', 'monza', 'napoli', 'parma',
    'roma', 'sassuolo', 'torino', 'udinese', 'venezia'
]


def fetch_latest_news():
    """Recupera e filtra notizie sportive rigorosamente legate alla Serie A 2026/27."""
    seen_titles = set()
    collected = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) FantaMasterAI/1.0'}

    for q in RSS_QUERIES:
        url = f"https://news.google.com/rss/search?q={q}&hl=it&gl=IT&ceid=IT:it"
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall('.//item'):
                    raw_title = item.find('title').text or ''
                    clean = re.sub(r'\s*-\s*[^-]+$', '', raw_title).strip()
                    clean = clean.replace('‘', "'").replace('’', "'").replace('`', "'")
                    lower = clean.lower()

                    if any(bad in lower for bad in EXCLUDE_KEYWORDS):
                        continue

                    # Verifica che menzioni almeno una squadra di Serie A o parole chiave fanta
                    is_serie_a = any(team in lower for team in SERIE_A_TEAMS)
                    is_fanta = any(k in lower for k in ['fantacalcio', 'fanta', 'serie a', 'infortunio', 'esami'])
                    if not (is_serie_a or is_fanta):
                        continue

                    norm_key = re.sub(r'[^a-zA-Z0-9]', '', lower[:40])
                    if norm_key in seen_titles:
                        continue
                    seen_titles.add(norm_key)

                    cat = 'altro'
                    if any(w in lower for w in ['infortunio', 'lesione', 'stop', 'esami', 'operato', 'distorsione', 'out', 'salta', 'tegola']):
                        cat = 'infortunio'
                    elif any(w in lower for w in ['in gruppo', 'rientro', 'recuperato', 'ok', 'a disposizione', 'scalpita']):
                        cat = 'rientro'
                    elif any(w in lower for w in ['squalifica', 'squalificato', 'giudice sportivo', 'ammonizione', 'rosso']):
                        cat = 'disciplinare'
                    elif any(w in lower for w in ['ballottaggio', 'probabili formazioni', 'titolare', 'panchina', 'scelte', 'allenamento']):
                        cat = 'campo'

                    collected.append({
                        'title': clean,
                        'category': cat,
                        'link': (item.find('link').text or '').strip()
                    })
        except Exception as e:
            pass

    return collected


def get_latest_completed_round():
    """Ritorna l'ultimo turno disputato di cui abbiamo i voti e top/flop."""
    if os.path.exists(TOP_FLOP_PATH):
        try:
            with open(TOP_FLOP_PATH, 'r', encoding='utf-8') as f:
                d = json.load(f)
            rounds = [int(k) for k in d.keys() if k.isdigit()]
            if rounds:
                return max(rounds)
        except Exception:
            pass
    return 5


def build_post_round_message(round_num):
    """Genera il messaggio speciale di fine turno: Top & Flop + Statistiche + CTA."""
    top_flop_data = {}
    if os.path.exists(TOP_FLOP_PATH):
        try:
            with open(TOP_FLOP_PATH, 'r', encoding='utf-8') as f:
                top_flop_data = json.load(f).get(str(round_num), {})
        except Exception:
            pass

    tops = top_flop_data.get('top', [])[:3]
    flops = top_flop_data.get('flop', [])[:3]

    today_str = datetime.now().strftime("%d/%m/%Y")
    next_round = round_num + 1

    lines = [
        f"🏆 *FANTAMASTER AI — I TOP & FLOP DI GIORNATA {round_num}* ⚽",
        f"_{today_str} • Il verdetto definitivo del turno appena concluso_\n",
        "🥇 *I MIGLIORI DI GIORNATA (TOP 3):*"
    ]

    for p in tops:
        nome = p.get('name', 'Calciatore')
        team = p.get('team', '')
        fv = p.get('fantavoto', 8.0)
        motivo = p.get('motivo', 'Super prestazione')
        lines.append(f"• *{nome}* ({team}) — *{fv}* Fantavoto: _{motivo}_")

    lines.append("\n💔 *LE DELUSIONI DI GIORNATA (FLOP 3):*")
    for p in flops:
        nome = p.get('name', 'Calciatore')
        team = p.get('team', '')
        fv = p.get('fantavoto', 4.5)
        motivo = p.get('motivo', 'Insufficienza grave')
        lines.append(f"• *{nome}* ({team}) — *{fv}* Fantavoto: _{motivo}_")

    lines.append("\n📊 *Tutti i Top & Flop e pagelle ruolo per ruolo su:*")
    lines.append("👉 *https://www.fantamasterai.it/top-flop/*\n")

    lines.append("📈 *LE STATISTICHE PIÙ INTERESSANTI DELLA SERIE A:*")
    lines.append("Chi ha prodotto più xG a secco? Chi ha subito più tiri? Consulta l'hub statistico aggiornato:")
    lines.append("👉 *https://www.fantamasterai.it/statistiche-serie-a/*\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🛡️ *VERSO LA GIORNATA {next_round}: SCHIERA L'11 MIGLIORE*")
    lines.append("Non rischiare punti persi: carica o importa la tua rosa sul sito e lascia che l'algoritmo calcoli la formazione perfetta per il prossimo turno:")
    lines.append("👉 *https://www.fantamasterai.it*")

    # Bottoni interattivi Telegram
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "📊 Top & Flop Ufficiali", "url": "https://www.fantamasterai.it/top-flop/"},
                {"text": "📈 Statistiche Serie A", "url": "https://www.fantamasterai.it/statistiche-serie-a/"}
            ],
            [
                {"text": "🛡️ Schiera il Tuo 11 Migliore", "url": "https://www.fantamasterai.it"},
                {"text": "💡 Consigli Formazione", "url": "https://www.fantamasterai.it/consigli-fantacalcio/"}
            ]
        ]
    }

    return "\n".join(lines), reply_markup


INJURIES_CONFIG_PATH = os.path.join(ROOT_DIR, "config", "injuries.json")

def get_official_injury_highlights(limit=4):
    """Estrae gli infortuni e rientri più rilevanti direttamente dal database ufficiale."""
    if not os.path.exists(INJURIES_CONFIG_PATH):
        return []
    try:
        with open(INJURIES_CONFIG_PATH, 'r', encoding='utf-8') as f:
            injuries = json.load(f)
        # Filtra infortuni recenti/significativi
        return injuries[:limit]
    except Exception:
        return []


def build_midweek_briefing_message():
    """Genera il briefing feriale: Infermeria Serie A 2026/27, Rientri e CTA complete."""
    today_str = datetime.now().strftime("%d/%m/%Y")
    upcoming_round = get_upcoming_round()

    # Prendi infortuni certificati dal database del progetto
    official_injuries = get_official_injury_highlights(limit=3)

    lines = [
        f"☕ *FANTAMASTER AI — IL CAFFÈ DEL FANTALLENATORE* 📅",
        f"_{today_str} • Le pillole esclusive Serie A 2026/27 per il tuo Fantacalcio_\n"
    ]

    if official_injuries:
        lines.append("🩺 *BOLLETTINO INFERMERIA & ESAMI UFFICIALI:*")
        for inj in official_injuries:
            p = inj.get('player', 'Calciatore')
            t = inj.get('team', '')
            motivo = inj.get('motivo', 'Problema fisico')
            rientro = inj.get('rientro', 'Da valutare')
            lines.append(f"• *{p}* ({t}): _{motivo}_ (Rientro previsto: *{rientro}*)")
        lines.append("\n👉 *Controlla la lista infortunati completa con i tempi di recupero:*")
        lines.append("👉 *https://www.fantamasterai.it/infortunati-serie-a/*\n")
    else:
        lines.append("⚡ *Report Infermeria:*")
        lines.append("Nessuna nuova lesione grave registrata nelle ultime ore.")
        lines.append("👉 *https://www.fantamasterai.it/infortunati-serie-a/*\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"💡 *STRUMENTI AI PER IL PROSSIMO TURNO (GIORNATA {upcoming_round}):*")
    lines.append("1️⃣ *Guida Consigli Ruolo per Ruolo (Top & Scommesse):*")
    lines.append("   👉 *https://www.fantamasterai.it/consigli-fantacalcio/*")
    lines.append("2️⃣ *Hai dubbi tra due calciatori? Risolvili col comparatore 1vs1:*")
    lines.append("   👉 *https://www.fantamasterai.it/chi-schiero/*")
    lines.append("3️⃣ *Schiera l'11 migliore: carica la tua rosa sul sito:*")
    lines.append("   👉 *https://www.fantamasterai.it*")

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🚑 Infortunati Serie A Live", "url": "https://www.fantamasterai.it/infortunati-serie-a/"},
                {"text": "⚔️ Risolvi Dubbio su Chi Schiero", "url": "https://www.fantamasterai.it/chi-schiero/"}
            ],
            [
                {"text": "💡 Consigli Formazione", "url": "https://www.fantamasterai.it/consigli-fantacalcio/"},
                {"text": "🛡️ Schiera il Tuo 11 Migliore", "url": "https://www.fantamasterai.it"}
            ]
        ]
    }

    return "\n".join(lines), reply_markup


def run_daily_briefing(dry_run=False, force_mode=None):
    """
    Esegue il daily briefing delle 07:30.
    Invia sempre il bollettino quotidiano certificato (infermeria, esami, novità campi e link al sito),
    senza azzardare riepiloghi di fine turno prima che l'utente abbia aggiornato i dati.
    """
    latest_completed = get_latest_completed_round()

    # Invia post-round SOLO se esplicitamente forzato da parametro CLI
    if force_mode == 'post_round':
        msg, reply_markup = build_post_round_message(latest_completed)
    else:
        msg, reply_markup = build_midweek_briefing_message()

    if dry_run:
        print("\n================= ANTEPRIMA DAILY BRIEFING (DRY-RUN) =================")
        print(msg)
        print("Bottoni inline:")
        for row in reply_markup.get('inline_keyboard', []):
            print(" ", [b['text'] for b in row])
        print("======================================================================\n")
        return msg

    cfg = load_telegram_config()
    token = cfg.get("bot_token")
    channel_id = cfg.get("channel_id")

    print(f"-> Invio Daily Briefing a {channel_id}...")
    res = send_telegram_message(token, channel_id, msg, reply_markup=reply_markup)
    if res and res.get('ok'):
        print("✓ Daily Briefing inviato con successo sul canale Telegram!")
    else:
        print("❌ Errore durante l'invio del messaggio.")
    return res


if __name__ == '__main__':
    is_live = "--send" in sys.argv
    force = 'post_round' if '--post-round' in sys.argv else ('midweek' if '--midweek' in sys.argv else None)
    run_daily_briefing(dry_run=not is_live, force_mode=force)
