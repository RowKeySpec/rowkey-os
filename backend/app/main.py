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


class ImportPayload(BaseModel):
    source: str


class Listing(BaseModel):
    title: str
    price: float | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    square_feet: int | None = None
    neighborhood: str | None = None
    notes: str | None = None
    score: float | None = None
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
        if len(parts) < 2:
            continue
        title = parts[0] or "Untitled"
        price_value = parts[1].replace("$", "").replace(",", "")
        try:
            price = float(price_value)
        except ValueError:
            price = None

        bedrooms = None
        bathrooms = None
        square_feet = None
        neighborhood = None
        notes = None

        if len(parts) > 2 and parts[2]:
            try:
                bedrooms = int(parts[2])
            except ValueError:
                pass
        if len(parts) > 3 and parts[3]:
            try:
                bathrooms = int(parts[3])
            except ValueError:
                pass
        if len(parts) > 4 and parts[4]:
            try:
                square_feet = int(parts[4])
            except ValueError:
                pass
        if len(parts) > 5 and parts[5]:
            neighborhood = parts[5]
        if len(parts) > 6 and parts[6]:
            notes = parts[6]

        score, reasons = score_listing(
            {
                "title": title,
                "price": price,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "square_feet": square_feet,
                "neighborhood": neighborhood,
                "notes": notes,
            }
        )
        parsed.append(
            {
                "title": title,
                "price": price,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "square_feet": square_feet,
                "neighborhood": neighborhood,
                "notes": notes,
                "score": round(score, 1),
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
    imported = parse_manual_import(payload.source)
    if not imported:
        raise HTTPException(status_code=400, detail="No listings were parsed from the supplied text.")

    current = load_listings()
    current.extend(imported)
    save_listings(current)
    return {"imported": len(imported), "total": len(current), "listings": current}


@app.delete("/api/listings")
def clear_listings() -> Dict[str, int]:
    save_listings([])
    return {"deleted": 0}


@app.get("/")
def index() -> Dict[str, str]:
    return {"message": "RowKey OS / Project Titan backend is running. Open the frontend at /frontend or use the API endpoints."}
