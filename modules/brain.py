import streamlit as st
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.oauth2 import service_account

class Brain:
    def __init__(self):
        # 1. Load API Key
        api_key = st.secrets.get("GOOGLE_API_KEY")
        
        # 2. Universal Credential Loader (Checks BOTH methods)
        creds = None
        
        # Priority A: Check for the Bulletproof JSON String (Best for Cloud)
        json_str = st.secrets.get("GCP_CREDENTIALS_JSON")
        
        if json_str:
            try:
                creds_info = json.loads(json_str)
                creds = service_account.Credentials.from_service_account_info(creds_info)
            except Exception as e:
                # If JSON fails, log it but don't stop yet; try Method B
                print(f"JSON Load Warning: {e}")
        
        # Priority B: Check for the TOML Block (What your Local Test found)
        if not creds and "gcp_service_account" in st.secrets:
            creds_info = st.secrets["gcp_service_account"]
            creds = service_account.Credentials.from_service_account_info(creds_info)

        # Final Security Check
        if not creds:
            st.error("⚠️ System Offline: No valid Service Account keys found in Secrets!")
            st.stop()

        # 3. Initialize the High-End Model (Gemini 2.0 Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            credentials=creds,
            temperature=0.1
        )
        
        # 4. Define the Instructions (Fixed variable name!)
        self.system_instruction = (
            "You are Spark, the Senior Real Estate Expert for Safelanddeal. "
            "Your goal is to provide grounded answers based on available venture data. "
            "Keep answers professional, concise, and helpful."
        )

    def think(self, prompt):
        combined_prompt = f"{self.system_instruction}\n\nUser Question: {prompt}"
        try:
            # Send as a single HumanMessage for stability
            response = self.llm.invoke([HumanMessage(content=combined_prompt)])
            return response.content
        except Exception as e:
            return f"⚠️ Brain Error: {str(e)}"