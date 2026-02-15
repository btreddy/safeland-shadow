import os
import time
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part

class Brain:
    def __init__(self, role_id="1"):
        # UPGRADE: Switching to the high-end Gemini 3 Flash model
        self.model = GenerativeModel("gemini-3-flash")
        self.system_instruction = "You are a Senior BaaS Architect with active Vision and Web-Crawling tools. You MUST analyze all uploaded images and provided real estate links for JB Infra, Srigdha, SSVD, and Arising."

    def think(self, prompt, uploaded_file=None):
        content = [prompt]
        
        # ACTIVATE EYES: Packing the actual file data into the request
        if uploaded_file is not None:
            visual_data = Part.from_data(
                data=uploaded_file.getvalue(), 
                mime_type=uploaded_file.type
            )
            content.append(visual_part)

        # EXECUTE: High-speed multimodal generation
        response = self.model.generate_content(content)
        return response.text

def think(self, prompt, uploaded_file=None, language="en"):
    # Create the content list starting with the text prompt
    content = [prompt]
    
    # If a file was uploaded, read the bytes and pack them into the 'bag'
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type
        visual_part = Part.from_data(data=file_bytes, mime_type=mime_type)
        content.append(visual_part)

    # Generate response using the multimodal engine (Gemini 1.5)
    response = self.model.generate_content(content)
    return response.text

# Foundation logic
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA 

load_dotenv(override=True)

# --- Spark Personas Configuration ---
PERSONAS = {
    "1": {
        "name": "Spark (BaaS Master Architect)",
        "prompt": "You are Spark, the lead BaaS Architect. Focus strictly on AI agents, software scaling, and technology.",
        "index": "faiss_index_baas"
    },
    "2": {
        "name": "Spark (Real Estate Example)",
        "prompt": "You are Spark, showcasing a Real Estate replica. Use Hyderabad market data to prove how a specialized brain works.",
        "index": "faiss_index_real_estate"
    }
}

class SmartMemory:
    def __init__(self, index_name):
        self.vector_store = None
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        if os.path.exists(index_name):
            try:
                # Load the specific brain index
                self.vector_store = FAISS.load_local(index_name, embeddings, allow_dangerous_deserialization=True)
                print(f"✅ [SPARK MEMORY] Success: Loaded {index_name}")
            except Exception as e:
                print(f"❌ [MEMORY ERR] {e}")

class Brain:
    def __init__(self, role_id="1"):
        # 1. Select Persona
        self.current_persona = PERSONAS.get(role_id, PERSONAS["1"])
        index_to_load = self.current_persona['index']
        
        # 2. Initialize Model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            temperature=0.1,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # 3. Initialize Memory
        self.memory = SmartMemory(index_name=index_to_load)

    def think(self, user_input, language="en"):
        if not self.memory.vector_store:
            return "⚠️ System Alert: Memory Uplink Failed."

        # Define linguistic rules
        lang_map = {
            "en": "Respond strictly in English.",
            "te": "Respond strictly in professional Telugu script (తెలుగు).",
            "tenglish": "Respond in Telugu script, but use common English terms like 'Plots' and 'Venture'."
        }
        
        instruction = lang_map.get(language, "en")
        
        # Build the specialist query
        full_query = f"{self.current_persona['prompt']}\n{instruction}\n\nQuestion: {user_input}"
        
        # Tactical delay for live presentation stability
        time.sleep(1)

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.memory.vector_store.as_retriever(search_kwargs={"k": 5})
        )

        try:
            response = qa_chain.invoke({"query": full_query})
            return response["result"].strip()
        except Exception as e:
            return f"Recalibrating Spark... (Err: {str(e)[:50]})"