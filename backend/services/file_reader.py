from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
import logging
logger = logging.getLogger(__name__)

def read_file_content(file: UploadFile) -> str:
    logger.info("Reading file content: %s", file.filename)
    if file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    else:
        logger.error("Unsupported file format: %s", file.filename)
        raise HTTPException(status_code=400, detail="Nieobsługiwany format pliku.")
