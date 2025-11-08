# app/agents/payment_agent.py
import logging
import datetime
import uuid
from typing import Dict, Any, Optional

from app.services.db import SessionLocal
from app.models.order import Order

logger = logging.getLogger("payment_agent")


def _find_order(db, order_identifier: Any) -> Optional[Order]:
    """Find an order by numeric id or external_id."""
    try:
        if isinstance(order_identifier, int) or (isinstance(order_identifier, str) and order_identifier.isdigit()):
            order = db.query(Order).filter(Order.id == int(order_identifier)).one_or_none()
            if order:
                return order
    except Exception:
        pass

    try:
        order = db.query(Order).filter(Order.external_id == str(order_identifier)).one_or_none()
        return order
    except Exception:
        return None


def authorize_payment_sync(order_id: str, amount: int, payment_method: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate payment authorization and update order in DB.
    """
    auth_code = "AUTH-" + uuid.uuid4().hex[:8].upper()
    ts = datetime.datetime.utcnow().isoformat() + "Z"

    result = {
        "status": "authorized",
        "auth_code": auth_code,
        "amount": amount,
        "currency": "INR",
        "timestamp": ts,
        "order_id": order_id,
    }

    try:
        db = SessionLocal()
    except Exception as e:
        logger.exception("Payment agent cannot acquire DB session: %s", e)
        result.update({"db_update": "skipped_or_failed", "db_error": str(e)})
        return result

    try:
        order = _find_order(db, order_id)
        if not order:
            logger.warning("⚠️ Order not found: %s", order_id)
            result.update({"db_update": "order_not_found"})
            return result

        # ✅ Update order fields
        order.payment_status = "PAID"
        order.status = "completed"

        db.add(order)
        db.commit()       # <— force actual DB commit
        db.refresh(order) # <— reload fresh data from DB

        logger.info(f"✅ Payment recorded for order {order.external_id}")

        result.update({
            "db_update": "success",
            "payment_status": order.payment_status,
            "status": order.status
        })
        return result

    except Exception as e:
        db.rollback()
        logger.exception("Payment agent DB update failed: %s", e)
        result.update({"db_update": "failed", "db_error": str(e)})
        return result

    finally:
        db.close()
