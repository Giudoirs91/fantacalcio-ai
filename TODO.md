# To-Do List Ufficiale & Prossimi Passi - FantaMaster AI

File di tracciamento persistente delle attività pianificate per il progetto FantaMaster AI (`fantamasterai.it`).

---

## 🟢 FASE 1: Conformità Legale & Trasparenza (Copertura 100%)
- [x] **Creare la pagina `/privacy-policy` (e modale interattivo accessibile nel footer):**
  - Dichiarazione formale di *Privacy by Design* (nessuna raccolta di dati personali identificativi, nessun indirizzo IP conservato).
  - Esenzione dal Cookie Banner preventivo per sole metriche statistiche aggregate anonime (Linee Guida Garante Privacy 10/06/2021).
  - Indicazione del contatto di riferimento del portale (`info@fantamasterai.it`).
- [x] **Aggiungere il Disclaimer Legale sui Marchi nel Footer:**
  - Clausola di indipendenza editoriale da Lega Serie A e testate commerciali.
  - Specifica sull'uso dei nomi a fini statistici e di legittima cronaca sportiva (Diritto d'autore / Fair Use).
  - Footer presente in tutte le pagine (Dashboard SPA, 8 Clean URL sections, 533 schede calciatore, 20 club, 3 pillar e web app).

---

## 🟡 FASE 2: Fidelizzazione & Strumenti ad Alto Valore (Retention)
- [x] **Tool "Chi Schiero?" (Comparatore 1vs1 del Weekend):**
  - Rilevamento dinamico automatico della prossima giornata di Serie A da voti reali + calendario a 38 turni.
  - Interfaccia rapida a 2 caselle con ricerca istantanea, filtri ruolo e preset ballottaggi caldi.
  - Incrocio deterministico xFM, fattore casa/trasferta, difficoltà matchup (xGA difesa rivale) e status rigoristi/piazzati.
  - Verdetto percentuale immediato (*es. Consigliato Politano 89% vs Orsolini 11%*) con 3 motivazioni AI e confronto testa a testa tabellare.
  - Pulsante per condivisione istantanea formattata su WhatsApp / Telegram.
  - URL dedicato SEO `/chi-schiero/` indicizzato su Google e rotta Vercel configurata.
- [ ] **Modulo "La Mia Rosa" (Salvataggio in `localStorage`):**
  - Selezione dei 25 giocatori della propria squadra senza obbligo di registrazione o login.
  - Top 11 personalizzata consigliata automaticamente ogni settimana.
  - Alert "Punti Ciechi" per evitare di giocare in 10 in caso di infortuni o squalifiche.
- [ ] **"Trade Analyzer" (Valutatore di Scambi tra Leghe):**
  - Confronto matematico tra giocatori ceduti e ricevuti (*Scambio vantaggioso / equo / rischioso*).
- [ ] **"Simulatore Modificatore Difesa: 4-3-3 o 3-4-3?":**
  - Decision engine che calcola la media voto pura attesa dei 4 difensori + portiere vs potenziale offensivo del centrocampista aggiuntivo.
  - Verdetto probabilistico sul modulo con punteggio atteso più alto (*es. Il 4-3-3 garantisce +1.8 pt attesi*).
- [ ] **"Il Sospiro Statistico" (Player Similarity Engine):**
  - Algoritmo di clustering e affinità statistica basato sulle metriche avanzate (dribbling, passaggi progressivi, xG90, xA90).
  - Associa nuovi arrivi, scommesse ed esordienti a profili affermati della Serie A (*es. "Profilo affine per l'88% a Gudmundsson"*).

---

## 🔵 FASE 3: Viralità & Crescita del Traffico
- [x] **Generatore di Social Card Grafiche:**
  - Motore Python Pillow (`src/telegram_engine.py`) che genera social card HD (1080x1080) con i consigliati per ruolo, OVR e matchup.
- [x] **"Il Bollettino del Venerdì" (Briefing Telegram @fantamasterai ore 12:30):**
  - Bot ufficiale `@FantamasterBot` collegato al canale `t.me/fantamasterai`.
  - Invio automatico della Social Card HD + Briefing formattato prima degli anticipi del venerdì entro le ore 12:30.
- [ ] **"Il Lunedì dei Rimpianti & della Fortuna" (AI Post-Match Analysis):**
  - Pillole automatiche del lunedì: *La Fortunata della Settimana* (overperformance da cedere), *La Sfortuna Cieca* (alta produzione offensiva a secco da comprare a sconto), *La Panchina dei Rimpianti* (i top panchinati d'Italia).
- [ ] **Rilevatore di Regressione (Buy Low / Sell High):**
  - Tab per scovare chi ha fatto gol fortuiti (da cedere al picco) e chi ha xFM alto ma bonus sfortunati (da acquistare sottoprezzo).

---

## 🟣 FASE 4: Manutenzione Algoritmo & Dati Live
- [ ] **Aggiornamento Match Report alle prossime giornate (G6+):**
  - Inserimento dei nuovi report ufficiali e aggiornamento delle presenze/minuti.
  - Controllo del feedback loop AI per abbassare ulteriormente il MAE delle previsioni xFM.

---

## 📲 PALINSESTO TELEGRAM (@fantamasterai) — PROSSIMI INVIO & BROADCAST

### 1️⃣ Venerdì ore 19:00 — I Possibili Top di Giornata (Consigli Weekend)
- [ ] **Invio Broadcast Top Picks & Consigli di Giornata:**
  - **Orario:** Venerdì 09/10/2026 alle ore 19:00
  - **Script pronto all'uso:** `python tools/send_telegram_friday_top.py` (test: `python tools/send_telegram_friday_top.py --dry-run`)
  - **Pagine Promosse nel Messaggio:**
    - 📊 **Consigli Completi:** `https://www.fantamasterai.it/consigli-fantacalcio/` (guida completa a fasce, rigoristi e sorprese).
    - ⚔️ **Comparatore "Chi Schiero" (1vs1):** `https://www.fantamasterai.it/chi-schiero/` (promosso per risolvere i ballottaggi e i dubbi tra due calciatori prima del weekend).
  - **Asset grafici:** Social Card HD 1080x1080 con i 4 Top per ruolo (Portiere, Difensore, Centrocampista, Attaccante) allegata automaticamente.

### 2️⃣ Sabato ore 14:30 — Alert Scadenza Formazione (Mezz'ora prima del kick-off)
- [ ] **Invio Reminder Consegna Formazione & Check Infortunati:**
  - **Orario:** Sabato 10/10/2026 alle ore 14:30 (30 minuti prima delle gare delle ore 15:00)
  - **Script pronto all'uso:** `python tools/send_telegram_lineup_reminder.py` (test: `python tools/send_telegram_lineup_reminder.py --dry-run`)
  - **Pagine Promosse nel Messaggio:**
    - 🚑 **Lista Infortunati:** `https://www.fantamasterai.it/infortunati-serie-a/` (controllo perentorio per evitare di giocare in 10).
    - 💡 **Consigli Flash:** `https://www.fantamasterai.it/consigli-fantacalcio/` (riassunti rapidi per ruolo con teaser accattivanti).
    - ⚔️ **Risoluzione Dubbi "Chi Schiero":** `https://www.fantamasterai.it/chi-schiero/` (call to action finale: *"Dubbio atomico sull'ultimo titolare? Risolvilo in 3 secondi col comparatore AI"*).

---

## 🛠️ RECENT BUG FIXES & MONITORAGGIO
- [x] **Risoluzione mancato render iniziale su `/consigli-fantacalcio/` e `/chi-schiero/`:**
  - **Causa individuata:** Nel commit `abf79a9b` era stata involontariamente rimossa la chiamata a `switchTab(initialTab || 'home', false)` all'inizializzazione del DOM in `build_dashboard.py`.
  - **Fix applicato:** Ripristinata la chiamata `switchTab`, gestito `document.readyState` difensivo in `initApp()`, aggiunto `tabChiSchieroBtn` alla lista dei reset nav e aggiornato il Service Worker a `v2` con strategia *Network-First* per le pagine HTML.
  - **Verifica:** Testato in locale e convalidato online in produzione su `https://www.fantamasterai.it/consigli-fantacalcio/` e `https://www.fantamasterai.it/chi-schiero/` (schede e comparatore 1vs1 visibili e operativi).
- [x] **Integrazione "Scommesse Predittive & Differenziali Low-Cost" (Classic & Mantra):**
  - **Obiettivo:** Fornire il vero valore aggiunto predittivo che nessun competitor possiede, affiancando ai Big/Top di reparto i profili a basso costo ad altissimo potenziale asimmetrico.
  - **Architettura (4 Calciatori per Ruolo/Posizione):**
    - 2 Top di Reparto (Certezze assolute: 🥇 TOP 1, 🥈 2° SCELTA)
    - 2 Scommesse Predittive (Low-Cost / Differenziali AI: 🔮 SCOMMESSA AI, 💎 DIFFERENZIALE)
  - **Algoritmo di Opportunity Score:** Filtra i titolari a basso costo (`OVR <= 80` o `FVM <= 28 CR`, `titolarita >= 50%` per movimento e `>= 70%` per portieri) e premia asimmetrie favorevoli (difesa avversaria perforabile xGA/GC, fattore casa, 1° rigorista, Fuori Ruolo Positivo FRP, tiratore da fermo).
  - **Filtri Interattivi HUD:** Implementata barra filtri strategica `[⚡ TUTTI (2 Top + 2 Scommesse)]`, `[⭐ SOLO TOP & CERTEZZE (2)]`, `[🔮 SOLO SCOMMESSE LOW-COST (2)]`.
  - **Copertura Completa:** Attivo su Classic (4 ruoli P, D, C, A) e su tutte le 12 posizioni Mantra (`Por`, `Dd`, `Ds`, `Dc`, `B`, `E`, `M`, `C`, `T`, `W`, `A`, `Pc`).

---

## 🎯 MASTER CHECKLIST (16 PUNTI): ALGORITMO PREDITTIVO & CONSIGLI FORMAZIONE

Metodologia completa in ordine di priorità logica e computazionale per anticipare bonus, eliminare rimpianti e massimizzare il punteggio della rosa:

1. [x] **Controllo Assoluto Probabili Formazioni (`Fantapazz.com`):**
   - Scraping/parsing continuo delle probabili formazioni ufficiali da `https://www.fantapazz.com/calcio/fantacalcio/serie-a/probabili-formazioni`.
   - Verifica titolarità stimate, ballottaggi aperti e percentuali di subentro per i 20 club di Serie A.

2. [x] **Audit Infortunati, Squalificati & Riatletizzazione:**
   - Controllo sanitario DB (`config/injuries.json`, 66 report monitorati).
   - *Gestione Differenziata:* Esclusione dai titolari per infortunati al 100% (icona 🏥/🟥), ma riconoscimento del bonus "Super-Sub" ($+2.0\text{ pt}$) per Top Player in riatletizzazione che subentrano a gara in corso.

3. [x] **Fuori Ruolo Positivo (FRP - Out of Position):**
   - Bonus extra ($+3.5\text{ pt}$) per centrocampisti o trequartisti (`C`, `E`, `T`) che giocano nel tridente d'attacco o come seconda punta (es. Man, Zaccagni, Nico Paz, Pulisic).

4. [x] **Expected FantaMedia (xFM) & Caratura (OVR) (Baseline 65% xFM + 35% OVR):**
   - Valore prestazionale base pesando al 65% il rendimento atteso da metriche avanzate (xG, xA, xFM) e al 35% la qualità intrinseca del calciatore (OVR).

5. [x] **Matchup Avversario & Fattore Campo:**
   - **a. Difesa Avversaria:** $+6.5\text{ pt}$ se la squadra rivale concede molti xGA/gol; $-4.0\text{ pt}$ se la difesa avversaria è blindata ($\le 0.85$ gol subiti/partita).
   - **b. Fattore Campo:** $+2.5\text{ pt}$ per gare in Casa ($\text{🏠}$), $-1.5\text{ pt}$ per Trasferte ($\text{✈️}$).

6. [x] **Fattore Anti-Cannibalizzazione Portiere/Attaccante:**
   - Penalità scontro diretto ($-5.5\text{ pt}$) se schieri un attaccante di movimento che gioca contro il tuo Portiere Titolare, evitando l'auto-annullamento del bonus imbattibilità.

7. [x] **Fattore Coppe Europee & Turnover Stanchezza:**
   - Penalità stanchezza ($-2.0\text{ pt}$) per titolari impegnati 90' in Champions/Europa League a metà settimana; bonus freschezza ($+2.5\text{ pt}$) per le seconde linee che partono titolari in Serie A.

8. [x] **Momento di Forma & Trend Recente (Hot-Streak 3 Gare):**
   - Bonus Momentum ($+3.0\text{ pt}$) per calciatori reduci da fanta-media $> 7.5$ nelle ultime 3 giornate con bonus consecutivi.

9. [x] **Potenziale di Riscatto (Bounce-Back Factor):**
   - Bonus extra ($+4.5\text{ pt}$) per i Top Player ($\text{OVR} \ge 85$) a secco di bonus da più gare che affrontano retroguardie fragili.

10. [x] **Piazzati & Rigori:**
    - $+5.0\text{ pt}$ per i 1° Rigoristi ufficiali dal dischetto; $+2.5\text{ pt}$ per i tiratori di punizioni e corner (maggior volume di xA atteso).

11. [x] **Rischio Malus Disciplinare:**
    - Penalità graduata per calciatori con alta frequenza di cartellini (gialli/rossi) o reduci da sanzioni disciplinari.

12. [x] **Copertura Panchina Antiscivolo (Garanzia 3 Cambi per Reparto):**
    - Disposizione intelligente della panchina assicurando almeno 1 copertura titolare sicura per reparto (P, D, C, A) nei primi 4 slot, prima dei jolly ad alto xFM, per eliminare del tutto il rischio di giocare in 10.

13. [x] **Impatto Modificatore Difesa sul Modulo Ottimale (Switch 3-4-3 vs 4-3-3 / 4-4-2):**
    - Se attivo il Modificatore Difesa, l'algoritmo calcola la Media Voto Pura attesa dei 4 difensori. Se $\text{MV} \ge 6.25$, il sistema converte il modulo dal 3-4-3 al 4-3-3/4-4-2 per incassare la fascia bonus ($+1 / +3 / +6\text{ pt}$).

14. [x] **Effetto Domino Assenze Chiave (Gerarchia Rigori & Assist Ereditati):**
    - Se il 1° rigorista o il rifinitore di un club è infortunato/squalificato, l'algoritmo trasferisce un bonus ereditario ($+3.5\text{ pt}$) al vice-rigorista o al sostituto naturale che prende in mano i piazzati.

15. [x] **Indice di Rischio Orario Match & Certezza Formazione (Anticipi vs Posticipi):**
    - Penalità rischio scontento ($-2.0\text{ pt}$) per calciatori in ballottaggio 50/50 nei posticipi del lunedì (senza formazione ufficiale al momento della consegna), premiando i titolari certi degli anticipi del venerdì/sabato.

16. [x] **Fattore Super-Sub (12° Uomo d'Oro) & Big Match Pressure Index:**
    - Neutralizzazione penalità panchina per subentratori ad alto impatto ($+2.5\text{ pt}$ `⚡ SUPER-SUB`), penalizzazione trasferte proibitive vs Top Club ($-3.5\text{ pt}$) e rimozione badge ridondante `🟢 Disponibile` per pulizia UX.



