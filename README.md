# ⚽ Fanta Master AI — Serie A 2026/27

Motore quantitativo e dashboard standalone per l'Asta del Fantacalcio (Base 1000 Crediti - 8 Squadre).

---

## 📁 Struttura del Progetto

```text
FantacalcioAi/
│
├── config/                      # ⚙️ Configurazioni & Dati di Mercato (facilmente modificabili)
│   ├── tactical_db.json         # 20 formazioni titolari, moduli, rigoristi, corner, piazzati, OOP
│   ├── injuries.json            # Infortuni attuali, date rientro stimate e motivi clinici
│   ├── fragile_players.json     # Calciatori con storico di infortuni cronici
│   ├── team_ratings.json        # Moltiplicatori e rating di forza per i 20 club
│   └── league_settings.json     # Regole di lega (8 squadre, 1000 crediti, slot 3P-8D-8C-6A)
│
├── data/                        # 📊 Data Lake
│   ├── raw/                     # File grezzi originali (Excel Quotazioni, Voti, FBref)
│   └── processed/               # Dataset arricchiti generati dalla pipeline
│
├── src/                         # 🧠 Motore Quantitativo Python
│   ├── config_loader.py         # Caricamento sicuro dei JSON con fallback
│   ├── player_matcher.py        # Algoritmo fuzzy matching con disambiguazione omonimi e filtri squadra
│   ├── stats_processor.py       # Ingestione e normalizzazione voti storici e statistiche
│   ├── valuation_engine.py      # Modello continuo OVR, curve prezzi a 1000 CR e slotting
│   ├── gk_engine.py             # Calcolo incroci e alternanza casa/trasferta portieri
│   └── pipeline.py              # Orchestratore principale
│
├── web/                         # 💻 Frontend Modulare
│   ├── css/dashboard.css        # Grafica dark glassmorphism, responsive
│   ├── js/                      # Moduli JavaScript (state, auction, pitch, matchup, gk_grid)
│   └── build_dashboard.py       # Compilatore per creare il file HTML standalone portabile
│
├── tests/                       # 🧪 Test di Validazione e Regressione
├── tools/archive/               # 🗄️ Archivio script esplorativi e scrapers
├── main.py                      # 🚀 Entrypoint CLI del progetto
└── Dashboard_Fanta_1000.html    # 🌐 Dashboard Standalone pronta all'uso (funziona offline)
```

---

## 🚀 Come Usare il Progetto

### 1. Esecuzione Completa (Pipeline + Compilazione Dashboard)
```bash
python main.py --build
```
Questo comando:
1. Ricalcola le valutazioni, OVR e prezzi per tutti i calciatori.
2. Applica le ultime formazioni e infortuni da `config/`.
3. Genera il file `Dashboard_Fanta_1000.html` aggiornato e sincronizza gli asset dell'App Android.

### 2. Generazione App APK Android
```bash
python main.py --apk
```
Compila ed esporta il pacchetto Android pronto all'installazione in `dist/FantaMasterAI.apk`.

### 3. Sincronizzazione Live Real-Time (PC + Smartphone durante l'Asta)
```bash
python main.py --serve
```
Avvia il server FastAPI/WebSocket locale. Permette di usare il PC e lo smartphone in parallelo: ogni calciatore chiamato, acquistato o aggiunto ai preferiti si sincronizza istantaneamente al millisecondo su entrambi gli schermi!

### 4. Solo Compilazione Dashboard Web (Senza ricalcolare i dati)
```bash
python main.py --dashboard-only
```

### 5. Esecuzione Test Unitari
```bash
python -m pytest tests
```

---

## ✏️ Come Aggiornare i Dati Durante il Calciomercato

Tutte le modifiche si effettuano direttamente nei file JSON all'interno della cartella `config/` **senza bisogno di modificare una sola riga di codice Python**:

1. **Un calciatore cambia squadra o diventa titolare/rigorista?**
   - Apri `config/tactical_db.json`, trova la squadra interessata e aggiorna la lista `lineup`, `rigoristi`, `punizioni` o `corner`.
2. **Un calciatore si infortuna o rientra?**
   - Apri `config/injuries.json` e aggiungi/aggiorna la voce (es. `"lautaro": {"motivo": "Affaticamento", "rientro": "05/09/2026"}`).
3. **Aggiornamento del Listone Excel**:
   - Inserisci o sostituisci il file `Listone_definitivo_Fantacalcio_Stagione_2026_27.xlsx` con la versione ufficiale.
4. **Lancia `python main.py --build`**: la dashboard si aggiornerà istantaneamente!

---

## 🛡️ Funzionalità dell'Asta Live
- **Persistenza Automatica (`localStorage`)**: Tutti i calciatori acquistati e i crediti spesi vengono salvati in tempo reale. Se ricarichi la pagina o chiudi il browser, la tua asta viene ripristinata al 100%.
- **Max Bid Dinamico**: Calcola in ogni istante l'offerta massima consentita garantendo che resti sempre almeno 1 credito per ogni slot rimanente.
- **Confronto Testa a Testa 1vs1**: Analisi di tutti i parametri chiave tra due calciatori per sciogliere i dubbi in asta.
- **Griglia e Heatmap Portieri**: Incroci ottimali per massimizzare le partite in casa e risparmiare budget.
