import streamlit as st
import os
from modules.brain import Brain
from dotenv import load_dotenv

# 1. Force Local Environment Sync
load_dotenv(override=True)

st.set_page_config(page_title="Spark Master Console", layout="wide", page_icon="⚡")

# --- 2. THE SIDEBAR (Control Center) ---
with st.sidebar:
    st.title("⚡ Spark Console")
    st.info("Status: Online | BaaS Tier: Active") # Updated for Architect vibe
    
    role_options = {
        "1": "Senior BaaS Architect (Global)",
        "2": "Real Estate Use-Case (Demo Mode)"
    }

    role_id = st.selectbox(
        "Select Active Persona:",
        options=list(role_options.keys()),
        index=0, # Default to the Architect
        format_func=lambda x: role_options[x]
    ) 

    st.markdown("---")
    st.subheader("🌐 Communication Settings")
    
    lang_options = {
        "en": "Professional English", # Promoted to primary for demo
        "te": "Telugu (తెలుగు)",
        "tenglish": "Tenglish (Local Mix)"
    }
    
    selected_lang = st.selectbox(
        "Response Language:",
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x]
    )

    # NEW: Multi-Modal Upload for Owners to test live brochures/screenshots
    st.markdown("---")
    st.subheader("📂 Visual Intelligence")
    uploaded_file = st.file_uploader("Analyze Brochure/Screenshot:", type=['png', 'jpg', 'jpeg', 'pdf'])

    # Hot-reload logic
    if "current_role" not in st.session_state or st.session_state.current_role != role_id:
        with st.spinner(f"🔄 Initializing {role_options[role_id]}..."):
            st.session_state.brain = Brain(role_id=role_id)
            st.session_state.current_role = role_id
            st.session_state.messages = [] 

    if st.button("🗑️ Clear Transcript"):
        st.session_state.messages = []
        st.rerun()

# --- 3. THE WELCOME MESSAGE ---
if not st.session_state.messages:
    welcome_name = st.session_state.brain.current_persona['name']
    # Professional English Intro for the Architect Persona
    welcome_text = f"Greetings, Partner. I am **{welcome_name}**, your Senior BaaS Architect. I have mapped the ventures for JB Infra, Srigdha, SSVD, and Arising Developers. How shall we scale today? 🚀"
    st.session_state.messages.append({"role": "assistant", "content": welcome_text})

# --- 4. THE CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Command Spark..."):
    # If a file is uploaded, we prepend the context to the prompt
    if uploaded_file:
        prompt = f"[FILE UPLOADED: {uploaded_file.name}] " + prompt

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            # Spark now uses the merged BaaS + Venture Knowledge
            response = st.session_state.brain.think(prompt, language=selected_lang)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})