# RowKey OS / Project Titan

Phase 1 MVP for a lightweight heavy equipment opportunity workspace.

## What is included

- FastAPI backend with a manual import endpoint and a simple equipment ROI scoring engine
- React-style single-page dashboard for reviewing equipment opportunities
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
CAT|320D|2018|6200|125000|Denver|3500|4500|145000|Serviced and ready to work
Komatsu|PC200|2016|9800|110000|Phoenix|2800|6000|128000|Hydraulic leak repaired
```

### Frontend startup

From the frontend folder, run:

```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173 in your browser.

### Option 2: Docker Compose

```bash
docker compose up --build
```

The backend will be available at http://localhost:8000 and the frontend can be opened at http://localhost:5173 when started with Vite.

## Scoring model

Each imported equipment record calculates:

- total_cost = price + estimated_transport_cost + estimated_repair_cost
- expected_profit = estimated_resale_value - total_cost
- roi_percent = expected_profit / total_cost * 100

Recommendation rules:

- BUY_NOW if ROI >= 25%
- NEGOTIATE if ROI >= 15% and ROI < 25%
- PASS if ROI < 15%

## Notes

- Data is stored locally in backend/app/data/listings.json.
- This Phase 1 implementation intentionally keeps the experience simple and manual.
