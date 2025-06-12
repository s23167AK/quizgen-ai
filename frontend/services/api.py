import requests
import streamlit as st

API_URL = "http://backend:8000"

def upload_file_to_backend(file):
    files = {'file': (file.name, file, file.type)}
    try:
        response = requests.post(f"{API_URL}/upload", files=files)
    except Exception as e:
        st.error(f"Błąd przy wysyłaniu pliku: {e}")
        return False

    if not response.status_code == 200:
        st.error(f"Błąd przy wysyłaniu pliku: {response.json().get('detail') or 'Internal server error'}")
        return False

    return True

def fetch_quiz(question_count: int, question_types: list):
    try:
        params = {
            "question_count": question_count,
            "question_types": ",".join(question_types)
        }
        response = requests.get(f"{API_URL}/test", params=params)
    except Exception as e:
        st.error(f"Błąd przy pobieraniu quizu: {e}")
        return

    if not response.status_code == 200:
        st.error(f"Błąd przy pobieraniu quizu: {response.json().get('detail') or 'Internal server error'}")
        return

    return response.json().get("quiz", [])

def fetch_learn_quiz(question_count, selected_types):
    try:
        types_str = ",".join(selected_types)
        url = f"http://backend:8000/quiz/start?question_count={question_count}&question_types={types_str}"

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if "thread_id" not in data:
            raise ValueError("Brak thread_id w odpowiedzi z backendu")

        if "current_question" not in data:
            raise ValueError("Brak current_question w odpowiedzi z backendu")

        return data

    except requests.exceptions.Timeout:
        st.error("❌ Przekroczono limit czasu połączenia")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Błąd połączenia z backendem")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Błąd HTTP {e.response.status_code}: {e.response.text}")
        return None
    except ValueError as e:
        st.error(f"❌ Błąd danych: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Nieoczekiwany błąd: {e}")
        return None