# Manuale di Installazione e Deployment

Questa guida descrive la procedura tecnica completa per configurare l'ambiente di esecuzione, installare le dipendenze e avviare il prototipo software su una macchina Linux. Il sistema è stato sviluppato e testato su **Ubuntu 22.04 LTS** in ambiente virtualizzato.

---

## 📋 Capitolo 1: Preparazione dell'Ambiente Virtuale

Il progetto richiede un ambiente Linux isolato. Si consiglia l'utilizzo di una Macchina Virtuale (VM) per garantire l'isolamento e la riproducibilità dell'ambiente Hyperledger Fabric.

> [!NOTE]
> **Se hai già la macchina virtuale pronta, salta al Capitolo 2.** Altrimenti, procedi con la configurazione della VM.

### 1.1 Download e Installazione Software Base

*   **VirtualBox:** [Sito Ufficiale](https://www.virtualbox.org/wiki/Downloads)
*   **Ubuntu Server 22.04 LTS (ISO):** [Sito Ubuntu](https://ubuntu.com/download/server)

### 1.2 Creazione della Macchina Virtuale

1.  **Nuova macchina virtuale:**
    *   Tipo: Linux
    *   Versione: Ubuntu (64-bit)

2.  **Configurazione risorse:**
    *   **RAM:** Almeno 4096 MB (4 GB)
    *   **CPU:** Almeno 2 Core
    *   **Disco:** 20 GB o più (allocazione dinamica consigliata)

3.  **Installazione del sistema operativo:**
    *   Avvia la VM e seleziona l'immagine ISO di Ubuntu Server 22.04 LTS
    *   Segui l'installazione guidata
    *   **Nome utente consigliato:** `vboxuser` (per uniformità con i percorsi documentati)

4.  **Configurazione post-installazione:**
    *   Abilita le Guest Additions di VirtualBox per migliori prestazioni
    *   Configura la connessione di rete (NAT o Bridge, a seconda delle esigenze)
    *   **Configurazione SSH (opzionale ma consigliata):**
        *   Se si utilizza VirtualBox con port forwarding, configurare il forwarding della porta SSH:
            *   Impostazioni VM → Rete → Avanzate → Port Forwarding
            *   Aggiungere regola: Host Port `2222` → Guest Port `22`
        *   Abilitare il servizio SSH nella VM:
            ```bash
            sudo apt install openssh-server -y
            sudo systemctl enable ssh
            sudo systemctl start ssh
            ```
        *   Dalla macchina host, sarà possibile accedere alla VM tramite:
            ```bash
            ssh -p 2222 vboxuser@localhost
            ```

---

## ⚙️ Capitolo 2: Installazione delle Dipendenze di Sistema

Una volta completata l'installazione di Ubuntu all'interno della VM, apri il terminale ed esegui i seguenti comandi in sequenza.

### 2.1 Aggiornamento Sistema e Installazione Strumenti Base

Eseguire l'aggiornamento del sistema e l'installazione degli strumenti fondamentali per lo sviluppo:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git curl wget unzip python3 python3-pip build-essential -y
```

**Cosa stiamo installando:**
*   `git`: Sistema di controllo versione
*   `curl`, `wget`: Strumenti per il download di file
*   `python3`, `python3-pip`: Interprete Python e gestore pacchetti
*   `build-essential`: Toolchain di compilazione (necessario per alcune dipendenze)

### 2.2 Installazione Docker Engine

Hyperledger Fabric utilizza Docker per l'orchestrazione dei container che implementano i nodi della rete blockchain (Peer, Orderer, CouchDB).

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

> [!IMPORTANT]
> **AZIONE RICHIESTA:** Dopo l'esecuzione di questi comandi, è necessario effettuare un **logout e login** (oppure riavviare il sistema con `sudo reboot`) affinché le modifiche ai gruppi utente abbiano effetto e l'utente possa utilizzare Docker senza privilegi `sudo`.

**Verifica installazione:**
```bash
docker --version
docker ps
```
*(Se `docker ps` non restituisce errori di permessi, sei pronto per procedere).*

### 2.3 Installazione Go (Golang)

Il linguaggio Go è richiesto per la compilazione e l'esecuzione del Chaincode (Smart Contract) su Hyperledger Fabric.

```bash
wget https://go.dev/dl/go1.21.6.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.6.linux-amd64.tar.gz

# Configurazione variabili d'ambiente persistenti
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
source ~/.bashrc
```

> [!WARNING]
> Non dimenticare il comando `source ~/.bashrc`. Se salti questo passaggio, il comando `go` non verrà trovato nella sessione corrente.

**Verifica installazione:**
```bash
go version
```

### 2.4 Installazione Binari Hyperledger Fabric

Lo script ufficiale di Hyperledger Fabric scarica automaticamente le immagini Docker necessarie e i binari del framework nella directory `fabric-samples`.

```bash
cd ~
curl -sSL https://bit.ly/2ysbOFE | bash -s
```

Questo comando:
*   Scarica la cartella `fabric-samples` con tutti i binari necessari
*   Scarica le immagini Docker ufficiali di Fabric
*   Configura l'ambiente di test

**Tempo stimato:** 5-10 minuti a seconda della connessione Internet.

---

## 📦 Capitolo 3: Setup del Progetto

### 3.1 Clonazione del Repository

Scaricare il codice sorgente del progetto dal repository Git.

```bash
# Verifica preliminare di git
git --version

cd ~
# Sostituire l'URL seguente con il link alla repository ufficiale del progetto
git clone https://github.com/lp4tr/safefoodchain.git

# Rinomina della cartella per uniformità (Opzionale)
mv safefoodchain tesi
```

### 3.2 Installazione Dipendenze Python

Installare le librerie Python necessarie per il backend (orchestrazione AI) e il frontend Streamlit:

```bash
cd ~/tesi/orchestrator
pip3 install -r requirements.txt
```

Le dipendenze principali includono:
*   `streamlit`: Framework per l'interfaccia web
*   `google-generativeai`: SDK per l'integrazione con Google Gemini AI
*   `python-dotenv`: Gestione variabili d'ambiente da file .env

**Verifica installazione:**
```bash
pip3 list | grep -E "(streamlit|google-generativeai)"
```

### 3.3 Configurazione di Sicurezza (API Key)

Il sistema utilizza variabili d'ambiente per gestire le credenziali sensibili, evitando di esporre chiavi API nel codice sorgente.

1.  Posizionarsi nella cartella dell'orchestratore:
    ```bash
    cd ~/tesi/orchestrator
    ```

2.  Copiare il file template `.env.example` come `.env`:
    ```bash
    cp .env.example .env
    ```

3.  Modificare il file `.env` e inserire la propria chiave API Google Gemini:
    ```bash
    nano .env
    ```

4.  Sostituire il placeholder `AIzaSy...IncollaQuiLaTuaChiave...` con la tua chiave API reale.

    > [!TIP]
    > **Come ottenere la chiave API:**
    > 1. Visita [Google AI Studio](https://makersuite.google.com/app/apikey)
    > 2. Crea una nuova chiave API o usa una esistente
    > 3. Copia la chiave e incollala nel file `.env`

5.  Salvare e chiudere (`CTRL+O`, `Invio`, `CTRL+X`).

**Nota:** Il file `.env` è escluso dal controllo versione (Git) per sicurezza. Il file `.env.example` serve come template di riferimento.

### 3.4 Configurazione Permessi di Esecuzione

Assegnare i permessi di esecuzione allo script Bash che funge da bridge tra Python e Hyperledger Fabric:

```bash
chmod +x ~/tesi/orchestrator/fabric_helper.sh
```

---

## 🚀 Capitolo 4: Esecuzione del Sistema

### 4.1 Avvio della Rete Blockchain

Inizializzare la rete di test Hyperledger Fabric, creare il canale di comunicazione e deployare lo Smart Contract (Chaincode).

```bash
cd ~/fabric-samples/test-network

# 1. Reset preventivo dell'ambiente (rimuove container precedenti se presenti)
./network.sh down

# 2. Avvio della rete e creazione del canale 'mychannel'
./network.sh up createChannel -c mychannel -ca

# 3. Deploy del Chaincode (Logica di Business)
# Nota: Il percorso ~/tesi/chaincode deve contenere il file food_chaincode.go
./network.sh deployCC -ccn basic -ccp ~/tesi/chaincode/ -ccl go
```

**Attendere il messaggio di conferma:**
```text
Chaincode definition committed on channel 'mychannel'
```

### 4.2 Avvio dell'Interfaccia Utente Web

Lanciare l'applicazione web Streamlit che fornisce l'interfaccia utente grafica:

```bash
cd ~/tesi/orchestrator
export LANG=C.UTF-8
streamlit run app.py --server.address 0.0.0.0
```

Il parametro `--server.address 0.0.0.0` consente l'accesso remoto alla VM (utile per accedere dall'host).

---

## 🌐 Capitolo 5: Accesso e Utilizzo del Sistema

### 5.1 Accesso all'Applicazione Web

L'applicazione sarà accessibile via browser all'indirizzo:

🔴 **http://localhost:8501**

**Nota:** Se la VM è configurata con port forwarding e Streamlit è avviato con `--server.address 0.0.0.0`, l'applicazione sarà accessibile anche dalla macchina host tramite lo stesso indirizzo.

### 5.2 Credenziali di Test Preconfigurate

Il sistema include due utenze dimostrative per testare il meccanismo di Role-Based Access Control (RBAC):

| Ruolo | Username | Password | Funzionalità Abilitate |
| :--- | :--- | :--- | :--- |
| **Produttore** | `rossi` | `admin` | Creazione Asset (Scrittura), Lettura, Chat AI |
| **Consumatore** | `mario` | `1234` | Sola Lettura, Chat AI (Creazione bloccata) |

### 5.3 Interfaccia CLI Alternativa

Oltre all'interfaccia web, è disponibile un'interfaccia a riga di comando per utenti avanzati:

```bash
cd ~/tesi/orchestrator
python3 main.py
```

---

## ✅ Verifica dell'Installazione

Per verificare che tutte le componenti siano configurate correttamente, eseguire i seguenti comandi di verifica:

```bash
# Verifica Docker
docker --version
docker ps

# Verifica Go
go version

# Verifica Python e dipendenze
python3 --version
pip3 list | grep -E "(streamlit|google-generativeai)"

# Verifica stato della rete Fabric
cd ~/fabric-samples/test-network
./network.sh status
```

Tutti i comandi dovrebbero restituire output senza errori.

---

## 🔧 Troubleshooting

### Problema: Docker richiede privilegi sudo
> **Errore:** `permission denied while trying to connect to the Docker daemon socket`
*   **Soluzione:** L'utente non è nel gruppo docker. Esegui `sudo usermod -aG docker $USER`, poi fai logout/login.

### Problema: Chaincode non si deploya correttamente
> **Errore:** `Error: failed to normalize chaincode path` o `go: not found`
*   **Soluzione 1:** Controlla che il percorso `~/tesi/chaincode/` esista e contenga `food_chaincode.go`.
*   **Soluzione 2:** Verifica che Go sia nel PATH (`go version`). Se fallisce, riesegui `source ~/.bashrc`.

### Problema: Streamlit non si avvia
> **Errore:** `ModuleNotFoundError: No module named 'streamlit'`
*   **Soluzione:** Le dipendenze non sono installate. Esegui `pip3 install -r requirements.txt`.

### Problema: Errore API Key Gemini non valida
> **Errore:** `google.api_core.exceptions.InvalidArgument: 400 API key not valid`
*   **Soluzione:** La chiave in `.env` è errata. Rigenerala su Google AI Studio e aggiorna il file.

### Problema: Container Docker non si avviano
> **Errore:** `Cannot connect to the Docker daemon`
*   **Soluzione:** Docker non è attivo. Avvialo con `sudo systemctl start docker`.

---

## 📚 Riferimenti e Documentazione Aggiuntiva

*   **Documentazione funzionale:** Consultare `FLUSSO_ESECUZIONE.md` per i dettagli sul funzionamento del sistema.
*   **Documentazione generale:** Consultare `README.md` per informazioni generali sul progetto.
*   **Manuale di test:** Consultare `TEST_MANUAL.md` per le procedure di test e validazione.
*   **Hyperledger Fabric:** [Sito Ufficiale](https://hyperledger-fabric.readthedocs.io/)

---

**Fine Manuale di Installazione**
