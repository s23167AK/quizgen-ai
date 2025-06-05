from fastapi import FastAPI
from backend.routers import upload, quiz, evaluate

app = FastAPI()

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(evaluate.router, prefix="/evaluate", tags=["Evaluate"])
