import streamlit as st
from services.api import fetch_quiz, fetch_learn_quiz

def select_quiz_settings():
    st.subheader("\U0001F3AF Wybierz tryb quizu")
    mode = st.radio("Tryb", ["Testowy", "Nauki"], horizontal=True)

    st.markdown("## ⚙️ Ustawienia quizu")

    question_count = st.slider("Ilość pytań", 1, 20, 5)
    type_short = st.checkbox("Pytania otwarte", value=True)
    type_mc = st.checkbox("Wielokrotny wybór", value=True)
    type_blank = st.checkbox("Uzupełnianie zdań", value=True)

    selected_types = []
    if type_short:
        selected_types.append("short_answer")
    if type_mc:
        selected_types.append("multiple_choice")
    if type_blank:
        selected_types.append("fill_in_blank")

    return mode, question_count, selected_types

def start_quiz(mode, question_count, selected_types):
    if not selected_types:
        st.warning("Wybierz przynajmniej jeden typ pytania.")
        return

    if mode == "Testowy":
        try:
            quiz_data = fetch_quiz(question_count, selected_types)
            if quiz_data:
                st.session_state.quiz_data = quiz_data
                st.session_state.evaluation_result = []
                st.session_state.quiz_submitted = False
                st.success("✅ Quiz testowy wygenerowany!")
                st.rerun()
            else:
                st.error("❌ Nie udało się pobrać danych quizu testowego")
        except Exception as e:
            st.error(f"❌ Błąd podczas pobierania quizu testowego: {e}")
            
    elif mode == "Nauki":
        try:
            with st.spinner("Generowanie quizu w trybie nauki..."):
                learn_data = fetch_learn_quiz(question_count, selected_types)
                
            st.write("🔍 Debug - otrzymane dane z backendu:", learn_data)
            
            if learn_data:
                if "thread_id" in learn_data:
                    st.session_state.learn_data = learn_data
                    st.session_state.learn_mode = True
                    st.success("✅ Quiz w trybie nauki wygenerowany!")
                    st.rerun()
                else:
                    st.error("❌ Brak thread_id w odpowiedzi z backendu")
                    st.write("🔍 Otrzymane dane:", learn_data)
            else:
                st.error("❌ Nie udało się pobrać danych quizu w trybie nauki")
                
        except Exception as e:
            st.error(f"❌ Błąd podczas pobierania quizu (tryb nauki): {e}")
            st.write("🔍 Szczegóły błędu:", str(e))