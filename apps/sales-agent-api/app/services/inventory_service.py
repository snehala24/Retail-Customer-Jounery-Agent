# app/services/inventory_service.py
from sqlalchemy.orm import Session
from app.services.db import SessionLocal
from app.models.inventory import Inventory

def get_stock_by_sku(product_id: int):
    session: Session = SessionLocal()
    try:
        rows = session.query(Inventory).filter(Inventory.product_id == product_id).all()
        return [{"store_id": r.store_id, "qty": r.quantity} for r in rows]
    finally:
        session.close()

def adjust_stock(product_id: int, store_id: str, delta: int) -> bool:
    session: Session = SessionLocal()
    try:
        inv = session.query(Inventory).filter_by(product_id=product_id, store_id=store_id).first()
        if not inv:
            return False
        inv.quantity += delta
        session.commit()
        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
