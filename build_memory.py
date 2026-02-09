import os
import time
from typing import List
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader

# --- 1. SETUP & AUTH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, ".env"))

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ Error: API Key missing.")
    exit()

print(f"🔑 API Key Loaded: {api_key[:4]}...{api_key[-4:]}")

# --- 2. THE 'SLOW' EMBEDDER CLASS ---
class SlowEmbeddings(GoogleGenerativeAIEmbeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        batch_size = 5  # Only send 5 chunks at a time
        embeddings = []
        
        # Calculate total batches for progress bar
        total_batches = (len(texts) + batch_size - 1) // batch_size
        print(f"🐢 Starting Slow Embedding: {len(texts)} chunks in {total_batches} batches...")
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"   -> Processing batch {i//batch_size + 1}/{total_batches}...")
            
            # Call the real Google API
            try:
                batch_embeddings = super().embed_documents(batch)
                embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"❌ Batch Failed: {e}")
                # Optional: Add retry logic here if needed
            
            # WAIT! Give the API a break.
            time.sleep(2) 
            
        print("✅ All chunks embedded!")
        return embeddings

# --- 3. INITIALIZE EMBEDDINGS ---
# FIX 1: We use 'SlowEmbeddings' instead of the standard one!
embeddings = SlowEmbeddings(
    model="models/gemini-embedding-001", 
    google_api_key=api_key
)

# --- 4. LOAD DOCUMENTS WITH ROLL CALL ---
folder_path = "library"
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"📂 Created '{folder_path}'.")
    exit()

print(f"📂 Scanning '{folder_path}'...")
docs = []

# Helper function to print filenames
def load_and_log(loader, name):
    try:
        documents = loader.load()
        for doc in documents:
            # FIX 2: This prints the filename of every file found
            filename = os.path.basename(doc.metadata.get('source', 'Unknown'))
            print(f"   👀 Found {name}: {filename}")
        return documents
    except Exception as e:
        print(f"⚠️ {name} Error: {e}")
        return []

# Load Text Files
txt_loader = DirectoryLoader(folder_path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
docs.extend(load_and_log(txt_loader, "Text File"))

# Load PDF Files
pdf_loader = DirectoryLoader(folder_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
docs.extend(load_and_log(pdf_loader, "PDF File"))

if not docs:
    print("⚠️ No files found. Memory not updated.")
    exit()

print(f"📄 Total Documents: {len(docs)}. Starting Build process...")

# --- 5. BUILD & SAVE ---
try:
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local("faiss_index")
    print("\n🎉 SUCCESS! Memory Updated.")
    print("   -> 'faiss_index' folder created.")
except Exception as e:
    print(f"\n❌ Failed: {e}")