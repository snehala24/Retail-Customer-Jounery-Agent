from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.services.db import Base

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

    # ✅ Match back_populates on both sides
    order = relationship("Order", back_populates="items")
