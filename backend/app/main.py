from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import get_db, Ticket
from .services.ingestion import retriever
from .services.rag import generate_response

app = FastAPI(title="SAHAYA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    retriever.load_index()

class ChatRequest(BaseModel):
    query: str
    language: str = "en"

@app.post("/api/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Retrieve
    docs = retriever.retrieve(request.query)
    # 2. RAG & Verification
    response = generate_response(request.query, docs)
    # 3. Create Ticket if Escalated
    if response["status"] == "ESCALATED":
        ticket = Ticket(
            id=response["ticket_id"],
            query=request.query,
            language=request.language,
            intent=response["intent"],
            confidence=response["confidence"],
            reason=response["reason"]
        )
        db.add(ticket)
        db.commit()
    return response

@app.get("/api/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()

@app.post("/api/ingest")
def ingest_docs():
    success = retriever.ingest_documents()
    return {"status": "success" if success else "failed", "message": "Index rebuilt."}

@app.get("/api/health")
def health():
    return {"status": "healthy"}
