import os
import json
import pickle
import faiss
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

# 1. Resolve absolute path to .env and load it FIRST
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# 2. Now import SentenceTransformer (which will now see HF_TOKEN in os.environ)
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

INDEX_DIR = "./data/index"
DOCS_DIR = "./data/documents"

class HybridRetriever:
    # ... rest of your existing class code remains exactly the same ...
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)
        self.chunks = []
        self.faiss_index = None
        self.bm25 = None
        
    def ingest_documents(self):
        self.chunks = []
        # Fallback dummy data if folder is empty
        if not os.path.exists(DOCS_DIR) or not os.listdir(DOCS_DIR):
            self._create_demo_docs()

        for filename in os.listdir(DOCS_DIR):
            if filename.endswith(".txt"):
                with open(os.path.join(DOCS_DIR, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple chunking by paragraph for MVP
                    paragraphs = [p for p in content.split('\n\n') if len(p.strip()) > 20]
                    for i, p in enumerate(paragraphs):
                        self.chunks.append({
                            "text": p.strip(),
                            "source": filename,
                            "page": i + 1,
                            "section": "General",
                            "document_id": filename.split('.')[0]
                        })
        
        if not self.chunks:
            return False

        # 1. Build FAISS (Dense)
        embeddings = self.encoder.encode([c["text"] for c in self.chunks])
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(np.array(embeddings).astype('float32'))

        # 2. Build BM25 (Sparse)
        tokenized_corpus = [c["text"].lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        os.makedirs(INDEX_DIR, exist_ok=True)
        faiss.write_index(self.faiss_index, os.path.join(INDEX_DIR, "dense.index"))
        with open(os.path.join(INDEX_DIR, "meta.pkl"), "wb") as f:
            pickle.dump({"chunks": self.chunks, "bm25": self.bm25}, f)
        return True

    def load_index(self):
        try:
            self.faiss_index = faiss.read_index(os.path.join(INDEX_DIR, "dense.index"))
            with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
                data = pickle.load(f)
                self.chunks = data["chunks"]
                self.bm25 = data["bm25"]
            return True
        except Exception:
            return self.ingest_documents()

    def retrieve(self, query, top_k=3):
        if not self.chunks:
            return []
        
        # Dense Search
        q_emb = self.encoder.encode([query])
        D, I = self.faiss_index.search(np.array(q_emb).astype('float32'), top_k)
        dense_results = [(self.chunks[i], 1.0 / (1.0 + D[0][idx])) for idx, i in enumerate(I[0])]

        # Sparse Search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_idx = np.argsort(bm25_scores)[::-1][:top_k]
        sparse_results = [(self.chunks[i], bm25_scores[i] / 10.0) for i in top_bm25_idx] # Normalize rough

        # Combine & Deduplicate (Simple Reciprocal Rank Fusion mock)
        combined = {}
        for item, score in dense_results + sparse_results:
            text = item["text"]
            if text in combined:
                combined[text]["score"] += score
            else:
                combined[text] = {"item": item, "score": score}
        
        ranked = sorted(combined.values(), key=lambda x: x["score"], reverse=True)[:top_k]
        return [{"chunk": r["item"], "score": min(r["score"], 0.99)} for r in ranked]

    def _create_demo_docs(self):
        os.makedirs(DOCS_DIR, exist_ok=True)
        with open(os.path.join(DOCS_DIR, "PMFBY_Guidelines.txt"), "w") as f:
            f.write("Pradhan Mantri Fasal Bima Yojana (PMFBY) Operational Guidelines.\n\n"
                    "Claim Settlement Procedure: All claims must be settled within 21 days of crop cutting experiments. "
                    "The farmer must notify the insurance company or cooperative bank within 72 hours of localized crop loss.\n\n"
                    "Eligibility: All farmers growing notified crops in a notified area during the season who have insurable interest in the crop are eligible.")
        with open(os.path.join(DOCS_DIR, "Cooperative_Bylaws.txt"), "w") as f:
            f.write("Model Cooperative Society By-laws.\n\n"
                    "Membership: Any person aged 18 years and above, residing in the operational area of the society, "
                    "can become a member by paying a share capital of Rs. 1000 and an admission fee of Rs. 100.\n\n"
                    "Grievance Redressal: Disputes regarding membership must be submitted in writing to the Board of Directors, "
                    "who shall constitute a 3-member committee to resolve it within 30 days.")

retriever = HybridRetriever()
