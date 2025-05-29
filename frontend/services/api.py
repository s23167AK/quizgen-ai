import requests

API_URL = "http://backend:8000"

def upload_file_to_backend(file):
    files = {'file': (file.name, file, file.type)}
    try:
<<<<<<< Updated upstream
        response = requests.post("http://localhost:8000/upload", files=files)
        response.raise_for_status()
        return True
=======
        response = requests.post(f"{API_URL}/upload", files=files)
>>>>>>> Stashed changes
    except Exception as e:
        st.error(f"Błąd przy wysyłaniu pliku: {e}")
        return False

def fetch_quiz(question_count: int, question_types: list):
    try:
        params = {
            "question_count": question_count,
            "question_types": ",".join(question_types)
        }
<<<<<<< Updated upstream
        response = requests.get("http://localhost:8000/quiz", params=params)
        response.raise_for_status()
        return response.json().get("quiz", [])
=======
        response = requests.get(f"{API_URL}/quiz", params=params)
>>>>>>> Stashed changes
    except Exception as e:
        st.error(f"Błąd przy pobieraniu quizu: {e}")
        return []