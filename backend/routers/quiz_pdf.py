from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from io import BytesIO
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from backend.services.quiz_generator import generate_quiz
from backend.services.quiz_to_pdf import quiz_to_PDF

router = APIRouter()

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
        quiz = generate_quiz(full_text, question_count, types_list)
        pdf_bytes = quiz_to_PDF(quiz)

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=quiz.pdf"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")