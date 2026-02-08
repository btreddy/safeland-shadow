import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from modules.memory import SmartMemory

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
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        self.current_persona = PERSONAS.get(role_id, PERSONAS["1"])
        print(f"   [BRAIN] Personality Loaded: {self.current_persona['name']}")

        self.memory = SmartMemory()

        # Your Verified Model List
        self.model_priority = [
            'gemini-2.5-flash-lite', 
            'gemini-2.5-flash',      
            'gemini-3-flash'         
        ]

    def think(self, user_input):
        context = self.memory.retrieve(user_input)
        if not context:
            context = "(No specific data found in memory. Answer generally based on your role.)"

        system_prompt = f"""
        ROLE: {self.current_persona['prompt']}
        
        RELEVANT KNOWLEDGE FROM DATABASE:
        {context}
        
        INSTRUCTIONS:
        - Answer using ONLY the Relevant Knowledge above.
        - If the answer isn't in the data, say "I don't have that information in my records."
        - Keep answers concise (2-3 sentences max).
        """
        
        full_prompt = f"{system_prompt}\n\nUSER INPUT: {user_input}\n\nYOUR RESPONSE:"
        
        for model_name in self.model_priority:
            try:
                time.sleep(2) # Speed Governor
                model = genai.GenerativeModel(model_name=model_name)
                response = model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                print(f"   [DEBUG] {model_name} failed: {e}")
                time.sleep(5) 
                continue 
        
        return "System Offline. All models failed to respond."