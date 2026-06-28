from __future__ import annotations

import csv
import io
import re
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.database import clear_deals, init_db, list_deals, save_deal
from app.scoring import score_listing

app = FastAPI(title="RowKey OS / Project Titan", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


from typing import List

class ImportPayload(BaseModel):
    rows: List[str]


class ListingParsePayload(BaseModel):
    description: str


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


KNOWN_BRANDS = {
    "caterpillar": "Caterpillar",
    "cat": "Caterpillar",
    "kubota": "Kubota",
    "takeuchi": "Takeuchi",
    "bobcat": "Bobcat",
    "john deere": "John Deere",
    "johndeere": "John Deere",
    "deere": "John Deere",
    "komatsu": "Komatsu",
    "case": "Case",
    "new holland": "New Holland",
    "jcb": "JCB",
    "doosan": "Doosan",
    "hitachi": "Hitachi",
    "volvo": "Volvo",
}


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    cleaned = re.sub(r"[^0-9]", "", value)
    return int(cleaned) if cleaned else None


def _parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = value.replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_listing_fields(description: str) -> Dict[str, Any]:
    text = _normalize_text(description or "")
    if not text:
        return {
            "brand": None,
            "model": None,
            "year": None,
            "hours": None,
            "purchasePrice": None,
            "location": None,
            "notes": None,
            "analysis": None,
        }

    brand = None
    for key, candidate in KNOWN_BRANDS.items():
        if re.search(rf"\b{re.escape(key)}\b", text, re.IGNORECASE):
            brand = candidate
            break

    model = None
    if brand:
        match = re.search(rf"{re.escape(brand)}\s+([A-Za-z0-9\-/]+)", text, re.IGNORECASE)
        if match:
            model = match.group(1).strip(" ,;:-")
    if not model:
        model_match = re.search(r"(?:model|mdl)\s*[:#-]?\s*([A-Za-z0-9\-/]+)", text, re.IGNORECASE)
        if model_match:
            model = model_match.group(1).strip(" ,;:-")

    year = None
    year_match = re.search(r"\b((19|20)\d{2})\b", text)
    if year_match:
        year = int(year_match.group(1))

    hours = None
    hours_match = re.search(r"\b(\d{1,3}(?:,\d{3})*|\d+)\s*(?:hrs?|hours?|operating hours?|hour meter)\b", text, re.IGNORECASE)
    if hours_match:
        hours = _parse_int(hours_match.group(1))

    purchase_price = None
    price_keyword_pattern = re.compile(
        r"(?:price|asking|listed|cash price|sale price|buy now)\s*(?:is|:|=|-)?\s*\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)",
        re.IGNORECASE,
    )
    price_keyword_match = price_keyword_pattern.search(text)
    if price_keyword_match:
        purchase_price = _parse_float(price_keyword_match.group(1))
    else:
        currency_matches = re.findall(r"\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?)", text)
        if len(currency_matches) == 1:
            purchase_price = _parse_float(currency_matches[0])

    location = None
    location_match = re.search(r"(?:location|located|city)\s*(?:in|:)?\s*([A-Za-z0-9 .,'-]+)", text, re.IGNORECASE)
    if location_match:
        location = location_match.group(1).strip(" ,;:-")

    notes = None
    if text:
        notes = text[:1000]

    analysis = None
    parsed_listing = {
        "brand": brand,
        "model": model,
        "year": year,
        "hours": hours,
        "price": purchase_price,
        "location": location,
        "estimated_transport_cost": None,
        "estimated_repair_cost": None,
        "estimated_resale_value": None,
        "notes": notes,
    }
    if brand or model or year or hours or purchase_price or location or notes:
        analysis = score_listing(parsed_listing)[3]

    return {
        "brand": brand,
        "model": model,
        "year": year,
        "hours": hours,
        "purchasePrice": purchase_price,
        "location": location,
        "notes": notes,
        "analysis": analysis,
    }


def load_listings() -> List[Dict[str, Any]]:
    return list_deals()


def save_listings(listings: List[Dict[str, Any]]) -> None:
    clear_deals()
    for listing in listings:
        save_deal(
            {
                "brand": listing.get("brand", "Unknown"),
                "model": listing.get("model", "Unknown"),
                "year": listing.get("year"),
                "hours": listing.get("hours"),
                "purchase_price": listing.get("price"),
                "transport_cost": listing.get("estimated_transport_cost"),
                "repair_cost": listing.get("estimated_repair_cost"),
                "estimated_resale": listing.get("estimated_resale_value"),
                "location": listing.get("location"),
                "notes": listing.get("notes"),
                "roi": listing.get("roi_percent"),
                "recommendation": listing.get("recommendation"),
                "total_investment": listing.get("total_investment"),
                "estimated_gross_profit": listing.get("estimated_gross_profit"),
                "net_profit": listing.get("net_profit"),
                "interest_cost": listing.get("interest_cost"),
                "annualized_roi": listing.get("annualized_roi"),
                "expected_days_to_sell": listing.get("expected_days_to_sell"),
                "recommended_max_offer": listing.get("recommended_max_offer"),
                "overall_score": listing.get("overall_score"),
                "profit_potential": listing.get("profit_potential"),
                "risk": listing.get("risk"),
                "repair_difficulty": listing.get("repair_difficulty"),
                "ease_of_transport": listing.get("ease_of_transport"),
            }
        )


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
                "total_investment": metrics["total_cost"],
                "estimated_gross_profit": metrics["estimated_gross_profit"] if "estimated_gross_profit" in metrics else None,
                "net_profit": metrics["expected_profit"],
                "interest_cost": metrics["interest_cost"],
                "annualized_roi": metrics["annualized_roi"],
                "expected_days_to_sell": metrics["expected_days_to_sell"],
                "recommended_max_offer": metrics["recommended_max_offer"],
                "overall_score": metrics["overall_score"],
                "profit_potential": metrics["profit_potential"],
                "risk": metrics["risk"],
                "repair_difficulty": metrics["repair_difficulty"],
                "ease_of_transport": metrics["ease_of_transport"],
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


@app.post("/api/listings/parse")
def parse_listing_description(payload: ListingParsePayload) -> Dict[str, Any]:
    extracted = extract_listing_fields(payload.description)
    return {
        "extracted": extracted,
        "ready": True,
    }


@app.get("/api/listings/export.csv")
def export_listings_csv() -> Any:
    deals = load_listings()
    fieldnames = [
        "brand",
        "model",
        "year",
        "hours",
        "purchase_price",
        "transport_cost",
        "repair_cost",
        "estimated_resale",
        "roi",
        "recommendation",
        "location",
        "notes",
        "created_at",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for deal in deals:
        writer.writerow(
            {
                "brand": deal.get("brand", ""),
                "model": deal.get("model", ""),
                "year": deal.get("year", ""),
                "hours": deal.get("hours", ""),
                "purchase_price": deal.get("price", ""),
                "transport_cost": deal.get("estimated_transport_cost", ""),
                "repair_cost": deal.get("estimated_repair_cost", ""),
                "estimated_resale": deal.get("estimated_resale_value", ""),
                "roi": deal.get("roi_percent", ""),
                "recommendation": deal.get("recommendation", ""),
                "location": deal.get("location", ""),
                "notes": deal.get("notes", ""),
                "created_at": deal.get("created_at", ""),
            }
        )
    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=equipment_deals.csv"
    return response


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

    for listing in imported:
        save_deal(
            {
                "brand": listing.get("brand", "Unknown"),
                "model": listing.get("model", "Unknown"),
                "year": listing.get("year"),
                "hours": listing.get("hours"),
                "purchase_price": listing.get("price"),
                "transport_cost": listing.get("estimated_transport_cost"),
                "repair_cost": listing.get("estimated_repair_cost"),
                "estimated_resale": listing.get("estimated_resale_value"),
                "location": listing.get("location"),
                "notes": listing.get("notes"),
                "roi": listing.get("roi_percent"),
                "recommendation": listing.get("recommendation"),
                "total_investment": listing.get("total_investment"),
                "estimated_gross_profit": listing.get("estimated_gross_profit"),
                "net_profit": listing.get("net_profit"),
                "interest_cost": listing.get("interest_cost"),
                "annualized_roi": listing.get("annualized_roi"),
                "expected_days_to_sell": listing.get("expected_days_to_sell"),
                "recommended_max_offer": listing.get("recommended_max_offer"),
                "overall_score": listing.get("overall_score"),
                "profit_potential": listing.get("profit_potential"),
                "risk": listing.get("risk"),
                "repair_difficulty": listing.get("repair_difficulty"),
                "ease_of_transport": listing.get("ease_of_transport"),
            }
        )

    current = load_listings()
    return {
        "imported": len(imported),
        "total": len(current),
        "listings": current,
    }
@app.delete("/api/listings")
def clear_listings() -> Dict[str, int]:
    clear_deals()
    return {"deleted": 0}


@app.get("/")
def index() -> Dict[str, str]:
    return {"message": "RowKey OS / Project Titan backend is running. Open the frontend to review equipment opportunities."}
