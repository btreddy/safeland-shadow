import streamlit as st
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.oauth2 import service_account

class Brain:
    def __init__(self):
        # 1. Load API Key
        api_key = st.secrets.get("GOOGLE_API_KEY")
        
        # 2. Load Service Account (The Raw JSON Method)
        creds = None
        
        # We look for the big text block we just saved
        if "GCP_CREDENTIALS" in st.secrets:
            try:
                # json.loads handles the quotes and newlines for us!
                creds_info = json.loads(st.secrets["GCP_CREDENTIALS"])
                
                # Create the credentials object
                creds = service_account.Credentials.from_service_account_info(creds_info)
            except json.JSONDecodeError:
                st.error("⚠️ Secrets Error: The 'GCP_CREDENTIALS' block is not valid JSON. Check for missing commas or braces.")
                st.stop()
            except Exception as e:
                st.error(f"⚠️ Credential Error: {str(e)}")
                st.stop()
        else:
            st.error("⚠️ System Offline: 'GCP_CREDENTIALS' secret is missing!")
            st.stop()

        # 3. Initialize the High-End Model (Gemini 2.0 Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            credentials=creds,
            temperature=0.1
        )
        
        # 4. Define the Instructions
        self.system_instruction = (
            "You are Spark, the Senior Real Estate Expert for Safelanddeal. "
            "Your goal is to provide grounded answers based on available venture data. "
            "Keep answers professional, concise, and helpful."
        )

    def think(self, prompt):
        combined_prompt = f"{self.system_instruction}\n\nUser Question: {prompt}"
        try:
            return self.llm.invoke([HumanMessage(content=combined_prompt)]).content
        except Exception as e:
            return f"⚠️ Brain Error: {str(e)}"