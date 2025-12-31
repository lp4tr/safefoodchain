"""
Presentation Layer - Web Interface (Streamlit)

Interfaccia web per interazione utente tramite browser. Implementa MVC:
- Model: Business Logic in main.py
- View: Interfaccia Streamlit (questo file)
- Controller: Routing richieste tra View e Model
- Controller: Routing richieste tra View e Model
"""

from typing import Dict
import streamlit as st
from main import call_gemini_auto, submit_fabric_transaction, evaluate_fabric_query, GeminiIntent

st.set_page_config(page_title="Safe Food Chain", page_icon="🍏")
st.title("🍏 Assistente Filiera Alimentare Sicura")

# Database utenti in memoria
# In produzione: database esterno, hashing password, session tokens, HTTPS
USERS: Dict[str, Dict[str, str]] = {
    "rossi": {"pass": "admin", "role": "Producer"},
    "mario": {"pass": "1234", "role": "Consumer"}
}

# Gestione sessione
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    with st.form("login_form"):
        username: str = st.text_input("Username")
        password: str = st.text_input("Password", type="password")
        if st.form_submit_button("Accedi"):
            if username in USERS and USERS[username]["pass"] == password:
                st.session_state.user = USERS[username]
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Credenziali non valide")
else:
    user: Dict[str, str] = st.session_state.user
    role: str = user["role"]
    
    st.sidebar.success(f"Loggato come: {st.session_state.username} ({role})")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

    # Interfaccia basata su ruolo (RBAC)
    if role == "Producer":
        tab1, tab2 = st.tabs(["Registra", "Chat"])

        with tab1:
            st.header("Registra Prodotto")
            with st.form("register_form"):
                col1, col2 = st.columns(2)
                with col1:
                    asset_id: str = st.text_input("ID Asset", value="FOOD123")
                    product_type: str = st.text_input("Tipo", value="Mela")
                with col2:
                    quantity: float = st.number_input("Quantità", min_value=1.0, value=100.0)
                    unit: str = st.text_input("Unità", value="kg")

                origin: str = st.text_input("Origine", value="Trento")

                if st.form_submit_button("Registra"):
                    intent: GeminiIntent = GeminiIntent(
                        intent="createAsset",
                        args={
                            "assetId": asset_id,
                            "productType": product_type,
                            "quantity": quantity,
                            "unit": unit,
                            "origin": origin
                        }
                    )
                    with st.spinner("Registrazione..."):
                        res: str = submit_fabric_transaction(intent, "producer")
                        if "SUCCESS" in res:
                            st.success(res)
                        else:
                            st.error(res)

        with tab2:
            st.header("Chat Producer")
            if "messages" not in st.session_state:
                st.session_state.messages = []

            with st.form("producer_chat_form", clear_on_submit=True):
                col_input, col_btn = st.columns([6, 1])
                with col_input:
                    prompt: str = st.text_input("Scrivi...", label_visibility="collapsed")
                with col_btn:
                    submitted: bool = st.form_submit_button("Invia")

            if submitted and prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                intent: GeminiIntent = call_gemini_auto(prompt, "producer")
                resp: str = ""
                
                if intent.intent == "createAsset":
                    resp = submit_fabric_transaction(intent, "producer")
                elif intent.intent == "updateStage":
                    resp = submit_fabric_transaction(intent, "producer")
                elif intent.intent == "deleteAsset":
                    resp = submit_fabric_transaction(intent, "producer")
                elif intent.intent == "queryAsset":
                    resp = evaluate_fabric_query(intent)
                else:
                    resp = f"Intento non chiaro o non autorizzato: {intent.intent}"

                st.session_state.messages.append({"role": "assistant", "content": resp})

            for m in st.session_state.messages:
                st.chat_message(m["role"]).write(m["content"])

    elif role == "Consumer":
        tab1, = st.tabs(["Chat"])

        with tab1:
            st.header("Chat Consumer")
            if "messages" not in st.session_state:
                st.session_state.messages = []

            with st.form("consumer_chat_form", clear_on_submit=True):
                col_input, col_btn = st.columns([6, 1])
                with col_input:
                    prompt: str = st.text_input("Chiedi info...", label_visibility="collapsed")
                with col_btn:
                    submitted: bool = st.form_submit_button("Invia")

            if submitted and prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                intent: GeminiIntent = call_gemini_auto(prompt, "consumer")
                resp: str = ""

                if intent.intent == "queryAsset":
                    resp = evaluate_fabric_query(intent)
                elif intent.intent == "unauthorized":
                    resp = "Non autorizzato."
                else:
                    resp = "Non ho capito."

                st.session_state.messages.append({"role": "assistant", "content": resp})

            for m in st.session_state.messages:
                st.chat_message(m["role"]).write(m["content"])