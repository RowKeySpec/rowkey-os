from __future__ import annotations

from typing import Any, Dict, List, Tuple


PREFERRED_BRANDS = {"kubota", "takeuchi", "bobcat", "caterpillar", "john deere"}


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def score_listing(listing: Dict[str, Any]) -> Tuple[float, List[str], str, Dict[str, float | None]]:
    price = listing.get("price")
    transport = listing.get("estimated_transport_cost")
    repair = listing.get("estimated_repair_cost")
    resale = listing.get("estimated_resale_value")

    total_cost = 0.0
    if price is not None:
        total_cost += float(price)
    if transport is not None:
        total_cost += float(transport)
    if repair is not None:
        total_cost += float(repair)

    expected_profit = 0.0
    if resale is not None:
        expected_profit = float(resale) - total_cost

    roi_percent = 0.0
    if total_cost > 0:
        roi_percent = (expected_profit / total_cost) * 100.0

    profit_score = _clamp(roi_percent / 10.0, 1.0, 10.0)

    year = listing.get("year")
    hours = listing.get("hours")
    risk_score = 6.0
    if year is not None:
        if year >= 2020:
            risk_score -= 2.0
        elif year >= 2018:
            risk_score -= 1.0
        elif year <= 2010:
            risk_score += 1.5
    if hours is not None:
        if hours <= 4000:
            risk_score -= 1.5
        elif hours <= 8000:
            risk_score -= 0.5
        elif hours >= 15000:
            risk_score += 2.0
    risk_score = _clamp(risk_score, 1.0, 10.0)

    repair_score = 10.0
    if repair is not None:
        if repair <= 2500:
            repair_score = 9.0
        elif repair <= 5000:
            repair_score = 7.0
        elif repair <= 10000:
            repair_score = 5.0
        else:
            repair_score = 2.0
    repair_score = _clamp(repair_score, 1.0, 10.0)

    transport_score = 10.0
    if transport is not None:
        if transport <= 2000:
            transport_score = 9.0
        elif transport <= 4000:
            transport_score = 7.0
        elif transport <= 8000:
            transport_score = 4.0
        else:
            transport_score = 2.0
    transport_score = _clamp(transport_score, 1.0, 10.0)

    brand = str(listing.get("brand") or "").strip().lower()
    preferred_brand_bonus = 1 if brand in PREFERRED_BRANDS else 0
    days_to_sell = 45
    if roi_percent >= 25:
        days_to_sell = 20
    elif roi_percent >= 15:
        days_to_sell = 30
    if preferred_brand_bonus:
        days_to_sell = max(7, days_to_sell - 7)
    if risk_score >= 8:
        days_to_sell += 10
    if repair_score <= 3:
        days_to_sell += 7

    overall_score = round((profit_score * 0.5) + ((11 - risk_score) * 0.2) + (repair_score * 0.15) + (transport_score * 0.15), 1)
    overall_score = _clamp(overall_score, 1.0, 10.0)

    reasons: List[str] = []
    if roi_percent >= 25:
        recommendation = "BUY_NOW"
        reasons.append("Strong resale upside")
    elif roi_percent >= 15:
        recommendation = "NEGOTIATE"
        reasons.append("Solid margin for negotiation")
    else:
        recommendation = "PASS"
        reasons.append("Weak ROI profile")

    year = listing.get("year")
    hours = listing.get("hours")
    if year is not None and year >= 2018:
        reasons.append("Newer model year")
    if hours is not None and hours < 5000:
        reasons.append("Low usage hours")
    elif hours is not None and hours > 12000:
        reasons.append("High usage hours")

    if transport is not None and transport <= 3000:
        reasons.append("Manageable transport cost")
    if repair is not None and repair <= 5000:
        reasons.append("Repair budget is modest")
    if preferred_brand_bonus:
        reasons.append("Preferred brand")

    metrics = {
        "total_cost": round(total_cost, 2),
        "expected_profit": round(expected_profit, 2),
        "roi_percent": round(roi_percent, 1),
        "overall_score": round(overall_score, 1),
        "profit_potential": round(profit_score, 1),
        "risk": round(risk_score, 1),
        "repair_difficulty": round(11 - repair_score, 1),
        "ease_of_transport": round(transport_score, 1),
        "expected_days_to_sell": int(days_to_sell),
        "recommendation": recommendation,
    }
    return round(roi_percent, 1), reasons, recommendation, metrics