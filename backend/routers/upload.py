from fastapi import APIRouter, UploadFile, File, HTTPException
from services.file_reader import read_file_content
from services.faiss_utils import embed_note_and_save_faiss
import logging
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    logger.info("Uploading file: %s", file.filename)
    ext = file.filename.split(".")[-1].lower()

    if ext not in ["txt", "pdf"]:
        raise HTTPException(status_code=400, detail="Dozwolone są tylko pliki .txt i .pdf")

    try:
        content = read_file_content(file)
    except Exception as e:
        logger.exception("Error reading file content")
        raise HTTPException(status_code=500, detail=f"Błąd podczas zapisu: {str(e)}")

    if not content:
        raise HTTPException(status_code=400, detail="Plik jest pusty lub nie zawiera czytelnego tekstu.")

    try:
        embed_note_and_save_faiss(content)
        logger.info("File %s indexed into FAISS", file.filename)
        return {"message": "Notatka została zindeksowana w FAISS."}
    except Exception as e:
        logger.exception("Error indexing FAISS")
        raise HTTPException(status_code=500, detail=f"Błąd podczas zapisu: {str(e)}")
