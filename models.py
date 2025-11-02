from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ChannelType(str, Enum):
    WEB = "web"
    MOBILE = "mobile"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    INSTORE_KIOSK = "in_store_kiosk"
    VOICE_ASSISTANT = "voice_assistant"

class CustomerTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    NET_BANKING = "net_banking"
    WALLET = "wallet"
    COD = "cod"
    GIFT_CARD = "gift_card"
    LOYALTY_POINTS = "loyalty_points"

class Customer(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    age: Optional[int] = None
    tier: CustomerTier
    loyalty_points: int = 0
    preferred_channels: List[ChannelType] = []
    channel_preferences: List[ChannelType] = []
    purchase_history: List[str] = []
    preferences: Dict[str, Any] = {}
    location: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: Optional[datetime] = None

class Product(BaseModel):
    sku: str
    name: str
    category: str
    price: float
    description: str
    attributes: Dict[str, Any] = {}
    images: List[str] = []
    in_stock: bool = True
    stock_quantity: int = 0

class InventoryItem(BaseModel):
    sku: str
    location: str  # "online", "store_001", "warehouse_001", etc.
    quantity: int
    reserved: int = 0

class Order(BaseModel):
    id: str
    customer_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: OrderStatus
    payment_method: PaymentMethod
    fulfillment_method: str  # "ship_to_home", "click_collect", "in_store_pickup"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ConversationSession(BaseModel):
    id: str
    customer_id: str
    channel: ChannelType
    messages: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)

class AgentTask(BaseModel):
    id: str
    agent_type: str
    customer_id: str
    task_data: Dict[str, Any]
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
