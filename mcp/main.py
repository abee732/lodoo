from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="MCP AI Server")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok"}

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
        print(f"DEBUG INTERNAL ERROR: {str(e)}")
        return {"reply": f"Lỗi hệ thống MCP: {str(e)}"}