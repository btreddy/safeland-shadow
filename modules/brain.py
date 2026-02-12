import os
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

# --- 1. IP WATERMARK ---
OWNERSHIP_BLOCK = "© 2026 Safeland Intelligence | Owner: [Btrin] | System: Shadow-Dev"

PERSONAS = {
    "1": {
        "name": "Shadow-Dev (BaaS Architect)",
        "folder": "data/baas",
        "prompt": "You are Shadow-Dev. Technical Lead for Safeland Intelligence. Answer strictly using the provided technical documentation."
    },
    "2": {
        "name": "Shadow-Land (Market Intelligence)",
        "folder": "data/real_estate",
        "prompt": """
        You are Shadow-Land, a Real Estate Intelligence Agent.
        - DO NOT use hardcoded property names or old ad copy.
        - READ the provided DATA files for every query to find current listings and specs.
        - If the data is not in the files, state that you are verifying the latest satellite records.
        - Style: Professional, localized Hyderabad context, natural Telugu-English mix.
        """
    }
}

# --- 3. SMART MEMORY ---
class SmartMemory:
    def __init__(self, role_id):
        self.vector_store = None
        # Using local embeddings as verified in your terminal
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        index_map = {"1": "faiss_index_data_baas", "2": "faiss_index_data_real_estate"}
        index_path = index_map.get(role_id, "faiss_index_data_real_estate")

        if os.path.exists(index_path):
            try:
                self.vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f" [MEMORY ERR] {e}")

    def retrieve(self, query):
        if not self.vector_store: return None
        docs = self.vector_store.similarity_search(query, k=3)
        return "\n".join([doc.page_content for doc in docs])

# --- 4. THE BRAIN ---
class Brain:
    def __init__(self, role_id="1"):
        self.current_persona = PERSONAS.get(role_id, PERSONAS["1"])
        
        # Setup API using your active key
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        
        self.memory = SmartMemory(role_id=role_id)
        
        # Priority updated to bypass the 21/20 rate limit on 2.5 Flash
        self.model_priority = ['gemini-1.5-flash', 'gemini-3-flash', 'gemini-2.0-flash-exp']

    def think(self, user_input):
        context = self.memory.retrieve(user_input) or "No specific data found."
        full_prompt = f"{self.current_persona['prompt']}\n\nDATA:\n{context}\n\nUSER:\n{user_input}"
        
        for model_name in self.model_priority:
            try:
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except:
                continue
        return "I am having trouble connecting. Please check the API key status."