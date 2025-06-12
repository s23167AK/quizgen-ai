import streamlit as st
import requests

API_URL = "http://backend:8000"

def run_learn_mode():
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
        question_data = st.session_state.learn_data.get("question")
        if question_data is None:
            st.error("❌ Brak pytania w danych! Backend nie zwrócił pytania.")
            st.write("🔍 Debug - learn_data:", st.session_state.learn_data)
            return
        if isinstance(question_data, tuple) and len(question_data) > 0:
            if hasattr(question_data[0], 'question'):
                st.session_state.learn_current_question = {
                    'question': question_data[0].question,
                    'question_type': getattr(question_data[0], 'question_type', 'short_answer'),
                    'options': getattr(question_data[0], 'options', None)
                }
            elif isinstance(question_data[0], dict):
                st.session_state.learn_current_question = question_data[0]
            else:
                st.error("❌ Niepoprawny format pytania z backendu")
                return
        elif isinstance(question_data, dict):
            st.session_state.learn_current_question = question_data
        elif hasattr(question_data, 'question'):
            st.session_state.learn_current_question = {
                'question': question_data.question,
                'question_type': getattr(question_data, 'question_type', 'short_answer'),
                'options': getattr(question_data, 'options', None)
            }
        else:
            st.error("❌ Niepoprawny format danych pytania")
            st.write("🔍 Debug - otrzymane dane:", question_data)
            return

    if "learn_finished" not in st.session_state:
        st.session_state.learn_finished = False

    if "learn_summary" not in st.session_state:
        st.session_state.learn_summary = None

    with st.expander("🔍 Debug Info (kliknij aby rozwinąć)"):
        st.write("**Raw learn_data:**", st.session_state.learn_data)
        st.write("**Parsed current_question:**", st.session_state.learn_current_question)
        st.write("**Thread ID:**", st.session_state.learn_thread_id)
        st.write("**Finished:**", st.session_state.learn_finished)

    if st.session_state.learn_finished and st.session_state.learn_summary:
        st.success("🎉 Tryb nauki zakończony!")
        st.markdown("### 📋 Podsumowanie:")
        
        summary_text = st.session_state.learn_summary
        if isinstance(summary_text, dict):
            summary_text = summary_text.get("text", "Brak podsumowania")
        
        st.markdown(summary_text)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔁 Zacznij od nowa"):
                reset_learn_mode()
                st.rerun()
        with col2:
            if st.button("🔙 Powrót do głównego menu"):
                reset_learn_mode()
                st.session_state.learn_mode = False
                st.rerun()
        return

    if st.session_state.learn_current_question and not st.session_state.learn_finished:
        current_q = st.session_state.learn_current_question
        
        question_text = current_q.get('question', 'Brak treści pytania')
        st.markdown(f"**Pytanie:** {question_text}")
        
        if current_q.get('options') and current_q.get('question_type') == 'multiple_choice':
            st.markdown("**Opcje odpowiedzi:**")
            st.markdown(current_q['options'])
        
        user_input = st.text_input(
            "Twoja odpowiedź:", 
            key=f"learn_answer_{st.session_state.learn_thread_id}_{hash(question_text)}"
        )
        
        col1, col2 = st.columns([1, 4])
        
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

def send_answer_to_backend(user_answer):
    """Wysyła odpowiedź do backendu i obsługuje response"""
    if not st.session_state.learn_thread_id:
        st.error("❌ Brak identyfikatora sesji")
        return
    
    payload = {
        "thread_id": st.session_state.learn_thread_id,
        "user_answer": user_answer
    }
    
    try:
        with st.spinner("Wysyłanie odpowiedzi..."):
            response = requests.post(f"{API_URL}/quiz/answer", json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        
        if data.get("question") is None or data.get("finished", False):
            st.session_state.learn_finished = True
            st.session_state.learn_current_question = None
            st.session_state.learn_summary = data.get("summary", {}).get("text", "Quiz zakończony")
            st.success("✅ Odpowiedź wysłana! Quiz zakończony.")
        else:
            next_question = data.get("question")
            
            if isinstance(next_question, tuple) and len(next_question) > 0:
                if hasattr(next_question[0], 'question'):
                    st.session_state.learn_current_question = {
                        'question': next_question[0].question,
                        'question_type': getattr(next_question[0], 'question_type', 'short_answer'),
                        'options': getattr(next_question[0], 'options', None)
                    }
                elif isinstance(next_question[0], dict):
                    st.session_state.learn_current_question = next_question[0]
            elif isinstance(next_question, dict):
                st.session_state.learn_current_question = next_question
            elif hasattr(next_question, 'question'):
                st.session_state.learn_current_question = {
                    'question': next_question.question,
                    'question_type': getattr(next_question, 'question_type', 'short_answer'),
                    'options': getattr(next_question, 'options', None)
                }
            
            st.success("✅ Odpowiedź wysłana! Następne pytanie:")
        
        st.rerun()
        
    except requests.exceptions.Timeout:
        st.error("❌ Przekroczono limit czasu - spróbuj ponownie")
    except requests.exceptions.ConnectionError:
        st.error("❌ Błąd połączenia z serwerem")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ Błąd HTTP: {e.response.status_code}")
        st.write("Szczegóły:", e.response.text)
    except Exception as e:
        st.error(f"❌ Błąd podczas wysyłania odpowiedzi: {str(e)}")
        # Debug info
        st.write("🔍 Debug - payload:", payload)
        if 'response' in locals():
            st.write("🔍 Debug - response:", response.text)

def reset_learn_mode():
    """Resetuje stan trybu nauki"""
    keys_to_reset = [
        "learn_data", 
        "learn_thread_id", 
        "learn_current_question", 
        "learn_summary",
        "learn_finished"
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]