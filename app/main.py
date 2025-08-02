# --- app/main.py ---
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag_pipeline import answer_question

app = FastAPI()

class QARequest(BaseModel):
    repo_path: str
    question: str

@app.post("/ask")
async def ask_question(request: QARequest):
    try:
        answer = answer_question(request.repo_path, request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
