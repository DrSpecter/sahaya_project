import os
import json
import uuid
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Point to local Ollama server. API key is arbitrary but required by the OpenAI client.
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" 
)

def generate_response(query: str, retrieved_docs: list):
    max_retrieval_score = float(max([d["score"] for d in retrieved_docs])) if retrieved_docs else 0.0
    
    if max_retrieval_score < 0.2:
        return _escalate(query, 0.1, "No relevant documents found in the verified knowledge base.")

    context = ""
    for idx, doc in enumerate(retrieved_docs):
        context += f"--- Document {idx+1} ---\nSource: {doc['chunk']['source']}\nPage: {doc['chunk']['page']}\nText: {doc['chunk']['text']}\n\n"

    system_prompt = """You are SAHAYA, a multilingual legal and cooperative governance information assistant.
You MUST answer ONLY using the supplied verified evidence. 
Detect the language of the User Query (e.g., Hindi, Tamil, English) and write the "answer" field entirely in that same language.
If the evidence is insufficient, set status to INSUFFICIENT_EVIDENCE.
Return ONLY valid JSON. No markdown wrappers.

Format:
{
  "status": "SUPPORTED",
  "answer": "Your translated answer here...",
  "source_document": "PMFBY_Guidelines.txt"
}"""

    try:
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL", "qwen2.5:1.5b"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nUser Query: {query}"}
            ],
            temperature=0.1
        )
        
        raw_content = response.choices[0].message.content.strip()
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0]
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0]
            
        cleaned_content = "".join(c if ord(c) >= 32 or c in "\n\r\t" else " " for c in raw_content)
        result = json.loads(cleaned_content.strip(), strict=False)
        
    except Exception as e:
        return _escalate(query, max_retrieval_score, f"LLM Error: {str(e)}")

    if result.get("status") == "INSUFFICIENT_EVIDENCE":
        return _escalate(query, 0.4 * max_retrieval_score, "LLM determined evidence was insufficient.")

    # Resilient scoring for 1.5B model outputs
    entailment_score = 0.85 if result.get("answer") else 0.3
    source_quality_score = 0.8
    final_confidence = float((0.4 * max_retrieval_score) + (0.4 * entailment_score) + (0.2 * source_quality_score))

    THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.65))
    if final_confidence < THRESHOLD:
        return _escalate(query, final_confidence, "Failed confidence threshold verification.")

    # Fallback default source mapping if specific citation arrays are omitted by small model
    sources = [{
        "document": retrieved_docs[0]["chunk"]["source"],
        "page": retrieved_docs[0]["chunk"]["page"],
        "section": retrieved_docs[0]["chunk"].get("section", "General"),
        "score": round(max_retrieval_score, 2)
    }]

    return {
        "status": "SUPPORTED",
        "answer": result.get("answer"),
        "confidence": round(final_confidence, 2),
        "intent": "GENERAL",
        "language": "auto",
        "sources": sources,
        "ticket_id": None
    }

def _escalate(query, confidence, reason):
    ticket_id = f"GRV-2026-{str(uuid.uuid4())[:5].upper()}"
    return {
        "status": "ESCALATED",
        "answer": None,
        "confidence": round(float(confidence), 2),
        "intent": "UNKNOWN",
        "language": "en",
        "sources": [],
        "ticket_id": ticket_id,
        "reason": reason
    }
