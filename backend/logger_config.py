import logging
from logging.handlers import RotatingFileHandler

def setup_logging(
    log_file: str = "logs/app.log",
    max_bytes: int = 5 * 1024 * 1024,  # 5 MB
    backup_count: int = 2,
    level: int = logging.INFO
):
    """
    Konfiguruje root logger i logger Uvicorn do zapisu do pliku rotującego.
    """
    # Handler z rotacją
    handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Unikaj duplikatów handlerów
    if not any(isinstance(h, RotatingFileHandler) and h.baseFilename.endswith(log_file)
               for h in root_logger.handlers):
        root_logger.addHandler(handler)

    # Przekieruj też logi Uvicorna
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(level)
    uvicorn_logger.handlers = [handler]
