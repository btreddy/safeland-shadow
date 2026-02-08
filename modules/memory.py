import os
import json
import numpy as np
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
from modules.librarian import Librarian
from dotenv import load_dotenv

load_dotenv()

# Configuration
EMBEDDING_MODEL = "models/gemini-embedding-001"
MEMORY_FILE = "brain_data.json"

class SmartMemory:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found.")
            return
        genai.configure(api_key=api_key)
        self.librarian = Librarian()
        self.knowledge_base = [] # List to hold text chunks
        self.vectors = None      # Numpy array for math

        # Load existing memory if it exists
        self.load_memory_from_disk()

    def split_text(self, text, chunk_size=800):
        """Splits a huge text file into smaller, digestible pieces."""
        chunks = []
        # Simple splitting by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def build_memory(self):
        """
        1. Reads all files from Librarian.
        2. Chunks them.
        3. Creates Embeddings (Vectors).
        4. Saves to disk.
        """
        print("   [MEMORY] Scanning Library & Building Index... (This may take a moment)")
        
        # 1. Get raw text from Librarian
        full_text = self.librarian.compile_knowledge()
        
        if not full_text:
            print("   [MEMORY] Library is empty.")
            return

        # 2. Split into chunks
        chunks = self.split_text(full_text)
        print(f"   [MEMORY] Created {len(chunks)} knowledge chunks.")

        # 3. Create Embeddings
        vectors = []
        clean_chunks = []
        
        # We process in batches to be safe
        for i, chunk in enumerate(chunks):
            if not chunk.strip(): continue
            try:
                # Ask Google for the "Vector" of this text
                result = genai.embed_content(
                    model=EMBEDDING_MODEL,
                    content=chunk,
                    task_type="retrieval_document"
                )
                vectors.append(result['embedding'])
                clean_chunks.append(chunk)
                print(f"   [MEMORY] Indexed chunk {i+1}/{len(chunks)}...", end="\r")
            except Exception as e:
                print(f"   [Error] Failed to embed chunk {i}: {e}")

        # 4. Save to Disk
        data = {
            "chunks": clean_chunks,
            "vectors": vectors
        }
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        print(f"\n   [MEMORY] Success! Saved {len(clean_chunks)} items to Permanent Memory.\n")
        
        # Reload immediately
        self.load_memory_from_disk()

    def load_memory_from_disk(self):
        """Loads the JSON file into RAM for fast access."""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.knowledge_base = data["chunks"]
                # Convert list back to numpy array for fast math
                self.vectors = np.array(data["vectors"])
        else:
            self.knowledge_base = []
            self.vectors = None

    def retrieve(self, query, top_k=3):
        """
        Finds the 3 most relevant chunks for the user's question.
        """
        if self.vectors is None or len(self.knowledge_base) == 0:
            return ""

        try:
            # 1. Embed the User's Question
            query_result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query"
            )
            query_vector = np.array(query_result['embedding']).reshape(1, -1)

            # 2. Calculate Similarity (Math Magic)
            # Compare query_vector vs all stored vectors
            similarities = cosine_similarity(query_vector, self.vectors)[0]

            # 3. Get Top K indices
            top_indices = similarities.argsort()[-top_k:][::-1]

            # 4. Construct Context
            relevant_context = ""
            for idx in top_indices:
                relevant_context += f"\n--- RELEVANT INFO ---\n{self.knowledge_base[idx]}\n"
            
            return relevant_context
        except Exception as e:
            print(f"   [Error] Retrieval failed: {e}")
            return ""