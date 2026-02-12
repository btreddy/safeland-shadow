import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_welcome_text(user_name):
    return (
        f"👋 Welcome {user_name} to Safeland Intelligence!\n\n"
        "🇮🇳 సేఫ్ ల్యాండ్ కి స్వాగతం. భూమి వివరాలను ఇక్కడ సరిచూసుకోండి.\n"
        "👉 **మనం ఇప్పుడే మీ భాషలో మాట్లాడుకుందామా?**\n\n"
        "🇮🇳 सुरक्षित भूमि में स्वागत है। यहाँ अपनी ज़मीन की जाँच करें।\n"
        "👉 **क्या हम अभी आपकी भाषा में चर्चा करें?**\n\n"
        "🚀 **Shadow AI Agent**: Built for the next generation of AI Agents.\n"
        "🖥️ **Experience the Console**: Witness technical land facts at maps.safelanddeal.com\n"
        "🗣️ **Shall we discuss right now in your language?** Just ask Shadow!"
    )

# Your new Telegram Token from @BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

@app.route("/telegram", methods=["POST"])
def unified_telegram_handler(): # Changed the name to be unique
    data = request.get_json()
    
    # 1. Handle New Members (The Welcome Message)
    if "message" in data and "new_chat_members" in data["message"]:
        for new_user in data["message"]["new_chat_members"]:
            user_name = new_user.get("first_name", "Investor")
            chat_id = data["message"]["chat"]["id"]
            
            welcome_msg = get_welcome_text(user_name)
            send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(send_url, json={
                "chat_id": chat_id, 
                "text": welcome_msg, 
                "parse_mode": "Markdown"
            })
        return "ok", 200

    # 2. Handle Regular Messages (The Truth Engine)
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"].lower()
        
        # Shadow's Real Estate Intelligence
        if "shadnagar" in user_text or "safe" in user_text:
            reply = "Shadow here. Analysis of Star City Shadnagar shows high growth potential. Verify at maps.safelanddeal.com"
        else:
            reply = "Shadow is here. Ask me about land verification or the Safeland Console!"

        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": reply})

    return "ok", 200

    # 2. Handle Regular Messages (The Truth Engine)
    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"].lower()
        
        # Shadow's Real Estate Intelligence
        if "shadnagar" in user_text or "safe" in user_text:
            reply = "Shadow here. Analysis of Star City Shadnagar shows high growth potential. Verify at maps.safelanddeal.com"
        else:
            reply = "Shadow is here. Ask me about land verification or the Safeland Console!"

        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": reply})

    return "ok", 200

    # --- STEP 2: REGULAR CHAT LOGIC ---
    # (Your existing Shadnagar / Safe land logic goes here)
    ...    
    # Handle both private and group messages
    message_data = data.get("message") or data.get("edited_message")
    
    if message_data:
        chat_id = message_data["chat"]["id"]
        chat_type = message_data["chat"]["type"] # 'private', 'group', or 'supergroup'
        text = message_data.get("text", "").lower()

        # Logic to only respond if it's a private chat OR Shadow is mentioned in a group
        is_private = chat_type == "private"
        is_mentioned = "@Safeland_Shadow_bot" in text # Replace with your bot username

        if is_private or is_mentioned:
            if "shadnagar" in text:
                reply = "Shadow here. Analysis of Star City Shadnagar shows 100% clear title. See map: maps.safelanddeal.com"
            else:
                reply = "Shadow is listening. How can I help the group verify land today?"

            send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(send_url, json={"chat_id": chat_id, "text": reply})

    return "ok", 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)