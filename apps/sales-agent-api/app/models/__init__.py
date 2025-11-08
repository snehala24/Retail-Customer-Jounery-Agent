# app/models/__init__.py
# Import product model (exists) and new models so metadata contains them all
from app.models.product import Product  # existing
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.loyalty import LoyaltyAccount
