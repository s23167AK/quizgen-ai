from fastapi import FastAPI
from backend.routers import upload, quiz
from backend.services.faiss_utils import search_in_faiss

app = FastAPI()

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])

@app.get("/search")
def search(query: str):
    results = search_in_faiss(query)
    return {"results": results}