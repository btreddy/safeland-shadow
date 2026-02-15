import streamlit as st
import json
from google.oauth2 import service_account

st.title("🔑 Key Connection Test")

# 1. Try to Load the API Key
api_key = st.secrets.get("GOOGLE_API_KEY")
if api_key:
    st.success(f"✅ API Key Found: {api_key[:5]}... (Valid Format)")
else:
    st.error("❌ GOOGLE_API_KEY is missing!")

# 2. Try to Load the Service Account (JSON String Method)
json_str = st.secrets.get("GCP_CREDENTIALS_JSON")

if json_str:
    try:
        # Attempt to parse the string into a dictionary
        creds_info = json.loads(json_str)
        # Attempt to create credentials from that dictionary
        creds = service_account.Credentials.from_service_account_info(creds_info)
        st.success(f"✅ Service Account Authenticated: {creds.service_account_email}")
        st.info("System is ready for High-End Brain logic.")
    except json.JSONDecodeError:
        st.error("❌ JSON Error: The text in 'GCP_CREDENTIALS_JSON' is not valid JSON. Check your quotes!")
    except Exception as e:
        st.error(f"❌ Credential Error: {str(e)}")
else:
    st.warning("⚠️ GCP_CREDENTIALS_JSON not found. Checking for [gcp_service_account] block...")
    # Fallback check for the old method
    if "gcp_service_account" in st.secrets:
        st.success("✅ Found [gcp_service_account] block! (Old method is active)")
    else:
        st.error("❌ No Service Account keys found in secrets.toml")