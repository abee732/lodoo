from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

app = FastAPI(
    title="MCP AI Gateway",
    version="1.0.0",
    description="Production-grade AI Gateway for Odoo ERP"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # nếu public, còn private thì fix domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health():
    return {"status": "ok"}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def call_openai(payload: dict):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
    return r


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured"
        )

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are a professional Odoo ERP AI assistant."},
            {"role": "user", "content": req.message}
        ],
        "temperature": 0.3
    }

    try:
        res = await call_openai(payload)
        data = res.json()

        if res.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=data.get("error", {}).get("message", "OpenAI error")
            )

        return {"reply": data["choices"][0]["message"]["content"]}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))