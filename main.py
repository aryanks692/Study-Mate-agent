import os
import shutil
from typing import List, Optional
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from studymate_core import (
    get_notes_folder,
    load_notes,
    get_notes_summary,
    search_notes,
    ask_ai,
    generate_quiz,
    generate_mcq_quiz,
    evaluate_answer,
    NOTES_FOLDER
)

app = FastAPI(
    title="StudyMate AI Agent",
    description="Interactive Web Interface for StudyMate AI Coach",
    version="1.0.0"
)

# Global notes cache
notes_cache = {}

def refresh_notes():
    global notes_cache
    notes_cache = load_notes()
    return notes_cache

@app.on_event("startup")
def startup_event():
    refresh_notes()

# Request schemas
class ChatRequest(BaseModel):
    message: str

class QuizGenerateRequest(BaseModel):
    topic: str

class QuizEvaluateRequest(BaseModel):
    question: str
    answer: str

# API Endpoints
@app.get("/api/health")
def health_check():
    import ollama
    ollama_ok = False
    models = []
    try:
        res = ollama.list()
        ollama_ok = True
        if hasattr(res, 'models'):
            models = [m.model for m in res.models]
        elif isinstance(res, dict) and 'models' in res:
            models = [m.get('name') or m.get('model') for m in res['models']]
    except Exception as e:
        pass

    return {
        "status": "healthy",
        "ollama_connected": ollama_ok,
        "models": models,
        "active_notes_count": len(notes_cache)
    }

@app.get("/api/notes")
def list_notes():
    summary = get_notes_summary()
    return {
        "notes": summary,
        "total_documents": len(summary),
        "total_characters": sum(item.get("char_count", 0) for item in summary)
    }

@app.post("/api/notes/upload")
async def upload_notes(files: List[UploadFile] = File(...)):
    folder = get_notes_folder()
    uploaded = []
    errors = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            errors.append(f"{file.filename}: Only PDF files are supported.")
            continue
        try:
            target_path = folder / file.filename
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded.append(file.filename)
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")

    refresh_notes()
    summary = get_notes_summary()
    return {
        "uploaded": uploaded,
        "errors": errors,
        "notes": summary
    }

@app.delete("/api/notes/{filename}")
def delete_note(filename: str):
    folder = get_notes_folder()
    target_path = folder / filename
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        os.remove(target_path)
        refresh_notes()
        return {"message": f"Successfully deleted {filename}", "notes": get_notes_summary()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Query message cannot be empty")

    results = search_notes(req.message, notes_cache)
    if not results:
        return {
            "answer": "I couldn't find relevant information in your uploaded study notes to answer this question. Try asking about topics present in your PDFs or upload more material!",
            "sources": []
        }

    try:
        answer = ask_ai(req.message, results)
        formatted_sources = [
            {"score": score, "filename": filename, "snippet": snippet}
            for score, filename, snippet in results
        ]
        return {
            "answer": answer,
            "sources": formatted_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Agent error: {str(e)}")

@app.post("/api/quiz/generate")
def quiz_generate(req: QuizGenerateRequest):
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    results = search_notes(req.topic, notes_cache)
    if not results:
        return {
            "questions": [],
            "message": "I couldn't find enough information in your notes regarding this topic to create an MCQ quiz.",
            "sources": []
        }

    try:
        mcq_data = generate_mcq_quiz(req.topic, results)
        formatted_sources = [
            {"score": score, "filename": filename, "snippet": snippet}
            for score, filename, snippet in results
        ]
        
        # If mcq_data returned as a string fallback, wrap it nicely
        if isinstance(mcq_data, str):
            return {
                "topic": req.topic,
                "raw_text": mcq_data,
                "questions": [],
                "sources": formatted_sources
            }
            
        return {
            "topic": req.topic,
            "questions": mcq_data,
            "sources": formatted_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz Generation error: {str(e)}")

@app.post("/api/quiz/evaluate")
def quiz_evaluate(req: QuizEvaluateRequest):
    if not req.question.strip() or not req.answer.strip():
        raise HTTPException(status_code=400, detail="Question and answer are required")

    results = search_notes(req.question, notes_cache)
    try:
        evaluation = evaluate_answer(req.question, req.answer, results)
        formatted_sources = [
            {"score": score, "filename": filename, "snippet": snippet}
            for score, filename, snippet in results
        ]
        return {
            "evaluation": evaluation,
            "sources": formatted_sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")

# Serve Static Files
static_path = Path("static")
static_path.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    index_file = static_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "StudyMate Backend API is running. Frontend static/index.html not found."}
