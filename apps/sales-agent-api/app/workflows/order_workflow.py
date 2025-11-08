# app/workflows/order_workflow.py
from datetime import datetime
import logging
from sqlalchemy import text

from app.agents.payment_agent import authorize_payment_sync
from app.agents.fulfillment_agent import fulfill_order_sync
from app.agents.loyalty_agent import add_loyalty_points_sync
from app.services.db import get_db_session

logger = logging.getLogger(__name__)


def process_order_sync(order_id: str, customer_id: int, total_amount: int, payment_method: dict):
    """
    Unified post-purchase workflow (synchronous helper):
      1. Capture / authorize payment
      2. Submit fulfillment
      3. Award loyalty points
      4. Mark order completed in DB

    Returns a dict with details or {"status": "error", "message": "..."} on failure.
    """
    db = get_db_session()
    try:
        logger.info(f"🚀 Starting full workflow for order {order_id}")

        # 1️⃣ Payment
        payment = authorize_payment_sync(order_id=order_id, amount=total_amount, payment_method=payment_method)
        logger.info(f"payment result: {payment}")
        if payment.get("status") not in ("authorized", "completed"):
            raise RuntimeError(f"Payment not successful: {payment}")

        # 2️⃣ Fulfillment
        fulfillment = fulfill_order_sync(order_id=order_id)
        logger.info(f"fulfillment result: {fulfillment}")
        if fulfillment.get("db_update") != "success":
            raise RuntimeError(f"Fulfillment failed: {fulfillment}")

        # 3️⃣ Loyalty
        loyalty = add_loyalty_points_sync(customer_id=customer_id, order_total=total_amount)
        logger.info(f"loyalty result: {loyalty}")
        if loyalty.get("db_update") != "success":
            raise RuntimeError(f"Loyalty update failed: {loyalty}")

        # 4️⃣ Update order status in DB
        # NOTE: remove trailing commas — Postgres errors if SET list ends with a comma.
        update_sql = text(
            """
            UPDATE orders
               SET status = :status,
                   payment_status = :payment_status,
                   created_at = COALESCE(created_at, NOW())
             WHERE external_id = :external_id
            """
        )
        db.execute(update_sql, {"status": "completed", "payment_status": "PAID", "external_id": order_id})
        db.commit()

        logger.info(f"✅ Workflow completed successfully for {order_id}")

        return {
            "order_id": order_id,
            "payment": payment,
            "fulfillment": fulfillment,
            "loyalty": loyalty,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "workflow_status": "success",
        }

    except Exception as e:
        try:
            db.rollback()
        except Exception:
            logger.exception("Rollback failed")
        logger.error(f"❌ Workflow failed for {order_id}: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        try:
            db.close()
        except Exception:
            logger.exception("Failed to close DB session")
