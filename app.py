import streamlit as st
from modules.brain import Brain
from PIL import Image

st.set_page_config(page_title="Safeland Console", layout="wide")

# Sidebar
with st.sidebar:
    try:
        st.image(Image.open("assets/logo.png"), width=150)
    except:
        st.title("Safeland Console")
    
    st.markdown("---")
    role_options = {"1": "Shadow-Dev (BaaS Architect)", "2": "Shadow-Land (RE Intelligence)"}
    role_id = st.selectbox("Select Active Engine:", options=list(role_options.keys()), format_func=lambda x: role_options[x])

# Ensure Brain reloads when Role changes
if "current_role" not in st.session_state or st.session_state.current_role != role_id:
    st.session_state.brain = Brain(role_id=role_id)
    st.session_state.current_role = role_id
    st.session_state.messages = []

# Header
active_name = st.session_state.brain.current_persona['name']
st.info(f"🏷️ **Active ID:** {active_name} | **Status:** Secured & Isolated")

# Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask Shadow..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    response = st.session_state.brain.think(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"): st.markdown(response)