import streamlit as st

def show_wrong_answers(evaluation_result):
    st.markdown("---")
    st.subheader("📘 Szczegóły błędnych odpowiedzi:")

    for q in evaluation_result:
        if not q["correct"]:
            user_ans = q.get("user_answer", "")
            correct_ans = q.get("correct_answer", "")

            if isinstance(user_ans, list):
                user_ans = ", ".join(user_ans)
            elif user_ans is None or str(user_ans).strip() == "":
                user_ans = "(brak odpowiedzi)"

            if isinstance(correct_ans, list):
                correct_ans = ", ".join(correct_ans)

            st.markdown(f"""
            **{q['question']}**  
            👉 Twoja odpowiedź: _{user_ans}_  
            ✅ Poprawna odpowiedź: _{correct_ans}_  
            """)
