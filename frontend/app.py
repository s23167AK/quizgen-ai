import streamlit as st
import requests

st.title("📄 GenAI: Generator Testów z Notatek")

def upload_file_to_backend(file):
    files = {'file': (file.name, file, file.type)}
    try:
        response = requests.post("http://localhost:8000/upload", files=files)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Błąd przy wysyłaniu pliku: {e}")
        return False

def fetch_quiz(query: str, question_count: int):
    try:
        params = {"query": query, "question_count": question_count}
        response = requests.get("http://localhost:8000/quiz", params=params)
        response.raise_for_status()
        return response.json().get("quiz", "")
    except Exception as e:
        st.error(f"Błąd przy pobieraniu quizu: {e}")
        return None

uploaded_file = st.file_uploader("Wrzuć plik z notatkami (.pdf lub .txt)", type=["pdf", "txt"])

if uploaded_file is not None:
    if upload_file_to_backend(uploaded_file):
        st.success("✅ Plik został przesłany!")

        st.subheader("⚙️ Ustawienia testu")
        query = st.text_input("Temat quizu (np. Python, Biologia, Zbrodnia i kara):", "Zbrodnia i kara")
        question_count = st.slider("Ilość pytań", min_value=1, max_value=20, value=3)

        if st.button("📥 Pobierz quiz"):
            quiz_text = fetch_quiz(query, question_count)

            if quiz_text:
                st.subheader("📝 Wygenerowany test:")
                st.markdown(quiz_text)