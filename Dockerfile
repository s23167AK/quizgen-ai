# Etap 1: Budowa środowiska z zależnościami
FROM python:3.11-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie plików do obrazu
COPY . .

# Instalacja zależności
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Otwarcie portów
EXPOSE 8501 8000

# Komenda startowa do uruchomienia backendu FastAPI oraz frontendowego Streamlita
CMD uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
