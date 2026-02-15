import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

class Brain:
    def __init__(self):
        # 1. Pull API Key from Streamlit Secrets
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("⚠️ System Offline: GOOGLE_API_KEY missing in Cloud Secrets.")
            st.stop()

        # 2. High-End Multimodal Engine (Gemini 1.5 Flash)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1 # Grounded, factual responses
        )

        # 3. Dynamic Persona (No Hardcoding)
        self.system_instruction = (
            "You are the Senior Real Estate Expert for Safelanddeal. "
            "You provide grounded answers based on web pages and file storage data. "
            "If info is missing, ask for a web link or file source. "
            "You have authority to analyze site maps and public web content in Professional English."
        )

    def think(self, prompt, image_data=None):
        # Build the multimodal 'Trekking Bag'
        content = [{"type": "text", "text": prompt}]
        if image_data:
            content.append({
                "type": "image_url",
                "image_url": f"data:image/png;base64,{image_data}"
            })
        
        messages = [
            SystemMessage(content=self.system_instruction),
            HumanMessage(content=content)
        ]
        return self.llm.invoke(messages).content