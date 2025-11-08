# app/models/fulfillment.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.services.db import Base

class Fulfillment(Base):
    __tablename__ = "fulfillments"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    carrier = Column(String(50))
    tracking_id = Column(String(50), unique=True)
    status = Column(String(50), default="processing")
    estimated_delivery = Column(DateTime)
    created_at = Column(DateTime, default=func.now())

    order = relationship("Order", backref="fulfillments")
