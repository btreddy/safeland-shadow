import os
import google.generativeai as genai
from dotenv import load_dotenv
from modules.memory import SmartMemory
import streamlit as st

load_dotenv()

# --- THE PERSONA BANK ---
PERSONAS = {
    "1": {
        "name": "Real Estate Agent",
        "prompt": "Your name is Shadow. You are a top-tier Real Estate Venture Owner. Your goal is to sell plots in Hyderabad. Tone: Professional, persuasive, and trustworthy. Base answers on the 'Real estate' folder data.",
    },
    "2": {
        "name": "Safeland Console (Biz Dev)",
        "prompt": "Your name is Shadow. You are the Business Development Head for 'Safeland Console'. Your Audience: Investors, Real Estate Agents, and Developers. Your Goal: Explain how Safeland uses Map-based verification and Ad management to solve their problems. Highlight: 'Satellite Verified', 'Owner's Voice', and 'Govt Data Integration'. Tone: Professional, Strategic, and Convincing. Base answers on the 'Safeland Console' folder data.",
    },
    "3": {
        "name": "SaaS Architect (Tech)",
        "prompt": "Your name is Shadow. You are the Lead Software Architect for the SaaS Division. Your Audience: Developers and Technical Partners. Your Goal: Discuss the software stack, coding structure, APIs, and future development features. Tone: Technical, Precise, and Innovative. Base answers on the 'Saas' folder data.",
    },
    "4": {
        "name": "Pharma Consultant",
        "prompt": "Your name is Shadow. You are a Medical Representative. Your goal is to provide accurate drug information to doctors. Tone: Scientific, precise, and formal. USE DISCLAIMERS. Base answers on the 'Pharma' folder data.",
    }
}

class Brain:
    def __init__(self, role_id="1"):
        self.api_key = None
        
        # 1. Try Local .env
        try:
            self.api_key = os.getenv("GEMINI_API_KEY")
        except:
            pass

        # 2. If no local key, try Streamlit Cloud Secrets
        if not self.api_key:
            try:
                self.api_key = st.secrets["GEMINI_API_KEY"]
            except:
                pass

        if not self.api_key:
            st.error("🚨 CRITICAL ERROR: API Key not found! Check 'secrets.toml' in Streamlit.")
            return

        try:
            genai.configure(api_key=self.api_key)
            
            # --- AUTO-DISCOVERY: SEE WHAT MODELS ARE ACTUALLY AVAILABLE ---
            self.available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        self.available_models.append(m.name)
                print(f"   [SYSTEM] Available Models: {self.available_models}")
            except Exception as e:
                print(f"   [SYSTEM] Could not list models: {e}")

        except Exception as e:
            st.error(f"🚨 Configuration Error: {e}")
        
        self.current_persona = PERSONAS.get(role_id, PERSONAS["1"])
        self.memory = SmartMemory()

        # PRIORITY LIST: Try the best ones, fall back to "gemini-pro" (the classic)
        self.model_priority = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-1.0-pro', # <--- Added the reliable fallback
            'gemini-pro'      # <--- The original classic
        ]
    
    def think(self, user_input):
        context = self.memory.retrieve(user_input)
        if not context:
            context = "(No specific data found. Answer generally.)"

        system_prompt = f"""
        ROLE: {self.current_persona['prompt']}
        RELEVANT KNOWLEDGE: {context}
        INSTRUCTIONS: Answer concisely based on knowledge.
        """
        
        full_prompt = f"{system_prompt}\n\nUSER INPUT: {user_input}\n\nYOUR RESPONSE:"
        
        for model_name in self.model_priority:
            try:
                # Clean up model name (sometimes API needs 'models/' prefix, sometimes not)
                # We try it as is first.
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                # If it fails, we just silently try the next one
                print(f"   [DEBUG] {model_name} failed. Trying next...")
                continue 
        
        # If ALL failed, print the list of what IS available so we can debug
        st.error(f"⚠️ System Offline. I tried these models: {self.model_priority} but they all failed.")
        if self.available_models:
             st.info(f"ℹ️ The server says only these models are available: {self.available_models}")
        
        return "System Offline. Please check the API Key and Model availability."