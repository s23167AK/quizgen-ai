FROM python:3.11-slim AS builder
WORKDIR /app

# 1) Zainstaluj zależności (z rootowego requirements.txt lub własnego)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Finalny obraz
FROM python:3.11-slim
WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# kopiuj tylko kod backendu:
COPY backend/ ./backend/

EXPOSE 8000

# **TU jest klucz** – uruchamiamy uvicorn, nie streamlit
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
