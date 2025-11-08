# app/agents/loyalty_agent.py
from datetime import datetime
from app.services.db import get_db_session
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

def calculate_points(amount: int) -> int:
    """Simple points rule: 1 point for every ₹100 spent."""
    return max(1, amount // 100)


def add_loyalty_points_sync(customer_id: int, order_total: int):
    db = get_db_session()
    try:
        points_to_add = calculate_points(order_total)

        # ✅ Check if the customer already has a loyalty account
        account = db.execute(
            text("SELECT * FROM loyalty_accounts WHERE customer_id = :cid"),
            {"cid": customer_id}
        ).fetchone()

        if account:
            new_balance = account.points + points_to_add
            db.execute(
                text("UPDATE loyalty_accounts SET points = :p WHERE customer_id = :cid"),
                {"p": new_balance, "cid": customer_id}
            )
            logger.info(f"✅ Added {points_to_add} points (new total: {new_balance})")
        else:
            db.execute(
                text("INSERT INTO loyalty_accounts (customer_id, points) VALUES (:cid, :p)"),
                {"cid": customer_id, "p": points_to_add}
            )
            new_balance = points_to_add
            logger.info(f"🎉 Created new loyalty account for customer {customer_id} with {points_to_add} points.")

        db.commit()

        return {
            "customer_id": customer_id,
            "points_added": points_to_add,
            "total_points": new_balance,
            "timestamp": datetime.utcnow().isoformat(),
            "db_update": "success"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"❌ Loyalty update failed: {e}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()
