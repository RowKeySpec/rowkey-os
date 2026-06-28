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


fastapi_module.FastAPI = FastAPI
fastapi_module.HTTPException = HTTPException
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

from app.main import parse_manual_import


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
