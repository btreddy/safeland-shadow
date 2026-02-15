import os
import time
import pandas as pd
from pypdf import PdfReader
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import PIL.Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class Librarian:
    def __init__(self):
        self.library_path = "library"
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash-lite-001')

    # --- HELPER: UPLOAD FILE TO GEMINI ---
    def upload_to_gemini(self, path, mime_type=None):
        """Uploads a file to Gemini so it can process audio/video."""
        try:
            file = genai.upload_file(path, mime_type=mime_type)
            # Wait for processing (Videos need time)
            while file.state.name == "PROCESSING":
                time.sleep(2)
                file = genai.get_file(file.name)
            return file
        except Exception as e:
            print(f"Error uploading {path}: {e}")
            return None

    # --- READERS ---
    def read_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            return f"\n[EXCEL DATA: {os.path.basename(file_path)}]\n{df.to_string(index=False)}\n"
        except: return ""

    def read_pdf(self, file_path):
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted: text += extracted + "\n"
            return f"\n[PDF DATA: {os.path.basename(file_path)}]\n{text}\n"
        except: return ""

    def read_image(self, file_path):
        try:
            img = PIL.Image.open(file_path)
            response = self.vision_model.generate_content(["Extract all text/data.", img])
            return f"\n[IMAGE DATA: {os.path.basename(file_path)}]\n{response.text}\n"
        except: return ""

    def read_audio(self, file_path):
        print(f"   -> Listening to Audio: {os.path.basename(file_path)}...")
        try:
            # Upload MP3/WAV
            audio_file = self.upload_to_gemini(file_path, mime_type="audio/mp3")
            if not audio_file: return ""
            
            response = self.vision_model.generate_content([
                "Listen to this audio and provide a detailed transcript and summary of the key points.", 
                audio_file
            ])
            return f"\n[AUDIO TRANSCRIPT: {os.path.basename(file_path)}]\n{response.text}\n"
        except Exception as e:
            return f"\n[Error reading Audio: {e}]\n"

    def read_video(self, file_path):
        print(f"   -> Watching Video: {os.path.basename(file_path)}...")
        try:
            # Upload MP4
            video_file = self.upload_to_gemini(file_path, mime_type="video/mp4")
            if not video_file: return ""

            response = self.vision_model.generate_content([
                "Watch this video. Describe the location, the plot details, and any text shown on screen.", 
                video_file
            ])
            return f"\n[VIDEO ANALYSIS: {os.path.basename(file_path)}]\n{response.text}\n"
        except Exception as e:
            return f"\n[Error reading Video: {e}]\n"

    def read_youtube(self, url):
        """Extracts text from YouTube captions."""
        try:
            # Extract Video ID
            if "v=" in url: video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url: video_id = url.split("youtu.be/")[1]
            else: return ""

            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([t['text'] for t in transcript])
            return f"\n[YOUTUBE LINK: {url}]\n{full_text[:5000]}\n"
        except:
            return f"\n[YOUTUBE ERROR] Could not get transcript for {url}. (Video might not have captions)\n"

    def read_website(self, url):
        # ... (Same website code as before) ...
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url.strip(), headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return f"\n[WEBSITE DATA: {url}]\n{text[:5000]}\n"
            else: return ""
        except: return ""

    # --- MAIN COMPILE FUNCTION ---
    def compile_knowledge(self):
        full_context = "IMPORTANT BUSINESS DATA:\n"
        if not os.path.exists(self.library_path): return full_context

        print(f"[LIBRARIAN] Indexing multimedia files...")

        for root, dirs, files in os.walk(self.library_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                folder_tag = f"[{os.path.basename(root)} | {filename}]"

                # 1. Documents
                if filename.lower().endswith(('.xlsx', '.xls')):
                    full_context += self.read_excel(file_path).replace("[EXCEL DATA:", f"[EXCEL: {folder_tag}")
                elif filename.lower().endswith('.pdf'):
                    full_context += self.read_pdf(file_path).replace("[PDF DATA:", f"[PDF: {folder_tag}")
                elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    full_context += self.read_image(file_path).replace("[IMAGE DATA:", f"[IMAGE: {folder_tag}")

                # 2. AUDIO (New)
                elif filename.lower().endswith(('.mp3', '.wav', '.m4a')):
                    full_context += self.read_audio(file_path).replace("[AUDIO TRANSCRIPT:", f"[AUDIO: {folder_tag}")

                # 3. VIDEO FILES (New)
                elif filename.lower().endswith(('.mp4', '.mov')):
                    full_context += self.read_video(file_path).replace("[VIDEO ANALYSIS:", f"[VIDEO: {folder_tag}")

                # 4. LINKS (Web + YouTube)
                elif filename == "links.txt":
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            urls = f.readlines()
                            for url in urls:
                                if "youtube.com" in url or "youtu.be" in url:
                                    full_context += self.read_youtube(url.strip())
                                elif "http" in url:
                                    full_context += self.read_website(url.strip())
                    except: pass
                
                # 5. Notes
                elif filename.lower().endswith('.txt') and filename != "links.txt":
                    try:
                        with open(file_path, "r") as f: full_context += f"\n[NOTE: {folder_tag}]\n{f.read()}\n"
                    except: pass

        return full_context