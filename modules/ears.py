import speech_recognition as sr
from colorama import Fore

class Ears:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        
        # --- SENSITIVITY FIX ---
        # We manually set the threshold lower so it hears whispers
        self.recognizer.energy_threshold = 300  
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8 

    def listen(self):
        with self.mic as source:
            # Print a visual cue so you know it's active
            print(Fore.CYAN + "   (Listening...)" + Fore.RESET, end="\r", flush=True)
            try:
                # Increased timeout to 8 seconds to give you more time to think
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=10)
                
                # Using Indian English for better recognition of local terms
                text = self.recognizer.recognize_google(audio, language='en-IN')
                return text.lower()
            except sr.WaitTimeoutError:
                return "" 
            except sr.UnknownValueError:
                return "" 
            except Exception:
                return ""