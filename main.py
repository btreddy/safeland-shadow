import sys
import datetime
from colorama import init, Fore, Style
from modules.brain import Brain
from modules.mouth import Mouth
from modules.ears import Ears

init(autoreset=True)
DIRECT_MODE = True 

# --- LOGGING FUNCTION (The Secretary) ---
def log_conversation(speaker, message):
    """Saves the conversation to a text file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("meeting_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {speaker}: {message}\n")

def main():
    print(Fore.CYAN + "\n" + "="*40)
    print(Fore.CYAN + "   UNIVERSAL VIRTUAL PARTNER (v5.0)   ")
    print(Fore.CYAN + "="*40 + "\n")
    
    # --- ROLE SELECTION MENU ---
    print(Fore.YELLOW + "Select Your Role:")
    print("1. Real Estate Agent 🏠 (Sell Plots)")
    print("2. Safeland Console 🌍 (Business Dev: Agents/Investors)")
    print("3. SaaS Architect 💻 (Software Development)")
    print("4. Pharma Rep 💊 (Medical Info)")
    print("5. Demo Rep 💊 (folder and web Info)")
    
    role_choice = input(Fore.WHITE + "\nEnter number (1-5): ").strip()
    # Default to 1 if they type garbage
    if role_choice not in ["1", "2", "3", "4", "5"]:
        role_choice = "1" 
    
    try:
        # Pass the choice to the Brain
        my_brain = Brain(role_id=role_choice)
        my_mouth = Mouth()
        my_ears = Ears()
        print(Fore.GREEN + f"✓ System Ready. Active Role: {my_brain.current_persona['name']}\n")
        
        # Log the start
        log_conversation("SYSTEM", f"--- NEW SESSION: {my_brain.current_persona['name']} ---")
        
    except Exception as e:
        print(Fore.RED + f"Startup Error: {e}")
        return

    # --- MAIN LOOP ---
    while True:
        try:
            print(Fore.BLUE + "---")
            choice = input(Fore.WHITE + "You: " + Style.RESET_ALL).strip()
            
            final_input = ""

            # --- CHECK FOR SPECIAL COMMANDS FIRST ---
            
            # Command 1: Update Memory (Re-scan files)
            if choice.lower() == 'update memory':
                print(Fore.YELLOW + "   [SYSTEM] Updating Knowledge Base... Please wait.")
                my_brain.memory.build_memory()
                print(Fore.GREEN + "   [SYSTEM] Memory Updated! I have read your new files.")
                continue # Skip the rest and go back to start
            
            # Command 2: Exit
            elif choice.lower() in ['exit', 'quit']:
                print("Goodbye.")
                log_conversation("SYSTEM", "--- SESSION ENDED ---")
                break

            # Command 3: Microphone (Empty Enter)
            elif choice == "":
                final_input = my_ears.listen()
                if not final_input: 
                    continue # If no sound, loop back
                print(Fore.YELLOW + f"  (Whisper): {final_input}")

            # Command 4: Normal Text Input
            else:
                final_input = choice

            # --- PROCESS THE INPUT ---

            # 1. LOG USER INPUT
            log_conversation("USER", final_input)

            # 2. THINK
            polished_response = my_brain.think(final_input)
            
            # 3. SHOW & SPEAK
            print(Fore.GREEN + f"Agent: {polished_response}")
            
            if DIRECT_MODE:
                my_mouth.speak(polished_response)
            
            # 4. LOG AGENT RESPONSE
            log_conversation("AGENT", polished_response)

        except KeyboardInterrupt:
            print(Fore.RED + "\nForce closing...")
            log_conversation("SYSTEM", "--- FORCE CLOSED ---")
            sys.exit()
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()