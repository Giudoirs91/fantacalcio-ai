import os
import sys
import json
from PIL import Image, ImageDraw, ImageFont

def generate_ig_story_v2():
    # Dimensioni IG Story
    width, height = 1080, 1920
    
    # Carica il background super-premium (generato dall'AI)
    bg_path = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\b4ede5df-8782-4a51-b06d-3ff5ccc2c412\ig_story_bg_1790711411479.jpg"
    try:
        base_img = Image.open(bg_path).convert('RGBA')
        base_img = base_img.resize((width, height))
    except Exception as e:
        print(f"Errore caricamento BG: {e}")
        base_img = Image.new('RGBA', (width, height), color=(10, 15, 25, 255))
        
    overlay = Image.new('RGBA', (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    
    # Carica font moderni (fallback ad arial se non disponibili)
    try:
        font_mega = ImageFont.truetype("arialbd.ttf", 85)
        font_title = ImageFont.truetype("arialbd.ttf", 65)
        font_sub = ImageFont.truetype("arial.ttf", 36)
        font_role = ImageFont.truetype("arialbd.ttf", 32)
        font_pname = ImageFont.truetype("arialbd.ttf", 50)
        font_pteam = ImageFont.truetype("arial.ttf", 30)
        font_ovr = ImageFont.truetype("arialbd.ttf", 40)
    except Exception:
        font_mega = font_title = font_sub = font_role = font_pname = font_pteam = font_ovr = ImageFont.load_default()

    # Dati dei giocatori
    players_path = r"c:\Users\dorsi\.gemini\antigravity-ide\scratch\FantacalcioAi\data\processed\processed_players_master.json"
    dummy_data = [
        {"role": "POR", "name": "DI GREGORIO", "team": "JUVENTUS", "ovr": 88, "color": (245, 158, 11, 255)},
        {"role": "DIF", "name": "DIMARCO", "team": "INTER", "ovr": 92, "color": (16, 185, 129, 255)},
        {"role": "CEN", "name": "KOOPMEINERS", "team": "JUVENTUS", "ovr": 90, "color": (6, 182, 212, 255)},
        {"role": "ATT", "name": "LAUTARO M.", "team": "INTER", "ovr": 95, "color": (239, 68, 68, 255)}
    ]
    
    if os.path.exists(players_path):
        with open(players_path, 'r', encoding='utf-8') as f:
            all_players = json.load(f)
            best = {}
            for p in all_players:
                r = p.get('ruolo')
                if r not in best or p.get('ovr', 0) > best[r].get('ovr', 0):
                    best[r] = p
            if len(best) >= 4:
                dummy_data = [
                    {"role": "POR", "name": best['P']['nome'].upper(), "team": best['P']['squadra'].upper(), "ovr": best['P']['ovr'], "color": (245, 158, 11, 255)},
                    {"role": "DIF", "name": best['D']['nome'].upper(), "team": best['D']['squadra'].upper(), "ovr": best['D']['ovr'], "color": (16, 185, 129, 255)},
                    {"role": "CEN", "name": best['C']['nome'].upper(), "team": best['C']['squadra'].upper(), "ovr": best['C']['ovr'], "color": (6, 182, 212, 255)},
                    {"role": "ATT", "name": best['A']['nome'].upper(), "team": best['A']['squadra'].upper(), "ovr": best['A']['ovr'], "color": (239, 68, 68, 255)}
                ]

    # Titolo (Testo Glowing simulato tramite drop shadow)
    draw.text((width//2 + 3, 150 + 3), "Fanta Master AI", font=font_sub, fill=(0,0,0,180), anchor="mm")
    draw.text((width//2, 150), "Fanta Master AI", font=font_sub, fill=(0, 230, 118, 255), anchor="mm")
    
    draw.text((width//2, 230), "TOP 11 ALGORITMO", font=font_mega, fill=(255, 255, 255, 255), anchor="mm")
    draw.text((width//2, 300), "PREVISIONI GIORNATA 5", font=font_sub, fill=(180, 200, 230, 255), anchor="mm")
    
    # Layout box giocatori (Glassmorphism)
    y_start = 420
    box_height = 240
    spacing = 50
    
    for i, item in enumerate(dummy_data):
        y1 = y_start + i * (box_height + spacing)
        y2 = y1 + box_height
        
        # Sfondo Semi-trasparente (Glass)
        draw.rounded_rectangle([70, y1, width-70, y2], radius=35, fill=(15, 25, 45, 160), outline=(255, 255, 255, 40), width=2)
        
        # Linea accento laterale
        draw.rounded_rectangle([90, y1+40, 96, y2-40], radius=3, fill=item["color"])
        
        # Nome e squadra
        draw.text((130, y1+70), item["name"], font=font_pname, fill=(255, 255, 255, 255), anchor="ls")
        draw.text((130, y1+125), f"[{item['role']}] {item['team']}", font=font_role, fill=item["color"], anchor="ls")
        
        # Cerchio OVR
        ovr_center_x = width - 180
        ovr_center_y = y1 + (box_height // 2)
        draw.ellipse([ovr_center_x-60, ovr_center_y-60, ovr_center_x+60, ovr_center_y+60], fill=(0,0,0,100), outline=item["color"], width=6)
        draw.text((ovr_center_x, ovr_center_y-10), str(item["ovr"]), font=font_mega, fill=(255, 255, 255, 255), anchor="mm")
        draw.text((ovr_center_x, ovr_center_y+45), "OVR", font=font_role, fill=(200, 200, 200, 255), anchor="mm")

    # Footer
    footer_y = 1720
    draw.rounded_rectangle([150, footer_y, width-150, footer_y+100], radius=50, fill=(0, 230, 118, 255))
    draw.text((width//2, footer_y+50), "SCOPRI TUTTI SU FANTAMASTERAI.IT", font=font_role, fill=(10, 15, 25, 255), anchor="mm")

    # Composite
    final_img = Image.alpha_composite(base_img, overlay)
    
    # Save
    final_img = final_img.convert('RGB')
    out_path = r"C:\Users\dorsi\.gemini\antigravity-ide\brain\b4ede5df-8782-4a51-b06d-3ff5ccc2c412\ig_preview_v2.png"
    final_img.save(out_path, quality=95)
    print(f"Generato {out_path}")

if __name__ == '__main__':
    generate_ig_story_v2()
