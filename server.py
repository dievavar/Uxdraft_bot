import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from config import OUTPUT_DIR

app = FastAPI(title="UXDraft Previews")
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/previews", StaticFiles(directory=OUTPUT_DIR), name="previews")

@app.get("/health")
async def health():
    return {"status": "ok"}
