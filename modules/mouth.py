import os
import asyncio
import edge_tts
import time

# --- SAFETY SWITCH ---
try:
    import pygame
    import msvcrt
    AUDIO_AVAILABLE = True
except ImportError:
    # If we are on the Cloud, these won't exist.
    # We set a flag so the code knows to skip audio.
    AUDIO_AVAILABLE = False
    print("   [SYSTEM] Audio libraries not found. Running in Silent Mode (Cloud).")

VOICE = "en-IN-PrabhatNeural" 
OUTPUT_FILE = "response.mp3"

class Mouth:
    def __init__(self):
        if AUDIO_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"   [MOUTH] Audio Init Error: {e}")

    async def _generate_audio(self, text):
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(OUTPUT_FILE)

    def speak(self, text):
        # 1. IF ON CLOUD, SKIP EVERYTHING
        if not AUDIO_AVAILABLE:
            return 

        if not text: return

        # 2. GENERATE AUDIO (Only if local)
        try:
            clean_text = text.replace("*", "").replace("#", "")
            asyncio.run(self._generate_audio(clean_text))
        except Exception as e:
            print(f"   [MOUTH] Generation Error: {e}")
            return

        # 3. PLAY AUDIO
        try:
            pygame.mixer.music.load(OUTPUT_FILE)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                # Keyboard interaction only works on Windows/Local
                if msvcrt and msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b' ' or key.lower() == b's':
                        pygame.mixer.music.stop()
                        print("\n   [Shadow Silenced] 🤫")
                        break
                time.sleep(0.1)
                
        except Exception as e:
            print(f"   [MOUTH] Playback Error: {e}")
            
        finally:
            try:
                pygame.mixer.music.unload()
            except:
                pass

    def close(self):
        if AUDIO_AVAILABLE:
            pygame.mixer.quit()
        if os.path.exists(OUTPUT_FILE):
            try:
                os.remove(OUTPUT_FILE)
            except:
                pass