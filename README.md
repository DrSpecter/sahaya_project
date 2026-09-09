# SAHAYA 🇮🇳
**Multilingual Cooperative & Legal Assistance RAG**

SAHAYA is a fully local, privacy-centric Retrieval-Augmented Generation (RAG) system designed to provide verified answers on cooperative governance and government schemes (like PMFBY). It uses hybrid search (Dense FAISS + Sparse BM25) and local LLM inference to provide offline, multilingual support.

## Tech Stack
* **Backend:** FastAPI, Python
* **Frontend:** React, Vite
* **LLM Inference:** Ollama (Qwen2.5:1.5b)
* **Embeddings:** SentenceTransformers (`all-MiniLM-L6-v2`)
* **Retrieval:** FAISS (Dense) + BM25Okapi (Sparse)

## Prerequisites
1. [Ollama](https://ollama.com/) installed and running.
2. Node.js (v18+)
3. Python 3.10+

## Local Installation & Setup

**1. Start the Local LLM**
`ollama run qwen2.5:1.5b`

**2. Setup Backend**
Navigate to the backend folder:
`cd backend`
`python3 -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`
`uvicorn app.main:app --reload --port 8000`

*(Note: On the first run, the backend will auto-ingest documents from `backend/data/documents` and build the FAISS/BM25 indexes).*

**3. Setup Frontend**
Navigate to the frontend folder:
`cd frontend`
`npm install`
`npm run dev`

Visit `http://localhost:5173` to access the Chat Officer Dashboard.
