from fastapi import FastAPI
from routers import test, upload, quiz
from logger_config import setup_logging

setup_logging()
app = FastAPI()

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(test.router, prefix="/test", tags=["Test"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])


import logging
logging.getLogger().info("Starting FastAPI application…")