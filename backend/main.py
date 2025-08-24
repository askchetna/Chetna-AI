# backend/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from openai import OpenAI

app = FastAPI()

# CORS: frontend ko allow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/chat")
async def chat(req: Request):
    if not client:
        return JSONResponse({"error": "OPENAI_API_KEY not set"}, status_code=500)

    body = await req.json()
    user_msg = (body.get("message") or "").strip()
    if not user_msg:
        return JSONResponse({"error": "message is required"}, status_code=400)

    # Simple single-turn completion
    prompt = f"You are Chetna, a helpful Indian assistant.\nUser: {user_msg}\nAssistant:"
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a concise, practical assistant named Chetna."},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.7,
        )
        reply = resp.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Replit/CloudRun runner (Railway ignores this and uses Procfile/command)
if _name_ == "_main_":
    import uvicorn
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
