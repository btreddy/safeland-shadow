import os
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
load_dotenv()

def build_specific_brain(folder_path):
    # Create a unique name for this brain's index
    index_name = f"faiss_index_{folder_path.replace('/', '_')}"
    
    if not os.path.exists(folder_path) or not os.listdir(folder_path):
        print(f" [SKIP] Folder {folder_path} is empty or missing.")
        return

    print(f" [PROCESSING] Building brain for: {folder_path}...")
    
    try:
        # 1. Load PDFs
        loader = DirectoryLoader('./data/', glob="./**/*.pdf", show_progress=True)
        documents = loader.load()
        
        # 2. Split Text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        texts = text_splitter.split_documents(documents)
        
        # 3. Create Embeddings & Save Index (Using the new stable model)
        # Change this line in BOTH ingest.py and modules/brain.py
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_documents(texts, embeddings)
        vector_store.save_local(index_name)
        
        print(f" [SUCCESS] Created {index_name}\n")
    except Exception as e:
        print(f" [ERROR] Failed to build {folder_path}: {e}")

if __name__ == "__main__":
    # The new structured folder path
    folders_to_process = ["data/baas", "data/real_estate", "data/temp_demo"]
    
    for folder in folders_to_process:
        build_specific_brain(folder)
    
    print(" [DONE] All specialist brains are ready for Shadow.")