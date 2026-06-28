from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine, inspect, text
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
    total_investment = Column(Float, nullable=True)
    estimated_gross_profit = Column(Float, nullable=True)
    net_profit = Column(Float, nullable=True)
    interest_cost = Column(Float, nullable=True)
    annualized_roi = Column(Float, nullable=True)
    expected_days_to_sell = Column(Integer, nullable=True)
    recommended_max_offer = Column(Float, nullable=True)
    overall_score = Column(Float, nullable=True)
    profit_potential = Column(Float, nullable=True)
    risk = Column(Float, nullable=True)
    repair_difficulty = Column(Float, nullable=True)
    ease_of_transport = Column(Float, nullable=True)
    comparable_low_value = Column(Float, nullable=True)
    comparable_average_value = Column(Float, nullable=True)
    comparable_high_value = Column(Float, nullable=True)
    desired_minimum_roi_percent = Column(Float, nullable=True)
    market_value_low = Column(Float, nullable=True)
    market_value_average = Column(Float, nullable=True)
    market_value_high = Column(Float, nullable=True)
    target_offer = Column(Float, nullable=True)
    max_offer = Column(Float, nullable=True)
    walk_away_price = Column(Float, nullable=True)
    resale_confidence = Column(String, nullable=True)
    negotiation_confidence = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def _ensure_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("equipment_deals"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("equipment_deals")}
    columns_to_add = {
        "total_investment": "FLOAT",
        "estimated_gross_profit": "FLOAT",
        "net_profit": "FLOAT",
        "interest_cost": "FLOAT",
        "annualized_roi": "FLOAT",
        "expected_days_to_sell": "INTEGER",
        "recommended_max_offer": "FLOAT",
        "overall_score": "FLOAT",
        "profit_potential": "FLOAT",
        "risk": "FLOAT",
        "repair_difficulty": "FLOAT",
        "ease_of_transport": "FLOAT",
        "comparable_low_value": "FLOAT",
        "comparable_average_value": "FLOAT",
        "comparable_high_value": "FLOAT",
        "desired_minimum_roi_percent": "FLOAT",
        "market_value_low": "FLOAT",
        "market_value_average": "FLOAT",
        "market_value_high": "FLOAT",
        "target_offer": "FLOAT",
        "max_offer": "FLOAT",
        "walk_away_price": "FLOAT",
        "resale_confidence": "TEXT",
        "negotiation_confidence": "INTEGER",
    }

    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            with engine.begin() as connection:
                connection.execute(text(f"ALTER TABLE equipment_deals ADD COLUMN {column_name} {column_type}"))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    _ensure_columns()


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
        "total_investment": deal.total_investment,
        "estimated_gross_profit": deal.estimated_gross_profit,
        "net_profit": deal.net_profit,
        "interest_cost": deal.interest_cost,
        "annualized_roi": deal.annualized_roi,
        "expected_days_to_sell": deal.expected_days_to_sell,
        "recommended_max_offer": deal.recommended_max_offer,
        "overall_score": deal.overall_score,
        "profit_potential": deal.profit_potential,
        "risk": deal.risk,
        "repair_difficulty": deal.repair_difficulty,
        "ease_of_transport": deal.ease_of_transport,
        "comparable_low_value": deal.comparable_low_value,
        "comparable_average_value": deal.comparable_average_value,
        "comparable_high_value": deal.comparable_high_value,
        "desired_minimum_roi_percent": deal.desired_minimum_roi_percent,
        "market_value_low": deal.market_value_low,
        "market_value_average": deal.market_value_average,
        "market_value_high": deal.market_value_high,
        "target_offer": deal.target_offer,
        "max_offer": deal.max_offer,
        "walk_away_price": deal.walk_away_price,
        "resale_confidence": deal.resale_confidence,
        "negotiation_confidence": deal.negotiation_confidence,
        "comparable_low": deal.comparable_low_value,
        "comparable_average": deal.comparable_average_value,
        "comparable_high": deal.comparable_high_value,
        "desired_min_roi": deal.desired_minimum_roi_percent,
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
        total_investment=payload.get("total_investment"),
        estimated_gross_profit=payload.get("estimated_gross_profit"),
        net_profit=payload.get("net_profit"),
        interest_cost=payload.get("interest_cost"),
        annualized_roi=payload.get("annualized_roi"),
        expected_days_to_sell=payload.get("expected_days_to_sell"),
        recommended_max_offer=payload.get("recommended_max_offer"),
        overall_score=payload.get("overall_score"),
        profit_potential=payload.get("profit_potential"),
        risk=payload.get("risk"),
        repair_difficulty=payload.get("repair_difficulty"),
        ease_of_transport=payload.get("ease_of_transport"),
        comparable_low_value=payload.get("comparable_low_value", payload.get("comparable_low")),
        comparable_average_value=payload.get("comparable_average_value", payload.get("comparable_average")),
        comparable_high_value=payload.get("comparable_high_value", payload.get("comparable_high")),
        desired_minimum_roi_percent=payload.get("desired_minimum_roi_percent", payload.get("desired_min_roi")),
        market_value_low=payload.get("market_value_low"),
        market_value_average=payload.get("market_value_average"),
        market_value_high=payload.get("market_value_high"),
        target_offer=payload.get("target_offer"),
        max_offer=payload.get("max_offer"),
        walk_away_price=payload.get("walk_away_price"),
        resale_confidence=payload.get("resale_confidence"),
        negotiation_confidence=payload.get("negotiation_confidence"),
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
