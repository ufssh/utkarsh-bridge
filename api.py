from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import mimetypes
import uuid
import shutil

app = FastAPI()

# --- CORS Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Download + Serve Logic ---
def download_and_serve_file(url: str, file_extension: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://utkarsh.com/",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers, timeout=60, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to download file")

        unique_id = str(uuid.uuid4())
        filename = f"/tmp/{unique_id}{file_extension}"
        with open(filename, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        mime_type, _ = mimetypes.guess_type(filename)
        return FileResponse(filename, media_type=mime_type or "application/octet-stream", filename=os.path.basename(filename))

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Endpoints ---
@app.get("/api/pdf")
def proxy_pdf(url: str = Query(...)):
    return download_and_serve_file(url, ".pdf")

@app.get("/api/video")
def proxy_video(url: str = Query(...)):
    ext = os.path.splitext(url)[1] or ".mp4"
    return download_and_serve_file(url, ext)

# --- Root for health check ---
@app.get("/")
def root():
    return {"status": "ok", "message": "Utkarsh proxy bridge is live"}
