from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.scoring import score_listing

app = FastAPI(title="RowKey OS / Project Titan", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "listings.json"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
if not DATA_PATH.exists():
    DATA_PATH.write_text("[]", encoding="utf-8")


from typing import List

class ImportPayload(BaseModel):
    rows: List[str]


class Listing(BaseModel):
    title: str
    brand: str | None = None
    model: str | None = None
    year: int | None = None
    hours: int | None = None
    price: float | None = None
    location: str | None = None
    estimated_transport_cost: float | None = None
    estimated_repair_cost: float | None = None
    estimated_resale_value: float | None = None
    notes: str | None = None
    score: float | None = None
    recommendation: str | None = None
    total_cost: float | None = None
    expected_profit: float | None = None
    roi_percent: float | None = None
    reasons: List[str] | None = None


def load_listings() -> List[Dict[str, Any]]:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_listings(listings: List[Dict[str, Any]]) -> None:
    with DATA_PATH.open("w", encoding="utf-8") as handle:
        json.dump(listings, handle, indent=2)


def parse_manual_import(source: str) -> List[Dict[str, Any]]:
    parsed: List[Dict[str, Any]] = []
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 10:
            raise ValueError(
                f"Expected 10 pipe-delimited fields for equipment rows, received {len(parts)}: {line}"
            )

        brand = parts[0] or "Unknown"
        model = parts[1] or "Unknown"
        title = f"{brand} {model}".strip()

        def parse_float(text: str) -> float | None:
            value = text.replace("$", "").replace(",", "")
            try:
                return float(value)
            except ValueError:
                return None

        def parse_int(text: str) -> int | None:
            try:
                return int(text)
            except ValueError:
                return None

        year = parse_int(parts[2])
        hours = parse_int(parts[3])
        price = parse_float(parts[4])
        location = parts[5]
        transport = parse_float(parts[6])
        repair = parse_float(parts[7])
        resale = parse_float(parts[8])
        notes = parts[9]

        score, reasons, recommendation, metrics = score_listing(
            {
                "title": title,
                "brand": brand,
                "model": model,
                "year": year,
                "hours": hours,
                "price": price,
                "location": location,
                "estimated_transport_cost": transport,
                "estimated_repair_cost": repair,
                "estimated_resale_value": resale,
                "notes": notes,
            }
        )

        parsed.append(
            {
                "title": title,
                "brand": brand,
                "model": model,
                "year": year,
                "hours": hours,
                "price": price,
                "location": location,
                "estimated_transport_cost": transport,
                "estimated_repair_cost": repair,
                "estimated_resale_value": resale,
                "notes": notes,
                "score": round(score, 1),
                "recommendation": recommendation,
                "total_cost": metrics["total_cost"],
                "expected_profit": metrics["expected_profit"],
                "roi_percent": metrics["roi_percent"],
                "reasons": reasons,
            }
        )
    return parsed


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "rowkey-os"}


@app.get("/api/listings")
def get_listings() -> List[Dict[str, Any]]:
    return load_listings()


@app.post("/api/listings/import")
def import_listings(payload: ImportPayload) -> Dict[str, Any]:
    try:
        imported = parse_manual_import("\n".join(payload.rows))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not imported:
        raise HTTPException(
            status_code=400,
            detail="No equipment opportunities were parsed from the supplied text."
        )

    current = load_listings()
    current.extend(imported)
    save_listings(current)
    return {
        "imported": len(imported),
        "total": len(current),
        "listings": current,
    }
@app.delete("/api/listings")
def clear_listings() -> Dict[str, int]:
    save_listings([])
    return {"deleted": 0}


@app.get("/")
def index() -> Dict[str, str]:
    return {"message": "RowKey OS / Project Titan backend is running. Open the frontend to review equipment opportunities."}
