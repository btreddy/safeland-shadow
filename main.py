from time import time
import streamlit as st
from modules.brain import Brain
from PIL import Image
import os
from dotenv import load_dotenv

# 1. Force Local Environment Sync
load_dotenv(override=True)

st.set_page_config(page_title="Safeland Console", layout="wide", page_icon="🎯")

# --- 2. SESSION STATE (The Engine Room) ---
# Initialize Brain and Chat History if they don't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. SIDEBAR ---
with st.sidebar:
    try:
        st.image(Image.open("assets/logo.png"), width=150)
    except:
        st.title("Safeland Console")
    
    st.markdown("---")
    
    role_options = {
        "1": "Shadow-Dev (BaaS Architect)",
        "2": "Shadow-Land (Market Intelligence)" 
    }

    role_id = st.selectbox(
        "Select Active Engine:", 
        options=list(role_options.keys()), 
        format_func=lambda x: role_options[x]
    )

def think(self, user_input):
    # 1. Immediate Conversation Check (Stop the data dump!)
    greetings = ["hi", "hello", "hey", "who are you"]
    if any(greet in user_input.lower() for greet in greetings):
        return f"Greetings! I am {self.current_persona['name']}. How can I assist you with Safeland Intelligence today?"

    # 2. Proceed to Memory Retrieval only if needed
    time.sleep(1) # Your tactical delay
    # ... rest of your RetrievalQA logic ...
    # Hot-Reload Brain when Role Changes
    if "current_role" not in st.session_state or st.session_state.current_role != role_id:
        with st.spinner(f"🔄 Switching to {role_options[role_id]}..."):
            st.session_state.brain = Brain(role_id=role_id)
            st.session_state.current_role = role_id
            # Optional: Clear chat on role swap to avoid context confusion
            # st.session_state.messages = [] 

    st.markdown("---")
    if st.button("🗑️ Clear Meeting Transcript"):
        st.session_state.messages = []
        st.rerun()

# --- 4. MAIN INTERFACE ---
active_name = st.session_state.brain.current_persona['name']
st.info(f"🏷️ **Active ID:** {active_name} | **Status:** Secured & Isolated")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input Logic
if prompt := st.chat_input("Speak to Shadow..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response via Brain
    with st.chat_message("assistant"):
        with st.spinner("Shadow is thinking..."):
            response = st.session_state.brain.think(prompt)
            st.markdown(response)
    
    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})