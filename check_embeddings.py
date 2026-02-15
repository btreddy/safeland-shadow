import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

print("\n🔍 CHECKING YOUR API PRIVILEGES...")
print("====================================")
try:
    found_any = False
    for m in genai.list_models():
        # We only care about models that can EMBED (create memory)
        if 'embedContent' in m.supported_generation_methods:
            print(f"✅ AVAILABLE: {m.name}")
            found_any = True
    
    if not found_any:
        print("❌ NO EMBEDDING MODELS FOUND.")
        print("   (Your API Key might be restricted to Chat only)")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
print("====================================\n")