# Sistema di Tracciabilità Alimentare basato su Hyperledger Fabric e Generative AI

**Anno Accademico:** 2025/2026

![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge&logo=medallion)
![Blockchain](https://img.shields.io/badge/Hyperledger-Fabric-blue?style=for-the-badge&logo=hyperledger)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange?style=for-the-badge&logo=google)
![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=for-the-badge&logo=python)
![Go](https://img.shields.io/badge/Go-1.21+-cyan?style=for-the-badge&logo=go)

---

## 📌 Abstract

Il presente progetto di tesi propone un'architettura ibrida per la gestione della Supply Chain alimentare. L'obiettivo è risolvere il problema della barriera tecnica nell'interazione con la Blockchain, integrando un modello di Intelligenza Artificiale Generativa (Google Gemini) che funge da interprete semantico tra il linguaggio naturale dell'utente e le transazioni rigide del registro distribuito.

Il sistema garantisce **immutabilità** dei dati, **trasparenza** di filiera e **accessibilità** tramite interfaccia utente semplificata.

---

## 🎯 Caratteristiche Principali

*   ✅ **Blockchain-based**: Tracciabilità immutabile e trasparente dei prodotti alimentari.
*   ✅ **AI-Powered**: Interfaccia in linguaggio naturale tramite Google Gemini AI.
*   ✅ **Role-Based Access Control**: Gestione differenziata dei permessi (Produttore/Consumatore).
*   ✅ **Dual Interface**: Interfaccia Web (Streamlit) e CLI per massima flessibilità.
*   ✅ **Smart Contract**: Chaincode in Go per la gestione della logica di business.

---

## 🏗️ Architettura del Sistema

Il sistema è strutturato su tre livelli logici:

### 1. Livello Data (Blockchain)

*   **Network:** Hyperledger Fabric (Test Network)
*   **Smart Contract (Chaincode):** Sviluppato in **Go**
*   **Funzionalità:**
    *   Gestisce la logica di business e la persistenza degli asset alimentari (`FoodAsset`) sul ledger.
    *   Implementa controlli di accesso a livello di transazione.
    *   Operazioni supportate: `CreateAsset`, `UpdateStage`, `ReadAsset`, `DeleteAsset`.

### 2. Livello Application (Middleware)

*   **Orchestrator:** Script Python che gestisce il flusso delle richieste.
*   **AI Engine:** Integrazione con **Google Gemini** per l'estrazione di *intent* (azione) ed *entity* (dati) dal prompt utente.
*   **Fabric Client:** Script Bash wrapper per l'invocazione dei binari del peer Fabric.

### 3. Livello Presentation (Frontend)

*   **User Interface:** Sviluppata in **Streamlit**.
*   **RBAC (Role-Based Access Control):** Gestione simulata delle identità (*Producer* vs *Consumer*) per dimostrare la segregazione dei permessi.
*   **Interfaccia CLI:** Alternativa a riga di comando per utenti avanzati.

```text
[ UTENTE ] ↔ [ FRONTEND (Web/CLI) ]
                     ↕
             [ ORCHESTRATOR (Python) ]
                     ↕
             [ FABRIC BRIDGE (Bash) ]
                     ↕
             [ BLOCKCHAIN (Hyperledger) ]
```

---

## 📂 Struttura della Repository

```text
tesi/
├── chaincode/
│   ├── food_chaincode.go      # Smart Contract in Go
│   ├── go.mod                 # Dipendenze Go
│   └── go.sum                 # Checksum dipendenze
├── orchestrator/
│   ├── main.py                # Core orchestrator e logica AI
│   ├── app.py                 # Interfaccia web Streamlit
│   ├── fabric_helper.sh       # Script bridge Python-Fabric
│   ├── requirements.txt       # Dipendenze Python
│   ├── .env.example           # Template per file .env (chiave API)
│   └── .gitignore             # File esclusi da Git
├── README.md                  # Questo file
├── INSTALL.md                 # Guida tecnica per il deployment
├── FLUSSO_ESECUZIONE.md       # Documentazione dettagliata del flusso
└── TEST_MANUAL.md             # Manuale operativo per test e validazione
```

---

## 🔐 Sicurezza e Ruoli

Il sistema implementa una logica di accesso differenziata per dimostrare l'integrità del registro:

| Ruolo | Permessi | Descrizione |
| :--- | :--- | :--- |
| **Producer** | `Read` + `Write` | Può registrare, aggiornare ed eliminare i lotti dal ledger |
| **Consumer** | `Read Only` | Può interrogare la storia del prodotto, ma non può alterarla |

### Credenziali di Test

| Ruolo | Username | Password |
| :--- | :--- | :--- |
| **Produttore** | `rossi` | `admin` |
| **Consumatore** | `mario` | `1234` |

---

## 🚀 Quick Start

### Prerequisiti

*   Ubuntu 22.04 LTS (o equivalente)
*   4 GB RAM, 2 CPU Cores, 20 GB spazio disco
*   Accesso a Internet

### Installazione Rapida

1.  **Clona il repository:**
    ```bash
    git clone https://github.com/lp4tr/safefoodchain.git
    cd tesi
    ```

2.  **Segui la guida di installazione completa:**
    Consulta [INSTALL.md](INSTALL.md) per i dettagli completi dell'installazione.

3.  **Avvia la rete blockchain:**
    ```bash
    cd ~/fabric-samples/test-network
    ./network.sh up createChannel -c mychannel -ca
    ./network.sh deployCC -ccn basic -ccp ~/tesi/chaincode/ -ccl go
    ```

4.  **Avvia l'interfaccia web:**
    ```bash
    cd ~/tesi/orchestrator
    streamlit run app.py --server.address 0.0.0.0
    ```

5.  **Accedi all'applicazione:**
    Apri il browser su `http://localhost:8501`

---

## 💻 Utilizzo

### Interfaccia Web

1.  Esegui il login con le credenziali di test.
2.  **Produttore:** Puoi usare il tab "Registra" per creare nuovi asset o il tab "Chat" per interagire in linguaggio naturale.
3.  **Consumatore:** Puoi usare il tab "Chat" per consultare informazioni sui prodotti.

### Interfaccia CLI

```bash
cd ~/tesi/orchestrator
python3 main.py
```

Seleziona il ruolo e interagisci con il sistema usando comandi in linguaggio naturale, ad esempio:
*   *"Registra 100kg di mele da Trento"*
*   *"Mostra informazioni sul prodotto FOOD123"*
*   *"Aggiorna lo stadio di FOOD123 a distribuzione"*

---

## 🔄 Flusso di Esecuzione

Per una comprensione dettagliata del flusso di esecuzione del sistema, consulta [FLUSSO_ESECUZIONE.md](FLUSSO_ESECUZIONE.md).

### Flusso Semplificato

```text
Utente → Interfaccia (Web/CLI)
    ↓
Orchestrator (Python) → Google Gemini AI
    ↓
Estrazione Intent e Parametri
    ↓
Fabric Helper Script (Bash)
    ↓
Hyperledger Fabric Network
    ↓
Chaincode (Go) → Ledger
    ↓
Risposta → Utente
```

---

## 🛠️ Tecnologie Utilizzate

*   **Blockchain:** Hyperledger Fabric 2.x
*   **Smart Contract:** Go (golang)
*   **Backend:** Python 3.8+
*   **AI/ML:** Google Gemini API
*   **Frontend:** Streamlit
*   **Container:** Docker
*   **Version Control:** Git

---

## 📋 Dipendenze Principali

### Python
*   `streamlit` - Framework web per l'interfaccia utente
*   `google-generativeai` - SDK per Google Gemini AI
*   `python-dotenv` - Gestione variabili d'ambiente da file .env

### Go
*   `github.com/hyperledger/fabric-contract-api-go` - API per chaincode Fabric

---

## 📖 Documentazione

*   **[INSTALL.md](INSTALL.md)** - Guida completa all'installazione e deployment
*   **[FLUSSO_ESECUZIONE.md](FLUSSO_ESECUZIONE.md)** - Documentazione dettagliata del flusso di esecuzione
*   **[TEST_MANUAL.md](TEST_MANUAL.md)** - Manuale operativo per test e validazione del sistema

---

## 🧪 Testing

Il sistema include utenti di test preconfigurati per verificare le funzionalità:

*   **Test Produttore:** Crea nuovi asset e aggiorna lo stato.
*   **Test Consumatore:** Consulta informazioni senza possibilità di modifica.

Per una guida dettagliata sui test, consulta [TEST_MANUAL.md](TEST_MANUAL.md).

---

## ⚠️ Note Importanti

*   Questo è un progetto di **dimostrazione** per scopi didattici.
*   Le credenziali di test sono hardcoded e **non devono essere usate in produzione**.
*   Le credenziali API sono gestite tramite variabili d'ambiente (file `.env`) e non sono incluse nel repository. È disponibile un file `.env.example` come template di riferimento.
*   Il sistema utilizza la Hyperledger Fabric Test Network, non adatta per ambienti di produzione.

---

## 🤝 Contribuire

Questo è un progetto di tesi. Per suggerimenti o segnalazioni di bug, apri una issue nella repository.

## 📄 Licenza

Progetto di tesi - Uso accademico

---

**Anno Accademico 2025/2026**