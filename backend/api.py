import shutil
import tempfile
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from main import run_pipeline
from core.rag_engine import ask_question

app = FastAPI(title="Video Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (a database replaces this later)
JOBS: dict[str, dict] = {}       # job_id -> status, step, meeting_id, error
MEETINGS: dict[str, dict] = {}   # meeting_id -> title, summary, transcript, ...
CHAINS: dict[str, object] = {}   # meeting_id -> RAG chain (cannot be sent to the browser)

pipeline_lock = threading.Lock()  # Whisper is heavy: process one video at a time
UPLOAD_DIR = Path(tempfile.gettempdir()) / "video_assistant_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


def friendly_error(e: Exception) -> str:
    msg = str(e)
    low = msg.lower()
    if "quota" in low or "429" in low or "resource_exhausted" in low:
        return "The AI daily limit was reached. Please try again later."
    if "private video" in low or "unavailable" in low:
        return "This video is private or unavailable. Try a different link."
    if "unsupported url" in low:
        return "This link isn't supported. Paste a direct video link (for example YouTube)."
    return f"Processing failed: {msg[:300]}"


def run_job(job_id: str, source: str, temp_file: Path | None):
    job = JOBS[job_id]
    try:
        with pipeline_lock:
            job["status"] = "running"
            result = run_pipeline(source, on_step=lambda i: job.update(step=i))

        meeting_id = uuid.uuid4().hex
        CHAINS[meeting_id] = result.pop("rag_chain")
        result["meeting_id"] = meeting_id
        MEETINGS[meeting_id] = result
        job.update(status="done", meeting_id=meeting_id)
    except Exception as e:
        job.update(status="error", error=friendly_error(e))
    finally:
        if temp_file:
            temp_file.unlink(missing_ok=True)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/jobs")
def create_job(url: str | None = Form(None), file: UploadFile | None = File(None)):
    temp_file = None

    if file and file.filename:
        suffix = Path(file.filename).suffix or ".mp4"
        temp_file = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
        with open(temp_file, "wb") as f:
            shutil.copyfileobj(file.file, f)
        source = str(temp_file)
    elif url and url.strip().startswith(("http://", "https://")):
        source = url.strip()
    else:
        raise HTTPException(400, "Please provide a valid link or a file.")

    job_id = uuid.uuid4().hex
    JOBS[job_id] = {"status": "queued", "step": 0}
    threading.Thread(target=run_job, args=(job_id, source, temp_file), daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found. The server may have restarted.")
    return job


@app.get("/api/meetings/{meeting_id}")
def get_meeting(meeting_id: str):
    meeting = MEETINGS.get(meeting_id)
    if not meeting:
        raise HTTPException(404, "Meeting not found.")
    return meeting


class ChatIn(BaseModel):
    meeting_id: str
    question: str


@app.post("/api/chat")
def chat(body: ChatIn):
    chain = CHAINS.get(body.meeting_id)
    if not chain:
        raise HTTPException(404, "This meeting isn't available anymore. Please process the video again.")
    try:
        answer = ask_question(chain, body.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(500, friendly_error(e))