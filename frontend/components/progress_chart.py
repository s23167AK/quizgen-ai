import streamlit as st
from streamlit_echarts import st_echarts

def show_progress_bar(correct, incorrect):
    total = correct + incorrect
    percent = int((correct / total) * 100) if total else 0

    bar_html = f"""
    <div style="border: 1px solid #ccc; border-radius: 10px; overflow: hidden; height: 30px; margin-bottom: 50px;">
        <div style="width: {percent}%; background: #00cc96; height: 100%; float: left; text-align: center; color: white; font-weight: bold;">
             {correct}
        </div>
        <div style="width: {100 - percent}%; background: #ff4b4b; height: 100%; float: left; text-align: center; color: white; font-weight: bold;">
             {incorrect}
        </div>
    </div>
    """
    st.markdown(bar_html, unsafe_allow_html=True)


def show_donut_chart(correct, incorrect):
    options = {
        "title": {"text": "Wyniki quizu", "left": "center"},
        "tooltip": {"trigger": "item"},
        "legend": {"orient": "vertical", "left": "left"},
        "color": ["#4CAF50", "#F44336"], 
        "series": [
            {
                "name": "Wynik",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "label": {"show": False, "position": "center"},
                "emphasis": {
                    "label": {
                        "show": True,
                        "fontSize": 20,
                        "fontWeight": "bold"
                    }
                },
                "labelLine": {"show": False},
                "data": [
                    {"value": correct, "name": "Poprawne"},
                    {"value": incorrect, "name": "Błędne"}
                ]
            }
        ]
    }
    st_echarts(options=options, height="400px")