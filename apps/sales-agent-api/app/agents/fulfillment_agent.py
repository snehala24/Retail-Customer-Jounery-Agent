# app/agents/fulfillment_agent.py
import logging
import datetime
import uuid
from app.services.db import SessionLocal
from app.models.order import Order
from app.models.fulfillment import Fulfillment

logger = logging.getLogger("fulfillment_agent")

def fulfill_order_sync(order_id: str, carrier: str = "Delhivery") -> dict:
    """
    Simulate order fulfillment: create a shipment record & mark order as shipped.
    """
    db = SessionLocal()
    try:
        # Step 1: Locate the order
        order = db.query(Order).filter(Order.external_id == order_id).one_or_none()
        if not order:
            return {"status": "error", "message": f"Order {order_id} not found"}

        # Step 2: Create a tracking ID and estimated delivery date
        tracking_id = "TRK-" + uuid.uuid4().hex[:8].upper()
        estimated_delivery = datetime.datetime.utcnow() + datetime.timedelta(days=3)

        # Step 3: Create Fulfillment record
        fulfillment = Fulfillment(
            order_id=order.id,
            carrier=carrier,
            tracking_id=tracking_id,
            status="shipped",
            estimated_delivery=estimated_delivery
        )
        db.add(fulfillment)

        # Step 4: Update order status
        order.status = "shipped"
        db.add(order)

        db.commit()
        db.refresh(fulfillment)
        db.refresh(order)

        logger.info(f"✅ Order {order_id} marked as shipped via {carrier}")

        return {
            "order_id": order.external_id,
            "status": order.status,
            "carrier": carrier,
            "tracking_id": tracking_id,
            "estimated_delivery": estimated_delivery.isoformat() + "Z",
            "db_update": "success"
        }

    except Exception as e:
        db.rollback()
        logger.exception(f"❌ Fulfillment failed for order {order_id}: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()
