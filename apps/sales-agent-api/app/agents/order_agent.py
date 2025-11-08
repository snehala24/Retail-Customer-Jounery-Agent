# app/agents/order_agent.py
import logging
from datetime import datetime
from app.services.db import SessionLocal

logger = logging.getLogger("order_agent")

def create_order_sync(customer_id: str, items: list, total_amount: int, external_id: str | None = None) -> dict:
    """
    Very small synchronous order creator:
    - Tries to import Order model and insert a row; otherwise returns a mock order.
    """
    order_info = {
        "order_id": external_id or f"ORD-{uuid_format()}",
        "customer_id": customer_id,
        "items": items,
        "total_amount": total_amount,
        "status": "created",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    try:
        from app.models.order import Order  # type: ignore
        from app.models.order_item import OrderItem  # optional
        session = SessionLocal()
        try:
            order = Order(
                external_id=order_info["order_id"],
                customer_id=customer_id,
                total_amount=total_amount,
                status="created",
            )
            session.add(order)
            session.commit()
            session.refresh(order)
            order_info["db_id"] = order.id
            order_info["status"] = order.status
        finally:
            session.close()
    except Exception as e:
        logger.info("Order DB insert skipped/failed: %s", e)
        order_info["db_error"] = str(e)

    return order_info

def uuid_format():
    import uuid
    return uuid.uuid4().hex[:8].upper()
