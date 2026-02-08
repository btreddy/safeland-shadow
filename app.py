import streamlit as st
from modules.brain import Brain

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Safeland Intelligence",
    page_icon="🌍",
    layout="centered"
)

# --- CSS FOR CLEAN LOOK (Hides the top colored bar and footer) ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (HIDDEN OR MINIMAL) ---
# We removed the Radio Buttons so users can't switch roles.
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.title("Safeland Console")
    st.caption("Satellite-Verified Intelligence")
    
    # Optional: Keep the Memory Button for YOU, but maybe hide it later.
    if st.button("🔄 Refresh Data"):
        st.session_state["memory_updated"] = True
        # You might want to add code here to trigger the scan if needed

# --- MAIN APP LOGIC ---

# 1. HARDCODE THE ROLE TO "2" (Safeland Console)
# No more selection menu. It is always locked to Business Dev.
brain = Brain(role_id="2") 

# 2. Greet the User (Only once)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to Safeland Intelligence. I can analyze venture locations, verify legal zones (FTL/RERA), and explain our marketing data. Which venture are you interested in?"}
    ]

# 3. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Chat Input
if prompt := st.chat_input("Ask about ventures, boundaries, or pricing..."):
    # Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing Satellite Data..."):
            response = brain.think(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})