import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import logging
logger = logging.getLogger(__name__)
load_dotenv()

def evaluate_open_answer(question: str, correct_answers: list, user_answers: list):
    logger.info("evaluate_open_answer: question=%r, correct=%r, user=%r",question, correct_answers, user_answers)
    chat = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = (
        f"Oceń odpowiedź użytkownika na pytanie quizowe. "
        f"Twoim zadaniem jest sprawdzić, czy odpowiedź użytkownika jest poprawna, nawet jeśli użyto innych słów, pojawiły się literówki lub synonimy. "
        f"Oceń bardzo łagodnie, jeśli znaczenie jest tożsame, bardzo bliskie lub tylko trochę niepełne, uznaj odpowiedź za poprawną.\n"
        f"\n"
        f"Pytanie: {question}\n"
        f"Poprawne odpowiedzi (przynajmniej jedna): {correct_answers}\n"
        f"Odpowiedź użytkownika: {user_answers}\n"
        f"Odpowiedz tylko jednym słowem: True jeśli poprawne, False jeśli błędne."
    )
    
    response = chat.invoke([HumanMessage(content=prompt)])
    answer = response.content.strip()

    if answer.lower() == "true":
        return True
    elif answer.lower() == "false":
        return False
    try:
        return bool(json.loads(answer))
    except Exception:
        logger.exception("Invalid AI response format")
        raise ValueError(f"evaluate_open_answer: Niepoprawny format odpowiedzi z AI: {answer}")