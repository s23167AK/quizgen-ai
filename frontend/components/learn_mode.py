import streamlit as st
import requests

API_URL = "http://backend:8000"

def run_learn_mode():
    st.markdown("""
    <style>
    .stAlert, .stSuccess, .stError, .stWarning, .stInfo {
        width: 100% !important;
    }
    .stSpinner {
        width: 100% !important;
        text-align: center !important;
    }
    /* Wyśrodkowanie tekstu w spinnerze */
    .stSpinner > div {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-direction: row !important;
        gap: 10px !important;
    }
    .stSpinner > div > div:first-child {
        margin: 0 !important;
    }
    /* Wyśrodkowanie tekstu w przyciskach */
    .stButton > button {
        text-align: center !important;
        justify-content: center !important;
        display: flex !important;
        align-items: center !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📘 Tryb nauki")

    if "learn_data" not in st.session_state or not st.session_state.learn_data:
        st.warning("Brak danych do trybu nauki. Wygeneruj quiz.")
        if st.button("🔙 Powrót do głównego menu"):
            st.session_state.learn_mode = False
            st.rerun()
        return

    if "learn_thread_id" not in st.session_state:
        st.session_state.learn_thread_id = st.session_state.learn_data.get("thread_id")

    if "learn_current_question" not in st.session_state:
        current_q = st.session_state.learn_data.get("current_question")
        if not current_q:
            st.error("❌ Brak pytania w danych! Backend nie zwrócił current_question.")
            return
        st.session_state.learn_current_question = {
            "question": current_q.get("question"),
            "question_type": current_q.get("question_type", "short_answer"),
            "options": current_q.get("options")
        }

    if "learn_finished" not in st.session_state:
        st.session_state.learn_finished = False

    if "learn_summary" not in st.session_state:
        st.session_state.learn_summary = None


    if st.session_state.learn_current_question and not st.session_state.learn_finished:
        current_q = st.session_state.learn_current_question
        question_text = current_q.get("question", "Brak treści pytania")
        st.markdown(f"**Pytanie:** {question_text}")

        if current_q.get("options") and current_q.get("question_type") == "multiple_choice":
            st.markdown("**Opcje odpowiedzi:**")
            st.markdown(current_q["options"])

        user_input = st.text_input("Twoja odpowiedź:",
                                   key=f"learn_answer_{st.session_state.learn_thread_id}_{hash(question_text)}")

        col1, col2 = st.columns([2, 4])
        with col1:
            if st.button("✅ Wyślij odpowiedź"):
                if user_input.strip():
                    send_answer_to_backend(user_input.strip())
                else:
                    st.warning("⚠️ Wprowadź odpowiedź przed wysłaniem")
        with col2:
            if st.button("🚪 Zakończ quiz"):
                reset_learn_mode()
                st.session_state.learn_mode = False
                st.rerun()

    if "learn_feedback_result" in st.session_state:
        result = st.session_state.learn_feedback_result
        explanation = st.session_state.get("learn_feedback_explanation")

        if result == "Correct":
            st.success("✅ Poprawna odpowiedź!")
        elif result == "PartiallyCorrect":
            st.warning("🟡 Częściowo poprawna odpowiedź.")
        elif result == "InCorrect":
            st.error("❌ Niepoprawna odpowiedź.")

        if explanation:
            st.markdown("### 🧠 Wyjaśnienie:")
            st.info(explanation)

    if st.session_state.get("_show_next_button"):
        if st.button("➡️ Następne pytanie"):
            st.session_state.learn_current_question = st.session_state._next_learn_question
            del st.session_state._next_learn_question
            del st.session_state._show_next_button
            del st.session_state.learn_feedback_result
            del st.session_state.learn_feedback_explanation
            st.rerun()
        return
    if st.session_state.learn_finished:
        st.markdown("## 📊 Podsumowanie quizu")
        st.markdown(st.session_state.learn_summary or "Quiz zakończony.")

        if st.button("🔙 Powrót do głównego menu"):
            reset_learn_mode()
            st.session_state.learn_mode = False
            st.rerun()
        return

def send_answer_to_backend(user_answer):
    if not st.session_state.learn_thread_id:
        st.error("❌ Brak identyfikatora sesji")
        return

    payload = {
        "thread_id": st.session_state.learn_thread_id,
        "user_answer": user_answer
    }

    try:
        response = requests.post(f"{API_URL}/quiz/answer", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        previous_question = data.get("previous_question", {})
        result_obj = previous_question.get("question_result", {})
        result = result_obj.get("question_result") if isinstance(result_obj, dict) else None
        explanation = previous_question.get("explanation")

        st.session_state.learn_feedback_result = result
        st.session_state.learn_feedback_explanation = explanation

        if data.get("is_finished", False):
            st.session_state.learn_finished = True
            st.session_state.learn_current_question = None
            summary = data.get("summary")
            if isinstance(summary, dict):
                st.session_state.learn_summary = summary.get("text", "Quiz zakończony")
            else:
                st.session_state.learn_summary = summary or "Quiz zakończony"
        else:
            next_q = data.get("current_question")
            if next_q:
                st.session_state._next_learn_question = {
                    "question": next_q.get("question"),
                    "question_type": next_q.get("question_type", "short_answer"),
                    "options": next_q.get("options")
                }
                st.session_state._show_next_button = True
            


    except requests.exceptions.Timeout:
        st.error("❌ Przekroczono limit czasu - spróbuj ponownie")
    except requests.exceptions.ConnectionError:
        st.error("❌ Błąd połączenia z serwerem")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Błąd HTTP: {e.response.status_code}")
        st.write("Szczegóły:", e.response.text)
    except Exception as e:
        st.error(f"❌ Błąd podczas wysyłania odpowiedzi: {str(e)}")


def reset_learn_mode():
    keys_to_reset = [
        "learn_data",
        "learn_thread_id", 
        "learn_current_question",
        "learn_summary",
        "learn_finished",
        "learn_feedback_result",
        "learn_feedback_explanation",
        "learn_question_results",
        "learn_statistics"
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]