import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()  

def generate_quiz(note_content: str) -> str:
    chat = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = (
        "Na podstawie poniższej notatki wygeneruj co najmniej 3 pytania do quizu:\n"
        "- pytanie otwarte (krótka odpowiedź),\n"
        "- pytanie zamknięte (wielokrotny wybór – opcjonalnie),\n"
        "- pytanie z luką do uzupełnienia (definicja).\n\n"
        f"NOTATKA:\n{note_content}"
    )

    response = chat.invoke([HumanMessage(content=prompt)])
    return response.content
