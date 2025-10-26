import os
import json
from fastapi import HTTPException
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.transcriber import transcribe_audio
from services.summarizer import summarize_transcript
from search import add_document
from fastapi import Query
from search import semantic_search

from db import SessionLocal, init_db, Meeting
init_db()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # vite dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# project root and upload dir (you already have this)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "SmartMeetAI API is running 🚀"}

@app.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    # Save upload
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Transcribe (Whisper pipeline)
    transcript_text, transcript_path = transcribe_audio(file_path)

    # Summary with Ollama
    try:
        insights = summarize_transcript(transcript_text)  # model="mistral" if you prefer
    except Exception as e:
        insights = {"error": str(e)}

    session = SessionLocal()
    m = Meeting(
        filename=file.filename,
        transcript_path=transcript_path,
        transcript_preview=transcript_text[:1000],
        summary=json.dumps(insights, ensure_ascii=False),
    )
    session.add(m)
    session.commit()
    session.refresh(m)
    meeting_id = m.id
    session.close()

    add_document(
        doc_id=str(meeting_id),
        text=transcript_text,
        metadata={"meeting_id": meeting_id, "filename": file.filename}
    )

    # # combined result
    # return {
    #     "filename": file.filename,
    #     "transcript_path": transcript_path,
    #     "transcript_preview": transcript_text,
    #     "insights": insights
    # }

    return {
            "id": meeting_id,
            "filename": file.filename,
            "transcript_path": transcript_path,
            "transcript_preview": transcript_text[:500] + ("..." if len(transcript_text) > 500 else ""),
            "insights": insights
        }


@app.get("/meetings/")
def list_meetings():
    session = SessionLocal()
    rows = session.query(Meeting).order_by(Meeting.id.desc()).limit(50).all()
    session.close()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "created_at": r.created_at,
            "summary": (json.loads(r.summary) if r.summary else {})
        } for r in rows
    ]

@app.get("/meetings/{meeting_id}")
def get_meeting(meeting_id: int):
    session = SessionLocal()
    row = session.query(Meeting).filter(Meeting.id == meeting_id).first()
    session.close()
    if not row:
        raise HTTPException(404, "Meeting not found")
    return {
        "id": row.id,
        "filename": row.filename,
        "transcript_path": row.transcript_path,
        "transcript_preview": row.transcript_preview,
        "insights": (json.loads(row.summary) if row.summary else {})
    }

@app.get("/search")
def search(q: str = Query(..., min_length=2)):
    return semantic_search(q, n=5)
