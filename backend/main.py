from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from openai import OpenAI

app = FastAPI()

# Allow frontend requests (we'll serve frontend from the same app too)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- OpenAI client setup ----
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ---- Serve frontend ----
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(_file_)))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# serve /frontend as /static
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# GET /  -> index.html
@app.get("/")
async def root():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)

# Health
@app.get("/health")
async def health():
    return {"ok": True, "model": MODEL}

# Chat endpoint
@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    message = (data.get("message") or "").strip()
    if not message:
        return JSONResponse({"reply": "Please type a message."})

    # Simple system prompt (tweak as you like)
    system_prompt = (
        "You are Chetna AGI Console assistant. "
        "Answer clearly, be helpful, and keep responses concise unless asked for detail."
    )

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
        )
        reply = resp.choices[0].message.content
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"reply": f"Error: {str(e)}"}, status_code=500)

# For local / Railway run
if _name_ == "_main_":
    import uvicorn
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
