# app/models/product.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.services.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255))
    category = Column(String(100), index=True)
    price = Column(Integer)
    image_url = Column(String(255))
    stock = Column(Integer, default=0)

    # ✅ Relationship with Inventory
    inventory_records = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")
