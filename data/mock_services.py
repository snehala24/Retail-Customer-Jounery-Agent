from typing import List, Dict, Any, Optional
from models import Product, InventoryItem, Order, OrderStatus, PaymentMethod
import random
import json
from datetime import datetime, timedelta

# Indian Product Catalog with Rupee pricing
PRODUCTS = [
    # Electronics - Smartphones (Popular in India)
    Product(sku="PHONE001", name="Samsung Galaxy S24 Ultra", category="electronics", price=124999.00,
            description="Premium Android smartphone with S Pen", attributes={"brand": "Samsung", "color": "Titanium Gray", "storage": "512GB", "ram": "12GB"},
            images=["galaxy_s24.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="PHONE002", name="OnePlus 12", category="electronics", price=64999.00,
            description="Flagship killer with fast charging", attributes={"brand": "OnePlus", "color": "Flowy Emerald", "storage": "256GB", "ram": "12GB"},
            images=["oneplus12.jpg"], in_stock=True, stock_quantity=30),
    Product(sku="PHONE003", name="Xiaomi 14 Ultra", category="electronics", price=79999.00,
            description="Camera-focused flagship smartphone", attributes={"brand": "Xiaomi", "color": "Black", "storage": "512GB", "ram": "16GB"},
            images=["xiaomi14.jpg"], in_stock=True, stock_quantity=20),
    Product(sku="PHONE004", name="Realme GT 5 Pro", category="electronics", price=45999.00,
            description="Gaming-focused smartphone", attributes={"brand": "Realme", "color": "White", "storage": "256GB", "ram": "12GB"},
            images=["realme_gt.jpg"], in_stock=True, stock_quantity=35),
    Product(sku="PHONE005", name="Vivo X100 Pro", category="electronics", price=89999.00,
            description="Photography flagship with Zeiss optics", attributes={"brand": "Vivo", "color": "Blue", "storage": "512GB", "ram": "16GB"},
            images=["vivo_x100.jpg"], in_stock=True, stock_quantity=18),
    Product(sku="PHONE006", name="Oppo Find X7 Ultra", category="electronics", price=99999.00,
            description="Premium flagship with Hasselblad camera", attributes={"brand": "Oppo", "color": "Black", "storage": "512GB", "ram": "16GB"},
            images=["oppo_find.jpg"], in_stock=True, stock_quantity=15),
    
    # Electronics - Laptops
    Product(sku="LAPTOP001", name="MacBook Pro 16-inch M3", category="electronics", price=249999.00,
            description="Latest MacBook Pro with M3 chip", attributes={"brand": "Apple", "color": "Space Gray", "storage": "512GB", "ram": "18GB"},
            images=["macbook_pro.jpg"], in_stock=True, stock_quantity=12),
    Product(sku="LAPTOP002", name="Dell XPS 15", category="electronics", price=189999.00,
            description="High-performance laptop for professionals", attributes={"brand": "Dell", "color": "Silver", "storage": "1TB", "ram": "32GB"},
            images=["dell_xps.jpg"], in_stock=True, stock_quantity=15),
    Product(sku="LAPTOP003", name="HP Pavilion 15", category="electronics", price=59999.00,
            description="Budget-friendly laptop for students", attributes={"brand": "HP", "color": "Silver", "storage": "512GB", "ram": "8GB"},
            images=["hp_pavilion.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="LAPTOP004", name="Lenovo ThinkPad E15", category="electronics", price=69999.00,
            description="Business laptop with excellent keyboard", attributes={"brand": "Lenovo", "color": "Black", "storage": "512GB", "ram": "16GB"},
            images=["thinkpad_e15.jpg"], in_stock=True, stock_quantity=20),
    Product(sku="LAPTOP005", name="ASUS ROG Strix G15", category="electronics", price=129999.00,
            description="Gaming laptop with RTX graphics", attributes={"brand": "ASUS", "color": "Black", "storage": "1TB", "ram": "16GB"},
            images=["asus_rog.jpg"], in_stock=True, stock_quantity=18),
    
    # Electronics - Smartwatches
    Product(sku="WATCH001", name="Apple Watch Series 9", category="electronics", price=45999.00,
            description="Advanced smartwatch with health monitoring", attributes={"brand": "Apple", "color": "Midnight", "size": "45mm"},
            images=["apple_watch.jpg"], in_stock=True, stock_quantity=30),
    Product(sku="WATCH002", name="Samsung Galaxy Watch 6", category="electronics", price=29999.00,
            description="Premium smartwatch with fitness tracking", attributes={"brand": "Samsung", "color": "Graphite", "size": "47mm"},
            images=["galaxy_watch.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="WATCH003", name="Noise ColorFit Pro 4", category="electronics", price=2999.00,
            description="Budget smartwatch with health monitoring", attributes={"brand": "Noise", "color": "Black", "size": "1.78 inch"},
            images=["noise_watch.jpg"], in_stock=True, stock_quantity=50),
    Product(sku="WATCH004", name="Fire-Boltt Ninja Call Pro", category="electronics", price=1999.00,
            description="Affordable smartwatch with calling feature", attributes={"brand": "Fire-Boltt", "color": "Black", "size": "1.69 inch"},
            images=["fireboltt_watch.jpg"], in_stock=True, stock_quantity=40),
    
    # Electronics - Audio
    Product(sku="HEADPHONES001", name="Sony WH-1000XM5", category="electronics", price=29999.00,
            description="Premium noise-canceling headphones", attributes={"brand": "Sony", "color": "Black", "type": "Wireless"},
            images=["sony_headphones.jpg"], in_stock=True, stock_quantity=20),
    Product(sku="HEADPHONES002", name="AirPods Pro 2", category="electronics", price=24999.00,
            description="Active noise cancellation earbuds", attributes={"brand": "Apple", "color": "White", "type": "Wireless"},
            images=["airpods_pro.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="HEADPHONES003", name="Boat Airdopes 131", category="electronics", price=1299.00,
            description="Budget wireless earbuds", attributes={"brand": "Boat", "color": "Black", "type": "Wireless"},
            images=["boat_airdopes.jpg"], in_stock=True, stock_quantity=60),
    Product(sku="HEADPHONES004", name="JBL Flip 6 Speaker", category="electronics", price=9999.00,
            description="Portable waterproof Bluetooth speaker", attributes={"brand": "JBL", "color": "Blue", "type": "Portable"},
            images=["jbl_flip.jpg"], in_stock=True, stock_quantity=35),
    Product(sku="HEADPHONES005", name="Sennheiser HD 660S", category="electronics", price=39999.00,
            description="High-end audiophile headphones", attributes={"brand": "Sennheiser", "color": "Black", "type": "Wired"},
            images=["sennheiser.jpg"], in_stock=True, stock_quantity=15),
    
    # Fashion - Traditional Wear
    Product(sku="KURTA001", name="Fabindia Cotton Kurta", category="fashion", price=2499.00,
            description="Comfortable cotton kurta for men", attributes={"brand": "Fabindia", "color": "White", "size": "M", "material": "Cotton"},
            images=["fabindia_kurta.jpg"], in_stock=True, stock_quantity=50),
    Product(sku="SARE001", name="Global Desi Silk Saree", category="fashion", price=8999.00,
            description="Elegant silk saree for special occasions", attributes={"brand": "Global Desi", "color": "Red", "size": "Free Size", "material": "Silk"},
            images=["global_desi_saree.jpg"], in_stock=True, stock_quantity=30),
    Product(sku="LEHENGA001", name="Libas Designer Lehenga", category="fashion", price=15999.00,
            description="Designer lehenga for weddings", attributes={"brand": "Libas", "color": "Pink", "size": "M", "material": "Silk"},
            images=["libas_lehenga.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="SHERWANI001", name="Manyavar Sherwani", category="fashion", price=12999.00,
            description="Traditional sherwani for groom", attributes={"brand": "Manyavar", "color": "Cream", "size": "L", "material": "Silk"},
            images=["manyavar_sherwani.jpg"], in_stock=True, stock_quantity=20),
    
    # Fashion - Western Wear
    Product(sku="JEANS001", name="Levi's 501 Original Jeans", category="fashion", price=3999.00,
            description="Classic straight fit jeans", attributes={"brand": "Levi's", "color": "Blue", "size": "32", "fit": "Straight"},
            images=["levis_501.jpg"], in_stock=True, stock_quantity=40),
    Product(sku="SHIRT001", name="Van Heusen Formal Shirt", category="fashion", price=1999.00,
            description="Crisp formal shirt for office", attributes={"brand": "Van Heusen", "color": "White", "size": "M", "fit": "Regular"},
            images=["van_heusen_shirt.jpg"], in_stock=True, stock_quantity=35),
    Product(sku="DRESS001", name="W Women's Dress", category="fashion", price=2999.00,
            description="Elegant women's dress", attributes={"brand": "W", "color": "Black", "size": "M", "style": "A-Line"},
            images=["w_dress.jpg"], in_stock=True, stock_quantity=30),
    
    # Home - Appliances
    Product(sku="AC001", name="LG 1.5 Ton Inverter AC", category="home", price=45999.00,
            description="Energy-efficient split AC", attributes={"brand": "LG", "color": "White", "capacity": "1.5 Ton", "type": "Split"},
            images=["lg_ac.jpg"], in_stock=True, stock_quantity=15),
    Product(sku="WASHER001", name="Samsung 7kg Front Load Washing Machine", category="home", price=34999.00,
            description="Front load washing machine with AI", attributes={"brand": "Samsung", "color": "White", "capacity": "7kg", "type": "Front Load"},
            images=["samsung_washer.jpg"], in_stock=True, stock_quantity=20),
    Product(sku="FRIDGE001", name="Whirlpool 300L Refrigerator", category="home", price=28999.00,
            description="Double door refrigerator", attributes={"brand": "Whirlpool", "color": "Silver", "capacity": "300L", "type": "Double Door"},
            images=["whirlpool_fridge.jpg"], in_stock=True, stock_quantity=18),
    Product(sku="TV001", name="Sony 55-inch 4K Smart TV", category="home", price=79999.00,
            description="4K Android TV with Dolby Vision", attributes={"brand": "Sony", "color": "Black", "size": "55 inch", "resolution": "4K"},
            images=["sony_tv.jpg"], in_stock=True, stock_quantity=12),
    Product(sku="MIXER001", name="Preethi Zodiac Mixer Grinder", category="home", price=8999.00,
            description="Heavy-duty mixer grinder", attributes={"brand": "Preethi", "color": "Red", "jars": "3", "power": "750W"},
            images=["preethi_mixer.jpg"], in_stock=True, stock_quantity=25),
    
    # Sports - Cricket
    Product(sku="BAT001", name="MRF Genius Grand Edition Bat", category="sports", price=15999.00,
            description="Professional cricket bat", attributes={"brand": "MRF", "color": "Natural", "weight": "2.10 lbs", "grade": "Grade 1"},
            images=["mrf_bat.jpg"], in_stock=True, stock_quantity=20),
    Product(sku="BALL001", name="SG Test Cricket Ball", category="sports", price=899.00,
            description="Official test cricket ball", attributes={"brand": "SG", "color": "Red", "weight": "5.5 oz", "type": "Test"},
            images=["sg_ball.jpg"], in_stock=True, stock_quantity=50),
    Product(sku="GLOVES001", name="SS Gloves Professional", category="sports", price=2999.00,
            description="Professional wicket-keeping gloves", attributes={"brand": "SS", "color": "Brown", "size": "M", "type": "Wicket Keeping"},
            images=["ss_gloves.jpg"], in_stock=True, stock_quantity=30),
    
    # Sports - Fitness
    Product(sku="SHOES001", name="Nike Air Max 270", category="sports", price=12999.00,
            description="Comfortable running shoes", attributes={"brand": "Nike", "color": "White/Black", "size": "9", "type": "Running"},
            images=["nike_airmax.jpg"], in_stock=True, stock_quantity=40),
    Product(sku="SHOES002", name="Adidas Ultraboost 22", category="sports", price=14999.00,
            description="Responsive running shoes", attributes={"brand": "Adidas", "color": "White", "size": "9", "type": "Running"},
            images=["ultraboost.jpg"], in_stock=True, stock_quantity=35),
    Product(sku="SHOES003", name="Puma RS-X", category="sports", price=8999.00,
            description="Retro-inspired running shoes", attributes={"brand": "Puma", "color": "White/Gray", "size": "9", "type": "Lifestyle"},
            images=["puma_rsx.jpg"], in_stock=True, stock_quantity=30),
    
    # Beauty - Indian Brands
    Product(sku="LIPSTICK001", name="Lakme 9 to 5 Lipstick", category="beauty", price=399.00,
            description="Long-lasting matte lipstick", attributes={"brand": "Lakme", "color": "Red", "finish": "Matte", "shade": "Red Alert"},
            images=["lakme_lipstick.jpg"], in_stock=True, stock_quantity=60),
    Product(sku="FOUNDATION001", name="Maybelline Fit Me Foundation", category="beauty", price=599.00,
            description="Natural finish foundation", attributes={"brand": "Maybelline", "color": "Natural", "finish": "Natural", "coverage": "Medium"},
            images=["maybelline_foundation.jpg"], in_stock=True, stock_quantity=45),
    Product(sku="KAJAL001", name="Lakme Eyeconic Kajal", category="beauty", price=199.00,
            description="Long-lasting kajal", attributes={"brand": "Lakme", "color": "Black", "type": "Kajal", "formula": "Creamy"},
            images=["lakme_kajal.jpg"], in_stock=True, stock_quantity=80),
    Product(sku="FACE001", name="Nykaa Face Wash", category="beauty", price=299.00,
            description="Gentle face wash for all skin types", attributes={"brand": "Nykaa", "color": "Clear", "type": "Face Wash", "skin_type": "All"},
            images=["nykaa_facewash.jpg"], in_stock=True, stock_quantity=50),
    
    # Books - Indian Authors
    Product(sku="BOOK001", name="The Palace of Illusions by Chitra Banerjee", category="books", price=399.00,
            description="Mahabharata from Draupadi's perspective", attributes={"author": "Chitra Banerjee Divakaruni", "language": "English", "pages": "360"},
            images=["palace_illusions.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="BOOK002", name="The White Tiger by Aravind Adiga", category="books", price=499.00,
            description="Man Booker Prize winning novel", attributes={"author": "Aravind Adiga", "language": "English", "pages": "304"},
            images=["white_tiger.jpg"], in_stock=True, stock_quantity=20),
    Product(sku="BOOK003", name="The God of Small Things by Arundhati Roy", category="books", price=599.00,
            description="Man Booker Prize winning novel", attributes={"author": "Arundhati Roy", "language": "English", "pages": "352"},
            images=["god_small_things.jpg"], in_stock=True, stock_quantity=18),
    Product(sku="BOOK004", name="Wings of Fire by APJ Abdul Kalam", category="books", price=299.00,
            description="Autobiography of India's missile man", attributes={"author": "APJ Abdul Kalam", "language": "English", "pages": "180"},
            images=["wings_fire.jpg"], in_stock=True, stock_quantity=30),
    
    # Automotive - Accessories
    Product(sku="CAR001", name="Maruti Swift Car Cover", category="automotive", price=1999.00,
            description="Waterproof car cover", attributes={"brand": "Generic", "color": "Gray", "size": "Medium", "material": "Polyester"},
            images=["car_cover.jpg"], in_stock=True, stock_quantity=25),
    Product(sku="CAR002", name="Bosch Car Battery", category="automotive", price=8999.00,
            description="High-performance car battery", attributes={"brand": "Bosch", "color": "Black", "capacity": "60Ah", "type": "Lead Acid"},
            images=["bosch_battery.jpg"], in_stock=True, stock_quantity=15),
    
    # Food - Indian Snacks
    Product(sku="SNACK001", name="Haldiram's Namkeen Mix", category="food", price=199.00,
            description="Traditional Indian namkeen mix", attributes={"brand": "Haldiram's", "weight": "200g", "type": "Namkeen", "flavor": "Mixed"},
            images=["haldiram_namkeen.jpg"], in_stock=True, stock_quantity=100),
    Product(sku="SNACK002", name="Bikanervala Bhujia", category="food", price=149.00,
            description="Crispy bhujia snack", attributes={"brand": "Bikanervala", "weight": "150g", "type": "Bhujia", "flavor": "Spicy"},
            images=["bikanervala_bhujia.jpg"], in_stock=True, stock_quantity=80),
    Product(sku="SNACK003", name="MTR Ready to Eat Dal", category="food", price=89.00,
            description="Ready to eat dal", attributes={"brand": "MTR", "weight": "200g", "type": "Ready to Eat", "flavor": "Dal"},
            images=["mtr_dal.jpg"], in_stock=True, stock_quantity=60),
]

# Indian Inventory Locations
INVENTORY = []
for product in PRODUCTS:
    # Online warehouse
    INVENTORY.append(InventoryItem(
        sku=product.sku,
        location="online",
        quantity=product.stock_quantity,
        reserved=0
    ))
    
    # Mumbai store
    INVENTORY.append(InventoryItem(
        sku=product.sku,
        location="mumbai_store",
        quantity=max(5, product.stock_quantity // 4),
        reserved=0
    ))
    
    # Delhi store
    INVENTORY.append(InventoryItem(
        sku=product.sku,
        location="delhi_store",
        quantity=max(5, product.stock_quantity // 4),
        reserved=0
    ))
    
    # Bangalore store
    INVENTORY.append(InventoryItem(
        sku=product.sku,
        location="bangalore_store",
        quantity=max(5, product.stock_quantity // 4),
        reserved=0
    ))

# Indian Payment Methods
INDIAN_PAYMENT_METHODS = [
    PaymentMethod.UPI,
    PaymentMethod.CREDIT_CARD,
    PaymentMethod.DEBIT_CARD,
    PaymentMethod.NET_BANKING,
    PaymentMethod.WALLET,
    PaymentMethod.COD
]

# Indian Promotions
INDIAN_PROMOTIONS = {
    "DIWALI20": {
        "discount": 0.20,
        "valid_until": datetime.now() + timedelta(days=30),
        "min_amount": 2000,
        "description": "20% off on Diwali shopping"
    },
    "FESTIVE10": {
        "discount": 0.10,
        "valid_until": datetime.now() + timedelta(days=15),
        "min_amount": 1000,
        "description": "10% off festive collection"
    },
    "NEWUSER15": {
        "discount": 0.15,
        "valid_until": datetime.now() + timedelta(days=7),
        "min_amount": 500,
        "description": "15% off for new users"
    },
    "MOBILE5": {
        "discount": 0.05,
        "valid_until": datetime.now() + timedelta(days=10),
        "min_amount": 5000,
        "description": "5% off on mobile app orders"
    }
}

# Export for use in agents
PROMOTIONS = INDIAN_PROMOTIONS

class MockProductService:
    def __init__(self):
        self.products = PRODUCTS
        self.inventory = INVENTORY
    
    def get_products(self, category: str = None, limit: int = 20) -> List[Product]:
        """Get products with optional category filter"""
        if category:
            filtered = [p for p in self.products if p.category == category]
        else:
            filtered = self.products
        
        return filtered[:limit]
    
    def get_product(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        for product in self.products:
            if product.sku == sku:
                return product
        return None
    
    def search_products(self, query: str) -> List[Product]:
        """Search products by name or description"""
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            if (query_lower in product.name.lower() or 
                query_lower in product.description.lower() or
                query_lower in product.category.lower()):
                results.append(product)
        
        return results[:20]
    
    def get_inventory(self, sku: str, location: str = None) -> List[InventoryItem]:
        """Get inventory for a product"""
        if location:
            return [item for item in self.inventory if item.sku == sku and item.location == location]
        else:
            return [item for item in self.inventory if item.sku == sku]
    
    def update_inventory(self, sku: str, location: str, quantity_change: int) -> bool:
        """Update inventory quantity"""
        for item in self.inventory:
            if item.sku == sku and item.location == location:
                item.quantity = max(0, item.quantity + quantity_change)
                return True
        return False

class MockInventoryService:
    def __init__(self):
        self.inventory = INVENTORY
    
    def check_availability(self, sku: str, quantity: int, location: str = "online") -> Dict[str, Any]:
        """Check product availability"""
        for item in self.inventory:
            if item.sku == sku and item.location == location:
                available = item.quantity - item.reserved
                return {
                    "available": available >= quantity,
                    "quantity_available": available,
                    "quantity_requested": quantity,
                    "location": location
                }
        return {"available": False, "quantity_available": 0, "quantity_requested": quantity, "location": location}
    
    def check_inventory(self, sku: str, location: str = None) -> List[InventoryItem]:
        """Get inventory for a product"""
        if location:
            return [item for item in self.inventory if item.sku == sku and item.location == location]
        else:
            return [item for item in self.inventory if item.sku == sku]
    
    def reserve_inventory(self, sku: str, quantity: int, location: str = "online") -> bool:
        """Reserve inventory for order"""
        for item in self.inventory:
            if item.sku == sku and item.location == location:
                if item.quantity - item.reserved >= quantity:
                    item.reserved += quantity
                    return True
        return False
    
    def reserve_item(self, sku: str, location: str, quantity: int) -> bool:
        """Reserve inventory item (alias for reserve_inventory)"""
        return self.reserve_inventory(sku, quantity, location)
    
    def release_inventory(self, sku: str, quantity: int, location: str = "online") -> bool:
        """Release reserved inventory"""
        for item in self.inventory:
            if item.sku == sku and item.location == location:
                if item.reserved >= quantity:
                    item.reserved -= quantity
                    return True
        return False
    
    def release_reservation(self, sku: str, location: str, quantity: int) -> bool:
        """Release reserved inventory (alias for release_inventory)"""
        return self.release_inventory(sku, quantity, location)

class MockPaymentService:
    def __init__(self):
        self.payment_methods = INDIAN_PAYMENT_METHODS
    
    def process_payment(self, amount: float, payment_method: PaymentMethod, customer_id: str) -> Dict[str, Any]:
        """Process payment with Indian payment methods"""
        # Mock payment processing
        success_rate = 0.95  # 95% success rate
        
        if random.random() < success_rate:
            return {
                "success": True,
                "transaction_id": f"TXN_{random.randint(100000, 999999)}",
                "amount": amount,
                "payment_method": payment_method.value,
                "timestamp": datetime.now().isoformat(),
                "gateway": self._get_payment_gateway(payment_method)
            }
        else:
            return {
                "success": False,
                "error": "Payment failed",
                "error_code": "PAYMENT_DECLINED",
                "timestamp": datetime.now().isoformat()
            }
    
    def refund_payment(self, transaction_id: str, amount: float) -> Dict[str, Any]:
        """Process refund"""
        return {
            "success": True,
            "refund_id": f"REF_{random.randint(100000, 999999)}",
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_payment_gateway(self, payment_method: PaymentMethod) -> str:
        """Get payment gateway for Indian payment methods"""
        gateways = {
            PaymentMethod.UPI: "Razorpay",
            PaymentMethod.CREDIT_CARD: "Razorpay",
            PaymentMethod.DEBIT_CARD: "Razorpay",
            PaymentMethod.NET_BANKING: "Razorpay",
            PaymentMethod.WALLET: "Paytm",
            PaymentMethod.COD: "Cash on Delivery"
        }
        return gateways.get(payment_method, "Razorpay")

class MockLoyaltyService:
    def __init__(self):
        self.promotions = INDIAN_PROMOTIONS
    
    def calculate_loyalty_points(self, amount: float, tier: str) -> int:
        """Calculate loyalty points based on Indian tier system"""
        multipliers = {
            "bronze": 1,
            "silver": 1.5,
            "gold": 2,
            "platinum": 3
        }
        base_points = int(amount / 100)  # 1 point per ₹100
        return int(base_points * multipliers.get(tier, 1))
    
    def apply_loyalty_discount(self, amount: float, tier: str, points: int) -> Dict[str, Any]:
        """Apply loyalty discount"""
        discount_rates = {
            "bronze": 0.05,
            "silver": 0.10,
            "gold": 0.15,
            "platinum": 0.20
        }
        
        discount_rate = discount_rates.get(tier, 0.05)
        discount_amount = amount * discount_rate
        
        # Apply points discount (1 point = ₹1)
        points_discount = min(points, amount * 0.1)  # Max 10% of order value
        
        total_discount = discount_amount + points_discount
        final_amount = amount - total_discount
        
        return {
            "discount_amount": total_discount,
            "final_amount": final_amount,
            "points_used": int(points_discount)
        }
    
    def get_available_promotions(self, tier: str, amount: float) -> List[Dict[str, Any]]:
        """Get available promotions for Indian customers"""
        available = []
        for code, promo in self.promotions.items():
            if promo["valid_until"] > datetime.now() and promo["min_amount"] <= amount:
                available.append({
                    "code": code,
                    "description": promo["description"],
                    "discount": promo["discount"],
                    "min_amount": promo["min_amount"]
                })
        return available