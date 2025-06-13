FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fonts app/fonts

COPY . .

EXPOSE 8000

RUN ls

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
