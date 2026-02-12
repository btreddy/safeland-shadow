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
# --- 4. TARGETED LOAD (Replaces Lines 56-80) ---
def get_clean_docs(role_folder):
    # This forces the scan to stay ONLY in the specific subfolder (e.g., data/real_estate)
    path = os.path.join("data", role_folder)
    
    if not os.path.exists(path):
        print(f"⚠️ Warning: Folder {path} not found.")
        return []

    # FIX: Use "./*.pdf" instead of "**/*.pdf" to stop recursive duplicate scanning
    pdf_loader = DirectoryLoader(path, glob="./*.pdf", loader_cls=PyPDFLoader)
    txt_loader = DirectoryLoader(path, glob="./*.txt", loader_cls=TextLoader)
    
    loaded_docs = pdf_loader.load() + txt_loader.load()
    
    # Log found files once to verify the fix
    for doc in loaded_docs:
        fname = os.path.basename(doc.metadata.get('source', 'Unknown'))
        print(f" ✅ Found unique file: {fname}")
        
    return loaded_docs

# --- 5. START BUILD (Targeted Folders) ---
role = "real_estate"  # Change to "baas" to build your tech brain
docs = get_clean_docs(role)

# --- 6. BUILD & SAVE TO SPECIALIST FOLDER ---
if docs:
    try:
        print(f"🧠 Building Specialist Brain for: {role}...")
        vector_store = FAISS.from_documents(docs, embeddings)
        
        # Save to the specific folder your brain.py expects
        save_path = f"faiss_index_data_{role}"
        vector_store.save_local(save_path)
        
        print(f"\n✨ SUCCESS! {role.upper()} Memory Updated.")
        print(f"   -> '{save_path}' folder created/updated.")
    except Exception as e:
        print(f"\n❌ Failed to build index: {e}")
else:
    print("❌ Build aborted: No documents found in the selected library.")