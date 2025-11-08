# app/models/inventory.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.services.db import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    location = Column(String(100))
    quantity = Column(Integer, default=0)

    # ✅ Match back_populates name in Product
    product = relationship("Product", back_populates="inventory_records")
