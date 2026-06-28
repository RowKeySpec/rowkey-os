from __future__ import annotations

from typing import Any, Dict, List, Tuple


PREFERRED_BRANDS = {"kubota", "takeuchi", "bobcat", "caterpillar", "john deere"}
TARGET_MARGIN = 0.20


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def analyze_deal(listing: Dict[str, Any]) -> Dict[str, float | int | str | None]:
    price = float(listing.get("price") or 0.0)
    transport = float(listing.get("estimated_transport_cost") or 0.0)
    repair = float(listing.get("estimated_repair_cost") or 0.0)
    resale = float(listing.get("estimated_resale_value") or 0.0)
    apr = float(listing.get("apr") or 0.0)

    total_investment = price + transport + repair
    estimated_gross_profit = resale - price
    net_profit = resale - total_investment
    roi_percent = (net_profit / total_investment * 100.0) if total_investment > 0 else 0.0

    year = listing.get("year")
    hours = listing.get("hours")
    brand = str(listing.get("brand") or "").strip().lower()
    preferred_brand = brand in PREFERRED_BRANDS

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
    if transport <= 2000:
        transport_score = 9.0
    elif transport <= 4000:
        transport_score = 7.0
    elif transport <= 8000:
        transport_score = 4.0
    else:
        transport_score = 2.0
    transport_score = _clamp(transport_score, 1.0, 10.0)

    profit_score = _clamp(roi_percent / 10.0, 1.0, 10.0)
    if roi_percent >= 20:
        profit_score = max(profit_score, 7.0)

    days_to_sell = 45
    if roi_percent >= 25:
        days_to_sell = 20
    elif roi_percent >= 15:
        days_to_sell = 30
    if preferred_brand:
        days_to_sell = max(7, days_to_sell - 7)
    if risk_score >= 8:
        days_to_sell += 10
    if repair_score <= 3:
        days_to_sell += 7
    if hours is not None and hours > 10000:
        days_to_sell += 5

    interest_cost = 0.0
    if price > 0 and apr > 0 and days_to_sell > 0:
        annual_interest = price * apr
        interest_cost = annual_interest * (days_to_sell / 365.0)

    annualized_roi = 0.0
    if total_investment > 0:
        annualized_roi = ((net_profit - interest_cost) / total_investment) * (365.0 / max(days_to_sell, 1)) * 100.0

    suggested_max_offer = max(0.0, (resale - repair - transport) * (1 - TARGET_MARGIN))

    overall_score = round(
        (profit_score * 0.5) + ((11 - risk_score) * 0.2) + (repair_score * 0.15) + (transport_score * 0.15),
        1,
    )
    overall_score = _clamp(overall_score, 1.0, 10.0)

    if roi_percent >= 25:
        recommendation = "BUY_NOW"
    elif roi_percent >= 15:
        recommendation = "NEGOTIATE"
    else:
        recommendation = "PASS"

    return {
        "total_investment": round(total_investment, 2),
        "estimated_gross_profit": round(estimated_gross_profit, 2),
        "net_profit": round(net_profit, 2),
        "roi_percent": round(roi_percent, 1),
        "interest_cost": round(interest_cost, 2),
        "annualized_roi": round(annualized_roi, 1),
        "expected_days_to_sell": int(days_to_sell),
        "recommended_max_offer": round(suggested_max_offer, 2),
        "overall_score": round(overall_score, 1),
        "profit_potential": round(profit_score, 1),
        "risk": round(risk_score, 1),
        "repair_difficulty": round(11 - repair_score, 1),
        "ease_of_transport": round(transport_score, 1),
        "recommendation": recommendation,
    }


def score_listing(listing: Dict[str, Any]) -> Tuple[float, List[str], str, Dict[str, float | None]]:
    analysis = analyze_deal(listing)
    reasons: List[str] = []
    if analysis["roi_percent"] >= 25:
        reasons.append("Strong resale upside")
    elif analysis["roi_percent"] >= 15:
        reasons.append("Solid margin for negotiation")
    else:
        reasons.append("Weak ROI profile")

    if listing.get("year") is not None and int(listing.get("year") or 0) >= 2018:
        reasons.append("Newer model year")
    if listing.get("hours") is not None and int(listing.get("hours") or 0) < 5000:
        reasons.append("Low usage hours")
    elif listing.get("hours") is not None and int(listing.get("hours") or 0) > 12000:
        reasons.append("High usage hours")

    if float(listing.get("estimated_transport_cost") or 0.0) <= 3000:
        reasons.append("Manageable transport cost")
    if float(listing.get("estimated_repair_cost") or 0.0) <= 5000:
        reasons.append("Repair budget is modest")
    if str(listing.get("brand") or "").strip().lower() in PREFERRED_BRANDS:
        reasons.append("Preferred brand")

    metrics = {
        "total_cost": analysis["total_investment"],
        "expected_profit": analysis["net_profit"],
        "roi_percent": analysis["roi_percent"],
        "overall_score": analysis["overall_score"],
        "profit_potential": analysis["profit_potential"],
        "risk": analysis["risk"],
        "repair_difficulty": analysis["repair_difficulty"],
        "ease_of_transport": analysis["ease_of_transport"],
        "expected_days_to_sell": analysis["expected_days_to_sell"],
        "recommendation": analysis["recommendation"],
        "interest_cost": analysis["interest_cost"],
        "annualized_roi": analysis["annualized_roi"],
        "recommended_max_offer": analysis["recommended_max_offer"],
    }
    return float(analysis["roi_percent"]), reasons, str(analysis["recommendation"]), metrics