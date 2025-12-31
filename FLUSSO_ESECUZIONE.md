# FLUSSO DI ESECUZIONE DEL SISTEMA - FILIERA ALIMENTARE SICURA

## Panoramica del Sistema

Il sistema è composto da 4 componenti principali che interagiscono tra loro:

1. **Interfaccia Utente** (CLI o Web)
   - `main.py`: Interfaccia a riga di comando (CLI)
   - `app.py`: Interfaccia web Streamlit

2. **Orchestratore** (`main.py`)
   - Interpreta il linguaggio naturale usando Google Gemini AI
   - Gestisce la logica di business e il routing delle richieste

3. **Helper Script** (`fabric_helper.sh`)
   - Bridge tra Python e Hyperledger Fabric
   - Esegue i comandi `peer chaincode` per comunicare con la blockchain

4. **Chaincode** (`food_chaincode.go`)
   - Smart contract sulla blockchain
   - Gestisce la logica di business per la tracciabilità

---

## FLUSSO COMPLETO: DALL'AVVIO ALLA TERMINAZIONE

### FASE 1: AVVIO DEL SISTEMA

#### Scenario A: Interfaccia CLI (`python main.py`)

```
1. main.py viene eseguito
   ↓
2. Configurazione e Inizializzazione
   - Carica variabili d'ambiente dal file .env usando load_dotenv()
   - Estrae GEMINI_API_KEY da os.getenv("GEMINI_API_KEY")
   - Se la chiave API non è presente: stampa errore e termina con sys.exit(1)
   - Configura genai.configure(api_key=GEMINI_API_KEY)
   - Chiama get_best_available_model() per trovare automaticamente il miglior modello Gemini disponibile:
     * Itera su tutti i modelli disponibili tramite genai.list_models()
     * Seleziona solo modelli Gemini che supportano 'generateContent'
     * Se nessun modello è trovato, usa fallback 'gemini-pro'
   - Salva ACTIVE_MODEL_NAME con il modello trovato
   ↓
3. Punto di ingresso
   - Chiama main_loop()
```

#### Scenario B: Interfaccia Web (`streamlit run app.py`)

```
1. app.py viene eseguito da Streamlit
   ↓
2. Configurazione pagina e database utenti
   - Carica il database USERS (rossi/mario)
   - Configura la pagina Streamlit
   ↓
3. Gestione autenticazione
   - Verifica se l'utente è loggato (st.session_state.user)
   - Se non loggato: mostra form di login
   - Se loggato: procede all'interfaccia basata sul ruolo
```

---

### FASE 2: INTERAZIONE UTENTE

#### Scenario A: CLI - Selezione Ruolo

```
main_loop() viene eseguito
   ↓
1. Mostra banner di benvenuto
   ↓
2. Loop per selezione ruolo:
   - Chiede: "Chi sei? (Produttore/Consumatore)"
   - Valida input: "produttore"/"producer" → user_role = "producer"
                  "consumatore"/"consumer" → user_role = "consumer"
   - Se "esci"/"exit" → termina programma
   ↓
3. Conferma ruolo e mostra istruzioni
```

#### Scenario B: Web - Login

```
Gestione autenticazione
   ↓
1. Utente inserisce username e password nel form
   ↓
2. Verifica credenziali:
   - Controlla se username esiste in USERS
   - Verifica password corrispondente
   ↓
3. Se valide:
   - Salva st.session_state.user = USERS[username]
   - Salva st.session_state.username = username
   - st.rerun() → ricarica pagina
   ↓
4. Interfaccia basata sul ruolo
   - Estrae role = user["role"]
   - Mostra interfaccia Producer o Consumer
```

---

### FASE 3: RICHIESTA UTENTE

#### Scenario A: CLI - Input Utente

```
Loop principale
   ↓
1. Legge input utente: user_text = input("\n👤 Tu: ")
   ↓
2. Gestisce comandi speciali:
   - "esci"/"exit"/"quit" → break (termina loop)
   - Input vuoto → continue (ignora)
   ↓
3. Interpretazione linguaggio naturale
   - Chiama call_gemini_auto(user_text, user_role)
```

#### Scenario B: Web - Form o Chat

**Producer - Tab "Registra":**
```
Interfaccia Producer
   ↓
1. Utente compila form (asset_id, product_type, quantity, unit, origin)
   ↓
2. Clicca "Registra"
   ↓
3. Crea GeminiIntent manuale:
   intent = GeminiIntent(
       intent="createAsset",
       args={...}
   )
   ↓
4. Chiama submit_fabric_transaction(intent, "producer")
```

**Producer/Consumer - Tab "Chat":**
```
Interfaccia Chat
   ↓
1. Utente scrive messaggio in chat
   ↓
2. Aggiunge messaggio a st.session_state.messages
   ↓
3. Interpretazione linguaggio naturale (main.py)
   - Chiama call_gemini_auto(prompt, user_role)
```

---

### FASE 4: INTERPRETAZIONE LINGUAGGIO NATURALE

```
call_gemini_auto(nl_text, user_role) (main.py)
   ↓
1. Stampa messaggio informativo: "🤖 (Gemini) Uso modello: {ACTIVE_MODEL_NAME}..."
   ↓
2. Costruisce prompt per Gemini AI:
   - Aggiunge istruzioni basate sul ruolo (producer/consumer)
   - Include esempi di output JSON attesi
   - Aggiunge il testo dell'utente
   ↓
3. Chiama Google Gemini AI:
   - Crea istanza del modello: model = genai.GenerativeModel(ACTIVE_MODEL_NAME)
     (usa il modello determinato all'avvio tramite get_best_available_model())
   - Genera risposta: response = model.generate_content(prompt)
   ↓
4. Processa risposta:
   - Pulisce testo: rimuove ```json ... ``` e spazi extra
   - Parsa JSON: data = json.loads(clean_text)
   ↓
5. Gestione errori:
   - Se parsing JSON fallisce o errore API: cattura Exception
   - Stampa: "❌ Errore IA: {e}"
   - Restituisce GeminiIntent(intent="error", args={})
   ↓
6. Crea e restituisce GeminiIntent:
   return GeminiIntent(
       intent=data.get("intent", "unknown"),
       args=data.get("args", {})
   )
```

**Possibili intent estratti:**
- `"createAsset"`: creare un nuovo prodotto
- `"updateStage"`: aggiornare lo stadio
- `"queryAsset"`: leggere informazioni
- `"deleteAsset"`: eliminare un prodotto
- `"unauthorized"`: azione non permessa
- `"error"`: errore nell'interpretazione

---

### FASE 5: ESECUZIONE OPERAZIONE

#### Caso A: Transazione di Scrittura (createAsset, updateStage)

```
submit_fabric_transaction(intent, user_role) (main.py)
   ↓
1. Estrae asset_id dagli argomenti
   ↓
2. In base a intent.intent:
   
   Se "createAsset":
      - Prepara argomenti: assetId, productType, quantity, unit, origin, userRole
      - Esegue: subprocess.run([SCRIPT_PATH, "create", ...])
   
   Se "updateStage":
      - Prepara argomenti: assetId, newStage, userRole
      - Esegue: subprocess.run([SCRIPT_PATH, "update", ...])
   
   Se "deleteAsset":
   - Prepara argomenti: assetId, userRole
   - Esegue: subprocess.run([SCRIPT_PATH, "delete", ...])
   ↓
3. Verifica risultato:
   - returncode == 0 AND "status:200" in stderr → SUCCESS
   - Altrimenti → FABRIC ERROR
   ↓
4. Restituisce stringa risultato
```

**Esecuzione fabric_helper.sh:**

```
fabric_helper.sh riceve argomenti da Python
   ↓
Configurazione Ambiente Fabric
   - Imposta variabili d'ambiente (FABRIC_SAMPLES_PATH, PATH, ecc.)
   - Configura certificati TLS (ORDERER_CA, PEER1_TLS, PEER2_TLS)
   ↓
Lettura Argomenti
   - FUNCTION = $1 (create/update/query)
   - ASSET_ID = $2
   - Altri argomenti = $3-$7
   ↓
Esecuzione Comandi Fabric
   
   Se FUNCTION == "create":
      - Esegue: peer chaincode invoke -c '{"function":"CreateAsset",...}'
      - Invoca CreateAsset() su food_chaincode.go
   
   Se FUNCTION == "update":
      - Esegue: peer chaincode invoke -c '{"function":"UpdateStage",...}'
      - Invoca UpdateStage() su food_chaincode.go
   
   Se FUNCTION == "delete":
   - Esegue: peer chaincode invoke -c '{"function":"DeleteAsset",...}'
   - Invoca DeleteAsset() su food_chaincode.go
```

**Esecuzione Chaincode:**

```
food_chaincode.go riceve invocazione da Fabric
   ↓
Funzioni di Scrittura
   
   CreateAsset():
      1. Valida permessi (solo producer)
      2. Verifica che asset non esista già
      3. Recupera clientID (identità utente)
      4. Crea struttura FoodAsset
      5. Serializza in JSON
      6. Salva sul ledger: ctx.GetStub().PutState(assetID, bytes)
      7. Restituisce risultato
   
   UpdateStage():
      1. Valida permessi (producer o logistics)
      2. Legge asset esistente dal ledger
      3. Aggiorna CurrentStage e Owner
      4. Serializza in JSON
      5. Salva sul ledger: ctx.GetStub().PutState(assetID, bytes)
      6. Restituisce risultato
   
   DeleteAsset():
      1. Valida permessi (solo producer)
      2. Verifica che asset esista
      3. Elimina dal world state: ctx.GetStub().DelState(assetID)
      4. Restituisce risultato
   ↓
Risultato torna a fabric_helper.sh → Python → Utente
```

#### Caso B: Query di Lettura (queryAsset)

```
evaluate_fabric_query(intent) (main.py)
   ↓
1. Estrae asset_id dagli argomenti
   ↓
2. Esegue: subprocess.run([SCRIPT_PATH, "query", asset_id])
   ↓
3. Verifica risultato:
   - returncode == 0 → DATI TROVATI
   - Altrimenti → Nessun dato trovato
   ↓
4. Restituisce stringa risultato
```

**Esecuzione fabric_helper.sh:**

```
Esecuzione Comandi Fabric
   ↓
Se FUNCTION == "query":
   - Esegue: peer chaincode query -c '{"function":"ReadAsset",...}'
   - Invoca ReadAsset() su food_chaincode.go
```

**Esecuzione Chaincode:**

```
food_chaincode.go riceve query da Fabric
   ↓
Funzioni di Lettura
   
   ReadAsset():
      1. Legge dal ledger: bytes = ctx.GetStub().GetState(assetID)
      2. Se bytes == nil → errore "asset not found"
      3. Deserializza JSON in FoodAsset
      4. Restituisce asset
   ↓
Risultato torna a fabric_helper.sh → Python → Utente
```

---

### FASE 6: RISPOSTA ALL'UTENTE

#### Scenario A: CLI

```
main_loop() (main.py)
   ↓
1. Riceve intent da call_gemini_auto()
   ↓
2. In base a intent.intent:
   
   "createAsset":
      - Verifica permessi (solo producer)
      - Chiama submit_fabric_transaction()
      - Stampa risultato
   
   "updateStage":
      - Verifica permessi (solo producer)
      - Chiama submit_fabric_transaction()
      - Stampa risultato
   
   "deleteAsset":
      - Verifica permessi (solo producer)
      - Chiama submit_fabric_transaction()
      - Stampa risultato

   "queryAsset":
      - Chiama evaluate_fabric_query()
      - Stampa risultato
   
   "unauthorized":
      - Stampa messaggio di errore
   
   "error":
      - Stampa messaggio di errore
   ↓
3. Torna al loop principale (FASE 3)
```

#### Scenario B: Web

```
app.py
   ↓
1. Riceve intent da call_gemini_auto()
   ↓
2. Esegue operazione (submit_fabric_transaction o evaluate_fabric_query)
   ↓
3. Aggiunge risposta a st.session_state.messages
   ↓
4. Mostra risposta con st.chat_message("assistant").write(resp)
   ↓
5. Streamlit ricarica automaticamente la pagina
   ↓
6. Torna in attesa di nuovo input (FASE 3)
```

---

### FASE 7: TERMINAZIONE

#### Scenario A: CLI

```
1. Utente scrive "esci"/"exit"/"quit"
   ↓
2. main_loop() → break (esce dal loop)
   ↓
3. Programma termina
```

**Oppure:**

```
1. Utente preme Ctrl+C
   ↓
2. KeyboardInterrupt exception
   ↓
3. main_loop() → break (esce dal loop)
   ↓
4. Programma termina
```

#### Scenario B: Web

```
1. Utente clicca "Logout" nella sidebar
   ↓
2. app.py - Gestione autenticazione:
   - st.session_state.user = None
   - st.session_state.messages = []
   - st.rerun()
   ↓
3. Torna al form di login
```

**Oppure:**

```
1. Utente chiude il browser
   ↓
2. Streamlit mantiene la sessione per un periodo limitato
   ↓
3. Dopo timeout, la sessione viene eliminata
```

---

## DIAGRAMMA DI FLUSSO COMPLETO

```
┌─────────────────────────────────────────────────────────────────┐
│                    AVVIO SISTEMA                                │
│  CLI: python main.py          Web: streamlit run app.py         │
└────────────────────┬──────────────────┬────────────────────────┘
                      │                  │
                      ▼                  ▼
        ┌─────────────────────┐  ┌──────────────────────┐
        │  Configurazione     │  │  Login Utente         │
        │  - Gemini API        │  │  - Verifica credenziali│
        │  - Modello AI        │  │  - Salva sessione     │
        └──────────┬───────────┘  └──────────┬───────────┘
                   │                          │
                   ▼                          ▼
        ┌─────────────────────┐  ┌──────────────────────┐
        │  Selezione Ruolo    │  │  Interfaccia Ruolo    │
        │  (CLI)              │  │  (Web)               │
        └──────────┬──────────┘  └──────────┬───────────┘
                   │                          │
                   └──────────┬───────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │      INPUT UTENTE                        │
        │  CLI: input()    Web: form/chat_input()  │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │  INTERPRETAZIONE LINGUAGGIO NATURALE     │
        │  call_gemini_auto() → Gemini AI          │
        │  → Restituisce GeminiIntent              │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      ROUTING INTENT                      │
        │  createAsset → submit_fabric_transaction │
        │  updateStage → submit_fabric_transaction |
        |  deleteAsset → submit_fabric_transaction │
        │  queryAsset  → evaluate_fabric_query     │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      ESECUZIONE FABRIC                   │
        │  subprocess.run(fabric_helper.sh)        │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      FABRIC HELPER SCRIPT                │
        │  - Configura ambiente Fabric             │
        │  - Esegue peer chaincode invoke/query    │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      CHAINCODE (BLOCKCHAIN)              │
        │  food_chaincode.go                       │
        │  - CreateAsset()                         |
        |  - UpdateStage()                         |
        |  - DeleteAsset()                         │
        │  - ReadAsset()                           │
        │  - Scrive/Legge dal ledger               │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      RISPOSTA                            │
        │  Chaincode → Helper → Python → Utente    │
        └──────────────────┬──────────────────────┘
                            │
                            ▼
        ┌─────────────────────────────────────────┐
        │      LOOP PRINCIPALE                     │
        │  Torna in attesa di nuovo input          │
        │  (o termina se "esci"/Ctrl+C)            │
        └─────────────────────────────────────────┘
```

---

## INTERAZIONI TRA FILE

### main.py
- **Importa**: 
  - `json`, `os`, `subprocess` (standard library)
  - `google.generativeai` (SDK Google Gemini)
  - `dataclasses`, `typing` (tipizzazione)
  - `dotenv` (caricamento variabili d'ambiente)
- **Viene importato da**: `app.py` (call_gemini_auto, submit_fabric_transaction, evaluate_fabric_query, GeminiIntent)
- **Chiama**: 
  - `fabric_helper.sh` tramite subprocess.run()
  - Google Gemini API tramite genai.GenerativeModel()
- **Dipendenze esterne**: 
  - File `.env` nella cartella orchestrator (contiene GEMINI_API_KEY)
- **Non chiama direttamente**: `food_chaincode.go` (viene chiamato indirettamente)

### app.py
- **Importa**: `main.py` (funzioni core)
- **Viene importato da**: Nessuno (entry point Streamlit)
- **Chiama**: Funzioni di `main.py`
- **Non chiama direttamente**: `fabric_helper.sh` o `food_chaincode.go`

### fabric_helper.sh
- **Riceve argomenti da**: `main.py` (tramite subprocess)
- **Chiama**: `peer chaincode invoke/query` (comandi Fabric)
- **Non chiama direttamente**: `food_chaincode.go` (viene invocato da Fabric)

### food_chaincode.go
- **Riceve invocazioni da**: Hyperledger Fabric (tramite peer chaincode)
- **Non chiama**: Nessun altro file (è isolato sulla blockchain)
- **Viene invocato indirettamente da**: `fabric_helper.sh` → `peer chaincode` → Fabric → Chaincode

---

## PUNTI CHIAVE DEL FLUSSO

1. **Separazione delle responsabilità**:
   - `main.py`: Logica di business e NLP
   - `app.py`: Interfaccia utente web
   - `fabric_helper.sh`: Bridge Python-Fabric
   - `food_chaincode.go`: Logica blockchain

2. **Configurazione e inizializzazione**:
   - Caricamento configurazione da file `.env` (variabili d'ambiente)
   - Validazione chiave API Gemini all'avvio (termina se mancante)
   - Selezione automatica del modello Gemini disponibile (get_best_available_model)
   - Fallback a 'gemini-pro' se nessun modello è trovato

3. **Comunicazione asincrona**:
   - Python → Bash: subprocess.run() (sincrono)
   - Bash → Fabric: peer chaincode (sincrono)
   - Fabric → Chaincode: invocazione (sincrona)

4. **Gestione errori**:
   - Ogni livello gestisce i propri errori
   - Gli errori vengono propagati verso l'alto fino all'utente
   - Errori AI: catturati e restituiti come intent "error"
   - Errori Fabric: restituiti come stringa di errore

5. **Persistenza**:
   - CLI: Nessuna (tutto in memoria durante l'esecuzione)
   - Web: Streamlit session_state (persiste durante la sessione)
   - Blockchain: Ledger Fabric (persistenza permanente)
   - Configurazione: File `.env` (chiavi API, non versionato)

---

## ESEMPIO CONCRETO: "Registra 100kg di mele da Trento"

```
1. Utente (Producer) → CLI: "Registra 100kg di mele da Trento"
   ↓
2. main.py → call_gemini_auto("Registra 100kg di mele da Trento", "producer")
   ↓
3. Gemini AI analizza e restituisce:
   {
     "intent": "createAsset",
     "args": {
       "assetId": "FOOD123",
       "productType": "Mela",
       "quantity": "100",
       "unit": "kg",
       "origin": "Trento"
     }
   }
   ↓
4. main.py → submit_fabric_transaction(intent, "producer")
   ↓
5. subprocess.run([fabric_helper.sh, "create", "FOOD123", "Mela", "100", "kg", "Trento", "producer"])
   ↓
6. fabric_helper.sh → peer chaincode invoke -c '{"function":"CreateAsset","Args":[...]}'
   ↓
7. Fabric invoca food_chaincode.go → CreateAsset()
   ↓
8. CreateAsset():
   - Valida permessi ✓
   - Verifica duplicati ✓
   - Crea FoodAsset
   - Salva sul ledger
   ↓
9. Risultato torna: "SUCCESS: Asset FOOD123 creato nel Ledger."
   ↓
10. main.py stampa: "SISTEMA: SUCCESS: Asset FOOD123 creato nel Ledger."
   ↓
11. Utente vede il messaggio di successo
```

---

## NOTE TECNICHE

- **Threading**: Il sistema è single-threaded, ogni operazione è sequenziale
- **Timeout**: Le operazioni Fabric possono avere timeout (configurabili)
- **Concorrenza**: Multiple istanze possono eseguire query simultaneamente, ma le transazioni richiedono consenso
- **Sicurezza**: 
  - I permessi sono validati sia in Python che nel chaincode (doppia verifica)
  - Chiave API Gemini caricata da variabile d'ambiente (file `.env`, non versionato)
  - Validazione chiave API all'avvio: il programma termina se mancante
- **Selezione Modello AI**:
  - All'avvio, il sistema cerca automaticamente il miglior modello Gemini disponibile
  - Itera su genai.list_models() per trovare modelli compatibili
  - Seleziona solo modelli Gemini che supportano 'generateContent'
  - Fallback a 'gemini-pro' se nessun modello è trovato o in caso di errore
