import streamlit as st
import json
import base64
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.oauth2 import service_account

class Brain:
    def __init__(self, role_id="1"):
        # --- HYBRID KEY LOADING (The Fix) ---
        # 1. Try Streamlit Secrets (Cloud)
        try:
            self.api_key = st.secrets.get("GOOGLE_API_KEY")
            self.b64_str = st.secrets.get("GCP_CREDENTIALS_BASE64")
        except:
            # 2. If that fails, try Environment Variables (Local/Flask)
            self.api_key = None
            self.b64_str = None

        # 3. Fallback: If Step 1 failed, check os.environ explicitly
        if not self.api_key:
            self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.b64_str:
            self.b64_str = os.getenv("GCP_CREDENTIALS_BASE64")

        # --- CRITICAL CHECK ---
        if not self.api_key:
            print("❌ Brain Error: GOOGLE_API_KEY is missing!")
            raise ValueError("GOOGLE_API_KEY missing")
        
        if not self.b64_str:
            print("❌ Brain Error: GCP_CREDENTIALS_BASE64 is missing!")
            raise ValueError("GCP_CREDENTIALS_BASE64 missing")

        # --- DECODE CREDENTIALS ---
        creds = None
        try:
            json_bytes = base64.b64decode(self.b64_str)
            creds_info = json.loads(json_bytes.decode("utf-8"))
            creds_unscoped = service_account.Credentials.from_service_account_info(creds_info)
            creds = creds_unscoped.with_scopes(["https://www.googleapis.com/auth/cloud-platform"])
        except Exception as e:
            print(f"❌ Credential Error: {e}")
            raise e

        # --- START MODEL ---
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=self.api_key,
            credentials=creds,
            temperature=0.1
        )
        
        self.system_instruction = (
            "You are Spark, the Senior Real Estate Expert for Safelanddeal. "
            "Your goal is to provide grounded answers based on available venture data. "
            "Keep answers professional, concise, and helpful."
        )

    def think(self, user_input, language="english"):
        combined_prompt = f"{self.system_instruction}\n\nUser Question: {user_input}"
        try:
            print(f"🧠 Spark is thinking about: {user_input[:20]}...")
            response = self.llm.invoke([HumanMessage(content=combined_prompt)]).content
            return response
        except Exception as e:
            print(f"❌ Brain Think Error: {e}")
            return "I am currently having trouble accessing my database. Please contact support."