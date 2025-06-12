import streamlit as st

def render_quiz_form(quiz_data):
    with st.form("quiz_form"):
        user_answers = []
        for i, q in enumerate(quiz_data):
            st.markdown(f"**{i+1}. {q['question']}**")

            answer = None
            if q["type"] == "multiple_choice":
                answer = st.multiselect("Wybierz odpowiedź(i)", q["options"], key=f"mc_{i}")
            elif q["type"] == "fill_in_blank":
                answer = st.text_input("Uzupełnij lukę:", key=f"blank_{i}")
            elif q["type"] == "short_answer":
                answer = st.text_area("Odpowiedź:", key=f"short_{i}")
            else:
                st.warning(f"Nieznany typ pytania: {q['type']}")

            user_answers.append({
                **q,
                "user_answer": answer
            })

        submitted = st.form_submit_button("✅ Sprawdź odpowiedzi")
        return submitted, user_answers