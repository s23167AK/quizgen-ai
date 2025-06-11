from fastapi import APIRouter, Query, HTTPException, Body
from io import BytesIO
from fastapi.responses import StreamingResponse
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from backend.services._test_generator import generate_test
from backend.services._test_to_pdf import test_to_PDF
from backend.services.evaluate_open_answer import evaluate_open_answer

router = APIRouter()

@router.get("/")
def get_quiz(
    question_count: int = Query(3),
    question_types: str = Query("short_answer,multiple_choice,fill_in_blank")
):
    try:
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = db.similarity_search("", k=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")

    if not docs:
        raise HTTPException(status_code=404, detail="Brak notatki do wygenerowania quizu.")

    try:
        full_text = docs[0].metadata.get("full_text", docs[0].page_content)
        types_list = [t.strip() for t in question_types.split(",")]

        quiz = generate_test(full_text, question_count, types_list)

        return {"quiz": quiz}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")
    
@router.get("/pdf")
def get_quiz_pdf(
    question_count: int = Query(3),
    question_types: str = Query("short_answer,multiple_choice,fill_in_blank")
):
    try:
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = db.similarity_search("", k=1)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")

    if not docs:
        raise HTTPException(status_code=404, detail="Brak notatki do wygenerowania quizu.")

    try:
        full_text = docs[0].metadata.get("full_text", docs[0].page_content)
        types_list = [t.strip() for t in question_types.split(",")]
        quiz = generate_test(full_text, question_count, types_list)
        pdf_bytes = test_to_PDF(quiz)

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=quiz.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")
    
@router.post("/evaluate")
def evaluate_quiz(payload: dict = Body(...)):
    try:
        quiz = payload.get("quiz", [])
        checked_quiz = []
        for q in quiz:
            q_out = dict(q)
            if q["type"] == "multiple_choice":
                correct = set(q.get("user_answer", [])) == set(q.get("correct_answer", []))
            else:
                correct = evaluate_open_answer(
                    question=q["question"],
                    correct_answers=q.get("correct_answer", []),
                    user_answers=q.get("user_answer", [])
                )
            q_out["correct"] = correct
            checked_quiz.append(q_out)
        return {"quiz": checked_quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd sprawdzania quizu: {str(e)}")
