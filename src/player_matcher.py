import re
import unicodedata
from rapidfuzz import fuzz

SPECIAL_CHAR_MAP = {
    'ø': 'o', 'Ø': 'o', 'æ': 'ae', 'Æ': 'ae', 'ð': 'd', 'Ð': 'd',
    'đ': 'd', 'Đ': 'd', 'ł': 'l', 'Ł': 'l', 'ß': 'ss', 'ı': 'i', 'İ': 'i', '’': "'", '`': "'"
}

def clean_text(val):
    if not isinstance(val, str):
        return ""
    for k, v in SPECIAL_CHAR_MAP.items():
        val = val.replace(k, v)
    val = unicodedata.normalize('NFKD', val).encode('ASCII', 'ignore').decode('utf-8')
    val = re.sub(r'[^a-zA-Z0-9\s]', ' ', val.lower())
    return re.sub(r'\s+', ' ', val).strip()

def match_player_name(a, b):
    """
    Verifica se due stringhe nome (es. 'Paz N.' e 'Nico Paz', 'Martinez L.' e 'Lautaro Martinez')
    fanno riferimento allo stesso calciatore.
    """
    ca = clean_text(a)
    cb = clean_text(b)
    if not ca or not cb:
        return False
    if ca == cb or ca in cb or cb in ca:
        return True
    
    ta = ca.split()
    tb = cb.split()
    if set(ta) == set(tb):
        return True
    
    long_a = [t for t in ta if len(t) > 2]
    init_a = [t[0] for t in ta if len(t) <= 2]
    long_b = [t for t in tb if len(t) > 2]
    init_b = [t[0] for t in tb if len(t) <= 2]
    
    if long_a and all(la in tb for la in long_a):
        rem_b = [t for t in tb if t not in long_a]
        if not init_a:
            return True
        if all(any(rb.startswith(ia) for rb in rem_b) for ia in init_a):
            return True

    if long_b and all(lb in ta for lb in long_b):
        rem_a = [t for t in ta if t not in long_b]
        if not init_b:
            return True
        if all(any(ra.startswith(ib) for ra in rem_a) for ib in init_b):
            return True

    return False


def resolve_player(clean_name, team_name, lookup_dict, role=None):
    """
    Risolve l'identità di un calciatore tra Listone Fantacalcio e Fonti Esterne (FotMob/Voti).
    Supporta caratteri speciali, cognomi singoli, iniziali composte (es. 'Esposito F.P.', 'Martinez L.')
    e disambigua rigorosamente gli omonimi sfruttando squadra e ruolo.
    """
    if not clean_name:
        return None

    tokens = clean_name.split()
    if not tokens:
        return None

    clean_team = clean_text(team_name) if team_name else ''
    clean_role = role.strip().upper() if role else ''

    candidates = []

    for cand_name, cand_data in lookup_dict.items():
        cand_tokens = cand_name.split()
        if not cand_tokens:
            continue

        base_score = 0
        
        # 1. Match Esatto o Equivalente
        if clean_name == cand_name:
            base_score = 100
        elif set(tokens) == set(cand_tokens):
            base_score = 95
        elif set(tokens).issubset(set(cand_tokens)) or set(cand_tokens).issubset(set(tokens)):
            base_score = 85
        else:
            # 2. Match Cognome + Iniziale/Abbreviazione (es. 'lautaro martinez' vs 'martinez l', 'martinez jo' vs 'josep martinez')
            long_t = [t for t in tokens if len(t) > 2]
            long_c = [ct for ct in cand_tokens if len(ct) > 2]
            short_t = [t for t in tokens if len(t) <= 2]
            short_c = [ct for ct in cand_tokens if len(ct) <= 2]

            common_long = set(long_t).intersection(set(long_c))
            if common_long:
                rem_t = [t for t in long_t if t not in common_long]
                rem_c = [ct for ct in long_c if ct not in common_long]

                # Se entrambi hanno parole lunghe diverse non corrispondenti (es. 'sconosciuto' vs 'rossi'), rifiuta
                if rem_t and rem_c:
                    base_score = 0
                elif rem_t and short_c:
                    if all(any(w.startswith(sc) for w in rem_t) for sc in short_c):
                        base_score = 85
                elif rem_c and short_t:
                    if all(any(w.startswith(st) for w in rem_c) for st in short_t):
                        base_score = 85
                elif short_t and short_c:
                    if all(any(w.startswith(sc) or sc.startswith(w) for sc in short_c) for w in short_t):
                        base_score = 85
                elif not rem_t and not rem_c and not short_t and not short_c:
                    base_score = 90
            elif match_player_name(clean_name, cand_name):
                base_score = 85
            elif len(tokens) == 1 and len(tokens[0]) >= 3 and tokens[0] in cand_tokens:
                base_score = 60
            elif len(cand_tokens) == 1 and len(cand_tokens[0]) >= 3 and cand_tokens[0] in tokens:
                base_score = 60

        # 3. Fallback Fuzzy
        if base_score == 0:
            ratio = fuzz.token_sort_ratio(clean_name, cand_name)
            if ratio >= 80:
                base_score = ratio * 0.75

        # 4. Ponderazione Deterministica con Ruolo e Squadra
        if base_score > 0:
            c_team_raw = cand_data.get('Squadra') or cand_data.get('team') or cand_data.get('team_2627') or ''
            c_role_raw = cand_data.get('R') or cand_data.get('role') or cand_data.get('Ruolo') or ''
            c_team = clean_text(str(c_team_raw))
            c_role = str(c_role_raw).strip().upper()

            score = base_score
            # Ruolo: bonus forte se coincide, penalità severa se differisce (es. P vs A)
            if clean_role and c_role:
                if clean_role == c_role:
                    score += 40
                else:
                    score -= 70

            # Squadra: bonus se coincide
            if clean_team and c_team:
                if clean_team in c_team or c_team in clean_team:
                    score += 35
                else:
                    score -= 20

            candidates.append((score, cand_data))

    if not candidates:
        return None

    candidates.sort(key=lambda x: -x[0])
    best_score, best_cand = candidates[0]
    if best_score >= 50:
        return best_cand
    return None

