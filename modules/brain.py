from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import streamlit as st

class Brain:
    def __init__(self):
        # Using the High-End Model Configuration from your Dashboard
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            google_api_key=st.secrets["GOOGLE_API_KEY"],
            temperature=0.1
        )
        self.instruction = "You are a Real Estate Expert. Use only provided venture data."

    def think(self, prompt):
        # We combine system instruction with the user prompt for stability
        combined = f"{self.instruction}\n\nUser: {prompt}"
        try:
            # Strictly HumanMessage to prevent multi-turn alternation errors
            return self.llm.invoke([HumanMessage(content=combined)]).content
        except Exception as e:
            return f"⚠️ Brain Error: {str(e)}"
        
        # Grounded Persona Instructions
        self.system_instruction = (
            "You are the Senior Real Estate Expert for Safelanddeal. "
            "Analyze linked content and provided data storage. "
            "Provide grounded answers only. If info is missing, ask for a source. "
            "Respond in Professional English."
        )

    def think(self, prompt):
        # We combine the system instruction with the prompt to prevent 400 errors
        combined_prompt = f"{self.system_instruction}\n\nUser Question: {prompt}"
        
        # Strictly send as a HumanMessage to ensure Gemini stability
        try:
            response = self.llm.invoke([HumanMessage(content=combined_prompt)])
            return response.content
        except Exception as e:
            return f"⚠️ Brain Offline: {str(e)}"