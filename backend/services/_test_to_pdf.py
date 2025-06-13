from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('DejaVu', 'fonts/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold', 'fonts/DejaVuSans-Bold.ttf'))

def split_text_to_lines(text, font_name, font_size, max_width):
    """Dzieli tekst na linie mieszczące się w max_width."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = (current_line + " " + word).strip()
        if stringWidth(test_line, font_name, font_size) <= max_width or not current_line:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def test_to_PDF(quiz) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    MARGIN_TOP = 30 * mm
    MARGIN_BOTTOM = 20 * mm
    MARGIN_LEFT = 40
    MARGIN_RIGHT = 40
    LINE_HEIGHT = 20
    BLOCK_SPACING = 15

    y = height - MARGIN_TOP

    answer_list = []

    for idx, q in enumerate(quiz, 1):
        font_name = "DejaVuBold"
        font_size = 14
        max_line_width = width - MARGIN_LEFT - MARGIN_RIGHT
        question_lines = split_text_to_lines(
            f"{idx}. {q['question']}",
            font_name,
            font_size,
            max_line_width
        )
        q_lines = len(question_lines)
        question_height = q_lines * LINE_HEIGHT

        c.setFont(font_name, font_size)
        block_height = question_height

        c.setFont("DejaVu", 12)
        if q["type"] in ["short_answer", "fill_in_blank"]:
            block_height += 3 * LINE_HEIGHT
        elif q["type"] == "multiple_choice":
            block_height += len(q["options"]) * LINE_HEIGHT
        block_height += BLOCK_SPACING

        if y - block_height < MARGIN_BOTTOM:
            c.showPage()
            y = height - MARGIN_TOP

        c.setFont(font_name, font_size)
        for line in question_lines:
            c.drawString(MARGIN_LEFT, y, line)
            y -= LINE_HEIGHT

        c.setFont("DejaVu", 12)
        if q["type"] in ["short_answer", "fill_in_blank"]:
            for _ in range(3):
                c.line(MARGIN_LEFT + 10, y, width - MARGIN_RIGHT, y)
                y -= LINE_HEIGHT
        elif q["type"] == "multiple_choice":
            for opt in q["options"]:
                c.rect(MARGIN_LEFT + 10, y - 10, 10, 10)
                c.drawString(MARGIN_LEFT + 30, y - 10, opt)
                y -= LINE_HEIGHT

        y -= BLOCK_SPACING

        answer = ", ".join(q.get("correct_answer", []))
        answer_list.append(f"{idx}. {answer}")

    c.showPage()
    c.setFont("DejaVuBold", 16)
    c.drawString(MARGIN_LEFT, height - MARGIN_TOP, "Odpowiedzi")
    c.setFont("DejaVu", 9)
    y = height - MARGIN_TOP - 30
    for a in answer_list:
        c.drawString(MARGIN_LEFT + 10, y, a)
        y -= 12
        if y < MARGIN_BOTTOM:
            c.showPage()
            c.setFont("DejaVu", 9)
            y = height - MARGIN_TOP

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
