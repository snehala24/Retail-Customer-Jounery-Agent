# app/services/recommend_service.py
from sqlalchemy.orm import Session
from app.models.product import Product
from app.services.db import get_db_session

def recommend_products(query: str, budget: int):
    """Fetch matching products based on query and budget."""
    session: Session = get_db_session()
    
    try:
        results = (
            session.query(Product)
            .filter(Product.category.ilike(f"%{query}%"))
            .filter(Product.price <= budget)
            .limit(5)
            .all()
        )

        if not results:
            return {"items": [], "message": "No products found under your criteria."}

        return {
            "items": [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "price": p.price,
                    "image_url": p.image_url,
                    "stock": p.stock,
                }
                for p in results
            ],
            "message": f"Found {len(results)} products for '{query}' under ₹{budget}"
        }

    finally:
        session.close()
