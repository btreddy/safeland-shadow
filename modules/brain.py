import streamlit as st
import json
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.oauth2 import service_account

class Brain:
    def __init__(self):
        api_key = st.secrets.get("GOOGLE_API_KEY")
        creds = None
        
        # 1. Decode the Base64 String
        b64_str = st.secrets.get("GCP_CREDENTIALS_BASE64")
        
        if b64_str:
            try:
                # Decode the string
                json_bytes = base64.b64decode(b64_str)
                creds_info = json.loads(json_bytes.decode("utf-8"))
                
                # 2. CREATE CREDENTIALS WITH SCOPE (The Fix for 'invalid_scope')
                # We explicitly tell Google: "This bot is allowed to use the Cloud Platform."
                creds_unscoped = service_account.Credentials.from_service_account_info(creds_info)
                creds = creds_unscoped.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
                
            except Exception as e:
                st.error(f"⚠️ Auth Error: {e}")
                st.stop()
        else:
            st.error("⚠️ System Offline: GCP_CREDENTIALS_BASE64 is missing!")
            st.stop()

        # 3. Initialize the High-End Model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            credentials=creds,
            temperature=0.1
        )
        
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