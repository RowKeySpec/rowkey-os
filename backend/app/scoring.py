from __future__ import annotations

from typing import Any, Dict, List, Tuple


def score_listing(listing: Dict[str, Any]) -> Tuple[float, List[str]]:
    score = 50.0
    reasons: List[str] = []

    title = (listing.get("title") or "").lower()
    notes = (listing.get("notes") or "").lower()
    neighborhood = (listing.get("neighborhood") or "").lower()

    if any(keyword in title for keyword in ["luxury", "renovated", "updated", "modern", "waterfront"]):
        score += 15
        reasons.append("Premium positioning")
    if any(keyword in notes for keyword in ["pet", "parking", "washer", "dryer", "gym", "pool"]):
        score += 8
        reasons.append("Convenience features")
    if any(keyword in neighborhood for keyword in ["downtown", "river", "midtown", "harbor", "west"]):
        score += 10
        reasons.append("High-demand neighborhood")

    price = listing.get("price")
    if price is not None:
        if price <= 2200:
            score += 8
            reasons.append("Competitive pricing")
        elif price >= 3600:
            score -= 8
            reasons.append("High price for the market")

    bedrooms = listing.get("bedrooms")
    if bedrooms is not None:
        if bedrooms >= 2:
            score += 6
            reasons.append("Two or more bedrooms")
        elif bedrooms == 1:
            score -= 3
            reasons.append("Studio-like footprint")

    bathrooms = listing.get("bathrooms")
    if bathrooms is not None:
        if bathrooms >= 2:
            score += 7
            reasons.append("Two or more baths")

    square_feet = listing.get("square_feet")
    if square_feet is not None:
        if square_feet >= 1000:
            score += 6
            reasons.append("Spacious layout")
        elif square_feet < 700:
            score -= 4
            reasons.append("Smaller footprint")

    if not title:
        score -= 5
        reasons.append("Title missing")

    return round(max(0.0, min(100.0, score)), 1), reasons
