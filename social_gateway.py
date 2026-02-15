import os
import requests
from flask import Flask, request
from modules.brain import Brain
from dotenv import load_dotenv

# Env variables లోడ్ చేయడం
load_dotenv(override=True)
app = Flask(__name__)

# Spark Brain ని ఇనిషియలైజ్ చేయడం
spark = None

def get_spark():
    global spark
    if spark is None:
        print("🔄 Loading Spark Brain for the first time...")
        api_key ="AIzaSyCe8NqsOJVasRsStPUkQx6ILPLBTPgIrug"
        spark = Brain(role_id="1")
    return spark

# --- Environment Variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "Spark2026")

SEND_URL_TG = "https://api.telegram.org/bot8441547674:AAFmqzQo3OPtxCgjT8hfbJzJoikL_LMpwgo/sendMessage"

# --- WhatsApp Webhook ---
@app.route("/whatsapp", methods=["GET", "POST"])
def whatsapp_handler():
    # --- వెరిఫికేషన్ పార్ట్ (దీనివల్ల డబుల్ టిక్ వస్తుంది) ---
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge") # ఇక్కడ వేరియబుల్ ని సరిగ్గా తీసుకోవాలి
        VERIFY_TOKEN = "Spark2026"

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # --- మెసేజ్ ప్రాసెసింగ్ పార్ట్ ---
    data = request.get_json()
    if data:
        # బ్యాక్‌గ్రౌండ్‌లో స్పార్క్ పని చేయడానికి వీలుగా వెంటనే 'ok' ఇచ్చేయాలి
        # మీ పాత ప్రాసెసింగ్ లాజిక్ ఇక్కడ రన్ చేయండి
        try:
            # process_whatsapp(data) వంటి ఫంక్షన్ ఇక్కడ పిలవండి
            pass 
        except Exception as e:
            print(f"❌ WhatsApp Process Error: {e}")

    return "ok", 200

def send_whatsapp_msg(recipient_id, text):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)

# --- Telegram Webhook ---
@app.route("/telegram", methods=["POST"])
def unified_telegram_handler():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return "ok", 200

        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # స్పార్క్ ఆలోచన
        agent = get_spark()
        reply = agent.think(user_input=text, language="tenglish")
        
        # టెలిగ్రామ్ సమాధానం
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
        print(f"✅ TG Send Result: {res.status_code} - {res.text}")        
    except Exception as e:
        print(f"❌ Telegram Error: {str(e)}")
    
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)