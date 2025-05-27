import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

def generate_quiz(note_content: str, question_count: int, question_types: list) -> list:
    chat = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    prompt = (
        f"Na podstawie poniższej notatki wygeneruj quiz w formacie JSON.\n"
        f"Liczba pytań: {question_count}.\n"
        f"Rodzaje pytań: {', '.join(question_types)}.\n\n"
        "Typy mogą być:\n"
        "- short_answer\n"
        "- multiple_choice (z kilkoma poprawnymi odpowiedziami jako lista)\n"
        "- fill_in_blank\n\n"
        "Zwróć tablicę JSON, np.:\n"
        "[\n"
        "  {\n"
        "    \"type\": \"short_answer\",\n"
        "    \"question\": \"Czym jest Python?\",\n"
        "    \"correct_answer\": \"Język programowania\"\n"
        "  },\n"
        "  {\n"
        "    \"type\": \"multiple_choice\",\n"
        "    \"question\": \"Które to języki programowania?\",\n"
        "    \"options\": [\"A) HTML\", \"B) Python\", \"C) JavaScript\", \"D) CSS\"],\n"
        "    \"correct_answer\": [\"B) Python\", \"C) JavaScript\"]\n"
        "  }\n"
        "]\n\n"
        f"NOTATKA:\n{note_content}\n\n"
        "Zwróć TYLKO surową tablicę JSON – BEZ komentarzy, markdown (```), opisów, tekstu wokół. Odpowiedź musi zaczynać się od [ i kończyć na ]."
    )

    response = chat.invoke([HumanMessage(content=prompt)])
    try:
        return json.loads(response.content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Niepoprawny JSON wygenerowany przez AI: {e}")
