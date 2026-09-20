from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import DataStore, get_data_store
from ..schemas import LineupRequest, LineupResponse, LineupPlayer

router = APIRouter(prefix="/api/lineup", tags=["Formazione & Ottimizzatore"])

MODULE_STRUCTURES = {
    "3-4-3": {"P": 1, "D": 3, "C": 4, "A": 3},
    "4-3-3": {"P": 1, "D": 4, "C": 3, "A": 3},
    "3-5-2": {"P": 1, "D": 3, "C": 5, "A": 2},
    "4-4-2": {"P": 1, "D": 4, "C": 4, "A": 2},
    "4-2-3-1": {"P": 1, "D": 4, "C": 5, "A": 1},
    "3-4-2-1": {"P": 1, "D": 3, "C": 6, "A": 1},
    "5-3-2": {"P": 1, "D": 5, "C": 3, "A": 2},
    "4-5-1": {"P": 1, "D": 4, "C": 5, "A": 1},
}

def calculate_player_expected_score(p: Dict[str, Any], risk_tolerance: str = "balanced") -> float:
    """Calcola il punteggio atteso del giocatore per la prossima giornata."""
    # Controllo rigoroso infortuni
    is_injured = p.get("is_injured", False) or (str(p.get("infortunio_status", "")).lower() == "infortunato")
    giornate_perse = p.get("giornate_perse", 0)
    
    if is_injured:
        if giornate_perse >= 2 or str(p.get("infortunio_severity", "")).lower() in ["grave", "media", "medio"]:
            return 0.0
        # Infortunio lieve o in dubbio
        return 0.0 if giornate_perse > 0 else round(float(p.get("fm", 6.0)) * 0.4, 2)

    # Ponderazione Bayesiana (Sample Size 2026/27 vs Storico)
    fm_hist = float(p.get("fm") or 6.0)
    mv_hist = float(p.get("mv") or 6.0)
    
    fm_2627 = p.get("fm_2627")
    mv_2627 = p.get("mv_2627")
    presenze_2627 = p.get("presenze_2627") or 0

    if fm_2627 is not None and presenze_2627 > 0:
        # Più presenze ci sono nel 2026/27, maggiore è il peso della stagione corrente
        if presenze_2627 == 1:
            w_curr = 0.25
        elif presenze_2627 == 2:
            w_curr = 0.45
        elif presenze_2627 == 3:
            w_curr = 0.65
        else:
            w_curr = 0.80
        
        fm_eff = w_curr * float(fm_2627) + (1.0 - w_curr) * fm_hist
        mv_eff = w_curr * float(mv_2627 or mv_hist) + (1.0 - w_curr) * mv_hist
    else:
        fm_eff = fm_hist
        mv_eff = mv_hist

    titolarita = float(p.get("titolarita") or 80) / 100.0

    score = 0.70 * fm_eff + 0.30 * mv_eff
    
    # Aggiustamento per titolarità
    if titolarita < 0.5:
        score *= (0.5 + titolarita)

    # Bonus rigorista / piazzati
    if p.get("is_rigorista_1"):
        score += 0.35
    elif p.get("is_rigorista_2"):
        score += 0.15

    # Risk tolerance adjustment
    role = p.get("role", "")
    if risk_tolerance == "aggressive" and role in ["A", "C"]:
        score *= 1.05
    elif risk_tolerance == "conservative" and role == "D":
        score *= 1.03

    return round(score, 2)

@router.get("/supported-modules")
def get_supported_modules():
    return {
        "modules": list(MODULE_STRUCTURES.keys()),
        "default": "3-4-3"
    }

@router.post("/recommend", response_model=LineupResponse)
def recommend_lineup(
    request: LineupRequest,
    store: DataStore = Depends(get_data_store)
):
    # Recupera i giocatori della rosa
    squad_players = []
    for pid in request.player_ids:
        p = store.get_player(pid)
        if p:
            squad_players.append(p)

    if len(squad_players) < 11:
        raise HTTPException(
            status_code=400,
            detail=f"La rosa inviata contiene solo {len(squad_players)} giocatori validi. Ne servono almeno 11."
        )

    # Raggruppa per ruolo
    by_role: Dict[str, List[Dict[str, Any]]] = {"P": [], "D": [], "C": [], "A": []}
    for p in squad_players:
        role = p.get("role", "").upper()
        if role in by_role:
            exp_score = calculate_player_expected_score(p, request.risk_tolerance)
            p_copy = dict(p)
            p_copy["expected_score"] = exp_score
            by_role[role].append(p_copy)

    # Ordina i giocatori per punteggio atteso decrescente
    for role in by_role:
        by_role[role].sort(key=lambda x: x["expected_score"], reverse=True)

    # Verifica portiere
    if not by_role["P"]:
        raise HTTPException(status_code=400, detail="Nessun portiere (P) valido trovato nella rosa.")

    # Seleziona il modulo migliore (o usa quello richiesto)
    modules_to_evaluate = [request.formation] if request.formation in MODULE_STRUCTURES else list(MODULE_STRUCTURES.keys())
    
    best_lineup = None
    best_total_score = -1.0
    best_module = "3-4-3"

    for mod in modules_to_evaluate:
        reqs = MODULE_STRUCTURES[mod]
        # Verifica se abbiamo abbastanza giocatori per ruolo
        if (len(by_role["P"]) < reqs["P"] or 
            len(by_role["D"]) < reqs["D"] or 
            len(by_role["C"]) < reqs["C"] or 
            len(by_role["A"]) < reqs["A"]):
            continue

        selected_starters = []
        total_score = 0.0

        for role, count in reqs.items():
            starters = by_role[role][:count]
            selected_starters.extend(starters)
            total_score += sum(s["expected_score"] for s in starters)

        # Bonus modificatore difesa regolamentare per moduli a 4 o 5 difensori (Portiere + 3 migliori Difensori)
        def_bonus = 0.0
        if request.use_defense_modifier and reqs["D"] >= 4:
            d_starters = by_role["D"][:reqs["D"]]
            # Prendi i 3 difensori con MV atteso più alto tra i titolari
            d_mv_list = sorted([float(d.get("mv_2627") or d.get("mv") or 6.0) for d in d_starters], reverse=True)[:3]
            p_mv = float(by_role["P"][0].get("mv_2627") or by_role["P"][0].get("mv") or 6.0)
            avg_def = (sum(d_mv_list) + p_mv) / 4.0
            
            if avg_def >= 6.5:
                def_bonus = 3.0
            elif avg_def >= 6.25:
                def_bonus = 1.5
            elif avg_def >= 6.0:
                def_bonus = 0.5
            total_score += def_bonus

        if total_score > best_total_score:
            best_total_score = total_score
            best_lineup = (selected_starters, mod, def_bonus)
            best_module = mod

    if not best_lineup:
        raise HTTPException(
            status_code=400,
            detail="Impossibile comporre una formazione valida con i giocatori forniti (mancano ruoli minimi)."
        )

    starters, module_used, def_bonus = best_lineup
    starter_ids = {s["id"] for s in starters}

    # Panchina: i migliori rimanenti per ruolo
    bench = []
    bench_order = 1
    for role in ["P", "D", "C", "A"]:
        for p in by_role[role]:
            if p["id"] not in starter_ids:
                bench.append(LineupPlayer(
                    id=p["id"],
                    name=p.get("name", ""),
                    role=p.get("role", ""),
                    team=p.get("team", ""),
                    expected_score=p["expected_score"],
                    starter=False,
                    bench_order=bench_order,
                    reason=f"Panchina {role} ({bench_order}º cambio)"
                ))
                bench_order += 1

    starters_response = [
        LineupPlayer(
            id=s["id"],
            name=s.get("name", ""),
            role=s.get("role", ""),
            team=s.get("team", ""),
            expected_score=s["expected_score"],
            starter=True,
            reason=f"Titolare nel modulo {module_used} con score atteso {s['expected_score']}"
        )
        for s in starters
    ]

    tactical_notes = [
        f"Modulo ottimale consigliato: {module_used}",
        f"Punteggio complessivo atteso: {round(best_total_score, 2)} pt"
    ]
    if def_bonus > 0:
        tactical_notes.append(f"Bonus Modificatore Difesa previsto: +{def_bonus} pt")

    return LineupResponse(
        formation=module_used,
        expected_team_score=round(best_total_score, 2),
        starters=starters_response,
        bench=bench,
        defense_modifier_bonus_expected=def_bonus,
        tactical_notes=tactical_notes
    )
