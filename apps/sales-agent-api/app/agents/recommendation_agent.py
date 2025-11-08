# app/agents/recommendation_agent.py
from typing import Dict, Any
from app.services.db import get_db_session
from app.models.product import Product
from sqlalchemy import select

def recommend_products_sync(query: str, budget: int, limit: int = 5) -> Dict[str, Any]:
    """
    Simple recommendation logic:
      - match category ILIKE %query% OR name ILIKE %query%
      - price <= budget
      - order by price asc
    Returns: dict with "items" list and "message"
    """
    db = get_db_session()
    try:
        stmt = (
            select(Product)
            .where(
                Product.price <= budget,
                (Product.category.ilike(f"%{query}%")) | (Product.name.ilike(f"%{query}%"))
            )
            .limit(limit)
        )
        rows = db.execute(stmt).scalars().all()

        items = [
            {
                "sku": p.sku,
                "name": p.name,
                "price": p.price,
                "image_url": p.image_url,
                "stock": p.stock
            } for p in rows
        ]

        message = f"Found {len(items)} products for '{query}' under ₹{budget}"
        return {"items": items, "message": message}
    finally:
        db.close()
