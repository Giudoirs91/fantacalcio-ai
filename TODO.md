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
