import streamlit as st
import base64
from modules.brain import Brain

st.set_page_config(page_title="Spark Console", page_icon="⚡", layout="wide")

# Persistent state to prevent ValidationError
if "brain" not in st.session_state:
    st.session_state.brain = Brain()
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Visual Intelligence
with st.sidebar:
    st.title("⚡ Spark Console")
    st.write("Status: Grounded Expert Active")
    uploaded_file = st.file_uploader("Upload Site Map:", type=['png', 'jpg', 'jpeg'])

# Chat UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Analyze venture data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    img_b64 = None
    if uploaded_file:
        img_b64 = base64.b64encode(uploaded_file.read()).decode()

    with st.chat_message("assistant"):
        response = st.session_state.brain.think(prompt, img_b64)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})