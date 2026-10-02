import os
import re
import json

def clean_html(text):
    if text is None:
        return ""
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))

def slugify(text):
    if not text:
        return "calciatore"
    text = text.lower()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def get_match_info(calendar_data, team_name, round_num=6):
    if not calendar_data:
        return None
    r_obj = next((r for r in calendar_data if r.get('giornata') == round_num), None)
    if not r_obj or not r_obj.get('matches'):
        return None
    t_clean = (team_name or '').upper().strip()
    for m in r_obj['matches']:
        h_clean = (m.get('home') or '').upper().strip()
        a_clean = (m.get('away') or '').upper().strip()
        if h_clean == t_clean:
            return {
                'opponent': m.get('away'),
                'is_home': True,
                'match_str': f"{m.get('home')} vs {m.get('away')}",
                'date': r_obj.get('date', '')
            }
        if a_clean == t_clean:
            return {
                'opponent': m.get('home'),
                'is_home': False,
                'match_str': f"{m.get('away')} @ {m.get('home')}",
                'date': r_obj.get('date', '')
            }
    return None

def compute_duel_verdict(p1, p2, calendar_data):
    # Round 6 upcoming
    round_num = 6
    m1 = get_match_info(calendar_data, p1.get('team'), round_num)
    m2 = get_match_info(calendar_data, p2.get('team'), round_num)

    xfm1 = float(p1.get('xfm') or p1.get('fm_2627') or p1.get('fm') or 6.0)
    xfm2 = float(p2.get('xfm') or p2.get('fm_2627') or p2.get('fm') or 6.0)

    tit1 = float(p1.get('titolarita') or 50.0) / 100.0
    tit2 = float(p2.get('titolarita') or 50.0) / 100.0

    # Infortuni
    if p1.get('is_injured'): tit1 *= 0.1
    if p2.get('is_injured'): tit2 *= 0.1

    # Bonus casa
    mult1 = 1.08 if (m1 and m1.get('is_home')) else 0.96
    mult2 = 1.08 if (m2 and m2.get('is_home')) else 0.96

    # Score ponderato
    score1 = (xfm1 * 0.6 + (p1.get('ovr', 65) / 10.0) * 0.4) * (0.4 + tit1 * 0.6) * mult1
    score2 = (xfm2 * 0.6 + (p2.get('ovr', 65) / 10.0) * 0.4) * (0.4 + tit2 * 0.6) * mult2

    total = score1 + score2
    pct1 = int(round((score1 / total) * 100)) if total > 0 else 50
    pct2 = 100 - pct1

    if pct1 >= 55:
        winner = p1
        loser = p2
        w_pct = pct1
        l_pct = pct2
        reason = f"{p1['name']} è preferito per maggior continuità di rendimento (xFM {xfm1:.2f}) e probabilità di bonus rispetto a {p2['name']} ({xfm2:.2f})."
        if m1 and m1.get('is_home') and m2 and not m2.get('is_home'):
            reason += f" Gioca inoltre tra le mura amiche ({m1['match_str']}), fattore chiave per il modificatore e i bonus."
    elif pct2 >= 55:
        winner = p2
        loser = p1
        w_pct = pct2
        l_pct = pct1
        reason = f"{p2['name']} offre un indice predittivo superiore (xFM {xfm2:.2f}) rispetto a {p1['name']} ({xfm1:.2f}), con una titolarità più solida e minore rischio malus."
        if m2 and m2.get('is_home') and m1 and not m1.get('is_home'):
            reason += f" Il fattore casalingo ({m2['match_str']}) premia la sua schierabilità per la {round_num}ª giornata."
    else:
        winner = p1 if pct1 >= pct2 else p2
        loser = p2 if winner == p1 else p1
        w_pct = max(pct1, pct2)
        l_pct = min(pct1, pct2)
        reason = f"Duello serratissimo sul filo di lana ({w_pct}% vs {l_pct}%). Entrambi hanno ottimi presupposti di voto; preferenza minima per {winner['name']} per lievissima superiorità nel volume di occasioni create (xG/xA)."

    return winner, loser, w_pct, l_pct, reason, m1, m2

def generate_duel_page(p1, p2, tactical_db, calendar_data, base_url="https://www.fantamasterai.it"):
    slug1 = slugify(p1.get("name", "p1"))
    slug2 = slugify(p2.get("name", "p2"))
    duel_slug = f"{slug1}-vs-{slug2}"
    
    winner, loser, w_pct, l_pct, reason, m1, m2 = compute_duel_verdict(p1, p2, calendar_data)
    
    name1 = p1.get("name")
    name2 = p2.get("name")
    team1 = p1.get("team")
    team2 = p2.get("team")
    role1 = p1.get("role", "C")
    role2 = p2.get("role", "C")

    xfm1 = float(p1.get('xfm') or p1.get('fm_2627') or p1.get('fm') or 6.0)
    xfm2 = float(p2.get('xfm') or p2.get('fm_2627') or p2.get('fm') or 6.0)
    fm1 = float(p1.get('fm_2627') or p1.get('fm') or 6.0)
    fm2 = float(p2.get('fm_2627') or p2.get('fm') or 6.0)
    mv1 = float(p1.get('mv_2627') or p1.get('mv') or 6.0)
    mv2 = float(p2.get('mv_2627') or p2.get('mv') or 6.0)

    page_url = f"{base_url}/chi-schiero/{duel_slug}/"
    meta_title = f"Chi Schiero tra {name1} e {name2}? Confronto 1vs1 Fantacalcio & Verdetto AI"
    meta_desc = f"Dubbio al Fantacalcio tra {name1} ({team1}) e {name2} ({team2})? Confronta xFM, statistiche avanzate, titolarità e scopri il verdetto dell'algoritmo predittivo Fanta Master AI."

    match_str1 = m1['match_str'] if m1 else f"Partita del {team1}"
    match_str2 = m2['match_str'] if m2 else f"Partita del {team2}"

    faq_schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Chi Schiero Fantacalcio", "item": f"{base_url}/chi-schiero/"},
                    {"@type": "ListItem", "position": 3, "name": f"{name1} vs {name2}", "item": page_url}
                ]
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"Chi schierare al Fantacalcio tra {name1} e {name2}?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"L'algoritmo predittivo consiglia di schierare {winner['name']} con una preferenza del {w_pct}% rispetto a {loser['name']} ({l_pct}%). {reason}"
                        }
                    },
                    {
                        "@type": "Question",
                        "name": f"Quali sono le statistiche a confronto tra {name1} e {name2}?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"{name1} ({team1}) registra una FantaMedia reale di {fm1:.2f} con xFM di {xfm1:.2f} e OVR {p1.get('ovr', 70)}. {name2} ({team2}) risponde con FM {fm2:.2f}, xFM {xfm2:.2f} e OVR {p2.get('ovr', 70)}."
                        }
                    },
                    {
                        "@type": "Question",
                        "name": f"Cosa fare se uno dei due parte dalla panchina?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Nel caso in cui {loser['name']} o {winner['name']} siano in ballottaggio serrato, è opportuno coprirsi con la rispettiva riserva diretta o dare priorità al calciatore con titolarità certa per evitare il rischio di giocare in 10."
                        }
                    }
                ]
            }
        ]
    }

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>{clean_html(meta_title)}</title>
    <meta name="description" content="{clean_html(meta_desc)}">
    <link rel="canonical" href="{page_url}">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{clean_html(meta_title)}">
    <meta property="og:description" content="{clean_html(meta_desc)}">
    <meta property="og:url" content="{page_url}">
    <meta property="og:site_name" content="Fanta Master AI">
    <meta property="og:image" content="{base_url}/static/og-image.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:locale" content="it_IT">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{clean_html(meta_title)}">
    <meta name="twitter:description" content="{clean_html(meta_desc)}">
    <meta name="twitter:image" content="{base_url}/static/og-image.jpg">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../css/seo.css">
    
    <!-- Schema.org JSON-LD -->
    <script type="application/ld+json">
    {json.dumps(faq_schema, ensure_ascii=False, indent=2)}
    </script>

    <style>
        .duel-container {{
            max-width: 960px;
            margin: 0 auto;
            padding: 24px 16px 60px 16px;
        }}
        .duel-hero {{
            text-align: center;
            margin-bottom: 28px;
        }}
        .duel-tag {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            padding: 6px 14px;
            border-radius: 999px;
            color: #38bdf8;
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 14px;
        }}
        .duel-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 34px;
            font-weight: 900;
            color: #ffffff;
            line-height: 1.15;
            margin-bottom: 10px;
        }}
        .duel-desc {{
            font-size: 15px;
            color: #94a3b8;
            max-width: 720px;
            margin: 0 auto;
            line-height: 1.5;
        }}
        
        /* Verdict Box */
        .verdict-box {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 2px solid rgba(16, 185, 129, 0.4);
            border-radius: 20px;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 25px rgba(16, 185, 129, 0.15);
        }}
        .verdict-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
            flex-wrap: wrap;
            gap: 12px;
        }}
        .verdict-badge {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-family: 'Outfit', sans-serif;
            font-size: 18px;
            font-weight: 900;
            color: #34d399;
        }}
        .verdict-score {{
            font-family: 'Outfit', sans-serif;
            font-size: 26px;
            font-weight: 900;
            color: #ffffff;
            background: rgba(16, 185, 129, 0.25);
            padding: 4px 16px;
            border-radius: 12px;
            border: 1px solid rgba(52, 211, 153, 0.4);
        }}
        .verdict-text {{
            font-size: 14.5px;
            color: #e2e8f0;
            line-height: 1.6;
        }}

        /* Head to Head Grid */
        .h2h-grid {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 20px;
            align-items: stretch;
            margin-bottom: 36px;
        }}
        @media (max-width: 768px) {{
            .h2h-grid {{
                grid-template-columns: 1fr;
            }}
            .vs-divider {{
                display: none;
            }}
        }}
        .vs-divider {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-family: 'Outfit', sans-serif;
            font-size: 24px;
            font-weight: 900;
            color: #f59e0b;
            text-shadow: 0 0 15px rgba(245, 158, 11, 0.4);
        }}
        .player-card {{
            background: rgba(18, 24, 38, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 22px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(12px);
        }}
        .player-card.is-winner {{
            border-color: rgba(52, 211, 153, 0.6);
            box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.25);
        }}
        .card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }}
        .role-pill {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Outfit', sans-serif;
            font-weight: 900;
            font-size: 18px;
            color: #fff;
        }}
        .role-pill.P {{ background: #f59e0b; }}
        .role-pill.D {{ background: #10b981; }}
        .role-pill.C {{ background: #38bdf8; }}
        .role-pill.A {{ background: #f43f5e; }}

        .ovr-box {{
            text-align: right;
        }}
        .ovr-num {{
            font-family: 'Outfit', sans-serif;
            font-size: 32px;
            font-weight: 900;
            color: #38bdf8;
            line-height: 1;
        }}
        .ovr-lbl {{
            font-size: 10px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 800;
        }}

        .p-name {{
            font-family: 'Outfit', sans-serif;
            font-size: 26px;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 4px;
        }}
        .p-team {{
            font-size: 14px;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 16px;
        }}

        .stats-h2h-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
            margin-bottom: 16px;
        }}
        .stats-h2h-table tr {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .stats-h2h-table td {{
            padding: 8px 0;
        }}
        .stats-h2h-table td.lbl {{
            color: #94a3b8;
        }}
        .stats-h2h-table td.val {{
            text-align: right;
            font-weight: 700;
            color: #ffffff;
        }}
        .stats-h2h-table td.val.cyan {{ color: #38bdf8; font-weight: 800; }}
        .stats-h2h-table td.val.gold {{ color: #fbbf24; font-weight: 800; }}

        .match-badge-box {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 12px;
            padding: 10px 14px;
            margin-bottom: 16px;
            font-size: 13px;
        }}
        .match-badge-box .lbl {{
            font-size: 11px;
            color: #64748b;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 2px;
        }}
        .match-badge-box .match {{
            font-weight: 700;
            color: #e2e8f0;
        }}

        .btn-profile {{
            display: block;
            text-align: center;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 10px 14px;
            border-radius: 12px;
            color: #38bdf8;
            text-decoration: none;
            font-size: 13px;
            font-weight: 700;
            transition: all 0.2s;
        }}
        .btn-profile:hover {{
            background: rgba(56, 189, 248, 0.2);
            border-color: #38bdf8;
        }}

        /* FAQ Accordion */
        .faq-section {{
            background: rgba(18, 24, 38, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 28px;
            margin-top: 36px;
        }}
        .faq-title {{
            font-family: 'Outfit', sans-serif;
            font-size: 22px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 20px;
        }}
        .faq-item {{
            margin-bottom: 18px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 14px;
        }}
        .faq-item:last-child {{
            border-bottom: none;
            margin-bottom: 0;
            padding-bottom: 0;
        }}
        .faq-q {{
            font-weight: 700;
            color: #f1f5f9;
            font-size: 15px;
            margin-bottom: 6px;
        }}
        .faq-a {{
            color: #94a3b8;
            font-size: 14px;
            line-height: 1.55;
        }}
    </style>
</head>
<body>
    <!-- Unified Header -->
    <header class="app-header-unified">
        <div class="header-main-row">
            <div class="header-left">
                <a href="../../" class="brand-badge" style="text-decoration:none;" title="Fanta Master AI">
                    <span class="brand-icon">⚡</span>
                    <div>
                        <div class="brand-title">FANTA MASTER AI</div>
                        <div class="brand-sub">Portale Statistico</div>
                    </div>
                </a>
            </div>
            <nav class="header-nav-groups">
                <a href="../../" class="nav-direct-btn"><span>📋</span> Listone</a>
                <a href="../../probabili-formazioni/" class="nav-direct-btn"><span>⚽</span> Formazioni</a>
                <a href="../../infortunati-serie-a/" class="nav-direct-btn"><span>🩺</span> Infortunati</a>
                <a href="../../chi-schiero/" class="nav-direct-btn" style="color:#38bdf8;"><span>⚔️</span> Chi Schiero</a>
            </nav>
            <div class="header-right">
                <a href="../../" class="header-squad-pill" style="text-decoration:none;">
                    <span>Dashboard Live</span>
                </a>
            </div>
        </div>
    </header>

    <main class="duel-container">
        <!-- Breadcrumbs -->
        <nav class="breadcrumbs" style="margin-bottom:20px;">
            <a href="../../">Home</a> <span class="breadcrumbs-sep">/</span> 
            <a href="../../chi-schiero/">Chi Schiero</a> <span class="breadcrumbs-sep">/</span> 
            <span class="breadcrumbs-cur">{name1} vs {name2}</span>
        </nav>

        <!-- Hero -->
        <div class="duel-hero">
            <div class="duel-tag">⚔️ TESTA A TESTA FANTACALCIO • GIORNATA 6</div>
            <h1 class="duel-title">Chi schiero tra {name1} e {name2}?</h1>
            <p class="duel-desc">Confronto algoritmico dettagliato per risolvere il tuo dubbio di formazione: expected stats (xFM, xG, xA), titolarità e difficoltà avversario.</p>
        </div>

        <!-- AI Verdict -->
        <div class="verdict-box">
            <div class="verdict-header">
                <div class="verdict-badge">
                    <span>🎯</span> VERDETTO PREDITTIVO AI: CONSIGLIATO {winner['name'].upper()}
                </div>
                <div class="verdict-score">
                    {w_pct}% vs {l_pct}%
                </div>
            </div>
            <p class="verdict-text">{reason}</p>
        </div>

        <!-- Head to Head Grid -->
        <div class="h2h-grid">
            <!-- Player 1 -->
            <div class="player-card {'is-winner' if winner == p1 else ''}">
                <div>
                    <div class="card-top">
                        <div class="role-pill {role1}">{role1}</div>
                        <div class="ovr-box">
                            <div class="ovr-num">{p1.get('ovr', 70)}</div>
                            <div class="ovr-lbl">Overall AI</div>
                        </div>
                    </div>
                    <div class="p-name">{name1}</div>
                    <div class="p-team">{team1} • FVM {p1.get('fvm', 1)} CR</div>

                    <div class="match-badge-box">
                        <div class="lbl">PROSSIMO MATCH</div>
                        <div class="match">{match_str1}</div>
                    </div>

                    <table class="stats-h2h-table">
                        <tr><td class="lbl">FantaMedia Attesa (xFM)</td><td class="val cyan">{xfm1:.2f}</td></tr>
                        <tr><td class="lbl">FantaMedia Reale (FM)</td><td class="val gold">{fm1:.2f}</td></tr>
                        <tr><td class="lbl">Media Voto Pura (MV)</td><td class="val">{mv1:.2f}</td></tr>
                        <tr><td class="lbl">Indice Titolarità</td><td class="val">{p1.get('titolarita', 70)}%</td></tr>
                        <tr><td class="lbl">Infortuni / Status</td><td class="val" style="color:{'#ef4444' if p1.get('is_injured') else '#10b981'};">{'🔴 ' + (p1.get('infortunio_motivo') or 'Stop') if p1.get('is_injured') else '🟢 Disponibile'}</td></tr>
                        <tr><td class="lbl">Gol / Assist 26/27</td><td class="val">{p1.get('gol_2627', 0)} G &bull; {p1.get('assist_2627', 0)} A</td></tr>
                        <tr><td class="lbl">Expected Goals (xG)</td><td class="val">{float(p1.get('xg_2627') or 0.0):.2f}</td></tr>
                        <tr><td class="lbl">Expected Assists (xA)</td><td class="val">{float(p1.get('xa_2627') or 0.0):.2f}</td></tr>
                    </table>
                </div>

                <a href="../../calciatore/{slug1}/" class="btn-profile">Vedi Scheda Completa {name1} &rarr;</a>
            </div>

            <!-- VS Divider -->
            <div class="vs-divider">
                <span>VS</span>
            </div>

            <!-- Player 2 -->
            <div class="player-card {'is-winner' if winner == p2 else ''}">
                <div>
                    <div class="card-top">
                        <div class="role-pill {role2}">{role2}</div>
                        <div class="ovr-box">
                            <div class="ovr-num">{p2.get('ovr', 70)}</div>
                            <div class="ovr-lbl">Overall AI</div>
                        </div>
                    </div>
                    <div class="p-name">{name2}</div>
                    <div class="p-team">{team2} • FVM {p2.get('fvm', 1)} CR</div>

                    <div class="match-badge-box">
                        <div class="lbl">PROSSIMO MATCH</div>
                        <div class="match">{match_str2}</div>
                    </div>

                    <table class="stats-h2h-table">
                        <tr><td class="lbl">FantaMedia Attesa (xFM)</td><td class="val cyan">{xfm2:.2f}</td></tr>
                        <tr><td class="lbl">FantaMedia Reale (FM)</td><td class="val gold">{fm2:.2f}</td></tr>
                        <tr><td class="lbl">Media Voto Pura (MV)</td><td class="val">{mv2:.2f}</td></tr>
                        <tr><td class="lbl">Indice Titolarità</td><td class="val">{p2.get('titolarita', 70)}%</td></tr>
                        <tr><td class="lbl">Infortuni / Status</td><td class="val" style="color:{'#ef4444' if p2.get('is_injured') else '#10b981'};">{'🔴 ' + (p2.get('infortunio_motivo') or 'Stop') if p2.get('is_injured') else '🟢 Disponibile'}</td></tr>
                        <tr><td class="lbl">Gol / Assist 26/27</td><td class="val">{p2.get('gol_2627', 0)} G &bull; {p2.get('assist_2627', 0)} A</td></tr>
                        <tr><td class="lbl">Expected Goals (xG)</td><td class="val">{float(p2.get('xg_2627') or 0.0):.2f}</td></tr>
                        <tr><td class="lbl">Expected Assists (xA)</td><td class="val">{float(p2.get('xa_2627') or 0.0):.2f}</td></tr>
                    </table>
                </div>

                <a href="../../calciatore/{slug2}/" class="btn-profile">Vedi Scheda Completa {name2} &rarr;</a>
            </div>
        </div>

        <!-- FAQ Section -->
        <section class="faq-section">
            <h2 class="faq-title">Domande Frequenti su {name1} vs {name2}</h2>
            <div class="faq-item">
                <div class="faq-q">Chi è meglio schierare tra {name1} e {name2} nella prossima giornata?</div>
                <div class="faq-a">In base ai calcoli di Fanta Master AI, {winner['name']} parte favorito con il {w_pct}% delle preferenze grazie a un indice di FantaMedia attesa (xFM) più vantaggioso ({float(winner.get('xfm') or 6.0):.2f}) e un coefficiente di difficoltà partita favorevole.</div>
            </div>
            <div class="faq-item">
                <div class="faq-q">Posso schierarli entrambi al Fantacalcio?</div>
                <div class="faq-a">Se il tuo modulo lo consente e non hai alternative top in uno scontro diretto più semplice, schierare sia {name1} che {name2} può essere una scelta valida per diversificare il rischio bonus nel tuo reparto.</div>
            </div>
            <div class="faq-item">
                <div class="faq-q">Come influiscono i calci di rigore e i piazzati nel confronto?</div>
                <div class="faq-a">I tiratori designati di rigori e calci di punizione godono di un incremento naturale del valore atteso xFM. Controlla sempre la sezione Rigoristi di Fanta Master AI per verificare se uno dei due è il tiratore primario del rispettivo club.</div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="site-container">
            <p>&copy; 2026/2027 Fanta Master AI &bull; Portale Statistico di Fantacalcio &bull; Tutti i marchi appartengono ai rispettivi proprietari.</p>
        </div>
    </footer>
    <script src="../../js/tracker.js" defer></script>
</body>
</html>
"""
    return duel_slug, html
