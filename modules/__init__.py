import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from google.oauth2 import service_account

class Brain:
    def __init__(self):
        # 1. Pull everything from your valid TOML
        api_key = st.secrets.get("GOOGLE_API_KEY")
        gcp_info = st.secrets.get("gcp_service_account")
        
        # 2. Extract Project ID directly from the Service Account
        project_id = gcp_info.get("project_id") if gcp_info else None

        if not gcp_info or not project_id:
            st.error("⚠️ System Offline: Service Account or Project ID missing!")
            st.stop()

        # 3. Create the 'Identity Card'
        creds = service_account.Credentials.from_service_account_info(gcp_info)

        # 4. Initialize with EXACT parameters for Vertex AI mode
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", # Or gemini-1.5-pro for deeper reasoning
            google_api_key=api_key,
            credentials=creds,
            project=project_id, # MUST match the ID in your dashboard
            temperature=0.1
        )