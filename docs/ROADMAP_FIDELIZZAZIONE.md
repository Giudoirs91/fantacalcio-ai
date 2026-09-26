# Roadmap Fidelizzazione Utenti - FantaMaster AI

Documento strategico delle funzionalità ad alto impatto per massimizzare la retention settimanale, la viralità organica e il valore percepito per i fantallenatori sul portale `fantamasterai.it`.

---

## 1. Tool "Chi Schiero?" (Head-to-Head Matchday Decider)
* **Obiettivo:** Risolvere il dubbio settimanale su chi schierare tra due o tre alternative di rosa.
* **Funzionamento:**
  - Confronto secco 1vs1 (o 1vs1vs1) tra calciatori selezionati dall'utente.
  - Algoritmo decisionale basato su:
    - Expected FantaMedia (xFM) ponderata sul momento di forma.
    - Fanta-Fixture Difficulty (difficoltà dell'avversario e gol/xG concessi dalla difesa rivale).
    - Fattore campo (rendimento storico casa vs trasferta).
    - Status rigorista / tiratore di piazzati.
  - Verdetto percentuale immediato (es. *68% Politano vs 32% Orsolini*) con motivazione sintetica in linguaggio naturale.
* **Frequenza d'uso:** Ogni venerdì/sabato prima della consegna delle formazioni.

---

## 2. "Trade Analyzer" (Valutatore Scambi AI)
* **Obiettivo:** Guidare gli utenti durante le sessioni di mercato e scambi privati tra leghe.
* **Funzionamento:**
  - Input: Pacchetto A ("I miei giocatori") vs Pacchetto B ("I giocatori offerti").
  - Calcolo del differenziale di valore:
    - Delta xFM complessivo su base settimanale.
    - Valutazione dell'indice di fragilità fisica e rischio stop muscolari residui.
    - Difficoltà del calendario da qui a fine stagione per i rispettivi club.
    - Copertura ruoli (segnalazione se lo scambio lascia un reparto scoperto).
  - Output visivo:
    - 🟢 *Scambio Vantaggioso (+X fantapunti attesi)*
    - 🟡 *Scambio Equo*
    - 🔴 *Scambio a Rischio / Sconsigliato* con spiegazione dei punti critici.

---

## 3. "La Mia Rosa" (Cruscotto Personale GDPR-Free in LocalStorage)
* **Obiettivo:** Trasformare il sito in uno strumento quotidiano salvando la squadra dell'utente senza barriere all'ingresso.
* **Funzionamento:**
  - Salvataggio dei 25 calciatori della rosa direttamente in `localStorage` del browser (nessun cookie tracciante, nessun login richiesto, 100% GDPR-compliant).
  - Funzionalità sbloccate per l'utente:
    - **Top 11 Personalizzata:** generazione della miglior formazione schierabile per ogni specifica giornata.
    - **Alert Rischio Inferiorità Numerica:** avvisi immediati su squalifiche, infortuni o ballottaggi a rischio voto nullo.
    - **Monitoraggio del Valore:** andamento delle quotazioni FVM e scostamento xFM della propria rosa.

---

## 4. "Il Bollettino del Venerdì" (AI Matchday Briefing)
* **Obiettivo:** Contenuto editoriale automatizzato ad alta frequenza per creare un appuntamento fisso.
* **Struttura:**
  1. 🎯 **I 5 Caldi della Giornata:** calciatori con xFM elevato e matchup difensivo favorevole.
  2. ⚠️ **Le 3 Trappole:** big o nomi altisonanti a rischio prestazione opaca, stanchezza da coppe o panchina da turnover.
  3. 💎 **Le 3 Scommesse Low-Cost:** giocatori a basso costo o titolari a sorpresa per completare la formazione con pochi crediti.

---

## 5. Generatore di Social Card Virali ("Condividi la tua Formazione")
* **Obiettivo:** Acquisizione organica di nuovo pubblico attraverso il passaparola spontaneo.
* **Funzionamento:**
  - Generazione client-side (via Canvas/SVG) di card grafiche premium ad alta risoluzione:
    - Formazione 2D sul campo con layout tattico ufficiale.
    - Badge con punteggio totale xFM atteso.
    - Branding discreto ed elegante *FantaMaster AI*.
  - Tasto di condivisione immediata su WhatsApp (gruppi lega fantacalcio), Telegram e download come immagine per Instagram Stories.

---

## 6. Rilevatore di Regressione (Buy Low / Sell High)
* **Obiettivo:** Fornire ai fanta-allenatori un vantaggio competitivo sul mercato prima degli avversari.
* **Funzionamento:**
  - Tab dedicata che evidenzia i massimi scostamenti tra FantaMedia reale (FM) ed Expected FantaMedia (xFM):
    - **Vendi al picco (Overperforming):** calciatori con media voto/bonus gonfiata da episodi fortuiti o sovraperformance statistica non sostenibile.
    - **Compra al ribasso (Underperforming):** calciatori con bonus ancora bassi ma volume di tiri, xG e passaggi chiave altissimi (imminente sblocco statistico).
