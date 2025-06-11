from fastapi import FastAPI
from backend.routers import test, upload, quiz

app = FastAPI()

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(test.router, prefix="/test", tags=["Test"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
