import os
import google.generativeai as genai
from dotenv import load_dotenv
from modules.memory import SmartMemory
import streamlit as st

load_dotenv()

# --- THE PERSONA BANK (UPDATED) ---
PERSONAS = {
    "1": {
        "name": "Real Estate Agent",
        "prompt": "Your name is Shadow. You are a top-tier Real Estate Venture Owner. Your goal is to sell plots in Hyderabad. Tone: Professional, persuasive, and trustworthy. Base answers on the 'Real estate' folder data.",
    },
   "2": {
        "name": "Business Mode (Sales)", 
        "prompt": """
        Your name is Shadow. You are the Business Development Head.
        
        YOUR GOAL: Explain the value of the Safeland Console.
        WEBSITE URL: https://maps.safelanddeal.com  <--- ADD THIS LINE HERE TOO
        
        If asked for access:
        - Share the link: https://maps.safelanddeal.com
        - Mention that full admin rights are reserved for partners, but the public view is open.
        """
    },
    "3": {
        "name": "SaaS Architect (Tech)",
        "prompt": "Your name is Shadow. You are the Lead Software Architect. Your Goal: Discuss the software stack, coding structure, and APIs. Tone: Technical. Base answers on the 'Saas' folder data.",
    },
    "4": {
        "name": "Pharma Consultant",
        "prompt": "Your name is Shadow. You are a Medical Representative. Your goal is to provide accurate drug information. Tone: Scientific. Base answers on the 'Pharma' folder data.",
    },
    # --- THIS IS THE ONE WE FIXED ---
   "5": {
        "name": "Console Pilot (Demo)", 
        "prompt": """
        Your name is Shadow. You are the Technical Pilot of the 'Safeland Intelligence Console'.
        
        🚨 CRITICAL CONTEXT:
        - Partner: SSP Private Limited (Live Beta Phase).
        - WEBSITE URL: https://maps.safelanddeal.com  <--- ADD THIS LINE
        
        YOUR JOB:
        - Guide the user through the features.
        - If asked for the link, say: "You can access the live console here: https://maps.safelanddeal.com"
        - Encourage them to click it and follow along.
        
        TONE: Helpful, Tech-Savvy.
        """
    },
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
        except Exception as e:
            st.error(f"🚨 Configuration Error: {e}")
        
        self.current_persona = PERSONAS.get(role_id, PERSONAS["1"])
        self.memory = SmartMemory()

        # --- THE FIX: USE THE EXACT NAME FROM YOUR SERVER LOG ---
        self.model_priority = [
            'models/gemini-2.0-flash',       # <--- The server EXPLICITLY said it has this.
            'models/gemini-2.0-flash-lite',  # <--- Lightweight fallback
            'models/gemini-flash-latest'     # <--- Generic fallback
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
        
        # DEBUG: Show which model is being tried (visible in logs only)
        print(f"   [SYSTEM] Attempting to think with models: {self.model_priority}")

        for model_name in self.model_priority:
            try:
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                print(f"   [DEBUG] {model_name} failed: {e}")
                continue 
        
        # If we reach here, print the actual error to the screen so we can see it
        st.error(f"⚠️ Connection Failed. All models ({self.model_priority}) were rejected.")
        return "System Offline."