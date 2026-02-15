import streamlit as st
from modules.brain import Brain

# 1. Page Config (Telegram Style: Wide and Clean)
st.set_page_config(page_title="Spark Console", page_icon="⚡", layout="wide")

# 2. Initialization & Welcome Message
if "brain" not in st.session_state:
    st.session_state.brain = Brain()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am Spark, your Senior Real Estate Expert. I am now grounded in Safelanddeal data. How can I help you today?"}
    ]

# 3. Clean Sidebar (No Confusing Elements)
with st.sidebar:
    st.title("⚡ Spark Console")
    st.write("Status: Grounded Expert Active")
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 4. Chat Interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about venture data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # The 'think' call is simplified to prevent the 400 error
        response = st.session_state.brain.think(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})