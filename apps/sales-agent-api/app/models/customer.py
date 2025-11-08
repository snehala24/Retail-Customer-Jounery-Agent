# app/models/customer.py
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.services.db import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    customer_id = Column(String(100), unique=True, nullable=False)  # external id like CUST-001
    name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True, unique=False)
    loyalty_tier = Column(String(50), nullable=True, default="standard")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ✅ Relationship to orders
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
