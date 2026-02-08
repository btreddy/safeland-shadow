import streamlit as st
import time
from modules.brain import Brain

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Safeland Shadow AI",
    page_icon="🤖",
    layout="centered"
)

# --- INITIALIZE SESSION STATE (Memory for the Web) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "brain" not in st.session_state:
    # Default to "Safeland Console" role for the website
    st.session_state.brain = Brain(role_id="2") 

# --- SIDEBAR (The Control Panel) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("Shadow AI Settings")
    
    # Role Switcher
    role = st.radio(
        "Choose Personality:",
        ["Real Estate Agent 🏠", "Safeland Console 🌍", "SaaS Architect 💻", "Pharma Rep 💊"]
    )
    
    # Map the selection to the ID
    role_map = {
        "Real Estate Agent 🏠": "1",
        "Safeland Console 🌍": "2",
        "SaaS Architect 💻": "3",
        "Pharma Rep 💊": "4"
    }
    
    # If role changes, reload the brain
    selected_id = role_map[role]
    if st.session_state.brain.current_persona != st.session_state.brain.current_persona: # Just a check
         st.session_state.brain = Brain(role_id=selected_id)
         st.rerun()

    st.markdown("---")
    if st.button("🔄 Update Memory (Re-Scan Files)"):
        with st.spinner("Scanning your documents..."):
            st.session_state.brain.memory.build_memory()
        st.success("Memory Updated!")

# --- MAIN CHAT INTERFACE ---
st.title("💬 Chat with Shadow")
st.caption("Powered by Gemini 2.5 • Safeland Intelligence")

# 1. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. User Input Area
if prompt := st.chat_input("Ask me about ventures, software, or APIs..."):
    # Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Get answer from the Brain
        with st.spinner("Thinking..."):
            try:
                # We use the existing Brain logic!
                full_response = st.session_state.brain.think(prompt)
            except Exception as e:
                full_response = f"Error: {e}"

        # Typewriter effect
        message_placeholder.markdown(full_response)
    
    # Add Assistant Message to history
    st.session_state.messages.append({"role": "assistant", "content": full_response})