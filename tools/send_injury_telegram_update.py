import os
import sys
import json
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "telegram_config.json")

def load_telegram_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def build_telegram_message():
    lines = []
    lines.append("🚑 *REPORT INFORTUNI SERIE A & GUIDA FANTA MASTER* 🩹")
    lines.append("_Aggiornamento ufficiale al 14 Ottobre verso la 7ª Giornata_\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🟢 *BUONE NOTIZIE: RECUPERATI PER VENERDÌ 16!*")
    lines.append("Hanno smaltito i rispettivi stop fisici e tornano a piena disposizione:")
    lines.append("• *Raspadori* (Atalanta) — Risentimento muscolare superato, arruolabile!")
    lines.append("• *Mbangula* (Bologna) — Stop precauzionale smaltito, disponibile per la 7ª.")
    lines.append("• *Rovella* (Lazio) — Fastidio al polpaccio assorbito, torna in regia.")
    lines.append("• *Zambo Anguissa & Santos A.* (Napoli) — Adduttore e flessori recuperati, convocabili da Conte.")
    lines.append("• *Idzes & Walukiewicz* (Sassuolo) — Lesione e contusione riassorbite, ok per il weekend.")
    lines.append("• *Amorim & Havel* (Genoa) — Entrambi disponibili per venerdì.")
    lines.append("• *Altri rientri confermati in gruppo:* Boga (Juve), Cancellieri, Gudmundsson A., Marusic (Lazio), Sulemana K. (Atalanta), Stulic (Lecce), Fortini (Torino).\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🔴 *I NUOVI STOP & GLI INDISPONIBILI DI GIORNATA:*")
    lines.append("Attenzione a chi NON sarà della partita nel weekend:")
    lines.append("• 🔴 *Kean* (Como) — Problema alla tibia, rientro stimato 20/10: *salta la 7ª giornata*.")
    lines.append("• 🟠 *Stones* (Inter) — Risentimento ai flessori (rientro 17/10): *in forte dubbio* per precauzione.")
    lines.append("• 🔴 *Jones C.* (Inter) — Risentimento all'adduttore: *out fino al 29/10*.")
    lines.append("• 🔴 *Yildiz* (Juventus) — Infortunio al piede sinistro (possibile operazione): *stop fino al 26/11*.")
    lines.append("• 🔴 *Locatelli* (Juventus) — Problema al menisco: *lungo stop fino a Febbraio 2027*.")
    lines.append("• 🔴 *Ekhator* (Juventus) — Lesione bicipite femorale: *out fino al 02/11*.")
    lines.append("• 🔴 *Colombo & Sow* (Genoa) — Distorsione caviglia per Colombo (rientro 01/11), lesione muscolare per Sow (rientro 02/11).")
    lines.append("• 🔴 *Birligea & Grillitsch* (Frosinone) — Entrambi out fino a inizio novembre.")
    lines.append("• 🔴 *Cristante* (Roma) — Lombalgia acuta, rientro stimato 26/10.")
    lines.append("• 🔴 *Svilar* (Roma) — Frattura al dito, out fino al 10/11.")
    lines.append("• 🔴 *Zaniolo* (Udinese) — Sospetto stiramento muscolare, rientro stimato 19/10.")
    lines.append("• 🔴 *Holm* (Bologna) — Operato all'hamstring: *fuori fino a fine Gennaio 2027*.\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("🤖 *CONSIGLIO TATTICO DELL'AI:*")
    lines.append("Verificate subito le vostre formazioni: schierate con serenità i recuperati (Raspadori, Rovella, Anguissa) e proteggete i reparti orfani di top player come Kean e Yildiz con panchine coperte al 100%!")
    lines.append("\n👉 *Consulta la cartella clinica completa con tempi di rientro e indici di fragilità medica:*")
    lines.append("👉 *https://www.fantamasterai.it/infortunati-serie-a/*")

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "🏥 Tabella Infortunati Completa Live", "url": "https://www.fantamasterai.it/infortunati-serie-a/"}
            ],
            [
                {"text": "⚔️ Risolvi Ballottaggi (Chi Schiero)", "url": "https://www.fantamasterai.it/chi-schiero/"},
                {"text": "💡 Consigli Formazione G7", "url": "https://www.fantamasterai.it/consigli-fantacalcio/"}
            ],
            [
                {"text": "🛡️ Schiera il Tuo 11 Migliore", "url": "https://www.fantamasterai.it"}
            ]
        ]
    }

    return "\n".join(lines), reply_markup

def send_telegram_update():
    cfg = load_telegram_config()
    token = cfg.get("bot_token")
    channel_id = cfg.get("channel_id")

    text, reply_markup = build_telegram_message()

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': channel_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': True,
        'reply_markup': reply_markup
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json', 'User-Agent': 'FantaMasterAI/1.0'}
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print("✓ [Telegram] Messaggio inviato con successo sul canale:", res.get('ok'))
            return res
    except Exception as e:
        print(f"❌ [Telegram] Errore invio messaggio: {e}")
        raise e

if __name__ == '__main__':
    send_telegram_update()
