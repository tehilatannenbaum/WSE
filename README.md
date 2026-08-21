# WSE Flight Booking & Travel Assistant

A modern, responsive desktop travel assistant built with PySide6 and FastAPI, implementing CQRS, Event Sourcing, and RAG-based AI support with a local Ollama llama3.2:1b daemon.

---

## Getting Started (Windows PowerShell)

Follow these steps to set up and run the application on Windows.

### 1. Clone or Open the Repository
Open PowerShell and navigate to the project directory:
```powershell
cd "C:\Users\Tehila\OneDrive - Jerusalem College of Technology - Machon Lev\מכון טל\שנה ד\הנדסת מערכות חלונות\פרוייקט סיום"
```

### 2. Create a Virtual Environment
```powershell
python -m venv venv
```

### 3. Activate the Virtual Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Create Configuration Environment File
Copy the example environment template into `.env`:
```powershell
Copy-Item .env.example .env
```
For local execution, the default values in `.env` are pre-configured to run out-of-the-box using SQLite.

> [!WARNING]
> The default JWT secret is a placeholder (`replace-with-a-long-random-secret`). Before running the application in a production environment, ensure you rotate the secret manually in `.env` with a strong random string.

### 6. Run Database Migrations
Run the initial Alembic schema migrations to set up the SQLite database:
```powershell
alembic upgrade head
```

### 7. Run the FastAPI Backend Server
Start the backend server on port `8080` (expected by the PySide6 client):
```powershell
uvicorn backend.app.main:app --port 8080
```

### 8. Run PySide6 Frontend Client
In a new PowerShell window (make sure the virtual environment is activated):
```powershell
python frontend/main.py
```

### 9. Start Ollama Docker (AI Advisor Service)
To enable the AI Travel Advisor, start the Ollama container and pull the required model:
```powershell
# Start the container
docker compose up -d

# Pull the llama3.2:1b model
docker exec -it ollama ollama pull llama3.2:1b
```
To verify the container and model are installed correctly, run:
```powershell
# Verify container is running
docker ps --filter name=ollama

# List installed models
docker exec -it ollama ollama list
```
*Note: If Ollama is offline or unavailable, the AI Advisor will gracefully fall back to displaying the raw matched travel documents directly in the chat.*

### 10. Run Automated Tests
Execute the pytest suite to verify system correctness:
```powershell
pytest -v
```
To compile and check python files for syntax/compilation issues:
```powershell
python -m compileall backend frontend
```

---

## Project Structure
- `backend/`: FastAPI CQRS backend gateway, auth services, flight search, events-sourcing bookings service, and Ollama RAG client.
- `frontend/`: PySide6 application shell and modules (Auth, Search, Booking, Weather Details, Statistics, AI Advisor).
- `migrations/`: Alembic database version history.
- `tests/`: Automated unit and integration test suite.
