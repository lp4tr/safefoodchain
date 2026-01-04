# FLUSSO DI ESECUZIONE DEL SISTEMA - FILIERA ALIMENTARE SICURA

## Panoramica del Sistema

Il sistema è composto da 4 componenti principali che interagiscono per fornire un'esperienza utente basata sull'Intelligenza Artificiale, garantita dalla sicurezza della Blockchain.

1.  **Interfaccia Utente (CLI/Web)**: Punto di ingresso per l'utente.
2.  **Orchestratore (Python)**: Cervello del sistema, gestisce l'NLP e la logica di business.
3.  **Fabric Helper (Bash)**: Ponte verso la rete Hyperledger Fabric.
4.  **Chaincode (Go)**: Smart Contract che gestisce il ledger immutabile.

---

## 🔄 Diagramma di Flusso Generale

```text
       👤 UTENTE
           │
           │ Input ("Crea mele...")
           ▼
  ┌──────────────────────┐
  │  INTERFACCIA (CLI)   │
  └────────┬─────────────┘
           │
           │ Testo
           ▼
  ┌──────────────────────┐              ┌────────────────┐
  │     ORCHESTRATOR     │  Prompt      │                │
  │      (Python)        ├─────────────►│    GEMINI      │
  │                      │              │      AI        │
  │                      │◄─────────────┤                │
  └────────┬─────────────┘   Intent     └────────────────┘
           │                 (JSON)
           │
           ▼
  ┌──────────────────────┐
  │    FABRIC HELPER     │
  │       (Bash)         │
  └────────┬─────────────┘
           │
           │ Peer Invoke
           ▼
  ┌──────────────────────┐
  │  HYPERLEDGER FABRIC  │
  │       (Network)      │
  └────────┬─────────────┘
           │
           │ Chaincode Call
           ▼
  ┌──────────────────────┐
  │    FOOD CHAINCODE    │
  │         (Go)         │◄───────────► [ 🗄️ LEDGER ]
  └──────────────────────┘
```

---

## ⚡ Flusso Dettagliato: Step-by-Step

### FASE 1: Avvio e Inizializzazione

Al lancio di `main.py` o `app.py`:

1.  **Caricamento Configurazione sicura**:
    *   Il sistema carica le variabili d'ambiente da `.env` (file non versionato per sicurezza).
    *   **CRITICO**: Se `GEMINI_API_KEY` manca, il sistema termina immediatamente (`sys.exit(1)`).

2.  **Selezione Modello AI Intelligente**:
    *   La funzione `get_best_available_model()` scansiona l'account Google dell'utente.
    *   Filtra i modelli che supportano `generateContent`.
    *   Seleziona automaticamente il modello più performante (es. `gemini-1.5-flash` o fallback su `gemini-pro`).

### FASE 2: Interazione e NLP (Natural Language Processing)

Quando l'utente scrive un messaggio (es. *"Crea 100kg di Mele da Trento"*):

1.  **Prompt Engineering Dinamico**:
    L'orchestratore costruisce un prompt specifico per il ruolo dell'utente per garantire il rispetto delle policy (RBAC).

    *Template del Prompt:*
    ```text
    Sei un Assistente per la Filiera Alimentare. Rispondi SOLO in JSON.
    Il tuo utente è un: {USER_ROLE}.
    
    ISTRUZIONI RUOLO:
    - Se Producer: Puoi creare 'createAsset', aggiornare 'updateStage'...
    - Se Consumer: Puoi SOLO leggere 'queryAsset'. Se chiedono creazione -> 'unauthorized'.
    
    Input Utente: "{USER_TEXT}"
    ```

2.  **Estrazione Intent (Semantic Parsing)**:
    Gemini restituisce un JSON strutturato, ad esempio:
    ```json
    {
      "intent": "createAsset",
      "args": {
        "assetId": "MELA_01",
        "productType": "Mela", 
        "quantity": "100", 
        "unit": "kg", 
        "origin": "Trento"
      }
    }
    ```

3.  **Gestione Errori AI**:
    Se l'AI non risponde in JSON valido, il sistema cattura l'eccezione e restituisce un intent di tipo `error`, prevenendo crash.

### FASE 3: Esecuzione Blockchain

L'orchestratore analizza l'`intent` e invoca lo script bash appropriato.

#### Caso A: Scrittura (Create/Update/Delete)
*   **Python**: Chiama `subprocess.run(["fabric_helper.sh", "create", ...])`.
*   **Bash**: Imposta le variabili TLS e invoca `peer chaincode invoke`.
    *   *Nota*: Le scritture richiedono l'invio della transazione all'Orderer e il consenso dei Peer.
*   **Chaincode (Go)**:
    1.  Verifica i permessi (es. solo "Producer").
    2.  Verifica la logica di business (es. "asset già esistente?").
    3.  Scrive sul World State (`PutState`).

#### Caso B: Lettura (Query)
*   **Python**: Chiama `subprocess.run(["fabric_helper.sh", "query", ...])`.
*   **Bash**: Invoca `peer chaincode query`.
    *   *Nota*: Le letture sono veloci perché interrogano solo il Peer locale, non generano blocchi.
*   **Chaincode (Go)**: Legge dal World State (`GetState`) e restituisce i dati grezzi.

### FASE 4: Feedback all'Utente

1.  Il risultato del comando Bash (stdout/stderr) viene catturato da Python.
2.  Python parsa il risultato cercando keyword come `status:200`.
3.  Formatta un messaggio leggibile ("✅ SUCCESS: ...") o un errore chiaro.
4.  L'interfaccia (CLI o Web) mostra il messaggio finale.

---

## 🛠️ Stack Tecnologico e Ruoli

| Componente | Tecnologia | Responsabilità Principale |
|------------|------------|---------------------------|
| **Orchestratore** | Python 3.10+ | NLP, Routing, Gestione Errori |
| **AI Driver** | Google Gemini SDK | Comprensione del linguaggio naturale |
| **Bridge** | Bash Scripting | Astrazione dei comandi complessi di Fabric |
| **Smart Contract** | Go (Golang) | Logica di business immutabile, RBAC |
| **Ledger** | Hyperledger Fabric | Registro distribuito e permissioned |

---

## 🔒 Focus Security

*   **API Key Protection**: Mai hardcoded, sempre caricate da environment.
*   **RBAC (Role Based Access Control)**:
    1.  **Livello AI**: Il prompt istruisce il modello a riconoscere tentativi non autorizzati.
    2.  **Livello App**: Python controlla il ruolo prima di invocare lo script.
    3.  **Livello Chaincode**: Il contratto Go esegue il controllo finale "on-chain" per massima sicurezza.

---
**Fine Documentazione Flusso**
