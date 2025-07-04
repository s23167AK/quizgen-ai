from fastapi import APIRouter, HTTPException, Body
from services.evaluate_open_answer import evaluate_open_answer
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/")
def evaluate_quiz(payload: dict = Body(...)):
    logger.info("evaluate_quiz called with payload: %s", payload)
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
        logger.exception("Error while evaluating quiz")
        raise HTTPException(status_code=500, detail=f"Błąd sprawdzania quizu: {str(e)}")
