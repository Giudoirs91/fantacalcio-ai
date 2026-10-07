"""
daily_telegram_briefing.py - Pillole Quotidiane Notizie Fantacalcio (Telegram)
=============================================================================
Raccoglie automaticamente le principali notizie delle ultime 24 ore relative a:
- Infortuni ed esiti esami strumentali
- Rientri in gruppo e report allenamenti
- Squalifiche e decisioni del giudice sportivo
- Novità formazioni e ballottaggi

Genera un messaggio compatto di 5-6 righe ("Il Caffè del Fantallenatore")
e lo invia al canale Telegram configurato in config/telegram_config.json.
Pianificabile automaticamente alle ore 01:00 AM.
"""

import os
import sys
import re
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.telegram_engine import load_telegram_config, send_telegram_message, get_upcoming_round

RSS_QUERIES = [
    'fantacalcio+infortunati+OR+serie+a+lesione+OR+allenamento+when:1d',
    'serie+a+fantacalcio+novita+when:1d',
    'infortuni+serie+a+esami+comunicato+when:1d'
]

EXCLUDE_KEYWORDS = [
    'serie b', 'serie bkt', 'serie c', 'serie d', 'premier league', 'liga', 'bundesliga',
    'champions league', 'europa league', 'motogp', 'formula 1', 'f1', 'basket',
    'tennis', 'sinner', 'alcaraz', 'mondiali'
]

CATEGORY_KEYWORDS = {
    'infortunio': ['lesione', 'infortunio', 'stop', 'esami', 'operato', 'distorsione', 'out', 'salta', 'tegola'],
    'rientro': ['in gruppo', 'rientro', 'recuperato', 'ok', 'a disposizione', 'scalpita', 'parzialmente in gruppo'],
    'disciplinare': ['squalifica', 'squalificato', 'giudice sportivo', 'ammonizione', 'rosso'],
    'campo': ['ballottaggio', 'probabili formazioni', 'titolare', 'panchina', 'scelte', 'allenamento']
}


def fetch_latest_news():
    """Recupera e filtra le notizie sportive delle ultime 24 ore."""
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
                    # Pulisce la testata giornalistica (es. " - Sky Sport")
                    clean = re.sub(r'\s*-\s*[^-]+$', '', raw_title).strip()
                    clean = clean.replace('‘', "'").replace('’', "'").replace('`', "'")
                    
                    lower = clean.lower()
                    if any(bad in lower for bad in EXCLUDE_KEYWORDS):
                        continue

                    # Evita duplicati simili
                    norm_key = re.sub(r'[^a-zA-Z0-9]', '', lower[:40])
                    if norm_key in seen_titles:
                        continue
                    seen_titles.add(norm_key)

                    # Determina categoria
                    cat = 'altro'
                    for c_name, words in CATEGORY_KEYWORDS.items():
                        if any(w in lower for w in words):
                            cat = c_name
                            break

                    collected.append({
                        'title': clean,
                        'category': cat,
                        'link': (item.find('link').text or '').strip()
                    })
        except Exception as e:
            print(f"⚠️ Errore recupero RSS ({q}): {e}")

    return collected


def select_top_pillole(news_items, max_pillole=5):
    """
    Seleziona le 5-6 notizie più rilevanti bilanciando
    infortuni, rientri, campo e disciplina ed evitando duplicati sullo stesso calciatore.
    """
    categories = ['infortunio', 'rientro', 'disciplinare', 'campo', 'altro']
    by_cat = {c: [] for c in categories}
    for item in news_items:
        by_cat[item['category']].append(item)

    selected = []
    seen_keyword_sets = []

    def get_title_keywords(t):
        words = re.findall(r'[a-zA-Z]{4,}', t.lower())
        stopwords = {'infortunio', 'lesione', 'rientro', 'tempi', 'esami', 'esito', 'comunicato', 'fantacalcio', 'serie', 'giornata', 'verso', 'recupero'}
        return {w for w in words if w not in stopwords}

    def can_add(title):
        kws = get_title_keywords(title)
        # Se condivide 2 o più parole chiave distintive con notizie già scelte, è un duplicato
        if kws and any(len(kws.intersection(seen_kw)) >= 2 for seen_kw in seen_keyword_sets):
            return False
        return True

    def try_add(icon, title):
        if len(selected) >= max_pillole:
            return False
        if can_add(title):
            selected.append((icon, title))
            seen_keyword_sets.append(get_title_keywords(title))
            return True
        return False

    # 1. Infortuni (fino a 2 diversi)
    for it in by_cat['infortunio']:
        if len([s for s in selected if s[0] == '🩺']) >= 2:
            break
        try_add('🩺', it['title'])

    # 2. Rientri / infermeria positiva (almeno 1)
    for it in by_cat['rientro']:
        if len([s for s in selected if s[0] == '🏃']) >= 2:
            break
        try_add('🏃', it['title'])

    # 3. Disciplinare o campo
    for it in (by_cat['disciplinare'] + by_cat['campo']):
        icon = '⚖️' if it['category'] == 'disciplinare' else '📋'
        try_add(icon, it['title'])

    # 4. Riempimento con altre notizie fresche
    for it in by_cat['altro']:
        try_add('⚡', it['title'])

    return selected


def build_daily_briefing_message():
    """Compone il messaggio formattato per Telegram."""
    news = fetch_latest_news()
    pillole = select_top_pillole(news, max_pillole=5)

    today_str = datetime.now().strftime("%d/%m/%Y")
    upcoming_round = get_upcoming_round()

    lines = [
        f"☕ *FANTAMASTER AI — IL BRIEFING DEL GIORNO* 📅",
        f"_{today_str} • Le pillole essenziali delle ultime 24 ore_\n"
    ]

    if pillole:
        for icon, text in pillole:
            # Rende il testo pulito e compatto
            text = text.strip()
            lines.append(f"{icon} {text}")
    else:
        lines.append("⚡ Giornata tranquilla sui campi: nessun intoppo grave registrato nelle ultime 24h.")

    lines.append("")
    lines.append(f"💡 *Verso la Giornata {upcoming_round}:*")
    lines.append("Indici xFM, probabili formazioni e statistiche live su:")
    lines.append("👉 [fantamasterai.it](https://www.fantamasterai.it)")

    return "\n".join(lines)


def run_daily_briefing(dry_run=False):
    """Esegue il briefing quotidiano (stampa a video o invio Telegram)."""
    cfg = load_telegram_config()
    token = cfg.get("bot_token")
    channel_id = cfg.get("channel_id")

    msg = build_daily_briefing_message()

    if dry_run:
        print("\n================= ANTEPRIMA DAILY BRIEFING (DRY-RUN) =================")
        print(msg)
        print("======================================================================\n")
        print("✓ Nessun messaggio inviato (modalità dry-run attiva).")
        return msg

    print(f"-> Invio Daily Briefing a {channel_id}...")
    res = send_telegram_message(token, channel_id, msg)
    if res and res.get('ok'):
        print("✓ Daily Briefing inviato con successo sul canale Telegram!")
    else:
        print("❌ Errore durante l'invio del messaggio.")
    return res


if __name__ == '__main__':
    # Default: se lanciato da CLI con argomento --send invia, altrimenti dry-run di sicurezza
    is_live = "--send" in sys.argv
    run_daily_briefing(dry_run=not is_live)
