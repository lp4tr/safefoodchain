# Manuale Operativo: Test e Validazione

Questo documento guida l'utente attraverso la verifica del sistema: dalla validazione delle funzionalità di scrittura, aggiornamento, eliminazione e lettura sulla Blockchain.

## 🧪 Esecuzione dei Test Funzionali

### ✅ TEST A: Creazione Asset (Ruolo: Produttore)

**Obiettivo:** Verificare che un utente autorizzato possa scrivere un nuovo asset sulla blockchain.

**Prerequisiti:** Sistema avviato e accessibile su `http://localhost:8501`

**Procedura:**

1. **Login:**
   - Username: `rossi`
   - Password: `admin`

2. **Azione:**
   - Vai nella tab **"Chat"** (o usa il tab **"Registra"** per inserimento manuale)
   - Scrivi nella chat:
     ```
     Crea un nuovo lotto ID OLIO_55, quantità 100 litri, origine Bari
     ```
   
   **Alternativa (Form):**
   - Vai nella tab **"Registra"**
   - Compila il form:
     - ID Asset: `OLIO_55`
     - Tipo: `Olio`
     - Quantità: `100`
     - Unità: `litri`
     - Origine: `Bari`
   - Clicca su **"Registra"**

3. **Verifica Immediata:**
   - Il sistema deve rispondere: `✅ SUCCESS: Asset OLIO_55 creato nel Ledger.`
   - Deve apparire un messaggio di conferma della transazione

4. **Risultato Atteso:** Transazione confermata con successo, asset creato sulla blockchain.

---

### 🔄 TEST B: Aggiornamento Asset (Ruolo: Produttore)

**Obiettivo:** Verificare che il proprietario possa modificare lo stato di un asset esistente.

**Prerequisiti:** Test A completato con successo (asset `OLIO_55` creato).

**Procedura:**

1. **Contesto:** Sei ancora loggato come `rossi` (Produttore).

2. **Azione:**
   - Nella tab **"Chat"**, scrivi:
     ```
     Aggiorna lo stato del lotto OLIO_55 in 'Imbottigliato'
     ```

3. **Verifica dell'Avvenuta Modifica:**
   - Chiedi all'AI nella chat:
     ```
     Dammi i dettagli di OLIO_55
     ```
   - Oppure:
     ```
     Mostra informazioni sul prodotto OLIO_55
     ```

4. **Risultato Atteso:**
   - Nel JSON di risposta, il campo `currentStage` deve essere `"Imbottigliato"` (e non più quello di default).
   - Il sistema deve mostrare i dati aggiornati dell'asset.

---
### 🗑️ TEST C: Eliminazione Asset (Ruolo: Produttore)

**Obiettivo:** Verificare che il produttore possa rimuovere un asset dal sistema.

**Procedura:**

1. **Contesto:** Sei ancora loggato come `rossi` (Produttore).

2. **Creazione Asset:**
   - Scrivi nella chat:
     ```
     Crea lotto SCARTO_01, tipo Test, qta 1, origine Void
     ```

3. **Azione:**
   - Nella tab **"Chat"**, scrivi:
     ```
     Elimina il lotto SCARTO_01
     ```

4. **Verifica dell'Avvenuta Modifica:**
   - Il sistema deve rispondere: ✅ SUCCESS: Asset SCARTO_01 eliminato dal Ledger.
   - Chiedi all'AI nella chat:
     ```
     Dammi i dettagli di SCARTO_01
     ```
   - Oppure:
     ```
     Mostra informazioni sul prodotto SCARTO_01
     ```

5. **Risultato Atteso:**
   - Il sistema deve rispondere: `Nessun dato trovato` o `Asset not found`.
   - L'asset viene rimosso correttamente e non è più rintracciabile nelle query successive.

---

### 👁️ TEST D: Lettura e Trasparenza (Ruolo: Consumatore)

**Obiettivo:** Verificare che un utente diverso possa vedere i dati aggiornati (Condivisione del Ledger).

**Prerequisiti:** Test A e B completati con successo.

**Procedura:**

1. **Logout:**
   - Clicca su **"Logout"** nella sidebar.

2. **Login:**
   - Username: `mario`
   - Password: `1234`

3. **Azione:**
   - Nella tab **"Chat"**, scrivi:
     ```
     Cerca informazioni su OLIO_55
     ```
   - Oppure:
     ```
     Mostra i dettagli del prodotto OLIO_55
     ```

4. **Verifica:**
   - Il sistema deve mostrare i dati inseriti da `rossi`.
   - Lo stato deve essere `"Imbottigliato"` (come aggiornato nel Test B).
   - Tutti i campi (quantità, origine, tipo) devono corrispondere ai dati originali.

5. **Risultato Atteso:** Il Consumatore può leggere tutti i dati dell'asset creato dal Produttore, dimostrando che la Blockchain funziona come "unica fonte di verità" tra attori diversi.

---

### ⛔ TEST E: Sicurezza e Immutabilità (Ruolo: Consumatore)

**Obiettivo:** Verificare che il Consumatore NON possa alterare i dati, dimostrando il meccanismo di Role-Based Access Control (RBAC).

**Prerequisiti:** Test C completato (loggato come `mario`).

**Procedura:**

#### Tentativo 1: Creazione Asset (Non Autorizzata)

1. **Azione:**
   - Nella chat, scrivi:
     ```
     Crea lotto FALSO_01, quantità 50 kg, origine Roma
     ```

2. **Risultato Atteso:**
   - `⛔ ERRORE: Accesso Negato` o `Non autorizzato.`
   - Il sistema deve bloccare l'operazione e informare l'utente che non ha i permessi necessari.

#### Tentativo 2: Aggiornamento Asset (Non Autorizzato)

1. **Azione:**
   - Nella chat, scrivi:
     ```
     Aggiorna lo stato di OLIO_55 in 'Venduto'
     ```

2. **Risultato Atteso:**
   - `⛔ ERRORE: Non hai i permessi per aggiornare lo stato.`
   - Il sistema deve rifiutare l'operazione.

3. **Verifica Finale:**
   - Chiedi nuovamente i dettagli di `OLIO_55`:
     ```
     Dammi i dettagli di OLIO_55
     ```
   - Lo stato deve essere ancora `"Imbottigliato"` (non modificato), dimostrando l'immutabilità dei dati per utenti non autorizzati.

4. **Risultato Atteso:** Entrambi i tentativi devono fallire, dimostrando che il sistema implementa correttamente il controllo degli accessi basato sui ruoli.

#### Tentativo 3: Eliminazione Asset (Non Autorizzata)

1. **Azione:**
   - (Come utente `mario` / Consumatore) Scrivi nella chat:
     ```
     Elimina il lotto OLIO_55
     ```

2. **Risultato Atteso:**
   - `⛔ ERRORE: Accesso Negato` oppure `Azione non permessa`.
   - L'assistente AI dovrebbe riconoscere che il ruolo Consumatore non ha il permesso di cancellare e bloccare l'intent (restituendo `unauthorized`) oppure il chaincode restituirà errore.

---

**Fine Manuale di Test**
