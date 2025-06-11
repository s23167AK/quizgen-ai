# ---- build stage ----
FROM python:3.11-slim AS builder
WORKDIR /app

# Kopiujemy globalny requirements.txt z root projektu
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ---- runtime stage ----
FROM python:3.11-slim
WORKDIR /app/frontend

# Przenosimy zbudowane pakiety Pythona
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Kopiujemy kod frontendu
COPY frontend/ .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
