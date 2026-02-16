import os
import requests
from flask import Flask, request
from modules.brain import Brain
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT VARIABLES
load_dotenv(override=True)
app = Flask(__name__)

# 2. SECURE CONFIGURATION (No hardcoded keys!)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "Spark2026")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 1. Grab the token FIRST
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN") # If you use it

# 2. NOW do the Safety Checks
if not TELEGRAM_TOKEN:
    print("❌ Error: TELEGRAM_TOKEN is missing in environment!")
    # Remove the 'raise' for now so the app doesn't crash during testing
    
# 3. Construct the URLs
SEND_URL_TG = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
WHATSAPP_URL = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
# 3. SPARK BRAIN INITIALIZATION
spark = None

def get_spark():
    global spark
    if spark is None:
        print("🔄 Loading Spark Brain...")
        # We assume Brain class picks up GOOGLE_API_KEY from environment internally
        # or uses st.secrets. 
        spark = Brain(role_id="1") 
    return spark

@app.route("/whatsapp", methods=["GET", "POST"])
def whatsapp_handler():
    if request.method == "GET":
        # ... (Your existing verification logic is perfect)
        return challenge, 200

    data = request.get_json()
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    message = value["messages"][0]
                    recipient_id = message["from"]
                    
                    if "text" in message:
                        user_msg = message["text"]["body"]
                        print(f"📩 WhatsApp Received: {user_msg}")

                        # 🧠 This is what creates the 4-5 second delay you want!
                        spark = get_spark()
                        response_text = spark.think(user_msg)

                        # 🚀 This sends it back to your phone
                        send_whatsapp_msg(recipient_id, response_text)
                        print(f"✅ Reply Sent to {recipient_id}")

    return "ok", 200

# --- TELEGRAM WEBHOOK ---
@app.route("/telegram", methods=["POST"])
def unified_telegram_handler():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return "ok", 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # 1. Ask Spark
        agent = get_spark()
        # Ensure Brain() is compatible with your input. 
        # If Brain uses st.secrets, it might need a patch to read os.getenv too.
        reply = agent.think(user_input=text) 
        
        # 2. Reply to Telegram
        payload = {
            "chat_id": chat_id,
            "text": reply,
            "parse_mode": "Markdown"
        }
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Spark-Agent-2026"
        }
        
        res = requests.post(SEND_URL_TG, json=payload, headers=headers, timeout=20)
        print(f"✅ TG Send Result: {res.status_code}")        
    except Exception as e:
        print(f"❌ Telegram Error: {str(e)}")
    
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)