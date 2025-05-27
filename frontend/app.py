import streamlit as st
import requests
from services.api import upload_file_to_backend, fetch_quiz

st.title("📄 GenAI: Generator Testów z Notatek")

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

uploaded_file = st.file_uploader("Wrzuć plik z notatkami (.pdf lub .txt)", type=["pdf", "txt"])

if uploaded_file is not None:
    if upload_file_to_backend(uploaded_file):
        st.success("✅ Plik został przesłany!")

        st.subheader("⚙️ Ustawienia testu")

        question_count = st.slider("Ilość pytań", min_value=1, max_value=20, value=5)
        type_short = st.checkbox("Pytania otwarte", value=True)
        type_mc = st.checkbox("Pytania wielokrotnego wyboru", value=True)
        type_blank = st.checkbox("Uzupełnianie zdań", value=True)

        selected_types = []
        if type_short:
            selected_types.append("short_answer")
        if type_mc:
            selected_types.append("multiple_choice")
        if type_blank:
            selected_types.append("fill_in_blank")

        if st.button("📥 Pobierz quiz"):
            quiz_data = fetch_quiz(question_count, selected_types)
            st.session_state.quiz_data = quiz_data

if st.session_state.quiz_data:
    st.subheader("📝 Wygenerowany test:")
    for i, q in enumerate(st.session_state.quiz_data):
        st.markdown(f"**{i+1}. {q['question']}**")

        if q["type"] == "multiple_choice":
            st.multiselect(
                f"Wybierz odpowiedź(i)",
                options=q["options"],
                key=f"mc_{i}"
            )
        elif q["type"] == "fill_in_blank":
            st.text_input("Uzupełnij lukę:", key=f"blank_{i}")
        elif q["type"] == "short_answer":
            st.text_area("Odpowiedź:", key=f"short_{i}")
        else:
            st.warning(f"Nieznany typ pytania: {q['type']}")

    st.button("✅ Sprawdź odpowiedzi")
