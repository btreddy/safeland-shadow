import os
import time
from dotenv import load_dotenv

# Foundation logic
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Force Local Sync
load_dotenv(override=True)

# Define the folders to build brains for
DATA_FOLDERS = {
    "baas": "./data/baas",
    "real_estate": "./data/real_estate"
}

def build_specialist_brain(brain_name, source_path):
    print(f"\n🧠 Building Specialist Brain for: {brain_name}...")
    
    documents = []
    # Manually iterate to avoid dependency errors
    for file in os.listdir(source_path):
        full_path = os.path.join(source_path, file)
        try:
            if file.endswith(".pdf"):
                loader = PyPDFLoader(full_path)
                documents.extend(loader.load())
                print(f" ✅ Loaded PDF: {file}")
            elif file.endswith(".txt"):
                loader = TextLoader(full_path, encoding='utf-8')
                documents.extend(loader.load())
                print(f" ✅ Loaded TXT: {file}")
        except Exception as e:
            print(f" ❌ Skipping {file}: {e}")

    if not documents:
        print(f" ⚠️ No documents found in {source_path}. Skipping.")
        return

    # Split logic
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    # Embedding logic
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    
    print(f" 🐢 Embedding {len(chunks)} chunks for {brain_name}...")
    
    # Build and Save
    vector_store = FAISS.from_documents(chunks, embeddings)
    index_name = f"faiss_index_{brain_name}"
    vector_store.save_local(index_name)
    print(f" ✨ SUCCESS! '{index_name}' updated.")

if __name__ == "__main__":
    for name, path in DATA_FOLDERS.items():
        if os.path.exists(path):
            build_specialist_brain(name, path)
        else:
            print(f" ❌ Folder not found: {path}")