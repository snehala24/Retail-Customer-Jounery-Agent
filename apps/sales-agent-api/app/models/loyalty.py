# app/models/loyalty.py
from sqlalchemy import Column, Integer, ForeignKey
from app.services.db import Base

class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    points = Column(Integer, nullable=False, default=0)
