## Jak uruchomić backend 

### ✅ Wymagania
- Python 3.10 lub nowszy
- `pip`

### Klonowanie repozytorium
```bash
git clone https://github.com/twoj-uzytkownik/genai-quizmaker.git
cd genai-quizmaker
```

### Instalacja zależności
#### Windows (PowerShell lub CMD):

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
### macOS / Linux (bash, zsh):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Uruchomienie backendu

Z katalogu głównego:
```bash
uvicorn backend.main:app --reload
```
### Dokumentacja API (Swagger UI)
Po uruchomieniu przejdź do: http://localhost:8000/docs

Znajdziesz tam wszystkie dostępne endpointy:
- /upload – przesyłanie pliku z notatką
- /quiz – generowanie quizu
- /search – wyszukiwanie semantyczne z FAISS

### Zatrzymanie serwera
Wciśnij Ctrl + C w terminalu.


## Jak uruchomić frontend

Z katalogu frontend

```bash
streamlit run app.py
```

### Zatrzymanie frontu
Wciśnij Ctrl + C w terminalu.


## Jak odpalić testy
W głównym folderze projektu quizgen-ai nalezy odpalic:
```bash
pytest --verbose
```
## 🚀 Uruchamianie aplikacji z Docker Compose

### 📦 Wymagania wstępne

* Zainstalowany [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Skonfigurowany plik `.env` z kluczem OpenAI:

```
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Plik `.env` powinien znajdować się w głównym katalogu projektu (obok `docker-compose.yml`).

---

### ▶️ Uruchomienie aplikacji

Z katalogu głównego projektu, uruchom:

```bash
docker compose up --build
```

* Backend (FastAPI) będzie dostępny pod: [http://localhost:8000](http://localhost:8000)
* Frontend (Streamlit) będzie dostępny pod: [http://localhost:8501](http://localhost:8501)

---

### ⏹️ Zatrzymanie aplikacji

Aby zatrzymać uruchomione kontenery, naciśnij `Ctrl+C` w terminalu, a następnie:

```bash
docker compose down
```

To polecenie:

* zatrzyma i usunie kontenery
* nie usuwa obrazów ani danych

---

### 🔁 Restart po zmianach

Jeśli wprowadzisz zmiany w kodzie i chcesz je zobaczyć w kontenerze:

```bash
docker compose up --build
```

---
