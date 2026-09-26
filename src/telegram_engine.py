"""
telegram_engine.py - Motore Telegram per Canale & Notifiche Fantacalcio
=======================================================================
Invia automaticamente prima dell'anticipo del venerdì (entro le ore 12:30):
1. Card Grafica Ufficiale HD (PNG 1080x1080) generata al volo con Pillow.
2. Messaggio di Briefing Tattico con i consigliati ruolo per ruolo, ballottaggi caldi
   e link diretti agli strumenti del portale fantamasterai.it.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

CONFIG_PATH = os.path.join(ROOT_DIR, "config", "telegram_config.json")
PLAYERS_PATH = os.path.join(ROOT_DIR, "data", "processed", "processed_players_master.json")
CALENDAR_PATH = os.path.join(ROOT_DIR, "config", "calendario_serie_a_2026_27.json")
TEAM_STATS_PATH = os.path.join(ROOT_DIR, "data", "raw", "fotmob_team_stats_2026_27.json")
OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "processed")


def load_telegram_config():
    """Carica la configurazione del bot Telegram."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "bot_token": "8790091730:AAHTpEKOcsYEV_XrZYBbmK44bvSsOJH7trU",
        "channel_id": "@fantamasterai",
        "scheduled_day": "Friday",
        "scheduled_time": "12:30",
        "bot_username": "FantamasterBot"
    }


def get_upcoming_round():
    """Rileva il turno di Serie A in arrivo dai dati del database."""
    if not os.path.exists(PLAYERS_PATH):
        return 6
    with open(PLAYERS_PATH, 'r', encoding='utf-8') as f:
        players = json.load(f)
    played = set()
    for p in players:
        for v in (p.get('voti_dettaglio_2627') or []):
            g = v.get('giornata')
            if g and v.get('voto') is not None:
                played.add(g)
    return max(played) + 1 if played else 6


def get_round_fixtures(round_num):
    """Estrae la mappa delle partite per la giornata indicata."""
    if not os.path.exists(CALENDAR_PATH):
        return {}, '', []
    with open(CALENDAR_PATH, 'r', encoding='utf-8') as f:
        calendar = json.load(f)
    r_data = next((r for r in calendar if r.get('giornata') == round_num), None)
    if not r_data:
        return {}, '', []
    
    fixture_map = {}
    matches_list = r_data.get('matches', [])
    round_date = r_data.get('date', '')
    for m in matches_list:
        fixture_map[m['home']] = {'opp': m['away'], 'is_home': True, 'label': f"vs {m['away']} 🏠"}
        fixture_map[m['away']] = {'opp': m['home'], 'is_home': False, 'label': f"@ {m['home']} ✈️"}
    return fixture_map, round_date, matches_list


def get_top_advice_by_role(round_num):
    """Calcola i 4 top consigliati dell'AI per ruolo per la giornata."""
    from src.matchday_evaluator import calculate_advice_score
    if not os.path.exists(PLAYERS_PATH):
        return {}
    with open(PLAYERS_PATH, 'r', encoding='utf-8') as f:
        players = json.load(f)
    team_stats = {}
    if os.path.exists(TEAM_STATS_PATH):
        with open(TEAM_STATS_PATH, 'r', encoding='utf-8') as f:
            team_stats = json.load(f)

    fixture_map, _, _ = get_round_fixtures(round_num)
    by_role = {'P': [], 'D': [], 'C': [], 'A': []}

    for p in players:
        team = p.get('team')
        fix = fixture_map.get(team)
        if fix and not p.get('is_injured') and float(p.get('titolarita', 50)) >= 50:
            score = calculate_advice_score(p, fix, team_stats)
            by_role[p.get('role', 'C')].append({
                'player': p,
                'score': score,
                'fixture': fix
            })

    top_advice = {}
    for role, plist in by_role.items():
        plist.sort(key=lambda x: -x['score'])
        top_advice[role] = plist[:3]
    return top_advice


def generate_telegram_card_image(round_num, out_filename=None):
    """
    Genera un'immagine grafica ad alta risoluzione (1080x1080)
    in stile social card con i consigliati ufficiali per Telegram.
    """
    if out_filename is None:
        out_filename = os.path.join(OUTPUT_DIR, f"telegram_briefing_g{round_num}.png")

    top_advice = get_top_advice_by_role(round_num)
    _, round_date, _ = get_round_fixtures(round_num)

    W, H = 1080, 1080
    img = Image.new('RGB', (W, H), color='#080b12')
    draw = ImageDraw.Draw(img)

    # Sfondo sfumato e griglia cyber
    for y in range(H):
        ratio = y / H
        r = int(8 + (18 - 8) * ratio)
        g = int(11 + (24 - 11) * ratio)
        b = int(18 + (38 - 18) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Pattern griglia sottile
    for x in range(0, W, 40):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 5))
    for y in range(0, H, 40):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 5))

    # Effetto neon / aura superiore
    draw.ellipse([(-200, -200), (W + 200, 300)], fill=(56, 189, 248, 25))
    draw.ellipse([(W // 2 - 300, H - 300), (W // 2 + 300, H + 300)], fill=(168, 85, 247, 25))

    # Font di default
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 52)
        font_sub = ImageFont.truetype("arial.ttf", 26)
        font_badge = ImageFont.truetype("arialbd.ttf", 22)
        font_role = ImageFont.truetype("arialbd.ttf", 30)
        font_pname = ImageFont.truetype("arialbd.ttf", 32)
        font_pteam = ImageFont.truetype("arial.ttf", 24)
        font_footer = ImageFont.truetype("arialbd.ttf", 24)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_badge = font_title
        font_role = font_title
        font_pname = font_title
        font_pteam = font_title
        font_footer = font_title

    # Header Card
    # Pillola superiore
    pill_text = f"IL BRIEFING DEL VENERDI (ORE 12:30) • SERIE A 2026/27"
    draw.rounded_rectangle([60, 45, 800, 88], radius=20, fill=(245, 158, 11), outline="#fbbf24", width=2)
    draw.text((85, 54), f">> {pill_text}", font=font_badge, fill="#0f172a")

    # Titolo Principale
    draw.text((60, 108), f"I CONSIGLIATI AI — GIORNATA {round_num}", font=font_title, fill="#ffffff")
    draw.text((60, 172), f"Previsioni ufficiali prima dell'anticipo • Data Turno: {round_date or 'Weekend di Campionato'}", font=font_sub, fill="#94a3b8")

    # 4 Riquadri dei Ruoli (2x2 Grid)
    # Riquadro P (alto sin), D (alto dx), C (basso sin), A (basso dx)
    roles_meta = [
        {'role': 'P', 'label': '[POR] PORTIERE CONSIGLIATO', 'color': '#f59e0b', 'box': [60, 230, 520, 560]},
        {'role': 'D', 'label': '[DIF] DIFENSORE CONSIGLIATO', 'color': '#10b981', 'box': [560, 230, 1020, 560]},
        {'role': 'C', 'label': '[CEN] CENTROCAMPISTA TOP', 'color': '#06b6d4', 'box': [60, 590, 520, 920]},
        {'role': 'A', 'label': '[ATT] ATTACCANTE BOMBER', 'color': '#ef4444', 'box': [560, 590, 1020, 920]}
    ]

    for rm in roles_meta:
        box = rm['box']
        r = rm['role']
        # Sfondo card ruolo
        draw.rounded_rectangle(box, radius=18, fill=(18, 24, 42), outline=rm['color'], width=2)

        # Header card ruolo
        draw.rectangle([box[0] + 1, box[1] + 1, box[2] - 1, box[1] + 55], fill=(255, 255, 255, 12))
        draw.text((box[0] + 20, box[1] + 14), rm['label'], font=font_role, fill=rm['color'])

        # Prendi i primi 2 consigliati per questo ruolo
        items = top_advice.get(r, [])
        if items:
            # 1° Consigliato
            p1 = items[0]['player']
            f1 = items[0]['fixture']
            y_base = box[1] + 75
            
            # Badge OVR
            draw.rounded_rectangle([box[0] + 20, y_base, box[0] + 85, y_base + 60], radius=10, fill=(30, 41, 59), outline=rm['color'], width=2)
            draw.text((box[0] + 26, y_base + 12), str(p1.get('ovr', 80)), font=font_role, fill="#ffffff")

            # Nome e squadra
            draw.text((box[0] + 100, y_base + 4), p1.get('name', ''), font=font_pname, fill="#ffffff")
            clean_f1 = f1.get('label', '').replace('🏠', '(Casa)').replace('✈️', '(Trasf.)')
            match_txt = f"{p1.get('team', '')} {clean_f1}"
            draw.text((box[0] + 100, y_base + 38), match_txt, font=font_pteam, fill="#94a3b8")

            # 2° Consigliato
            if len(items) > 1:
                p2 = items[1]['player']
                f2 = items[1]['fixture']
                y_base2 = box[1] + 180
                draw.line([(box[0] + 20, box[1] + 160), (box[2] - 20, box[1] + 160)], fill=(255, 255, 255, 25))

                draw.rounded_rectangle([box[0] + 20, y_base2, box[0] + 85, y_base2 + 60], radius=10, fill=(20, 27, 40), outline="#64748b", width=1)
                draw.text((box[0] + 26, y_base2 + 14), str(p2.get('ovr', 75)), font=font_badge, fill="#cbd5e1")

                draw.text((box[0] + 100, y_base2 + 4), p2.get('name', ''), font=font_pname, fill="#f1f5f9")
                clean_f2 = f2.get('label', '').replace('🏠', '(Casa)').replace('✈️', '(Trasf.)')
                match_txt2 = f"{p2.get('team', '')} {clean_f2}"
                draw.text((box[0] + 100, y_base2 + 38), match_txt2, font=font_pteam, fill="#94a3b8")

    # Footer Barra
    draw.rounded_rectangle([60, 955, 1020, 1025], radius=16, fill=(12, 16, 28), outline="#38bdf8", width=2)
    footer_text = "Risolvi i tuoi dubbi 1vs1 su: fantamasterai.it/chi-schiero/  •  Fanta Master AI"
    draw.text((80, 976), footer_text, font=font_footer, fill="#38bdf8")

    img.save(out_filename, 'PNG')
    print(f"✓ [TelegramEngine] Social Card HD generata: {out_filename}")
    return out_filename


def build_friday_briefing_text(round_num):
    """Costruisce il messaggio testuale del briefing con formattazione Telegram Markdown."""
    top_advice = get_top_advice_by_role(round_num)
    _, round_date, matches = get_round_fixtures(round_num)

    p_gk = top_advice.get('P', [{}])[0].get('player', {}) if top_advice.get('P') else {}
    f_gk = top_advice.get('P', [{}])[0].get('fixture', {}) if top_advice.get('P') else {}

    p_df = top_advice.get('D', [{}])[0].get('player', {}) if top_advice.get('D') else {}
    f_df = top_advice.get('D', [{}])[0].get('fixture', {}) if top_advice.get('D') else {}

    p_mf = top_advice.get('C', [{}])[0].get('player', {}) if top_advice.get('C') else {}
    f_mf = top_advice.get('C', [{}])[0].get('fixture', {}) if top_advice.get('C') else {}

    p_fw = top_advice.get('A', [{}])[0].get('player', {}) if top_advice.get('A') else {}
    f_fw = top_advice.get('A', [{}])[0].get('fixture', {}) if top_advice.get('A') else {}

    msg = f"⚽ *IL BRIEFING DEL VENERDÌ — GIORNATA {round_num}* 📅\n"
    msg += f"_(Inviato puntuale alle ore 12:30 prima degli anticipi)_\n\n"
    msg += f"Ecco i consigli del nostro algoritmo predittivo per schierare la formazione ideale del weekend:\n\n"

    msg += f"🧤 *PORTIERE TOP:* *{p_gk.get('name', 'N/D')}* ({p_gk.get('team', '')})\n"
    msg += f"   ↳ _{f_gk.get('label', '')} • OVR {p_gk.get('ovr', 80)}: garanzia di affidabilità tra i pali_\n\n"

    msg += f"🛡️ *DIFENSORE DA MODIFICATORE:* *{p_df.get('name', 'N/D')}* ({p_df.get('team', '')})\n"
    msg += f"   ↳ _{f_df.get('label', '')} • OVR {p_df.get('ovr', 80)}: voti costanti e respinte difensive_\n\n"

    msg += f"🪄 *CENTROCAMPISTA DA BONUS:* *{p_mf.get('name', 'N/D')}* ({p_mf.get('team', '')})\n"
    msg += f"   ↳ _{f_mf.get('label', '')} • OVR {p_mf.get('ovr', 80)}: inserimenti, piazzati ed Expected Assist_\n\n"

    msg += f"⚡ *ATTACCANTE BOMBER:* *{p_fw.get('name', 'N/D')}* ({p_fw.get('team', '')})\n"
    msg += f"   ↳ _{f_fw.get('label', '')} • OVR {p_fw.get('ovr', 90)}: volume di xG e rigori nei piedi_\n\n"

    msg += f"══════════════════════════════\n"
    msg += f"⚔️ *DUBBI DI FORMAZIONE? CHI SCHIERO?*\n"
    msg += f"Risolvi i tuoi ballottaggi 1vs1 testa a testa gratis con percentuali, motivazioni AI e pro/contro:\n"
    msg += f"👉 *https://fantamasterai.it/chi-schiero/*\n\n"

    msg += f"📊 *TUTTI I CONSIGLIATI DELLA GIORNATA {round_num}:*\n"
    msg += f"👉 *https://fantamasterai.it/consigli-fantacalcio/*"
    return msg


def send_telegram_photo(token, chat_id, photo_path, caption=None):
    """Invia un'immagine con didascalia su un canale o chat Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    with open(photo_path, 'rb') as f:
        file_bytes = f.read()

    boundary = '----FantaMasterAIBoundary' + datetime.now().strftime('%Y%m%d%H%M%S')
    body = bytearray()

    # chat_id
    body.extend(f'--{boundary}\r\n'.encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="chat_id"\r\n\r\n{chat_id}\r\n'.encode('utf-8'))

    # caption
    if caption:
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n'.encode('utf-8'))
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="parse_mode"\r\n\r\nMarkdown\r\n'.encode('utf-8'))

    # photo
    filename = os.path.basename(photo_path)
    body.extend(f'--{boundary}\r\n'.encode('utf-8'))
    body.extend(f'Content-Disposition: form-data; name="photo"; filename="{filename}"\r\n'.encode('utf-8'))
    body.extend(b'Content-Type: image/png\r\n\r\n')
    body.extend(file_bytes)
    body.extend(b'\r\n')

    # closing boundary
    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'User-Agent': 'FantaMasterAI-TelegramBot/1.0'
        }
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print("✓ [TelegramEngine] Immagine inviata con successo:", data.get('ok'))
            return data
    except Exception as e:
        print(f"❌ [TelegramEngine] Errore invio foto: {e}")
        return None


def send_telegram_message(token, chat_id, text):
    """Invia un messaggio di testo con formattazione Markdown."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json', 'User-Agent': 'FantaMasterAI/1.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            print("✓ [TelegramEngine] Messaggio inviato con successo:", res.get('ok'))
            return res
    except Exception as e:
        print(f"❌ [TelegramEngine] Errore invio messaggio: {e}")
        return None


def execute_friday_briefing(channel_id=None, dry_run=False):
    """
    Esegue il workflow completo del venerdì:
    1. Calcola il turno e i consigli.
    2. Genera la social card PNG.
    3. Spedisce l'immagine e il testo al canale Telegram.
    """
    config = load_telegram_config()
    token = config.get("bot_token")
    target_channel = channel_id or config.get("channel_id")
    round_num = get_upcoming_round()

    print(f"=== [TelegramEngine] Avvio Briefing Venerdì (G{round_num}) per {target_channel} ===")

    card_path = generate_telegram_card_image(round_num)
    briefing_text = build_friday_briefing_text(round_num)

    if dry_run:
        print("\n--- TEST / ANTEPRIMA MESSAGGIO TELEGRAM ---")
        print(briefing_text)
        print(f"Immagine generata in: {card_path}")
        print("--- FINE ANTEPRIMA (Nessun invio API eseguito) ---\n")
        return {"ok": True, "dry_run": True, "card": card_path}

    # Invia prima la foto con una caption sintetica
    caption = f"🎯 *FANTA MASTER AI — I CONSIGLIATI DELLA GIORNATA {round_num}* 📅\n_Briefing ufficiale del Venerdì ore 12:30 prima degli anticipi_"
    photo_res = send_telegram_photo(token, target_channel, card_path, caption=caption)

    # Invia il messaggio dettagliato con tutti i ruoli e i link
    msg_res = send_telegram_message(token, target_channel, briefing_text)

    return {
        "photo_result": photo_res,
        "message_result": msg_res,
        "round": round_num
    }


if __name__ == '__main__':
    # Esegue in modalità anteprima (dry run) o con invio effettivo
    execute_friday_briefing(dry_run=True)
