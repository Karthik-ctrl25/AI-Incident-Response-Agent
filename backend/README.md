# AI Incident Response Agent - Backend Service

FastAPI-powered backend for the **AI Incident Response Agent** (Hack With Bangalore 4.0).

This service receives server and application logs, queries long-term incident memory via **Hindsight Cloud**, generates diagnostic evidence and investigation recommendations using **Groq LLM**, and retains engineer-verified root causes and resolutions into memory.

---

## 1. Features

- **Log Analysis:** Fast, structured log diagnostics powered by Groq (`llama-3.3-70b-versatile`).
- **Semantic Incident Memory:** Long-term memory retrieval and retention with Hindsight Cloud.
- **Safety First:** AI suggestions are strictly marked as unverified suggestions.
- **Engineer Verification:** Only confirmed root causes and resolutions are retained into memory.
- **CORS Configured:** Out-of-the-box support for the React + Vite frontend (`http://localhost:5173`).
- **Interactive OpenAPI Documentation:** Available at `http://localhost:8000/docs`.

---

## 2. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check endpoint |
| `POST` | `/api/incidents/analyze` | Submit logs for Hindsight recall and Groq analysis |
| `POST` | `/api/incidents/{incident_id}/verify` | Confirm root cause & resolution; retains into Hindsight |
| `GET` | `/api/incidents/{incident_id}` | Retrieve incident analysis and verification status |

---

## 3. Environment Variables

Create a `.env` file inside `backend/` based on `.env.example`:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

# Groq LLM Configuration
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Hindsight Cloud Configuration
HINDSIGHT_API_KEY=hsk_your_hindsight_api_key_here
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_BANK_ID=incident-response-memory
```

> **Security Note:** Secrets and `.env` are ignored by Git (`backend/.gitignore`) and must never be committed.

---

## 4. Local Installation & Setup

1. **Install Dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run the Development Server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Or run from the repository root:
   ```bash
   python -m uvicorn app.main:app --app-dir backend --reload --port 8000
   ```

3. **Verify Health:**
   ```bash
   curl http://localhost:8000/
   ```
   Response:
   ```json
   {
     "status": "ok",
     "message": "Incident Response Backend is running"
   }
   ```

---

## 5. Running Tests

Automated tests mock external API calls to verify logic and failure recovery without requiring live credentials:

```bash
python -m pytest backend/tests/ -v
```
