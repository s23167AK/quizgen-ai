import uuid
from fastapi import APIRouter, Body, HTTPException, Query
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field
import logging
from backend.services.agents import run_chatbot, continue_chatbot, graph

logger = logging.getLogger(__name__)


router = APIRouter()

class QuizAnswerRequest(BaseModel):
    thread_id: str = Field(..., description="Unikalny identyfikator sesji quizu (z startu quizu)")
    user_answer: str = Field(..., description="Odpowiedź użytkownika na bieżące pytanie")

@router.get("/start")
def start(
    question_count: int = Query(3),
    question_types: str = Query("short_answer,multiple_choice,fill_in_blank")
):
    logger.info("START /quiz/start?question_count=%d&question_types=%r", question_count, question_types)
    try:
        embeddings = OpenAIEmbeddings()
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = db.similarity_search("", k=1)
    except Exception as e:
        logger.exception("Error loading FAISS index")
        raise HTTPException(status_code=500, detail=f"Błąd pobierania notatki: {str(e)}")

    if not docs:
        raise HTTPException(status_code=404, detail="Brak notatki do wygenerowania quizu.")

    try:
        full_text = docs[0].metadata.get("full_text", docs[0].page_content)

        types_list = [t.strip() for t in question_types.split(",")]

        allow_short_answer = "short_answer" in types_list
        allow_multiple_choice = "multiple_choice" in types_list
        allow_fill_in_blank = "fill_in_blank" in types_list
        
        print(allow_short_answer)
        print(allow_multiple_choice)
        print(allow_fill_in_blank)

        thread_id = str(uuid.uuid4())
        logger.info("Generating quiz thread_id=%s", thread_id)
        result = run_chatbot(
            note_content=full_text,
            number_of_questions=question_count,
            thread_id=thread_id,
            allow_short_answer=allow_short_answer,
            allow_multiple_choice=allow_multiple_choice,
            allow_fill_in_blank=allow_fill_in_blank,
            debug=False,
        )
        question = result.dict() if result else None
        return {
            "thread_id": thread_id,
            "question": question
        }



    except Exception as e:
        logger.exception("Error generating quiz")
        raise HTTPException(status_code=500, detail=f"Błąd generowania quizu: {str(e)}")
    
@router.post("/answer")
def answer(
    payload: QuizAnswerRequest
):
    logger.info("POST /quiz/answer payload: %s", payload.dict())
    thread_id = payload.thread_id
    user_answer = payload.user_answer

    if not thread_id or user_answer is None:
        raise HTTPException(status_code=400, detail="Brak thread_id lub user_answer")

    try:
        result = continue_chatbot(thread_id=thread_id, user_answer=user_answer, debug=False)
        if result is not None:
            question = result.dict() if hasattr(result, "dict") else result
            return {
                "question": question,
                "summary": None
            }
        else:
            state = graph.get_state({"configurable": {"thread_id": thread_id}})
            summary_msg = next(
                (m['content'] for m in state.get('messages', []) if "Podsumowanie odpowiedzi" in m.get('content', "")),
                None
            )
            return {
                "question": None,
                "summary": {
                    "text": summary_msg
                }
            }
    except Exception as e:
        logger.exception("Error in /quiz/answer")
        raise HTTPException(status_code=500, detail=f"Błąd obsługi odpowiedzi quizu: {str(e)}")