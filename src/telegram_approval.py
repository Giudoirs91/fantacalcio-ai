"""
src/telegram_approval.py
========================
Gestione Bozza e Approvazione Preventiva per Canale Telegram @fantamasterai.
Ogni messaggio viene inviato prima in privato all'amministratore con tasti interattivi
[ ✅ Approva e Pubblica ] e [ ❌ Scarta ].
Solo dopo il clic su "Approva", il post viene inviato sul canale pubblico.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

CONFIG_PATH = os.path.join(ROOT_DIR, "config", "telegram_config.json")
DRAFTS_DIR = os.path.join(ROOT_DIR, "data", "telegram_drafts")
SEEN_UPDATES_PATH = os.path.join(ROOT_DIR, "config", "telegram_seen_updates.json")
os.makedirs(DRAFTS_DIR, exist_ok=True)


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "bot_token": "8790091730:AAHTpEKOcsYEV_XrZYBbmK44bvSsOJH7trU",
        "channel_id": "@fantamasterai",
        "admin_chat_id": 713727654,
        "admin_username": "GiuProf",
        "bot_username": "FantamasterBot"
    }


def call_telegram_api(token, endpoint, payload):
    url = f"https://api.telegram.org/bot{token}/{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "FantaMasterAI-ApprovalBot/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[TelegramApproval] Errore chiamata {endpoint}: {e}")
        return None


def send_draft_for_approval(draft_id, category_title, text, channel_markup=None):
    """
    Invia la bozza formattata in privato all'admin con bottoni di approvazione.
    """
    cfg = load_config()
    token = cfg.get("bot_token")
    admin_id = cfg.get("admin_chat_id")

    if not admin_id:
        print("[TelegramApproval] Nessun admin_chat_id configurato!")
        return False

    # Salva il draft
    draft_file = os.path.join(DRAFTS_DIR, f"draft_{draft_id}.json")
    draft_data = {
        "id": draft_id,
        "category": category_title,
        "text": text,
        "channel_markup": channel_markup,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    with open(draft_file, "w", encoding="utf-8") as f:
        json.dump(draft_data, f, ensure_ascii=False, indent=2)

    admin_text = (
        f"🔔 *[ANTEPRIMA POST IN ATTESA DI APPROVAZIONE]*\n"
        f"📁 *Rubrica:* {category_title}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 *Vuoi pubblicare questo post sul canale @fantamasterai?*"
    )

    admin_markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Approva e Pubblica", "callback_data": f"app_{draft_id}"},
                {"text": "❌ Scarta", "callback_data": f"rej_{draft_id}"}
            ]
        ]
    }

    res = call_telegram_api(token, "sendMessage", {
        "chat_id": admin_id,
        "text": admin_text,
        "parse_mode": "Markdown",
        "reply_markup": admin_markup,
        "disable_web_page_preview": False
    })
    if res and res.get("ok"):
        print(f"✓ Bozza '{category_title}' (ID: {draft_id}) inviata all'admin ({admin_id})!")
        return True
    return False


def publish_draft_to_channel(draft_id):
    """Pubblica sul canale pubblico il draft approvato."""
    cfg = load_config()
    token = cfg.get("bot_token")
    channel_id = cfg.get("channel_id")

    draft_file = os.path.join(DRAFTS_DIR, f"draft_{draft_id}.json")
    if not os.path.exists(draft_file):
        return False, "Bozza non trovata"

    with open(draft_file, "r", encoding="utf-8") as f:
        draft = json.load(f)

    if draft.get("status") == "published":
        return True, "Già pubblicata"

    payload = {
        "chat_id": channel_id,
        "text": draft.get("text", ""),
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    if draft.get("channel_markup"):
        payload["reply_markup"] = draft["channel_markup"]

    res = call_telegram_api(token, "sendMessage", payload)
    if res and res.get("ok"):
        draft["status"] = "published"
        draft["published_at"] = datetime.now().isoformat()
        with open(draft_file, "w", encoding="utf-8") as f:
            json.dump(draft, f, ensure_ascii=False, indent=2)
        print(f"✓ Post {draft_id} pubblicato con successo su {channel_id}!")
        return True, "Pubblicato con successo"
    return False, "Errore durante l'invio su Telegram"


def check_approvals():
    """
    Controlla se l'amministratore ha cliccato su 'Approva' o 'Scarta'
    o ha risposto con 'ok' / 'approva'.
    """
    cfg = load_config()
    token = cfg.get("bot_token")
    admin_id = cfg.get("admin_chat_id")

    # Carica offset degli update
    offset = 0
    if os.path.exists(SEEN_UPDATES_PATH):
        try:
            with open(SEEN_UPDATES_PATH, "r", encoding="utf-8") as f:
                offset = json.load(f).get("offset", 0)
        except Exception:
            pass

    url = f"https://api.telegram.org/bot{token}/getUpdates?offset={offset}&timeout=0"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "FantaMasterAI/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return []

    processed = []
    highest_update_id = offset

    for u in data.get("result", []):
        up_id = u.get("update_id", 0)
        if up_id >= highest_update_id:
            highest_update_id = up_id + 1

        # 1. Callback query (clic sui pulsanti inline)
        cq = u.get("callback_query")
        if cq:
            cq_id = cq.get("id")
            from_id = cq.get("from", {}).get("id")
            c_data = cq.get("data", "")
            msg = cq.get("message", {})
            msg_id = msg.get("message_id")
            chat_id = msg.get("chat", {}).get("id")

            if from_id == admin_id:
                if c_data.startswith("app_"):
                    draft_id = c_data.replace("app_", "")
                    ok, note = publish_draft_to_channel(draft_id)
                    call_telegram_api(token, "answerCallbackQuery", {
                        "callback_query_id": cq_id,
                        "text": "✅ Post approvato e pubblicato su @fantamasterai!",
                        "show_alert": True
                    })
                    # Aggiorna messaggio admin
                    call_telegram_api(token, "editMessageText", {
                        "chat_id": chat_id,
                        "message_id": msg_id,
                        "text": f"✅ *[PUBBLICATO CON SUCCESSO SU @fantamasterai]*\n\nBozza: `{draft_id}`\nData: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                        "parse_mode": "Markdown"
                    })
                    processed.append(("APPROVED", draft_id))

                elif c_data.startswith("rej_"):
                    draft_id = c_data.replace("rej_", "")
                    draft_file = os.path.join(DRAFTS_DIR, f"draft_{draft_id}.json")
                    if os.path.exists(draft_file):
                        with open(draft_file, "r", encoding="utf-8") as f:
                            d = json.load(f)
                        d["status"] = "rejected"
                        with open(draft_file, "w", encoding="utf-8") as f:
                            json.dump(d, f, ensure_ascii=False, indent=2)

                    call_telegram_api(token, "answerCallbackQuery", {
                        "callback_query_id": cq_id,
                        "text": "❌ Post scartato.",
                        "show_alert": False
                    })
                    call_telegram_api(token, "editMessageText", {
                        "chat_id": chat_id,
                        "message_id": msg_id,
                        "text": f"❌ *[POST SCARTATO DALL'AMMINISTRATORE]*\n\nBozza: `{draft_id}`",
                        "parse_mode": "Markdown"
                    })
                    processed.append(("REJECTED", draft_id))

        # 2. Messaggi di testo diretti di risposta ("ok", "approva", "si")
        msg = u.get("message")
        if msg:
            from_id = msg.get("from", {}).get("id")
            text = (msg.get("text") or "").strip().lower()
            if from_id == admin_id and text in ["ok", "approva", "pubblica", "sì", "si"]:
                # Trova l'ultimo draft pending
                pending_drafts = []
                for fname in sorted(os.listdir(DRAFTS_DIR), reverse=True):
                    if fname.startswith("draft_") and fname.endswith(".json"):
                        fpath = os.path.join(DRAFTS_DIR, fname)
                        with open(fpath, "r", encoding="utf-8") as f:
                            d = json.load(f)
                        if d.get("status") == "pending":
                            pending_drafts.append(d)
                            break
                if pending_drafts:
                    d_id = pending_drafts[0]["id"]
                    ok, note = publish_draft_to_channel(d_id)
                    call_telegram_api(token, "sendMessage", {
                        "chat_id": admin_id,
                        "text": f"✅ Ricevuto! Ho pubblicato l'ultima bozza in attesa (`{d_id}`) sul canale @fantamasterai."
                    })
                    processed.append(("APPROVED_TEXT", d_id))

    # Aggiorna offset per non riprocessare vecchi messaggi
    if highest_update_id > offset:
        with open(SEEN_UPDATES_PATH, "w", encoding="utf-8") as f:
            json.dump({"offset": highest_update_id}, f)

    return processed
