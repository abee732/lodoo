from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import logging

# ==========================
# INIT
# ==========================

load_dotenv()

app = FastAPI(title="MCP AI Server")

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger("MCP")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", "http://qdrant:6333")

# ==========================
# AI + VECTOR INIT
# ==========================

_logger.info("Loading embedding model...")
embed_model = SentenceTransformer("paraphrase-MiniLM-L3-v2")

qdrant = QdrantClient(url=VECTOR_DB_URL)

COLLECTION_NAME = "odoo_knowledge"

# ==========================
# CREATE COLLECTION IF NOT EXISTS
# ==========================

def init_collection():
    collections = [c.name for c in qdrant.get_collections().collections]
    if COLLECTION_NAME not in collections:
        _logger.info("Creating vector collection: %s", COLLECTION_NAME)
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "size": 384,
                "distance": "Cosine"
            }
        )

init_collection()

# ==========================
# REQUEST MODELS
# ==========================

class ChatRequest(BaseModel):
    message: str

class EmbeddingRequest(BaseModel):
    doc_id: int
    content: str

class AskRequest(BaseModel):
    question: str

# ==========================
# HEALTH CHECK
# ==========================

@app.get("/health")
def health():
    return {"status": "ok", "vector_db": VECTOR_DB_URL}

# ==========================
# BASIC CHAT (OPENAI)
# ==========================

@app.post("/chat")
def chat(req: ChatRequest):
    # 1. Kiểm tra API Key đã nạp chưa
    if not OPENAI_API_KEY:
        return {"reply": "Lỗi: MCP Server chưa cấu hình OPENAI_API_KEY trong file .env"}

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant for Odoo ERP"},
            {"role": "user", "content": req.message}
        ]
    }

    try:
        # 2. Gửi request tới OpenAI
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        data = res.json()

        # 3. Kiểm tra xem OpenAI có trả về lỗi không (ví dụ: 401, 429, 500)
        if res.status_code != 200:
            error_msg = data.get('error', {}).get('message', 'Lỗi không xác định từ OpenAI')
            print(f"DEBUG OPENAI ERROR: {data}") # Xem log này trong terminal mcp_server
            return {"reply": f"Lỗi từ OpenAI: {error_msg}"}

        # 4. Kiểm tra xem cấu trúc dữ liệu 'choices' có tồn tại không
        if "choices" in data and len(data["choices"]) > 0:
            return {"reply": data["choices"][0]["message"]["content"]}
        else:
            return {"reply": "Lỗi: OpenAI trả về dữ liệu rỗng (không có 'choices')"}

    except Exception as e:
        _logger.exception("MCP Chat Error")
        raise HTTPException(500, str(e))

# ==========================
# EMBEDDING ENDPOINT
# ==========================

@app.post("/embedding")
def embedding(req: EmbeddingRequest):
    if not req.content:
        return {"status": "skipped"}

    vector = embed_model.encode(req.content).tolist()

    qdrant.upsert(
        collection_name=COLLECTION,
        points=[{
            "id": req.doc_id,
            "vector": vector,
            "payload": {"text": req.content[:1000]}
        }]
    )

    return {"status": "ok"}

@app.post("/ask")
def ask(req: AskRequest):
    vector = embed_model.encode(req.question).tolist()

    hits = qdrant.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=5
    )

    context = "\n".join([h.payload.get("text", "") for h in hits])

    prompt = f"""
Use only this context to answer:

{context}

Question: {req.question}
"""

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an enterprise ERP knowledge AI"},
            {"role": "user", "content": prompt}
        ]
    }

    res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    return {"reply": res.json()["choices"][0]["message"]["content"]}