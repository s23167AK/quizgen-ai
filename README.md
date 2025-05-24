## Jak uruchomić backend 
### ✅ Wymagania
- Python 3.10 lub nowszy
- `pip`

### Klonowanie repozytorium

```bash
git clone https://github.com/twoj-uzytkownik/genai-quizmaker.git
cd genai-quizmaker

### Instalacja zależności
#### Windows (PowerShell lub CMD):

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

#### macOS / Linux (bash, zsh):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


### Uruchomienie backendu

Z katalogu głównego:
```bash
uvicorn backend.main:app --reload

### Dokumentacja API (Swagger UI)
Po uruchomieniu przejdź do:
```bash
http://localhost:8000/docs

Znajdziesz tam wszystkie dostępne endpointy:
- /upload – przesyłanie pliku z notatką
- /quiz – generowanie quizu
- /search – wyszukiwanie semantyczne z FAISS

###Zatrzymanie serwera
Wciśnij Ctrl + C w terminalu.