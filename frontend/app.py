import streamlit as st
import requests
from services.api import upload_file_to_backend
from components.quiz_form import render_quiz_form
from components.progress_chart import show_donut_chart, show_progress_bar
from components.quiz_result import show_wrong_answers
from components.quiz_settings import select_quiz_settings, start_quiz
from components.learn_mode import run_learn_mode

API_URL = "http://backend:8000"

st.title("📄 GenAI: Generator Testów z Notatek")

# Inicjalizacja stanu
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

if "evaluation_result" not in st.session_state:
    st.session_state.evaluation_result = []

if "learn_data" not in st.session_state:
    st.session_state.learn_data = None

if "learn_mode" not in st.session_state:
    st.session_state.learn_mode = False

# Upload pliku
uploaded_file = st.file_uploader("📎 Wrzuć plik z notatkami (.pdf lub .txt)", type=["pdf", "txt"])

if uploaded_file:
    if upload_file_to_backend(uploaded_file):
        st.success("✅ Plik został przesłany!")

        mode, question_count, selected_types = select_quiz_settings()

        col1, col2 = st.columns([1, 1])

        if "quiz_pdf_bytes" not in st.session_state:
            st.session_state.quiz_pdf_bytes = None
        if "pdf_ready" not in st.session_state:
            st.session_state.pdf_ready = False
        if "pdf_generating" not in st.session_state:
            st.session_state.pdf_generating = False
        if "pdf_error" not in st.session_state:
            st.session_state.pdf_error = None

        with col1:
            if st.button("📥 Generuj quiz"):
                if mode == "Nauki":
                    with st.spinner("Generowanie quizu w trybie nauki..."):
                        start_quiz(mode, question_count, selected_types)
                else:
                    with st.spinner("Generowanie quizu..."):
                        start_quiz(mode, question_count, selected_types)

        with col2:
            if not st.session_state.pdf_ready and not st.session_state.pdf_generating:
                if st.button("📄 Wygeneruj PDF"):
                    st.session_state.pdf_generating = True
                    st.session_state.pdf_error = None
                    st.rerun()

            elif st.session_state.pdf_generating and not st.session_state.pdf_ready:
                with st.spinner("Generowanie PDF..."):
                    try:
                        response = requests.get(
                            f"{API_URL}/test/pdf",
                            params={
                                "question_count": question_count,
                                "question_types": ",".join(selected_types),
                            },
                            timeout=30
                        )
                        response.raise_for_status()
                        st.session_state.quiz_pdf_bytes = response.content
                        st.session_state.pdf_ready = True
                        st.session_state.pdf_generating = False
                        st.session_state.pdf_error = None
                        st.rerun()
                    except requests.exceptions.RequestException as e:
                        st.session_state.pdf_generating = False
                        st.session_state.pdf_error = str(e)
                        st.rerun()

            if st.session_state.pdf_ready and st.session_state.quiz_pdf_bytes:
                st.download_button(
                    label="⬇️ Pobierz quiz jako PDF",
                    data=st.session_state.quiz_pdf_bytes,
                    file_name="quiz.pdf",
                    mime="application/pdf"
                )
                st.success("✅ PDF gotowy do pobrania!")

            elif st.session_state.pdf_error:
                st.error(f"❌ Błąd pobierania PDF: {st.session_state.pdf_error}")

if st.session_state.learn_mode:
    run_learn_mode()

elif st.session_state.quiz_data and not st.session_state.evaluation_result:
    st.subheader("📝 Wypełnij test:")
    submitted, user_answers = render_quiz_form(st.session_state.quiz_data)

    if submitted:
        try:
            response = requests.post(f"{API_URL}/test/evaluate", json={"quiz": user_answers})
            result = response.json()["quiz"]
            st.session_state.evaluation_result = result
        except Exception as e:
            st.error(f"❌ Błąd oceny: {e}")

if st.session_state.evaluation_result:
    st.subheader("📊 Wyniki testu:")
    correct = sum(1 for q in st.session_state.evaluation_result if q["correct"])
    incorrect = len(st.session_state.evaluation_result) - correct

    show_progress_bar(correct, incorrect)
    show_donut_chart(correct, incorrect)
    show_wrong_answers(st.session_state.evaluation_result)

    st.markdown("### Co dalej?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔁 Rozwiąż ponownie ten sam quiz"):
            st.session_state.evaluation_result = []

    with col2:
        if st.button("🔙 Powrót do głównego menu"):
            st.session_state.quiz_data = []
            st.session_state.evaluation_result = []