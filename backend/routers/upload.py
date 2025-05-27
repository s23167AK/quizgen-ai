from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.services.file_reader import read_file_content
from backend.services.faiss_utils import embed_note_and_save_faiss

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()

    if ext not in ["txt", "pdf"]:
        raise HTTPException(status_code=400, detail="Dozwolone są tylko pliki .txt i .pdf")

    try:
        content = read_file_content(file)

        if not content.strip():
            raise HTTPException(status_code=400, detail="Plik jest pusty lub nie zawiera czytelnego tekstu.")

        embed_note_and_save_faiss(content)

        return {"message": "Notatka została zindeksowana w FAISS."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas zapisu: {str(e)}")

