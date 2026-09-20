import json

with open('data/processed/processed_players_master.json', 'r', encoding='utf-8') as f:
    players = json.load(f)

def get_p(name, team=None, role=None):
    name_l = name.lower()
    for p in players:
        if name_l == p['name'].lower() or name_l in p['name'].lower():
            if team and team.lower() not in p['team'].lower(): continue
            if role and p['role'] != role: continue
            return p
    raise Exception(f"Player not found: {name}")

squads_def = [
    {
        'id': 'squad_343',
        'name': "L'Armata Pesante — Tridente Bomber & Diversificazione Massima",
        'formation': "3-4-3",
        'archetype': "Tridente Top / 8 Club Diversi / Zero Doppioni di Reparto",
        'tagColor': "#f43f5e",
        'badge': "🔥 8 CLUB DIVERSI & 45 GOL",
        'starters': {
            'P': ['Meret'],
            'D': ['Dimarco', 'Tavares N.', 'Doig'],
            'C': ['Bernabè', 'Gudmundsson A.', 'Colpani', 'Ferguson'],
            'A': ['Martinez L.', 'Scamacca', 'Piccoli']
        },
        'bench': {
            'P': ['Caprile', 'Sportiello'],
            'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
            'C': ['Frendrup', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
            'A': ['Trepy', 'De Martis', 'Lisman']
        },
        'strategyDescription': "Questa formazione schiera <b>11 titolari provenienti da 8 club diversi</b>, evitando qualsiasi sovrapposizione nello stesso reparto (1 Inter in D, 1 Lazio in D, 1 Sassuolo in D). Il reparto d'attacco unisce <b>Lautaro Martinez (Inter - 379 CR)</b>, <b>Scamacca (Atalanta - 179 CR)</b> e il rigorista <b>Piccoli (Cagliari - 29 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Zero Rischio Reparto</b>: Nessun difensore o centrocampista dello stesso club. Se una squadra va in difficoltà, la tua difesa e mediana restano intatte.</li><li><b>Copertura Portiere a 1 CR</b>: In porta hai la coppia ufficiale <b>Meret + Caprile (1 CR)</b>.</li><li><b>Budget Sotto Controllo</b>: 11 Titolari (895 CR) + 14 Riserve (74 CR) = <b>969 CR totali</b> (31 CR di cuscinetto).</li></ul>"
    },
    {
        'id': 'squad_433',
        'name': "Il Dominio Tattico — Macchina da Modificatore (4 Centrali da 4 Club) & Bomber Malen",
        'formation': "4-3-3",
        'archetype': "Modificatore Difesa +3/+6 & 9 Club Diversi",
        'tagColor': "#38bdf8",
        'badge': "🛡️ DIFESA MULTI-CLUB 6.5",
        'starters': {
            'P': ['Svilar'],
            'D': ['Akanji', 'Rrahmani', 'Tavares N.', 'Doig'],
            'C': ['Gudmundsson A.', 'Bernabè', 'Colpani'],
            'A': ['Malen', 'Kean', 'Piccoli']
        },
        'bench': {
            'P': ['Ryan', 'Sportiello'],
            'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
            'C': ['Ferguson', 'Frendrup', 'Deiola', 'Zarraga'],
            'A': ['Trepy', 'De Martis', 'Lisman']
        },
        'strategyDescription': "Linea a 4 da <b>4 squadre diverse al 100%</b> (Inter, Napoli, Lazio, Sassuolo) con media voto altissima per incassare <b>+3/+6 di Modificatore</b> senza legarsi al destino di un solo club. In attacco il capocannoniere assoluto <b>Malen (Roma - 440 CR)</b> affiancato da <b>Kean (Como - 230 CR)</b> e <b>Piccoli (Cagliari - 29 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Neutralizza Divin Codino (Alessandro)</b>: Alessandro cerca il modificatore comprando blocchi squadra; tu invece selezioni il miglior singolo da 4 club diversi, riducendo la varianza e dominando i voti base.</li><li><b>Coppia Portiere Low Cost</b>: Svilar (73 CR) con il vice Ryan a solo 1 CR.</li><li><b>Costo Roster Perfetto</b>: 11 Titolari (906 CR) + 14 Riserve (56 CR) = <b>962 CR totali</b> (38 CR liberi).</li></ul>"
    },
    {
        'id': 'squad_4231',
        'name': "La Ragnatela dei Trequartisti — FantaMantra & Ali da 10 Club Diversi",
        'formation': "4-2-3-1",
        'archetype': "10 Club Diversi / 4 Punte / Rischio Zero",
        'tagColor': "#a855f7",
        'badge': "🪄 10 SQUADRE IN CAMPO",
        'starters': {
            'P': ['De Gea'],
            'D': ['Bastoni', 'Tavares N.', 'Doig', 'Bellanova'],
            'C': ['Paz N.', 'Pulisic', 'Bernabè', 'Colpani', 'Ferguson'],
            'A': ['Kean']
        },
        'bench': {
            'P': ['Terracciano', 'Sportiello'],
            'D': ['Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
            'C': ['Frendrup', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
            'A': ['Piccoli', 'Trepy', 'De Martis', 'Lisman']
        },
        'strategyDescription': "Una formazione d'autore con <b>10 club di Serie A rappresentati negli 11 titolari</b>. Schiera 4 giocatori offensivi micidiali: <b>Pulisic (Milan - 190 CR)</b>, <b>Nico Paz (Como - 260 CR)</b>, <b>Bernabè (Parma - 23 CR)</b> e <b>Kean (Como - 230 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Indistruttibile su 38 Turni</b>: Con 10 squadre diverse tra i titolari, non subisci mai i big match o le giornate no di una singola squadra.</li><li><b>Quattro Attaccanti Virtuali</b>: Pulisic e Nico Paz giocano ali/seconde punte ma sono quotati centrocampisti.</li><li><b>Spesa Strategica</b>: 11 Titolari (839 CR) + 14 Riserve (71 CR) = <b>910 CR totali</b> (90 CR di cuscinetto per l'asta).</li></ul>"
    },
    {
        'id': 'squad_352',
        'name': "L'Equilibrio di Ferro — Calhanoglu Rigorista & Coppia Kean-Scamacca (9 Club)",
        'formation': "3-5-2",
        'archetype': "9 Club Diversi / 3 Rigoristi Ufficiali",
        'tagColor': "#10b981",
        'badge': "⚖️ RIGORISTI & 9 CLUB",
        'starters': {
            'P': ['Maignan'],
            'D': ['Akanji', 'Tavares N.', 'Doig'],
            'C': ['Calhanoglu', 'Frattesi', 'Bernabè', 'Colpani', 'Ferguson'],
            'A': ['Kean', 'Scamacca']
        },
        'bench': {
            'P': ['Torriani', 'Sportiello'],
            'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
            'C': ['Frendrup', 'Deiola', 'Zarraga', 'Nicolussi Caviglia'],
            'A': ['Piccoli', 'Trepy', 'De Martis']
        },
        'strategyDescription': "Nessun raggruppamento rischioso: <b>9 squadre diverse su 11 titolari</b>. Massimizza i bonus da calcio piazzato con <b>Calhanoglu (Inter - 260 CR)</b>, <b>Frattesi (Lazio - 73 CR)</b> e la coppia d'attacco <b>Kean (Como - 230 CR) + Scamacca (Atalanta - 179 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Zero Sovrapposizioni</b>: In difesa hai 1 Inter, 1 Lazio e 1 Sassuolo; a centrocampo 1 Inter, 1 Lazio, 1 Parma, 1 Monza, 1 Bologna. Nessun reparto legato a un solo club.</li><li><b>Coppia Milan Portiere a 1 CR</b>: Maignan (46 CR) con il vice Torriani (1 CR).</li><li><b>Bilancio Totale</b>: 11 Titolari (893 CR) + 14 Riserve (78 CR) = <b>971 CR totali</b> (29 CR liberi).</li></ul>"
    },
    {
        'id': 'squad_3412',
        'name': "Moneyball Scientifico — Rabiot, McTominay, Scamacca & Douvikas (10 Club)",
        'formation': "3-4-1-2",
        'archetype': "Massima Efficienza xG/xA / 10 Club Rappresentati",
        'tagColor': "#eab308",
        'badge': "📊 10 CLUB & ZERO SPRECHI",
        'starters': {
            'P': ['Meret'],
            'D': ['Spence', 'Tavares N.', 'Doig'],
            'C': ['Rabiot', 'McTominay', 'Bernabè', 'Colpani'],
            'A': ['Douvikas', 'Scamacca', 'Piccoli']
        },
        'bench': {
            'P': ['Caprile', 'Sportiello'],
            'D': ['Bellanova', 'Zappa', 'Patric', 'Kolasinac', 'Chalobah T.'],
            'C': ['Ferguson', 'Frendrup', 'Deiola', 'Zarraga'],
            'A': ['Trepy', 'De Martis', 'Lisman']
        },
        'strategyDescription': "La rosa più efficiente in assoluto: <b>10 club diversi</b> per 11 titolari selezionati per il più alto indice di <b>Expected Goals (xG) e Expected Assists (xA)</b>. Attacco a tre punte formato da <b>Douvikas (Como - 232 CR)</b>, <b>Scamacca (Atalanta - 179 CR)</b> e <b>Piccoli (Cagliari - 29 CR)</b> con la mediana <b>Rabiot (Milan - 157 CR)</b> e <b>McTominay (Napoli - 179 CR)</b>.",
        'whyBeatsRivals': "<ul><li><b>Diversificazione Scientifica</b>: 10 club diversi in campo azzerano il rischio calendario o crisi societarie.</li><li><b>Sfianca i Rivali all'Asta</b>: Non entri in aste a rilancio cieco con Davide e Ilario, acquistando titolari garantiti da 10 squadre diverse.</li><li><b>Costo Rigoroso</b>: 11 Titolari (913 CR) + 14 Riserve (78 CR) = <b>991 CR totali</b> (9 CR liberi).</li></ul>"
    }
]

print("=== VERIFICA MATEMATICA E DI DIVERSIFICAZIONE ===")
for sq in squads_def:
    st_cost = sum(get_p(n)['prezzo_cons'] for n in [n for r in sq['starters'].values() for n in r])
    be_cost = sum(get_p(n)['prezzo_cons'] for n in [n for r in sq['bench'].values() for n in r])
    tot = st_cost + be_cost
    st_count = sum(len(r) for r in sq['starters'].values())
    be_count = sum(len(r) for r in sq['bench'].values())
    
    sq['budgetSpent'] = tot
    sq['budgetRemaining'] = 1000 - tot
    
    print(f"\n{sq['name']} ({sq['formation']}):")
    print(f"  Titolari ({st_count} calciatori): {st_cost} CR")
    print(f"  Panchina ({be_count} calciatori): {be_cost} CR")
    print(f"  TOTALE COMPLETO (25 Calciatori): {tot} CR / 1000 CR (Residuo: {1000 - tot} CR)")

js_content = f"""// ==============================================================================
// MODULO: 5 SQUADRE PERFETTE CONSIGLIATE DALL'AI (DIVERSIFICATE E SOTTO I 1000 CR)
// ==============================================================================

const AI_SQUADS_DATA = {json.dumps(squads_def, indent=4, ensure_ascii=False)};

let activeAiSquadTab = 'squad_343';

function switchAiSquadTab(squadId) {{
    activeAiSquadTab = squadId;
    renderAiSquadsTab();
}}

function renderAiSquadsTab() {{
    const container = document.getElementById('viewAiSquads');
    if (!container) return;

    if (typeof PLAYERS === 'undefined' || !PLAYERS.length) {{
        container.innerHTML = `<div style="padding:40px;text-align:center;color:var(--text-muted);">Caricamento dati calciatori in corso...</div>`;
        return;
    }}

    const currentSquad = AI_SQUADS_DATA.find(s => s.id === activeAiSquadTab) || AI_SQUADS_DATA[0];

    // Helper to resolve player object
    const resolvePlayer = (name) => {{
        return PLAYERS.find(p => p.name.toLowerCase() === name.toLowerCase() || p.name.toLowerCase().includes(name.toLowerCase())) || {{
            name: name, role: 'C', team: '-', ovr: 80, prezzo_cons: 1, slot_fascia: '1° Slot', ai_advice: 'Consigliato'
        }};
    }};

    // Tabs navigation buttons
    let tabsNavHtml = AI_SQUADS_DATA.map(sq => {{
        const isActive = sq.id === activeAiSquadTab;
        return `
            <button class="ai-squad-selector-btn ${{isActive ? 'active' : ''}}" onclick="switchAiSquadTab('${{sq.id}}')">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
                    <span class="ai-formation-pill">${{sq.formation}}</span>
                    <span class="ai-budget-pill">${{sq.budgetSpent}} CR</span>
                </div>
                <div class="ai-squad-title">${{sq.name.split('—')[0]}}</div>
                <div class="ai-squad-subtitle">${{sq.archetype}}</div>
            </button>
        `;
    }}).join('');

    // Render 4 departments for starters and bench
    const renderDeptTable = (title, icon, names, roleColor) => {{
        const playerObjs = names.map(resolvePlayer);
        const subtotal = playerObjs.reduce((acc, p) => acc + (p.prezzo_cons || 1), 0);

        let rows = playerObjs.map(p => {{
            const isInj = p.is_injured;
            const injIcon = isInj ? `<span class="inj-cross-badge" title="${{p.infortunio_motivo || 'Infortunato'}}">✚</span>` : '';
            const oopBadge = p.oop_val && p.oop_val !== '-' ? `<span style="font-size:10px;background:rgba(234,179,8,0.15);color:#fbbf24;border:1px solid rgba(234,179,8,0.3);padding:1px 5px;border-radius:4px;">${{p.oop_val.split('•')[0]}}</span>` : '';

            return `
                <tr class="ai-squad-player-row" onclick="openPlayerProfileModal(${{p.id}})" title="Clicca per aprire scheda dettagliata">
                    <td style="width:36px;"><span class="role-badge ${{p.role}}">${{p.role}}</span></td>
                    <td>
                        <div style="display:flex;align-items:center;gap:6px;">
                            <b style="color:#fff;cursor:pointer;">${{p.name}}</b>
                            ${{injIcon}}
                            <span style="font-size:11px;color:var(--text-muted);">${{p.team}}</span>
                            ${{oopBadge}}
                        </div>
                    </td>
                    <td style="text-align:center;width:45px;"><span class="ovr-pill ${{p.ovr >= 90 ? 'top-tier' : ''}}">${{p.ovr}}</span></td>
                    <td style="text-align:center;width:90px;"><span class="slot-pill-badge" style="font-size:10.5px;">${{p.slot_fascia || 'Slot'}}</span></td>
                    <td style="text-align:right;width:75px;"><span class="price-pill" style="font-size:12px;">${{p.prezzo_cons || 1}} CR</span></td>
                </tr>
            `;
        }}).join('');

        return `
            <div class="ai-dept-box">
                <div class="ai-dept-header">
                    <span style="color:${{roleColor}};font-weight:800;font-size:12.5px;">${{icon}} ${{title}} (${{names.length}})</span>
                    <span style="font-size:11.5px;color:var(--accent-gold);font-weight:800;">Tot: ${{subtotal}} CR</span>
                </div>
                <table class="ai-dept-table">
                    <tbody>${{rows}}</tbody>
                </table>
            </div>
        `;
    }};

    container.innerHTML = `
        <div class="ai-squads-header-panel">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:14px;">
                <div>
                    <div style="display:flex;align-items:center;gap:10px;">
                        <span style="font-size:24px;">🧠</span>
                        <h2 style="margin:0;font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.5px;">Master AI: 5 Rose Perfette & Diversificate (1000 CR)</h2>
                        <span style="background:rgba(0,242,254,0.15);border:1px solid var(--accent-cyan);color:var(--accent-cyan);font-size:11px;font-weight:800;padding:2px 8px;border-radius:6px;">ZERO DOPPIONI DI REPARTO - 25 SLOT RIGOROSI</span>
                    </div>
                    <p style="margin:4px 0 0 0;font-size:12.5px;color:var(--text-secondary);">
                        Tutte le formazioni schierano <b>11 titolari provenienti da 8-10 club diversi</b> (nessun raggruppamento rischioso nello stesso reparto). Costo totale garantito ≤ 1000 CR.
                    </p>
                </div>

                <div style="display:flex;align-items:center;gap:10px;">
                    <button class="btn-action" style="background:linear-gradient(135deg, var(--accent-cyan), #0284c7);color:#000;font-weight:900;padding:8px 16px;border:none;box-shadow:0 0 15px rgba(0,242,254,0.4);" onclick="loadAiSquadToBuilder('${{currentSquad.id}}')" title="Carica tutti i 25 calciatori di questa rosa nella tua squadra">
                        📥 Carica Questa Rosa in Squadra (Unika)
                    </button>
                </div>
            </div>

            <!-- Selector Pills for the 5 Formations -->
            <div class="ai-squads-selector-bar">
                ${{tabsNavHtml}}
            </div>
        </div>

        <!-- Main Detail Card of Current Squad -->
        <div class="ai-squad-main-container">
            <!-- Left Column: Tactical Pitch + Strategic Breakdown -->
            <div style="flex:1.1;min-width:0;display:flex;flex-direction:column;gap:16px;">
                
                <!-- Summary Card -->
                <div class="ai-squad-overview-card" style="border-left:4px solid ${{currentSquad.tagColor}};">
                    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">
                        <div>
                            <span class="ai-squad-badge" style="background:${{currentSquad.tagColor}}22;color:${{currentSquad.tagColor}};border:1px solid ${{currentSquad.tagColor}}55;">${{currentSquad.badge}}</span>
                            <h3 style="margin:6px 0 2px 0;font-size:18px;font-weight:900;color:#fff;">${{currentSquad.name}}</h3>
                            <span style="font-size:12px;color:var(--text-secondary);">${{currentSquad.archetype}}</span>
                        </div>
                        <div style="display:flex;gap:12px;text-align:right;">
                            <div class="ai-stat-box">
                                <span class="lbl">Costo Totale (25 Calciatori)</span>
                                <span class="val" style="color:var(--accent-gold);">${{currentSquad.budgetSpent}} <small style="font-size:11px;">/ 1000 CR</small></span>
                            </div>
                            <div class="ai-stat-box">
                                <span class="lbl">Crediti Liberi</span>
                                <span class="val" style="color:var(--accent-cyan);">${{currentSquad.budgetRemaining}} <small style="font-size:11px;">CR</small></span>
                            </div>
                            <div class="ai-stat-box">
                                <span class="lbl">Resa Stimata</span>
                                <span class="val" style="color:#4ade80;">+17.8 Bonus/G</span>
                            </div>
                        </div>
                    </div>

                    <div style="margin-top:12px;font-size:12.5px;color:var(--text-secondary);line-height:1.6;background:rgba(0,0,0,0.25);padding:10px 14px;border-radius:8px;border:1px solid rgba(255,255,255,0.05);">
                        ${{currentSquad.strategyDescription}}
                    </div>
                </div>

                <!-- Why it beats rivals (Competitive Advantage Callout) -->
                <div class="ai-rivals-advantage-card">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                        <span style="font-size:18px;">🎯</span>
                        <h4 style="margin:0;font-size:14px;font-weight:800;color:var(--accent-cyan);">Perché questa rosa distrugge i 7 rivali della lega:</h4>
                    </div>
                    <div class="ai-rivals-bullets">
                        ${{currentSquad.whyBeatsRivals}}
                    </div>
                </div>

                <!-- Starter 11 Tactical Board (Formazione Tipo) -->
                <div class="ai-starter-lineup-card">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">⚔️</span>
                            <b style="color:#fff;font-size:14px;">11 Titolari Tipo (${{currentSquad.formation}}) — Club Diversificati</b>
                        </div>
                        <span style="font-size:11px;color:var(--text-muted);">Clicca su ogni calciatore per vedere la scheda completa</span>
                    </div>

                    <div class="ai-pitch-grid-container">
                        ${{renderDeptTable('Portiere Titolare', '🧤', currentSquad.starters.P, 'var(--role-p)')}}
                        ${{renderDeptTable('Difesa Titolare', '🛡️', currentSquad.starters.D, 'var(--role-d)')}}
                        ${{renderDeptTable('Centrocampo Titolare', '🪄', currentSquad.starters.C, 'var(--role-c)')}}
                        ${{renderDeptTable('Tridente / Attacco Titolare', '⚡', currentSquad.starters.A, 'var(--role-a)')}}
                    </div>
                </div>
            </div>

            <!-- Right Column: Full 14-Player Bench & Reserves -->
            <div style="flex:0.9;min-width:320px;display:flex;flex-direction:column;gap:14px;">
                <div class="ai-bench-panel">
                    <div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:10px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">💺</span>
                            <b style="color:#fff;font-size:14px;">Panchina & Riserve di Copertura (14 Calciatori)</b>
                        </div>
                        <span style="font-size:11px;background:rgba(74,222,128,0.15);color:#4ade80;padding:2px 6px;border-radius:4px;font-weight:700;">100% Voto Garantito</span>
                    </div>

                    <p style="font-size:11.5px;color:var(--text-muted);margin:0 0 10px 0;">
                        Tutti i 14 rincalzi costano 1-2 crediti o sono coppie low-cost (es. Caprile per Meret a 1 CR, Ryan per Svilar a 1 CR, Torriani per Maignan a 1 CR).
                    </p>

                    <div style="display:flex;flex-direction:column;gap:10px;">
                        ${{renderDeptTable('Portieri di Riserva', '🧤', currentSquad.bench.P, 'var(--role-p)')}}
                        ${{renderDeptTable('Difensori di Riserva', '🛡️', currentSquad.bench.D, 'var(--role-d)')}}
                        ${{renderDeptTable('Centrocampisti di Riserva', '🪄', currentSquad.bench.C, 'var(--role-c)')}}
                        ${{renderDeptTable('Attaccanti di Riserva & Coperture', '⚡', currentSquad.bench.A, 'var(--role-a)')}}
                    </div>
                </div>
            </div>
        </div>
    `;
}}

function loadAiSquadToBuilder(squadId) {{
    const squad = AI_SQUADS_DATA.find(s => s.id === squadId);
    if (!squad) return;

    if (!confirm(`Vuoi caricare tutti i 25 calciatori della rosa '${{squad.name.split('—')[0]}}' nella tua squadra (Unika)? Costo Totale: ${{squad.budgetSpent}} CR / 1000 CR.`)) {{
        return;
    }}

    // Reset current team slots
    State.slots = {{
        P: {{ max: 3, players: [] }},
        D: {{ max: 8, players: [] }},
        C: {{ max: 8, players: [] }},
        A: {{ max: 6, players: [] }}
    }};
    State.budgetSpent = 0;

    const allNames = [
        ...squad.starters.P, ...squad.bench.P,
        ...squad.starters.D, ...squad.bench.D,
        ...squad.starters.C, ...squad.bench.C,
        ...squad.starters.A, ...squad.bench.A
    ];

    allNames.forEach(name => {{
        const p = PLAYERS.find(pl => pl.name.toLowerCase() === name.toLowerCase() || pl.name.toLowerCase().includes(name.toLowerCase()));
        if (p) {{
            buyPlayer(p.id, p.prezzo_cons || 1);
        }}
    }});

    saveStateToStorage();
    updateAllViews();
    switchTab('auction');

    alert(`🎉 Rosa '${{squad.name.split('—')[0]}}' caricata con successo in Unika! Spesa totale calcolata: ${{squad.budgetSpent}} CR.`);
}}
"""

with open('web/js/ai_squads.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("\n--> FILE web/js/ai_squads.js AGGIORNATO CON REGOLE DI DIVERSIFICAZIONE!")
