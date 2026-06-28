import sys
import types

fastapi_module = types.ModuleType("fastapi")


class FastAPI:
    def __init__(self, *args, **kwargs):
        pass

    def add_middleware(self, *args, **kwargs):
        return None

    def get(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def post(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def delete(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator


class HTTPException(Exception):
    def __init__(self, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class Response:
    def __init__(self, content=None, media_type=None):
        self.content = content
        self.media_type = media_type
        self.headers = {}


fastapi_module.FastAPI = FastAPI
fastapi_module.HTTPException = HTTPException
fastapi_module.Response = Response
sys.modules.setdefault("fastapi", fastapi_module)

cors_module = types.ModuleType("fastapi.middleware")
cors_module.__path__ = []
sys.modules.setdefault("fastapi.middleware", cors_module)

cors_submodule = types.ModuleType("fastapi.middleware.cors")


class CORSMiddleware:
    def __init__(self, *args, **kwargs):
        pass


cors_submodule.CORSMiddleware = CORSMiddleware
sys.modules.setdefault("fastapi.middleware.cors", cors_submodule)

pydantic_module = types.ModuleType("pydantic")


class BaseModel:
    def __init__(self, **data):
        self.__dict__.update(data)


pydantic_module.BaseModel = BaseModel
sys.modules.setdefault("pydantic", pydantic_module)

from app.database import clear_deals, list_deals, save_deal
from app.main import compute_market_intelligence, extract_listing_fields, parse_manual_import


def test_extract_listing_fields_parses_currency_values():
    examples = [
        ("Asking $32,000", 32000.0),
        ("Price: $32,000", 32000.0),
        ("$32,000 OBO", 32000.0),
        ("Selling for 32000", 32000.0),
        ("$145,000", 145000.0),
    ]

    for description, expected in examples:
        extracted = extract_listing_fields(description)
        assert extracted["purchasePrice"] == expected, description


def test_compute_market_intelligence_uses_comps_and_roi_targets():
    metrics = compute_market_intelligence(
        purchase_price=32000.0,
        transport_cost=1800.0,
        repair_cost=2200.0,
        estimated_resale_value=48000.0,
        comparable_low=45000.0,
        comparable_average=50000.0,
        comparable_high=55000.0,
        desired_min_roi=20.0,
    )

    assert metrics["market_value_low"] == 45000.0
    assert metrics["market_value_average"] == 50000.0
    assert metrics["market_value_high"] == 55000.0
    assert metrics["target_offer"] > 0
    assert metrics["max_offer"] > 0
    assert metrics["walk_away_price"] == metrics["max_offer"]
    assert metrics["resale_confidence"] in {"High", "Medium", "Low"}
    assert 0 <= metrics["negotiation_confidence"] <= 100


def test_parse_manual_import_accepts_optional_market_fields():
    source = "Kubota | SVL75 | 2022 | 1200 | 32000 | Gardendale, TX | 850 | 1500 | 43000 | Clean machine | 41000 | 45000 | 47000 | 15"
    parsed = parse_manual_import(source)

    assert len(parsed) == 1
    item = parsed[0]
    assert item["comparable_low_value"] == 41000.0
    assert item["comparable_average_value"] == 45000.0
    assert item["comparable_high_value"] == 47000.0
    assert item["market_value_low"] == 41000.0
    assert item["market_value_average"] == 45000.0
    assert item["market_value_high"] == 47000.0
    assert item["desired_minimum_roi_percent"] == 15.0
    assert item["desired_min_roi"] == 15.0


def test_parse_manual_import_accepts_equipment_row():
    source = "Kubota | SVL75 | 2022 | 1200 | 32000 | Gardendale, TX | 850 | 1500 | 43000 | Clean machine"
    parsed = parse_manual_import(source)

    assert len(parsed) == 1
    item = parsed[0]
    assert item["brand"] == "Kubota"
    assert item["model"] == "SVL75"
    assert item["year"] == 2022
    assert item["hours"] == 1200
    assert item["price"] == 32000.0
    assert item["location"] == "Gardendale, TX"
    assert item["estimated_transport_cost"] == 850.0
    assert item["estimated_repair_cost"] == 1500.0
    assert item["estimated_resale_value"] == 43000.0
    assert item["notes"] == "Clean machine"
    assert item["overall_score"] is not None
    assert item["profit_potential"] is not None
    assert item["risk"] is not None
    assert item["repair_difficulty"] is not None
    assert item["ease_of_transport"] is not None
    assert item["expected_days_to_sell"] is not None


def test_save_deal_persists_market_intelligence_metrics():
    clear_deals()
    save_deal(
        {
            "brand": "Kubota",
            "model": "SVL75",
            "purchase_price": 32000.0,
            "transport_cost": 1800.0,
            "repair_cost": 2200.0,
            "estimated_resale": 48000.0,
            "comparable_low_value": 45000.0,
            "comparable_average_value": 50000.0,
            "comparable_high_value": 55000.0,
            "desired_minimum_roi_percent": 20.0,
            "market_value_low": 45000.0,
            "market_value_average": 50000.0,
            "market_value_high": 55000.0,
            "target_offer": 42000.0,
            "max_offer": 45000.0,
            "walk_away_price": 40000.0,
            "resale_confidence": "High",
            "negotiation_confidence": 80,
        }
    )

    deals = list_deals()
    assert len(deals) == 1
    item = deals[0]
    assert item["comparable_low_value"] == 45000.0
    assert item["comparable_average_value"] == 50000.0
    assert item["comparable_high_value"] == 55000.0
    assert item["desired_minimum_roi_percent"] == 20.0
    assert item["market_value_low"] == 45000.0
    assert item["market_value_average"] == 50000.0
    assert item["market_value_high"] == 55000.0
    assert item["target_offer"] == 42000.0
    assert item["max_offer"] == 45000.0
    assert item["walk_away_price"] == 40000.0
    assert item["resale_confidence"] == "High"
    assert item["negotiation_confidence"] == 80
    assert item["desired_min_roi"] == 20.0
