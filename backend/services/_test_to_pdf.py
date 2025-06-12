from io import BytesIO
import pytest
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import logging

logger = logging.getLogger(__name__)

def test_to_PDF(quiz) -> bytes:
    logger.info("test_to_PDF called, quiz length=%d", len(quiz))
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
    logger.info("PDF generation complete, size=%d bytes", len(pdf))
    return pdf
