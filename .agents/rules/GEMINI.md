# Regole Progetto FantacalcioAi

## Regola Fondamentale: Solo Dati dal Progetto
- **Non fare mai assunzioni su dati esterni** (classifiche, rose, trasferimenti, infortuni) che non siano presenti nei file del progetto.
- Se hai bisogno di informazioni esterne (es. composizione Serie A, calciatori di una squadra), chiedi esplicitamente all'utente di fornirle.
- Attieniti sempre e solo ai file presenti in `config/`, `data/`, `src/`, `scripts/`, `web/`.

## Obiettivo del Progetto: Algoritmo Predittivo
- Lo scopo principale del progetto è **sviluppare un algoritmo sempre più predittivo** per il Fantacalcio.
- Ogni modifica all'algoritmo (OVR, xFM, advice tag, bias corrections) deve essere valutata in ottica predittiva: migliora la capacità di anticipare le performance reali dei calciatori?
- Il feedback loop AI (save snapshot → evaluate → bias corrections) è il cuore del sistema di apprendimento e va preservato e potenziato.
- Le metriche chiave da ottimizzare sono: **MAE dell'xFM**, accuratezza dei consigli AI, hit rate della fragilità fisica.

## Deployment Online con Backend
- Il progetto è destinato alla **pubblicazione online** su **Vercel** (free tier, CDN globale, HTTPS automatico).
- Il dominio viene acquistato/gestito su **Aruba** e il DNS puntato a Vercel.
- Architettura reale:
  1. **Pipeline Python** → eseguita in locale → genera i JSON processati
  2. **Deploy su Vercel** → i JSON/file statici vengono deployati via `vercel` CLI o git push
  3. **Frontend HTML/JS** → statico, servito da Vercel CDN
  4. **Vercel Functions (Python)** → mini-backend serverless per raccolta dati anonimi → Vercel Postgres o Supabase
- I dati da raccogliere sono **esclusivamente comportamentali e anonimi**: pagine visitate, click per ruolo/slot, zone di interesse, durata sessione. Nessun IP, nessun identificatore utente.
- Raccolta anonima aggregata = **nessun obbligo di banner cookie GDPR** (no cookie traccianti, no dati personali).

## Stack Tecnologico
- **Pipeline locale:** Python (pipeline, valuation engine, AI evaluator) → genera JSON
- **Hosting:** Vercel (free tier) — CDN globale, HTTPS, deploy via CLI/git
- **Backend dati:** Vercel Functions (Python serverless) → Vercel Postgres o Supabase (free)
- **Frontend:** HTML + Vanilla CSS + Vanilla JavaScript (no framework, no Tailwind)
- **Dati:** JSON + Excel/CSV per input, JSON per output processato
- **Dominio:** Aruba (`fantamasterai.it` — "il portale di statistiche sul fantacalcio", DNS puntato a Vercel)

## Convenzioni Codice
- Mantenere sempre i commenti e docstring esistenti non correlati alle modifiche
- I prezzi sono in Crediti (CR), scala 1–1000 per lega standard da 8 squadre
- `titolarita` nel dict del giocatore è **intero 0–100** (non float 0.0–1.0)
- `ovr` (Overall) è **intero** clampato tra 45 e 98
- `fvm` è il Fantalive Value Market (valore di quotazione, float)

## Stagione Corrente
- La stagione è **2026/27**. I dati storici di riferimento sono **2025/26**.
- I match report disponibili coprono le **prime giornate** della stagione corrente.
