import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from modules.brain import Brain

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Safeland Intelligence",
    page_icon="🌍",
    layout="centered"
)
# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Safeland Intelligence",
    page_icon="🌍",
    layout="centered"
)

# --- 🧹 FORCE RESET (Add this block) ---
# If the user refreshes, we want to make sure we re-load the correct brain
if "reset_trigger" not in st.session_state:
    st.session_state.clear()
    st.session_state["reset_trigger"] = True
# ---------------------------------------
# --- CSS FOR CLEAN LOOK ---
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 1. LOAD SHADOW'S BRAIN (Fixed Model Name) ---
@st.cache_resource
def load_memory():
    # We use the EXACT name your diagnostic script found earlier
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", 
        google_api_key=st.secrets["GEMINI_API_KEY"]
    )
    
    # Load the Vector Store
    try:
        vector_store = FAISS.load_local(
            "faiss_index", 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        return vector_store
    except Exception as e:
        st.error(f"⚠️ Brain Damage: Could not load memory. {e}")
        return None

# Initialize the Memory
vector_store = load_memory()


# --- MAIN APP LOGIC ---

# --- SIDEBAR (RESTORED) ---
with st.sidebar:
    st.image("assets/logo.png", width=120)
    st.title("Safeland Console")
    st.caption("Satellite-Verified Intelligence")
    
    # --- THE ROLE SWITCHER ---
    # We map the names to the ID numbers in brain.py
    persona_map = {
        "Technical Demo (Pilot)": "5",   # The Default (SSP Partner Mode)
        "Business Mode (Sales)": "2",    # The BizDev Mode
        "Real Estate Agent": "1"         # The Selling Mode
    }
    
    selected_role = st.selectbox(
        "Select Mode:", 
        list(persona_map.keys()),
        index=0 # Defaults to 'Technical Demo'
    )
    
    # Get the ID (e.g., "5") based on the name
    role_id = persona_map[selected_role]

# --- INITIALIZE BRAIN ---
# Pass the selected ID to the Brain
brain = Brain(role_id=role_id)

# Greet the User
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Console Active. I am Shadow, your Technical Pilot. I can guide you through the satellite verification features or explain the software. What would you like to see?"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. THE CONNECTED CHAT LOOP (Fixed Logic)
if prompt := st.chat_input("Ask about features, maps, or verification..."):
    # Show User Message
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing Database..."):
            
            # --- THE MISSING WIRE: RETRIEVAL ---
            # We search the memory BEFORE asking the Brain
            context_text = ""
            if vector_store:
                try:
                    # Find 3 relevant snippets
                    docs = vector_store.similarity_search(prompt, k=3)
                    context_text = "\n\n".join([d.page_content for d in docs])
                except Exception as e:
                    context_text = ""
            
            # We combine the User Question + The Found Data
            # This "tricks" the Brain into knowing the answer
            augmented_prompt = f"""
            CONTEXT FROM DATABASE:
            {context_text}
            
            USER QUESTION:
            {prompt}
            """
            
            # Send the combined package to the Brain
            response = brain.think(augmented_prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})