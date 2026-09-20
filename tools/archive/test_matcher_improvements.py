import re
import unicodedata
from rapidfuzz import fuzz
import pandas as pd

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

def resolve_player(clean_name, team_name, lookup_dict):
    if not clean_name:
        return None

    if clean_name in lookup_dict:
        return lookup_dict[clean_name]

    tokens = clean_name.split()
    if not tokens:
        return None

    # Estrai cognome e possibili iniziali dal listone
    # Se il nome è tipo "esposito f p", il cognome è tokens[0], le iniziali sono tokens[1:]
    long_tokens = [t for t in tokens if len(t) > 2]
    initials = [t[0] for t in tokens if len(t) <= 2]

    # 1. Match Esatto o Cognome + Tutte le Iniziali
    for cand_name, cand_data in lookup_dict.items():
        cand_tokens = cand_name.split()
        if not cand_tokens:
            continue

        # A. Se i token sono identici
        if set(tokens) == set(cand_tokens):
            return cand_data

        # B. Cognome presente e tutte le iniziali corrispondono ai nomi
        if long_tokens and all(lt in cand_tokens for lt in long_tokens):
            other_cand_tokens = [ct for ct in cand_tokens if ct not in long_tokens]
            if not initials:
                return cand_data
            if len(initials) <= len(other_cand_tokens):
                # Verifica che ogni iniziale corrisponda in ordine o presenza
                matched_inits = 0
                for init in initials:
                    if any(oct.startswith(init) for oct in other_cand_tokens):
                        matched_inits += 1
                if matched_inits == len(initials):
                    return cand_data

        # C. Se tutti i token del listone sono un sottoinsieme di quelli di FotMob
        if set(tokens).issubset(set(cand_tokens)):
            return cand_data

        # D. Se il cognome principale (>= 4 lettere) corrisponde ed è univoco
        if len(tokens) == 1 and len(tokens[0]) >= 4 and tokens[0] in cand_tokens:
            return cand_data

    # 2. Fuzzy Matching su token
    best_candidate = None
    best_score = 0
    for cand_name, cand_data in lookup_dict.items():
        score = fuzz.token_set_ratio(clean_name, cand_name)
        if score > best_score:
            best_score = score
            best_candidate = cand_data

    if best_score >= 82:
        return best_candidate

    return None

# Test con il dataset reale
df_fotmob = pd.read_csv('data/raw/fotmob_seriea_2025_26_clean.csv')
df_fotmob['clean_name'] = df_fotmob['name'].apply(clean_text)
fotmob_lookup = {row['clean_name']: row.to_dict() for _, row in df_fotmob.iterrows()}

df_quot = pd.read_excel('Quotazioni_Fantacalcio_Stagione_2026_27.xlsx', skiprows=1).dropna(subset=['Nome'])

test_cases = ['Esposito F.P.', 'Esposito Se.', 'Hojlund', 'Ostigard', 'Martinez L.', 'Martinez Jo.', 'Pellegrini Lo.', 'Pellegrino M.', 'Kean', 'Dimarco', 'Paz N.', 'Kolo Muani', 'Ramos G.']

print("=== TEST DISAMBIGUAZIONE E MATCHING FOTMOB ===")
for tc in test_cases:
    cn = clean_text(tc)
    res = resolve_player(cn, '', fotmob_lookup)
    print(f"{tc:<18} -> {res.get('name') if res else 'NON PRESENTE (Nuovo)'}")

total_matched = 0
for _, q in df_quot.iterrows():
    cn = clean_text(str(q['Nome']))
    if resolve_player(cn, '', fotmob_lookup):
        total_matched += 1

print(f"\nTOTALE MATCHATI SUL LISTONE: {total_matched} su {len(df_quot)} ({round(total_matched/len(df_quot)*100, 1)}%)")
