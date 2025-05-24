from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader

def read_file_content(file: UploadFile) -> str:
    if file.filename.endswith(".txt"):
        return file.file.read().decode("utf-8")

    elif file.filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

    else:
        raise HTTPException(status_code=400, detail="Nieobsługiwany format pliku.")
