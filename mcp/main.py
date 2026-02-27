from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import httpx

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    question: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    if not OPENAI_API_KEY:
        raise HTTPException(500, "Missing OPENAI_API_KEY")

    payload = {
        "model": "gpt-4o-mini",
        "input": req.question
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload
        )

    if r.status_code != 200:
        raise HTTPException(500, r.text)

    data = r.json()

    try:
        answer = data["output"][0]["content"][0]["text"]
    except Exception:
        raise HTTPException(500, f"Invalid OpenAI response: {data}")

    return {"answer": answer}