# app/agents/inventory_agent.py
from typing import Dict, Any, Optional
from app.services.db import get_db_session
from app.models.product import Product
from sqlalchemy import select

def check_stock_sync(sku: str, location: Optional[str] = None) -> Dict[str, Any]:
    """
    Return stock info for a SKU. For now we use `products.stock`.
    `location` is optional (reserved for store-level inventory later).
    """
    db = get_db_session()
    try:
        stmt = select(Product).where(Product.sku == sku).limit(1)
        p = db.execute(stmt).scalars().first()
        if not p:
            return {"sku": sku, "found": False, "message": "SKU not found", "stores": []}
        # sample store response (mocked)
        stores = [
            {"store_id": "STORE-MYLAI", "qty": p.stock},
        ]
        return {
            "sku": sku,
            "found": True,
            "total_stock": p.stock,
            "stores": stores,
            "ship_eta_days": 2
        }
    finally:
        db.close()
