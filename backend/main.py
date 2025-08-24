from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

import os
from pathlib import Path
from openai import OpenAI

app = FastAPI()

# Allow all origins (simple for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- OpenAI client -----
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ----- Serve frontend -----
ROOT_DIR = Path(_file_).resolve().parent.parent      # repo root
FRONTEND_DIR = ROOT_DIR / "frontend"

# /static -> serve the whole frontend folder (css/js/images if any)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=False), name="static")

# GET / -> index.html
@app.get("/")
async def root():
    index_path = FRONTEND_DIR / "index.html"
    return FileResponse(index_path)

# Health
@app.get("/health")
async def health():
    return {"ok": True, "model": MODEL}

# Chat endpoint (simple, non-streaming to stabilise)
@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    user_text = (body.get("message") or "").strip()
    if not user_text:
        return JSONResponse({"reply": "Please type something."}, status_code=400)

    # Minimal flexible prompt — NO fixed template lock
    system_msg = (
        "You are a helpful assistant. Answer clearly and practically. "
        "Keep formatting simple (short paragraphs, bullets when useful)."
    )

    try:
        resp = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_text},
            ],
        )
        reply = resp.output_text
        return {"reply": reply}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# Run local (Railway will use Procfile)
if _name_ == "_main_":
    import uvicorn, os
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
