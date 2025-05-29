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
        response = requests.get(f"{API_URL}/quiz", params=params)
    except Exception as e:
        st.error(f"Błąd przy pobieraniu quizu: {e}")
        return

    if not response.status_code == 200:
        st.error(f"Błąd przy wysyłaniu pliku: {response.json().get('detail') or 'Internal server error'}")
        return

    return response.json().get("quiz", [])