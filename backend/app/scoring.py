from __future__ import annotations

from typing import Any, Dict, List, Tuple


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

    metrics = {
        "total_cost": round(total_cost, 2),
        "expected_profit": round(expected_profit, 2),
        "roi_percent": round(roi_percent, 1),
    }
    return round(roi_percent, 1), reasons, recommendation, metrics
