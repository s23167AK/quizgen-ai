import requests

def upload_file_to_backend(file):
    files = {'file': (file.name, file, file.type)}
    try:
        response = requests.post("http://localhost:8000/upload", files=files)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Błąd przy wysyłaniu pliku: {e}")
        return False

def fetch_quiz(question_count: int, question_types: list):
    try:
        params = {
            "question_count": question_count,
            "question_types": ",".join(question_types)
        }
        response = requests.get("http://localhost:8000/quiz", params=params)
        response.raise_for_status()
        return response.json().get("quiz", [])
    except Exception as e:
        st.error(f"Błąd przy pobieraniu quizu: {e}")
        return []