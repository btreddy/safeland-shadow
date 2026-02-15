import streamlit as st
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.oauth2 import service_account

class Brain:
    def __init__(self):
        # 1. Load API Key
        api_key = st.secrets.get("GOOGLE_API_KEY")
        
        # 2. Universal Credential Loader (With Fix!)
        creds_info = None
        
        # Priority A: Check for JSON String
        json_str = st.secrets.get("GCP_CREDENTIALS_JSON")
        if json_str:
            try:
                creds_info = json.loads(json_str)
            except Exception as e:
                print(f"JSON Load Error: {e}")
        
        # Priority B: Check for TOML Block (Fallback)
        if not creds_info and "gcp_service_account" in st.secrets:
            creds_info = dict(st.secrets["gcp_service_account"]) # Convert to standard dict

        # 3. CRITICAL FIX: Sanitize the Private Key
        # This single line fixes the ValueError by turning text "\n" into real newlines
        if creds_info and "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")

        # 4. Authenticate
        if creds_info:
            try:
                creds = service_account.Credentials.from_service_account_info(creds_info)
            except ValueError as e:
                st.error(f"⚠️ Credential Error: {str(e)}")
                st.stop()
        else:
            st.error("⚠️ System Offline: No Service Account keys found!")
            st.stop()

        # 5. Initialize Model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            credentials=creds,
            temperature=0.1
        )
        
        # 6. Define Instructions
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