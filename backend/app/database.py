from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "deals.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class EquipmentDeal(Base):
    __tablename__ = "equipment_deals"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    hours = Column(Integer, nullable=True)
    purchase_price = Column(Float, nullable=True)
    transport_cost = Column(Float, nullable=True)
    repair_cost = Column(Float, nullable=True)
    estimated_resale = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    roi = Column(Float, nullable=True)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_deal(deal: EquipmentDeal) -> Dict[str, Any]:
    return {
        "id": deal.id,
        "title": f"{deal.brand} {deal.model}".strip(),
        "brand": deal.brand,
        "model": deal.model,
        "year": deal.year,
        "hours": deal.hours,
        "price": deal.purchase_price,
        "location": deal.location,
        "estimated_transport_cost": deal.transport_cost,
        "estimated_repair_cost": deal.repair_cost,
        "estimated_resale_value": deal.estimated_resale,
        "notes": deal.notes,
        "roi_percent": deal.roi,
        "recommendation": deal.recommendation,
        "created_at": deal.created_at.isoformat() if deal.created_at else None,
    }


def save_deal(payload: Dict[str, Any]) -> EquipmentDeal:
    deal = EquipmentDeal(
        brand=payload.get("brand", "Unknown"),
        model=payload.get("model", "Unknown"),
        year=payload.get("year"),
        hours=payload.get("hours"),
        purchase_price=payload.get("purchase_price"),
        transport_cost=payload.get("transport_cost"),
        repair_cost=payload.get("repair_cost"),
        estimated_resale=payload.get("estimated_resale"),
        location=payload.get("location"),
        notes=payload.get("notes"),
        roi=payload.get("roi"),
        recommendation=payload.get("recommendation"),
    )
    db = SessionLocal()
    try:
        db.add(deal)
        db.commit()
        db.refresh(deal)
        return deal
    finally:
        db.close()


def list_deals() -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        deals = db.query(EquipmentDeal).order_by(EquipmentDeal.created_at.asc()).all()
        return [serialize_deal(deal) for deal in deals]
    finally:
        db.close()


def clear_deals() -> None:
    db = SessionLocal()
    try:
        db.query(EquipmentDeal).delete()
        db.commit()
    finally:
        db.close()
