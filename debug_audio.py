import os
import requests
import pygame
import time
from dotenv import load_dotenv

load_dotenv()

def test_system():
    api_key = os.getenv("ELEVENLABS_API_KEY")
    print(f"1. Checking API Key: {'Found' if api_key else 'MISSING'}")
    
    # TEST 1: Try to generate a tiny sound
    print("2. Requesting Audio from ElevenLabs...")
    
    url = "https://api.elevenlabs.io/v1/text-to-speech/JBFqnCBsd6RMkjVDRZzb"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": "Testing audio system one two three.",
        "model_id": "eleven_turbo_v2_5", # Trying the Turbo model
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("   [SUCCESS] Audio downloaded from API.")
        with open("debug_test.mp3", "wb") as f:
            f.write(response.content)
            
        # TEST 2: Play it
        print("3. Attempting to play with Pygame...")
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("debug_test.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            print("   [SUCCESS] Playback finished.")
        except Exception as e:
            print(f"   [FAIL] Pygame error: {e}")
    else:
        print(f"   [FAIL] API Error: {response.text}")

if __name__ == "__main__":
    test_system()