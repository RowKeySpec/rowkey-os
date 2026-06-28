# RowKey OS / Project Titan

Phase 1 MVP for a lightweight heavy equipment opportunity workspace.

## What is included

- FastAPI backend with a manual import endpoint and a simple equipment ROI scoring engine
- React-style single-page dashboard for reviewing equipment opportunities
- AI listing import assistant for natural-language listing parsing
- Market Intelligence and Offer Strategy metrics on each deal card
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
python init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

This uses the lightweight FastAPI + Uvicorn + Pydantic stack without the `uvicorn[standard]` extra, so it avoids `httptools`, `watchfiles`, `orjson`, and `ujson` and stays compatible with Windows without Visual C++ Build Tools.

Then open http://localhost:8000/docs for API docs, and open the frontend file directly in a browser or serve it with a simple static server. For a quick test, use a file such as:

```text
CAT|320D|2018|6200|125000|Denver|3500|4500|145000|Serviced and ready to work
Komatsu|PC200|2016|9800|110000|Phoenix|2800|6000|128000|Hydraulic leak repaired
```

Optional market inputs can be appended after notes:

```text
brand|model|year|hours|purchasePrice|location|transportCost|repairCost|estimatedResaleValue|notes|comparableLowValue|comparableAverageValue|comparableHighValue|desiredMinimumRoiPercent
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

The backend now uses a dedicated Deal Intelligence Engine to evaluate each imported equipment deal.

It calculates:

- total_investment = purchase price + transport cost + repair cost
- estimated_gross_profit = estimated resale value - purchase price
- net_profit = estimated resale value - total investment
- roi_percent = net profit / total investment * 100
- interest_cost = financing cost based on purchase price, APR, and expected days to sell
- annualized_roi = adjusted return over a yearly basis
- expected_days_to_sell = driven by ROI, brand preference, risk, and repair burden
- recommended_max_offer = suggested ceiling for the purchase price based on margin targets
- overall_score, profit_potential, risk, repair_difficulty, and ease_of_transport

Market Intelligence and Offer Strategy also calculate:

- comparable_low_value, comparable_average_value, comparable_high_value
- desired_minimum_roi_percent
- market_value_low, market_value_average, market_value_high
- target_offer, max_offer, walk_away_price
- resale_confidence, negotiation_confidence

Offer strategy behavior:

- Comparable inputs are used when provided; otherwise market value falls back to estimated resale.
- Walk-away price applies the minimum ROI target after transport and repair costs.
- Target offer is intentionally below walk-away price to preserve room for negotiation.
- Confidence signals are based on market spread and ROI aggressiveness.

Business rules:

- Target minimum equipment margin: 20%
- Higher ROI improves profit potential
- Expensive repairs increase repair difficulty and lower the score
- Expensive transport lowers transport ease and the score
- Preferred brands receive a small boost: Kubota, Takeuchi, Bobcat, Caterpillar, John Deere
- Lower hours and newer equipment reduce risk
- Long expected sale times reduce the deal quality

Recommendation rules:

- BUY_NOW if ROI >= 25%
- NEGOTIATE if ROI >= 15% and ROI < 25%
- PASS if ROI < 15%

## Notes

- Deal data is now stored locally in SQLite at backend/app/data/deals.db.
- The database is created automatically on startup via the initialization step.
- You can export all stored deals as CSV from the dashboard or via GET /api/listings/export.csv.
- Market intelligence fields are persisted to SQLite and returned by GET /api/listings after reload.
- This Phase 1 implementation intentionally keeps the experience simple and manual.
