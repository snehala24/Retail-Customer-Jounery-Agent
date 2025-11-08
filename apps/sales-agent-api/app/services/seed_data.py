# app/services/seed_data.py
from app.models.product import Product
from app.services.db import Base, engine, SessionLocal

def seed_products():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Product).count() > 0:
        print("✅ Products already seeded.")
        db.close()
        return

    products = [
        Product(sku="SKU-1001", name="Casual Cotton Shirt", category="shirts", price=1299, image_url="https://img.shirt1", stock=12),
        Product(sku="SKU-1002", name="Formal Blue Shirt", category="shirts", price=1499, image_url="https://img.shirt2", stock=8),
        Product(sku="SKU-1003", name="Denim Jeans", category="pants", price=1799, image_url="https://img.jeans1", stock=15),
        Product(sku="SKU-1004", name="Casual T-Shirt", category="tshirts", price=899, image_url="https://img.tshirt1", stock=30),
        Product(sku="SKU-1005", name="Sneakers", category="shoes", price=2499, image_url="https://img.shoe1", stock=5),
    ]

    db.add_all(products)
    db.commit()
    db.close()
    print("🌱 Seeded mock products successfully.")

# 👇 ADD THIS at the end!
if __name__ == "__main__":
    seed_products()    
