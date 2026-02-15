import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from google.oauth2 import service_account

class Brain:
    def __init__(self):
        # 1. Load Credentials
        api_key = st.secrets.get("GOOGLE_API_KEY")
        gcp_info = st.secrets.get("gcp_service_account")
        
        if gcp_info:
            creds = service_account.Credentials.from_service_account_info(gcp_info)
        else:
            st.error("⚠️ Service Account Info Missing in Secrets!")
            st.stop()

        # 2. Initialize the High-End Model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            credentials=creds,
            temperature=0.1
        )
        
        # 3. DEFINE THE MISSING VARIABLE HERE
        self.system_instruction = (
            "You are Spark, the Senior Real Estate Expert for Safelanddeal. "
            "Your goal is to provide grounded answers based on available venture data. "
            "Keep answers professional, concise, and helpful."
        )

    def think(self, prompt):
        # 4. Now this line will work because the name matches above!
        combined_prompt = f"{self.system_instruction}\n\nUser Question: {prompt}"
        
        try:
            # Send as a single HumanMessage to prevent 400 errors
            response = self.llm.invoke([HumanMessage(content=combined_prompt)])
            return response.content
        except Exception as e:
            return f"⚠️ Brain Error: {str(e)}"