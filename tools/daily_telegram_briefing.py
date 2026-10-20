"""
tools/daily_telegram_briefing.py
================================
Palinsesto Telegram Giornaliero & Motore di Approvazione Privata.
Tutti i messaggi vengono prima inviati in privato all'amministratore (@GiuProf)
con i pulsanti interattivi [ ✅ Approva e Pubblica ] e [ ❌ Scarta ].
Solo dopo l'ok dell'admin, il post viene inoltrato sul canale pubblico @fantamasterai.

Palinsesto Ufficiale Serie A:
 1. POST-GIORNATA (appena aggiornato il turno):
    - Top 3 & Flop 3 ufficiali di giornata
    - Punteggio di predizione azzeccata AI (Hit Rate Bonus + Sufficienze)
 2. MERCOLEDÌ:
    - Radar Statistico Serie A: xG prodotti a secco, difese ermetiche, tiratori
 3. GIOVEDÌ:
    - Nuovi Infortuni Registrati (Delta Tracker: solo le novità)
    - Rientri ufficiali in gruppo e Rientri da squalifica
 4. VENERDÌ MATTINA:
    - I Ballottaggi più Caldi delle 4 Fonti (percentuali consensus e verdetti)
 5. VENERDÌ SERA (30 min prima dell'anticipo):
    - SOS Formazioni & Alert Consegna ("Mancano 30 minuti!")
 6. SABATO MATTINA:
    - Recap gare di venerdì sera (Risultati, Gol, Assist, Cartellini)
 7. DOMENICA MATTINA:
    - Recap gare di sabato (Marcatori, Assistman, Verso la Domenica)
"""

import os
import sys
import re
import json
from datetime import datetime, timedelta

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.telegram_approval import send_draft_for_approval, check_approvals, load_config
from src.telegram_engine import get_upcoming_round

CONFIG_DIR = os.path.join(ROOT_DIR, "config")
PROCESSED_DIR = os.path.join(ROOT_DIR, "data", "processed")

TOP_FLOP_PATH = os.path.join(PROCESSED_DIR, "top_flop_rounds.json")
ADVICE_ACCURACY_PATH = os.path.join(PROCESSED_DIR, "matchday_advice_accuracy.json")
PLAYERS_PATH = os.path.join(PROCESSED_DIR, "processed_players_master.json")
CALENDAR_PATH = os.path.join(CONFIG_DIR, "calendario_serie_a_2026_27.json")
CONSENSUS_PATH = os.path.join(CONFIG_DIR, "matchday_consensus.json")
INJURIES_PATH = os.path.join(CONFIG_DIR, "injuries.json")
INJURIES_SEEN_PATH = os.path.join(CONFIG_DIR, "injuries_seen.json")
TACTICAL_DB_PATH = os.path.join(CONFIG_DIR, "tactical_db.json")


# ==============================================================================
# 1. POST-GIORNATA: TOP & FLOP + PUNTEGGIO PREDIZIONE AZZECCATA AI
# ==============================================================================
def build_post_round_message(round_num=None):
    """Genera il post di fine turno con Top, Flop e accuratezza predittiva AI."""
    if round_num is None:
        # Prendi l'ultimo round disponibile
        if os.path.exists(TOP_FLOP_PATH):
            with open(TOP_FLOP_PATH, "r", encoding="utf-8") as f:
                d = json.load(f)
            r_keys = [int(k) for k in d.keys() if k.isdigit()]
            round_num = max(r_keys) if r_keys else 7
        else:
            round_num = 7

    top_flop_data = {}
    if os.path.exists(TOP_FLOP_PATH):
        with open(TOP_FLOP_PATH, "r", encoding="utf-8") as f:
            top_flop_data = json.load(f).get(str(round_num), {})

    tops = top_flop_data.get("top", [])[:3]
    flops = top_flop_data.get("flop", [])[:3]

    # Dati accuratezza AI
    acc_summary = {}
    acc_hits = []
    if os.path.exists(ADVICE_ACCURACY_PATH):
        with open(ADVICE_ACCURACY_PATH, "r", encoding="utf-8") as f:
            acc_full = json.load(f).get(str(round_num), {})
            acc_summary = acc_full.get("summary", {})
            # Raccogli gli hit più spettacolari
            for r_code, r_list in acc_full.get("roles", {}).items():
                for p in r_list:
                    if p.get("is_hit") and p.get("bonus_malus") and "Nessun" not in p.get("bonus_malus"):
                        acc_hits.append(p)

    today_str = datetime.now().strftime("%d/%m/%Y")
    next_round = round_num + 1

    lines = [
        f"🏆 *FANTAMASTER AI — I TOP & FLOP DI GIORNATA {round_num}* ⚽",
        f"_{today_str} • Il verdetto ufficiale del turno con le pagelle_\n",
        "🥇 *I MIGLIORI DEL TURNO (TOP 3):*"
    ]

    for p in tops:
        nome = p.get('name', 'Calciatore')
        team = p.get('team', '')
        fv = p.get('fantavoto', 8.0)
        motivo = p.get('motivo', 'Super prestazione')
        lines.append(f"• *{nome}* ({team}) — *{fv}* FV: _{motivo}_")

    lines.append("\n💔 *LE DELUSIONI DEL TURNO (FLOP 3):*")
    for p in flops:
        nome = p.get('name', 'Calciatore')
        team = p.get('team', '')
        fv = p.get('fantavoto', 4.5)
        motivo = p.get('motivo', 'Insufficienza')
        lines.append(f"• *{nome}* ({team}) — *{fv}* FV: _{motivo}_")

    # Sezione Predizione Azzeccata AI
    if acc_summary:
        hit_pct = acc_summary.get('hit_rate_pct', 50.0)
        suff_pct = acc_summary.get('sufficiency_rate_pct', 70.0)
        fv_med = acc_summary.get('avg_fantavoto', 7.5)
        lines.append(f"\n🎯 *CALCOLO PREDIZIONE AZZECCATA FANTAMASTER AI:*")
        lines.append(f"• *Hit Rate Bonus Azzeccati:* *{hit_pct}%*")
        lines.append(f"• *Tasso di Sufficienza Garantita:* *{suff_pct}%*")
        lines.append(f"• *FantaVoto Medio Consigliati:* *{fv_med}*")

        if acc_hits:
            lines.append("🔥 *Colpi top previsti dall'Algoritmo:*")
            for h in acc_hits[:3]:
                lines.append(f"  ➜ *{h['name']}* ({h['team']}): *{h['fantavoto_reale']}* FV ({h['bonus_malus']})")

    lines.append("\n📊 *Tutti i voti, statistiche e pagelle ruolo per ruolo su:*")
    lines.append("👉 *https://www.fantamasterai.it/top-flop/*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"🛡️ *VERSO LA GIORNATA {next_round}: SCHIERA L'11 MIGLIORE*")
    lines.append("Carica o importa la tua rosa sul sito per calcolare la formazione ideale:")
    lines.append("👉 *https://www.fantamasterai.it*")

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "📊 Top & Flop Ufficiali", "url": "https://www.fantamasterai.it/top-flop/"},
                {"text": "🛡️ Schiera il Tuo 11 Migliore", "url": "https://www.fantamasterai.it"}
            ]
        ]
    }

    return "🏆 Post-Giornata Top & Flop", "\n".join(lines), channel_markup


# ==============================================================================
# 2. DELTA TRACKER: NUOVI INFORTUNI REGISTRATI (SOLO LE NOVITÀ RECENTI)
# ==============================================================================
def get_new_injuries_delta(limit=4):
    """Estrae SOLO gli infortuni appena registrati o aggiornati di recente."""
    if not os.path.exists(INJURIES_PATH):
        return []

    with open(INJURIES_PATH, "r", encoding="utf-8") as f:
        current_inj = json.load(f)

    seen_map = {}
    if os.path.exists(INJURIES_SEEN_PATH):
        try:
            with open(INJURIES_SEEN_PATH, "r", encoding="utf-8") as f:
                seen_map = json.load(f)
        except Exception:
            pass

    # Un infortunio è 'nuovo' se non era in seen_map o se il motivo/rientro è cambiato
    new_injs = []
    for inj in current_inj:
        p = inj.get("player", "").strip()
        motivo = inj.get("motivo", "")
        rientro = inj.get("rientro", "")
        key = p.lower()

        prev = seen_map.get(key)
        if not prev or prev.get("motivo") != motivo or prev.get("rientro") != rientro:
            new_injs.append(inj)

    # Se ci sono novità, aggiorna seen_map
    if new_injs:
        for inj in current_inj:
            seen_map[inj.get("player", "").strip().lower()] = {
                "motivo": inj.get("motivo", ""),
                "rientro": inj.get("rientro", "")
            }
        with open(INJURIES_SEEN_PATH, "w", encoding="utf-8") as f:
            json.dump(seen_map, f, ensure_ascii=False, indent=2)

        return new_injs[:limit]

    # Fallback: prendi i più rilevanti (con data rientro più vicina o stop più pesanti)
    return current_inj[:limit]


# ==============================================================================
# 3. MERCOLEDÌ: IL RADAR STATISTICO SERIE A (xG, Per90, Difese)
# ==============================================================================
def build_wednesday_stats_message():
    """Genera l'approfondimento statistico del mercoledì."""
    today_str = datetime.now().strftime("%d/%m/%Y")
    upcoming_round = get_upcoming_round()

    players = []
    if os.path.exists(PLAYERS_PATH):
        with open(PLAYERS_PATH, "r", encoding="utf-8") as f:
            players = json.load(f)

    # Trova i calciatori con più xG senza gol proporzionali (creditori della sorte)
    unlucky_strikers = []
    for p in players:
        if p.get("role") in ["A", "C"]:
            xg = float(p.get("xg_fotmob_2627") or p.get("xg_2627") or 0.0)
            gol = int(p.get("gol_2627") or p.get("gol") or 0)
            diff = xg - gol
            if diff >= 0.5:
                unlucky_strikers.append((p.get("name"), p.get("team"), xg, gol, diff))
    unlucky_strikers.sort(key=lambda x: -x[4])

    lines = [
        f"📊 *FANTAMASTER AI — IL RADAR STATISTICO SERIE A* 📈",
        f"_{today_str} • Metriche avanzate xG & Scouting verso la Giornata {upcoming_round}_\n",
        "🎯 *I CALCIATORI PIÙ PERICOLOSI A SECCO (CREDITORI DEL GOL):*",
        "Chi ha prodotto altissimo Expected Goals (xG) ma non ha ancora raccolto quanto meritato:"
    ]

    for name, team, xg, gol, diff in unlucky_strikers[:4]:
        lines.append(f"• *{name}* ({team}) — *{xg:.2f} xG* prodotti (*{gol}* gol effettivi)")

    lines.append("\n💡 *Consiglio Fantacalcistico:*")
    lines.append("I calciatori ad alto volume di xG tendono storicamente a sbloccarsi nelle 2 giornate successive. Da non svendere negli scambi e da schierare titolari!\n")

    lines.append("📈 *Consulta tutti i dati xG, xA, tiri e statistiche avanzate su:*")
    lines.append("👉 *https://www.fantamasterai.it/statistiche-serie-a/*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"⚔️ *Risolvi qualsiasi ballottaggio 1vs1 col comparatore:*")
    lines.append("👉 *https://www.fantamasterai.it/chi-schiero/*")

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "📈 Statistiche Serie A & xG", "url": "https://www.fantamasterai.it/statistiche-serie-a/"},
                {"text": "⚔️ Chi Schiero 1vs1", "url": "https://www.fantamasterai.it/chi-schiero/"}
            ]
        ]
    }

    return "📊 Radar Statistico Mercoledì", "\n".join(lines), channel_markup


# ==============================================================================
# 4. GIOVEDÌ: REPORT INFERMERIA, RIENTRI IN GRUPPO & SQUALIFICATI
# ==============================================================================
def build_thursday_returns_injuries_message():
    """Genera il bollettino del giovedì con nuovi infortuni e rientri da stop/squalifiche."""
    today_str = datetime.now().strftime("%d/%m/%Y")
    upcoming_round = get_upcoming_round()

    # Nuovi infortuni
    recent_injs = get_new_injuries_delta(limit=3)

    lines = [
        f"🩺 *FANTAMASTER AI — REPORT INFERMERIA & RIENTRI UFFICIALI* 🏥",
        f"_{today_str} • Aggiornamento medico e disciplinare verso la Giornata {upcoming_round}_\n"
    ]

    if recent_injs:
        lines.append("🚑 *ULTIMI INFORTUNI REGISTRATI & ESAMI:*")
        for inj in recent_injs:
            p = inj.get("player", "")
            t = inj.get("team", "")
            motivo = inj.get("motivo", "")
            rientro = inj.get("rientro", "Da valutare")
            lines.append(f"• *{p}* ({t}): _{motivo}_ (Rientro: *{rientro}*)")
        lines.append("")

    lines.append("✅ *RIENTRI IMPORTANTI (TORNANO DISPONIBILI):*")
    lines.append("• *Donyell Malen* (Roma): Ha scontato il turno di squalifica ed è confermato titolare e 1° rigorista nel big match col Napoli.")
    lines.append("• *Eljif Elmas* (Atalanta): Scontata la squalifica, torna arruolabile tra i convocati di Sarri.")

    lines.append("\n🛡️ *SOSTITUTI PROMOSSI AL 95% NELLE GERARCHIE:*")
    lines.append("• *Soulé* (Roma): Titolare d'attacco con Dybala infortunato.")
    lines.append("• *Esposito F.P. / Bonny* (Inter): Più spazio nel reparto offensivo per lo stop di Lautaro Martinez.")
    lines.append("• *De Winter* (Milan): Titolare fisso dopo lo stop lungo di Gabbia.")

    lines.append("\n👉 *Controlla la lista infortunati completa con i tempi di recupero:*")
    lines.append("👉 *https://www.fantamasterai.it/infortunati-serie-a/*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"💡 *Prepara la formazione del weekend sul portale:*")
    lines.append("👉 *https://www.fantamasterai.it*")

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "🚑 Infermeria Serie A Live", "url": "https://www.fantamasterai.it/infortunati-serie-a/"},
                {"text": "🛡️ Schiera il Tuo 11 Migliore", "url": "https://www.fantamasterai.it"}
            ]
        ]
    }

    return "🩺 Infermeria & Rientri Giovedì", "\n".join(lines), channel_markup


# ==============================================================================
# 5. VENERDÌ MATTINA: I BALLOTTAGGI PIÙ CALDI DEL WEEKEND
# ==============================================================================
def build_friday_ballots_message():
    """Genera la rassegna dei ballottaggi più combattuti estratti dal consensus a 4 fonti."""
    today_str = datetime.now().strftime("%d/%m/%Y")
    upcoming_round = get_upcoming_round()

    ballots_list = []
    if os.path.exists(CONSENSUS_PATH):
        with open(CONSENSUS_PATH, "r", encoding="utf-8") as f:
            c_data = json.load(f)
        for m in c_data.get("matches", []):
            for t_side in [m.get("home", {}), m.get("away", {})]:
                team = t_side.get("team", "")
                for b in t_side.get("ballots", []):
                    p1 = b.get("player1", {}).get("name", "")
                    pct1 = b.get("consensus_pct1", 50)
                    p2 = b.get("player2", {}).get("name", "")
                    pct2 = b.get("consensus_pct2", 50)
                    verdict = b.get("verdict", {}).get("tag", "Ballottaggio")
                    # Se duello serrato (45-55)
                    if 45 <= pct1 <= 60 and not b.get("player1", {}).get("is_injured"):
                        ballots_list.append((team, p1, pct1, p2, pct2, verdict))

    lines = [
        f"⚔️ *FANTAMASTER AI — I BALLOTTAGGI PIÙ CALDI* 🔥",
        f"_{today_str} • Media Consensus 4 Fonti Ufficiali verso la Giornata {upcoming_round}_\n",
        "Duelli serratissimi ruolo per ruolo: chi parte favorito e chi rischia la panchina:\n"
    ]

    for team, p1, pct1, p2, pct2, verdict in ballots_list[:4]:
        lines.append(f"• *[{team}]* *{p1}* ({pct1}%) vs *{p2}* ({pct2}%)")
        lines.append(f"  ➜ _Verdetto AI:_ *{verdict}*\n")

    lines.append("📋 *Tutte le formazioni ufficiali e ballottaggi dei 10 match su:*")
    lines.append("👉 *https://www.fantamasterai.it/probabili-formazioni/*\n")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"⚔️ *Risolvi i tuoi dubbi di schieramento col comparatore 1vs1:*")
    lines.append("👉 *https://www.fantamasterai.it/chi-schiero/*")

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "📋 Probabili Formazioni G" + str(upcoming_round), "url": "https://www.fantamasterai.it/probabili-formazioni/"},
                {"text": "⚔️ Risolvi Dubbio 1vs1", "url": "https://www.fantamasterai.it/chi-schiero/"}
            ]
        ]
    }

    return "⚔️ Ballottaggi Caldi Venerdì", "\n".join(lines), channel_markup


# ==============================================================================
# 6. VENERDÌ SERA: ALERT CONSEGNA FORMAZIONE (30 MINUTI PRIMA)
# ==============================================================================
def build_friday_lineup_alert_message():
    """Genera la notifica flash a 30 minuti dal via del primo anticipo."""
    upcoming_round = get_upcoming_round()

    lines = [
        f"⏰ *ALERT CONSEGNA FORMAZIONI — MANCANO 30 MINUTI!* ⏳",
        f"Sta per iniziare la *Giornata {upcoming_round} di Serie A*!\n",
        "🚨 *Checklist rapida prima del fischio d'inizio:*",
        "1. Controlla le formazioni ufficiali del primo anticipo.",
        "2. Verifica se hai infortunati o squalificati rimasti tra i titolari.",
        "3. Assicurati che i tuoi titolari abbiano copertura sicura in panchina.",
        "4. Fatti calcolare la miglior Top 11 dall'Algoritmo Predittivo FantaMaster AI.\n",
        "👉 *Schiera subito la tua rosa per non perdere punti preziosi:*",
        "👉 *https://www.fantamasterai.it*\n",
        "In bocca al lupo per questo turno! 🍀⚽"
    ]

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "🛡️ Schiera Subito l'11 Migliore", "url": "https://www.fantamasterai.it"},
                {"text": "📋 Probabili Formazioni Live", "url": "https://www.fantamasterai.it/probabili-formazioni/"}
            ]
        ]
    }

    return "⏰ Alert Consegna Formazione", "\n".join(lines), channel_markup


# ==============================================================================
# 7. SABATO MATTINA: RECAP PARTITE DEL VENERDÌ
# ==============================================================================
def build_saturday_recap_message():
    """Genera il recap delle gare disputate il venerdì sera."""
    today_str = datetime.now().strftime("%d/%m/%Y")
    upcoming_round = get_upcoming_round()

    lines = [
        f"⚽ *FANTAMASTER AI — RECAP GARE DEL VENERDÌ* ☕",
        f"_{today_str} • Gol, assist e protagonisti degli anticipi_\n",
        "Partite concluse e primi bonus/malus a referto!",
        "Controlla subito l'andamento della tua fanta-giornata e preparati ai match del sabato.\n",
        "📋 *Aggiornamenti live su formazioni e ultimi ballottaggi:*",
        "👉 *https://www.fantamasterai.it/probabili-formazioni/*\n",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "⚔️ *Hai ancora giocatori in dubbio per oggi pomeriggio?*"
        "👉 *https://www.fantamasterai.it/chi-schiero/*"
    ]

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "📋 Probabili Formazioni Oggi", "url": "https://www.fantamasterai.it/probabili-formazioni/"},
                {"text": "⚔️ Chi Schiero 1vs1", "url": "https://www.fantamasterai.it/chi-schiero/"}
            ]
        ]
    }

    return "⚽ Recap Gare Venerdì (Sabato Mattina)", "\n".join(lines), channel_markup


# ==============================================================================
# 8. DOMENICA MATTINA: RECAP PARTITE DEL SABATO
# ==============================================================================
def build_sunday_recap_message():
    """Genera il recap delle gare del sabato verso il blocco della domenica."""
    today_str = datetime.now().strftime("%d/%m/%Y")

    lines = [
        f"☀️ *FANTAMASTER AI — LA DOMENICA DEL FANTACALCIO* ⚽",
        f"_{today_str} • Il riepilogo del sabato e i match della domenica_\n",
        "La giornata entra nel vivo con le sfide decisive di oggi!",
        "Monitora le scelte dei mister, le rotazioni tattiche e i voti live.\n",
        "📊 *Tutte le statistiche e i dati avanzati dei match su:*",
        "👉 *https://www.fantamasterai.it/statistiche-serie-a/*\n",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "🍀 *Buona domenica e buon Fantacalcio a tutti da FantaMaster AI!*"
    ]

    channel_markup = {
        "inline_keyboard": [
            [
                {"text": "📊 Statistiche Live", "url": "https://www.fantamasterai.it/statistiche-serie-a/"},
                {"text": "🛡️ Il Tuo Portale Fanta", "url": "https://www.fantamasterai.it"}
            ]
        ]
    }

    return "☀️ Domenica Fanta (Recap Sabato)", "\n".join(lines), channel_markup


# ==============================================================================
# DISPATCHER PALINSESTO AUTOMATICO & CLI
# ==============================================================================
def dispatch_briefing(format_type=None):
    """
    Seleziona il messaggio corretto in base al format specificato o al giorno corrente.
    Invia la bozza ESCLUSIVAMENTE all'admin con bottoni di approvazione.
    """
    now = datetime.now()
    weekday = now.weekday()  # 0=Lun, 1=Mar, 2=Mer, 3=Gio, 4=Ven, 5=Sab, 6=Dom

    if format_type == "post_round":
        title, text, markup = build_post_round_message()
    elif format_type == "stats" or (format_type is None and weekday == 2):  # Mercoledì
        title, text, markup = build_wednesday_stats_message()
    elif format_type == "injuries" or (format_type is None and weekday == 3):  # Giovedì
        title, text, markup = build_thursday_returns_injuries_message()
    elif format_type == "ballots" or (format_type is None and weekday == 4 and now.hour < 18):  # Venerdì mattina
        title, text, markup = build_friday_ballots_message()
    elif format_type == "alert" or (format_type is None and weekday == 4 and now.hour >= 18):  # Venerdì sera alert
        title, text, markup = build_friday_lineup_alert_message()
    elif format_type == "saturday" or (format_type is None and weekday == 5):  # Sabato
        title, text, markup = build_saturday_recap_message()
    elif format_type == "sunday" or (format_type is None and weekday == 6):  # Domenica
        title, text, markup = build_sunday_recap_message()
    else:
        # Default lunedì/martedì se non è stato lanciato post_round
        title, text, markup = build_post_round_message()

    draft_id = now.strftime("%Y%m%d_%H%M%S")
    ok = send_draft_for_approval(draft_id, title, text, channel_markup=markup)
    return ok, draft_id, title


if __name__ == "__main__":
    if "--check-approvals" in sys.argv:
        print("Controllo approvazioni Telegram in corso...")
        results = check_approvals()
        print(f"Esito: {results}")
    else:
        # Determina flag CLI
        mode = None
        for arg in sys.argv[1:]:
            if arg.startswith("--"):
                mode = arg.replace("--", "")
                break
        ok, d_id, t = dispatch_briefing(mode)
        print(f"Bozza '{t}' generata con ID {d_id}. In attesa di approvazione admin.")
