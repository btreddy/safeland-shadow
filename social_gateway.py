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
    # 1. Handle Meta's Verification (This part is already working!)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == "Spark2026":
            return challenge, 200
        return "Failed", 403

    # 2. Handle Real Messages (This is where the '3ms' skip happens)
    data = request.get_json()
    
    # Check if this is a real message from a user
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" in value:
                    # Found a message! Now we wake up the Brain
                    message = value["messages"][0]
                    from_no = message["from"]
                    user_text = message["text"]["body"]
                    
                    print(f"📩 Waking Brain for message: {user_text}")

                    # 🧠 THIS IS THE KEY: Call your Spark Brain
                    spark = get_spark()
                    ai_reply = spark.think(user_text) # This creates the 4s delay

                    # 🚀 Send the AI's reply back to the user
                    send_whatsapp_msg(from_no, ai_reply)
                    print(f"✅ Reply sent to {from_no}")

    # Return 200 immediately so Meta doesn't get angry
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