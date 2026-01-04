# Manuale Operativo: Test e Validazione

Questo documento guida l'utente attraverso la verifica completa del sistema **SafeFoodChain**.
Il sistema utilizza un'interfaccia a riga di comando (CLI) basata su AI che interpreta il linguaggio naturale per interagire con la Blockchain Hyperledger Fabric.

---

## 📋 Prerequisiti

1. **Sistema Avviato**: Assicurarsi che la rete Fabric e il servizio `orchestrator` siano attivi.
2. **Setup CLI**: Eseguire lo script principale:
   ```bash
   python3 orchestrator/main.py
   ```
   *(Assicurarsi di aver attivato il virtual environment e installato le dipendenze)*

---

## 🧪 Scenari di Test

Eseguire i test in sequenza per simulare il ciclo di vita reale di un prodotto.

### ✅ TEST 1: Ciclo di Vita del Produttore (Happy Path)

**Ruolo:** `Produttore` (Producer)
**Obiettivo:** Verificare la creazione e gestione standard di un asset.

| Step | Azione Utente (Prompt suggeriti) | Risultato Atteso | Note |
|------|----------------------------------|------------------|------|
| **1.1** | Seleziona ruolo: `Produttore` | CLI conferma ruolo: `PRODUCER` | |
| **1.2** | *"Crea un nuovo lotto di Mele ID MELA_01, quantità 500 kg, origine Trento"* | `SUCCESS: Asset MELA_01 creato nel Ledger.` | Verifica creazione. |
| **1.3** | *"Mostrami i dettagli di MELA_01"* | JSON con `currentStage: "Raccolto"` | Verifica lettura immediata. |
| **1.4** | *"Aggiorna MELA_01, lo stato ora è 'In Magazzino'"* | `SUCCESS: Asset MELA_01 aggiornato.` | Verifica aggiornamento stato. |
| **1.5** | *"Come sta il lotto MELA_01?"* | JSON con `currentStage: "In Magazzino"` | Verifica persistenza modifica. |

---

### ⛔ TEST 2: Controllo Accessi (RBAC) - Consumatore

**Ruolo:** `Consumatore` (Consumer)
**Obiettivo:** Verificare che il consumatore abbia accesso di *sola lettura* e non possa modificare il ledger.

| Step | Azione Utente | Risultato Atteso | Note |
|------|---------------|------------------|------|
| **2.1** | Seleziona ruolo: `Consumatore` | CLI conferma ruolo: `CONSUMER` | Riavviare script se necessario. |
| **2.2** | *"Dammi info su MELA_01"* | Mostra dettagli corretti (`In Magazzino`) | Condivisione ledger verificata. |
| **2.3** | *"Crea un nuovo asset FALSO_99"* | `ACCESSO NEGATO` o `Unauthorized` | L'AI o il Chaincode devono bloccare. |
| **2.4** | *"Aggiorna MELA_01 in 'Venduto'"* | `ACCESSO NEGATO` | Tentativo di modifica bloccato. |
| **2.5** | *"Cancella il lotto MELA_01"* | `ACCESSO NEGATO` | Tentativo di eliminazione bloccato. |

---

### ⚠️ TEST 3: Gestione Errori e Edge Cases

**Ruolo:** `Produttore`
**Obiettivo:** Verificare la robustezza del sistema contro input errati o duplicati.

| Step | Azione Utente | Risultato Atteso | Note |
|------|---------------|------------------|------|
| **3.1** | *"Crea MELA_01..."* (Asset già esistente) | `FABRIC ERROR` / `asset MELA_01 already exists` | Idempotenza creazione. |
| **3.2** | *"Aggiorna il lotto FANTASMA_999"* | `FABRIC ERROR` / `Asset not found` | Verifica integrità referenziale. |
| **3.3** | *"Elimina MELA_01"* | `SUCCESS: Asset MELA_01 eliminato` | Pulizia finale. |
| **3.4** | *"Cerca MELA_01"* | `Nessun dato trovato` | Verifica eliminazione avvenuta. |

---

## 🤖 TEST 4: Flessibilità Linguistica (AI)

**Ruolo:** `Produttore` o `Consumatore`
**Obiettivo:** Verificare che l'AI capisca diverse formulazioni della stessa intenzione.

Provate queste varianti per la **Ricerca**:
1. *"Voglio sapere tutto sul pacco MELA_01"*
2. *"MELA_01: status report"*
3. *"C'è qualcosa nel sistema con ID MELA_01?"*

Provate queste varianti per la **Creazione** (solo Produttore):
1. *"Inserisci nel sistema: 200 litri di Olio da Bari, codice OLIO_NEW"*
2. *"Registra produzione: OLIO_NEW, Olio, 200, litri, Bari"*

**Esito Positivo:** Se il sistema estrae correttamente l'intent (`queryAsset` o `createAsset`) e i parametri corretti (ID, Quantità, ecc.).

---

**Fine Manuale di Test**
