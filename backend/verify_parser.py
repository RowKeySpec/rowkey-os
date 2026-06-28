import sys
import types

fastapi = types.ModuleType('fastapi')

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

fastapi.FastAPI = FastAPI
fastapi.HTTPException = HTTPException
sys.modules['fastapi'] = fastapi

cors = types.ModuleType('fastapi.middleware')
cors.__path__ = []
sys.modules['fastapi.middleware'] = cors

cors_sub = types.ModuleType('fastapi.middleware.cors')
class CORSMiddleware:
    def __init__(self, *args, **kwargs):
        pass

cors_sub.CORSMiddleware = CORSMiddleware
sys.modules['fastapi.middleware.cors'] = cors_sub

pydantic = types.ModuleType('pydantic')
class BaseModel:
    def __init__(self, **data):
        self.__dict__.update(data)
pydantic.BaseModel = BaseModel
sys.modules['pydantic'] = pydantic

sys.path.insert(0, r'c:\Users\rocka\Documents\Codex\Project-Titan\backend')
from app.main import parse_manual_import

source = 'Kubota | SVL75 | 2022 | 1200 | 32000 | Gardendale, TX | 850 | 1500 | 43000 | Clean machine'
parsed = parse_manual_import(source)
print(parsed[0]['brand'], parsed[0]['model'], parsed[0]['year'], parsed[0]['hours'], parsed[0]['price'], parsed[0]['location'], parsed[0]['estimated_transport_cost'], parsed[0]['estimated_repair_cost'], parsed[0]['estimated_resale_value'], parsed[0]['notes'])
