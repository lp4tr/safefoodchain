"""
Business Logic Layer - Orchestration & Semantic Parsing

Orchestratore centrale che coordina l'interazione tra Presentation Layer (app.py),
servizio AI (Google Gemini) e Data Layer (Hyperledger Fabric Chaincode).

"""

import json
import os
import sys
import subprocess
import logging
from typing import Any, Dict, Optional
import google.generativeai as genai
from dataclasses import dataclass
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurazione da variabili d'ambiente (Twelve-Factor App)
load_dotenv()
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.critical("API Key non trovata nel file .env")
    print("ERRORE: API Key non trovata. Configurare GEMINI_API_KEY in .env")
    sys.exit(1)

SCRIPT_PATH: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fabric_helper.sh")
genai.configure(api_key=GEMINI_API_KEY)


def get_best_available_model() -> str:
    """
    Seleziona automaticamente il modello Gemini disponibile per l'account.
    
    Implementa fallback robusto: scansiona modelli disponibili e filtra quelli
    Gemini con supporto 'generateContent'. In caso di errore, usa 'gemini-pro'.
    
    Returns:
        str: Nome del modello Gemini da utilizzare
    """
    print("Scansione modelli compatibili...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
                print(f"Modello selezionato: {m.name}")
                return m.name
        logger.warning("Nessun modello trovato, uso fallback 'gemini-pro'")
        return 'gemini-pro'
    except Exception as e:
        logger.error(f"Errore scansione modelli: {e}")
        return 'gemini-pro'


ACTIVE_MODEL_NAME: str = get_best_available_model()


@dataclass
class GeminiIntent:
    """
    Struttura dati per l'intent estratto dal linguaggio naturale.
    
    Attributes:
        intent: Azione da eseguire (es. "createAsset", "queryAsset", "updateStage")
        args: Parametri dell'azione (es. assetId, productType, quantity, ecc.)
    """
    intent: str
    args: Dict[str, Any]


def call_gemini_auto(nl_text: str, user_role: str) -> GeminiIntent:
    """
    Interpreta il linguaggio naturale usando Google Gemini AI.
    
    Implementa semantic parsing: converte richiesta testuale in intent strutturato.
    Il comportamento dell'AI viene adattato al ruolo utente per RBAC.
    
    Args:
        nl_text: Testo in linguaggio naturale dell'utente
        user_role: Ruolo utente ("producer" o "consumer") per controllo accessi
    
    Returns:
        GeminiIntent: Intent estratto con parametri. In caso di errore, intent="error"
    """
    print(f"Elaborazione con modello: {ACTIVE_MODEL_NAME}...")
    
    # Costruzione istruzioni RBAC in base al ruolo
    if user_role == "producer":
        role_instruction = """
        Sei un Produttore.
        AZIONI PERMESSE:
        1. 'createAsset': Registrare un nuovo prodotto.
           Campi: assetId (inventa se manca), productType (es. Mela, Olio), quantity (numero), unit (es. kg, litri), origin (città).
        2. 'updateStage': Aggiornare lo stato (Opzionale).
           Campi: assetId, newStage.
        3. 'deleteAsset': Eliminare un prodotto.
           Campi: assetId.
        4. 'queryAsset': Cercare un prodotto.
           Campi: assetId.
        """
    elif user_role == "consumer":
        role_instruction = """
        Sei un Consumatore.
        AZIONI PERMESSE:
        1. 'queryAsset': Leggere info o storia di un prodotto.
           Campi: assetId.
        NON PUOI creare o modificare nulla. Se l'utente chiede di creare, rispondi con intent 'unauthorized'.
        """
    else:
        role_instruction = "Ruolo sconosciuto. Solo lettura permessa (queryAsset)."

    prompt: str = f"""
    Sei un Assistente per la Filiera Alimentare Sicura. Rispondi SOLO in JSON.
    
    Il tuo utente è un: {user_role.upper()}.
    {role_instruction}

    OUTPUT ESEMPIO CREAZIONE: {{ "intent": "createAsset", "args": {{ "assetId": "FOOD123", "productType": "Mela", "quantity": "100", "unit": "kg", "origin": "Trento" }} }}
    OUTPUT ESEMPIO QUERY: {{ "intent": "queryAsset", "args": {{ "assetId": "FOOD123" }} }}
    OUTPUT ESEMPIO UNAUTHORIZED: {{ "intent": "unauthorized", "args": {{ "reason": "Consumers cannot create assets" }} }}

    UTENTE: "{nl_text}"
    """

    try:
        model = genai.GenerativeModel(ACTIVE_MODEL_NAME)
        response = model.generate_content(prompt)
        clean_text: str = response.text.replace("```json", "").replace("```", "").strip()
        data: Dict[str, Any] = json.loads(clean_text)
        return GeminiIntent(intent=data.get("intent", "unknown"), args=data.get("args", {}))
    except json.JSONDecodeError as e:
        logger.error(f"Errore parsing JSON da Gemini: {e}")
        return GeminiIntent(intent="error", args={"reason": "JSON parsing failed"})
    except Exception as e:
        logger.error(f"Errore chiamata API Gemini: {e}")
        return GeminiIntent(intent="error", args={"reason": str(e)})


def submit_fabric_transaction(intent: GeminiIntent, user_role: str) -> str:
    """
    Esegue una transazione di scrittura su Hyperledger Fabric.
    Adatta interfaccia bash (fabric_helper.sh) al dominio Python.
    Supporta intent "createAsset" e "updateStage".
    
    Args:
        intent: Intent estratta dall'AI con azione e parametri
        user_role: Ruolo utente per logging e audit
    
    Returns:
        str: Risultato operazione (SUCCESS, FABRIC ERROR, SYSTEM ERROR)
    """
    asset_id: str = intent.args.get('assetId', 'N/A')

    if intent.intent == "createAsset":
        print(f"Creazione asset {asset_id} come {user_role}...")
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    SCRIPT_PATH, "create",
                    str(asset_id),
                    str(intent.args.get("productType", "Generico")),
                    str(intent.args.get("quantity", "0")),
                    str(intent.args.get("unit", "u")),
                    str(intent.args.get("origin", "Unknown")),
                    str(user_role)
                ],
                capture_output=True, text=True
            )
            if result.returncode == 0 and "status:200" in result.stderr:
                logger.info(f"Asset {asset_id} creato da {user_role}")
                return f"SUCCESS: Asset {asset_id} creato nel Ledger."
            else:
                logger.error(f"Errore Fabric: {result.stderr}")
                return f"FABRIC ERROR: {result.stderr.strip()}"
        except subprocess.SubprocessError as e:
            logger.error(f"Errore subprocess: {e}")
            return f"SYSTEM ERROR: {e}"
        except Exception as e:
            logger.error(f"Errore imprevisto: {e}")
            return f"SYSTEM ERROR: {e}"

    elif intent.intent == "updateStage":
        print(f"Aggiornamento asset {asset_id} come {user_role}...")
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    SCRIPT_PATH, "update",
                    str(asset_id),
                    str(intent.args.get("newStage", "In Transito")),
                    str(user_role)
                ],
                capture_output=True, text=True
            )
            if result.returncode == 0 and "status:200" in result.stderr:
                logger.info(f"Asset {asset_id} aggiornato da {user_role}")
                return f"SUCCESS: Asset {asset_id} aggiornato."
            else:
                logger.error(f"Errore Fabric: {result.stderr}")
                return f"FABRIC ERROR: {result.stderr.strip()}"
        except subprocess.SubprocessError as e:
            logger.error(f"Errore subprocess: {e}")
            return f"SYSTEM ERROR: {e}"
        except Exception as e:
            logger.error(f"Errore imprevisto: {e}")
            return f"SYSTEM ERROR: {e}"

    elif intent.intent == "deleteAsset":
        print(f"Eliminazione asset {asset_id} come {user_role}...")
        try:
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [
                    SCRIPT_PATH, "delete",
                    str(asset_id),
                    str(user_role)
                ],
                capture_output=True, text=True
            )
            if result.returncode == 0 and "status:200" in result.stderr:
                logger.info(f"Asset {asset_id} eliminato da {user_role}")
                return f"SUCCESS: Asset {asset_id} eliminato dal Ledger."
            else:
                logger.error(f"Errore Fabric: {result.stderr}")
                return f"FABRIC ERROR: {result.stderr.strip()}"
        except subprocess.SubprocessError as e:
            logger.error(f"Errore subprocess: {e}")
            return f"SYSTEM ERROR: {e}"
        except Exception as e:
            logger.error(f"Errore imprevisto: {e}")
            return f"SYSTEM ERROR: {e}"

    logger.warning(f"Intent non gestito: {intent.intent}")
    return "Intent non gestito in scrittura."


def evaluate_fabric_query(intent: GeminiIntent) -> str:
    """
    Esegue una query (lettura) su Hyperledger Fabric.
    
    Le query non modificano lo stato e non richiedono consenso tra i peer.
    
    Args:
        intent: Intent estratta dall'AI con assetId da leggere
    
    Returns:
        str: Dati asset o messaggio di errore
    """
    asset_id: str = intent.args.get('assetId', 'N/A')
    print(f"Lettura asset: {asset_id}...")
    try:
        result: subprocess.CompletedProcess[str] = subprocess.run(
            [SCRIPT_PATH, "query", str(asset_id)],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            logger.info(f"Query asset {asset_id} eseguita")
            return f"DATI TROVATI: {result.stdout.strip()}"
        else:
            logger.warning(f"Asset {asset_id} non trovato: {result.stderr}")
            return f"Nessun dato trovato per {asset_id}."
    except subprocess.SubprocessError as e:
        logger.error(f"Errore subprocess: {e}")
        return f"SYSTEM ERROR: {e}"
    except Exception as e:
        logger.error(f"Errore imprevisto: {e}")
        return f"SYSTEM ERROR: {e}"


def main_loop() -> None:
    """
    Loop principale CLI per interazione utente.
    
    Gestisce selezione ruolo (RBAC), richieste in linguaggio naturale e routing
    degli intent alle funzioni appropriate.
    """
    print("\n" + "="*50)
    print("   ASSISTENTE FILIERA ALIMENTARE SICURA")
    print("="*50)
    
    user_role: str = ""
    while True:
        role_input: str = input("Chi sei? (Produttore/Consumatore): ").strip().lower()
        if role_input in ["produttore", "producer"]:
            user_role = "producer"
            break
        elif role_input in ["consumatore", "consumer"]:
            user_role = "consumer"
            break
        elif role_input in ["esci", "exit"]:
            return
        else:
            print("Ruolo non valido. Riprova.")

    print(f"Ruolo impostato: {user_role.upper()}")
    print("Scrivi 'esci' per chiudere.")
    print("-" * 50)

    while True:
        try:
            user_text: str = input("\nTu: ")
            if user_text.lower() in ["esci", "exit", "quit"]:
                break
            if not user_text.strip():
                continue

            intent: GeminiIntent = call_gemini_auto(user_text, user_role)

            if intent.intent == "createAsset":
                if user_role != "producer":
                    print("ACCESSO NEGATO: Solo i produttori possono creare asset.")
                else:
                    print(f"Intento: Creazione ({intent.args.get('assetId')})")
                    print(f"SISTEMA: {submit_fabric_transaction(intent, user_role)}")
            
            elif intent.intent == "updateStage":
                if user_role != "producer":
                    print("ACCESSO NEGATO: Non hai i permessi per aggiornare lo stato.")
                else:
                    print(f"Intento: Aggiornamento ({intent.args.get('assetId')})")
                    print(f"SISTEMA: {submit_fabric_transaction(intent, user_role)}")

            elif intent.intent == "queryAsset":
                print(f"Intento: Ricerca ({intent.args.get('assetId')})")
                print(f"SISTEMA: {evaluate_fabric_query(intent)}")

            elif intent.intent == "unauthorized":
                print(f"SISTEMA: Azione non autorizzata ({intent.args.get('reason')}).")

            elif intent.intent == "error":
                print("SISTEMA: Errore IA.")
            else:
                print("SISTEMA: Non ho capito o azione non supportata.")
                
        except KeyboardInterrupt:
            print("\n\nUscita dal programma...")
            break


if __name__ == "__main__":
    main_loop()