# RowKey OS / Project Titan

Phase 1 MVP for a lightweight property-listing intelligence workspace.

## What is included

- FastAPI backend with a manual import endpoint and a simple scoring engine
- React-style single-page dashboard served as a static HTML file
- Docker Compose setup for local development
- README and workspace-local data storage

## Run locally

### Option 1: Python only

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --only-binary=:all: -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This uses the lightweight FastAPI + Uvicorn + Pydantic stack without the `uvicorn[standard]` extra, so it avoids `httptools`, `watchfiles`, `orjson`, and `ujson` and stays compatible with Windows without Visual C++ Build Tools.

Then open http://localhost:8000/docs for API docs, and open the frontend file directly in a browser or serve it with a simple static server. For a quick test, use a file such as:

```text
Modern Loft | $2400 | 2 | 2 | 1100 | Downtown | Pet friendly and renovated
Cozy Studio | $1800 | 1 | 1 | 650 | Midtown | Parking available
```

### Option 2: Docker Compose

```bash
docker compose up --build
```

The backend will be available at http://localhost:8000 and the frontend can be opened from the static file at frontend/index.html.

## Notes

- Data is stored locally in backend/app/data/listings.json.
- This Phase 1 implementation intentionally keeps the experience simple and manual.
