from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def quiz_to_PDF(quiz) -> bytes:
    buffer = BytesIO()
    # Stwórz canvas do rysowania PDF
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Przykładowy tytuł pliku PDF
    c.setTitle("test")
    
    # Napis na stronie
    c.setFont("Helvetica", 20)
    c.drawString(100, height - 100, "Hello World!")

    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
