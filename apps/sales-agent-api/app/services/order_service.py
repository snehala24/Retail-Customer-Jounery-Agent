# app/services/order_service.py
from sqlalchemy.orm import Session
from uuid import uuid4
from app.services.db import SessionLocal
from app.models.order import Order
from app.models.order_item import OrderItem

def create_order(customer_id: int | None, items: list[dict], total_amount: int) -> dict:
    """
    items: list of {sku, product_id, quantity, unit_price}
    """
    session: Session = SessionLocal()
    try:
        order = Order(order_ref=f"ORD-{uuid4().hex[:8]}", customer_id=customer_id, status="created", total_amount=total_amount)
        session.add(order)
        session.flush()  # get order.id
        for it in items:
            oi = OrderItem(order_id=order.id, product_id=it.get("product_id"), sku=it["sku"], quantity=it["quantity"], unit_price=it["unit_price"])
            session.add(oi)
        session.commit()
        return {"order_id": order.id, "order_ref": order.order_ref}
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
