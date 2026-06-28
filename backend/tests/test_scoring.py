from app.scoring import analyze_deal


def test_analyze_deal_returns_structured_metrics():
    result = analyze_deal(
        {
            "brand": "Kubota",
            "model": "L3301",
            "year": 2020,
            "hours": 3000,
            "price": 100000,
            "estimated_transport_cost": 3000,
            "estimated_repair_cost": 2000,
            "estimated_resale_value": 140000,
            "location": "Denver",
            "notes": "Clean unit",
            "apr": 0.12,
        }
    )

    assert result["total_investment"] == 105000.0
    assert result["estimated_gross_profit"] == 35000.0
    assert result["roi_percent"] > 30.0
    assert result["overall_score"] >= 1
    assert result["profit_potential"] >= 1
    assert result["risk"] <= 10
    assert result["repair_difficulty"] >= 1
    assert result["ease_of_transport"] >= 1
    assert result["recommended_max_offer"] > 0
    assert result["recommendation"] in {"BUY_NOW", "NEGOTIATE", "PASS"}
