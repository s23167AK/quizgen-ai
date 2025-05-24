from fastapi import APIRouter, Query, HTTPException
from backend.services.faiss_utils import search_in_faiss
from backend.services.quiz_generator import generate_quiz

router = APIRouter()

@router.get("/")
def get_quiz(query: str = Query(""), question_count: int = 3):
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Musisz podać zapytanie, np. ?query=Python")

        # 1. Pobierz kontekst z FAISS
        top_chunks = search_in_faiss(query, k=3)
        context = "\n".join(top_chunks)

        # 2. Przekaż jako prompt do GPT
        quiz = generate_quiz(context)

        return {"quiz": quiz}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")
