# app/models/product.py
from sqlalchemy import Column, Integer, String
from app.services.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255))
    category = Column(String(100))
    price = Column(Integer)
    image_url = Column(String(255))
    stock = Column(Integer, default=0)
