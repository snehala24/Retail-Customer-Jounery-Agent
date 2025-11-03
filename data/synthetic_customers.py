from faker import Faker
from models import Customer, CustomerTier, ChannelType
import random
from typing import List

fake = Faker('en_IN')  # Use Indian locale

# Generate a diverse list of Indian cities
INDIAN_CITIES = [
    "Mumbai, Maharashtra", "Delhi, Delhi", "Bangalore, Karnataka", "Hyderabad, Telangana",
    "Chennai, Tamil Nadu", "Kolkata, West Bengal", "Pune, Maharashtra", "Ahmedabad, Gujarat",
    "Jaipur, Rajasthan", "Surat, Gujarat", "Lucknow, Uttar Pradesh", "Kanpur, Uttar Pradesh",
    "Nagpur, Maharashtra", "Indore, Madhya Pradesh", "Thane, Maharashtra", "Bhopal, Madhya Pradesh",
    "Visakhapatnam, Andhra Pradesh", "Pimpri-Chinchwad, Maharashtra", "Patna, Bihar", "Vadodara, Gujarat",
    "Ghaziabad, Uttar Pradesh", "Ludhiana, Punjab", "Agra, Uttar Pradesh", "Nashik, Maharashtra",
    "Faridabad, Haryana", "Meerut, Uttar Pradesh", "Rajkot, Gujarat", "Kalyan-Dombivali, Maharashtra",
    "Vasai-Virar, Maharashtra", "Varanasi, Uttar Pradesh", "Srinagar, Jammu and Kashmir", "Aurangabad, Maharashtra",
    "Navi Mumbai, Maharashtra", "Solapur, Maharashtra", "Vijayawada, Andhra Pradesh", "Kolhapur, Maharashtra",
    "Amritsar, Punjab", "Noida, Uttar Pradesh", "Ranchi, Jharkhand", "Howrah, West Bengal",
    "Coimbatore, Tamil Nadu", "Raipur, Chhattisgarh", "Kochi, Kerala", "Bhubaneswar, Odisha",
    "Bhavnagar, Gujarat", "Salem, Tamil Nadu", "Warangal, Telangana", "Guntur, Andhra Pradesh",
    "Bhiwandi, Maharashtra", "Amravati, Maharashtra", "Nanded, Maharashtra", "Kolhapur, Maharashtra"
]

# Indian brand categories
INDIAN_BRAND_CATEGORIES = {
    "electronics": ["Samsung", "OnePlus", "Xiaomi", "Realme", "Vivo", "Oppo", "Apple", "Sony", "LG", "Panasonic", "Micromax", "Lava"],
    "fashion": ["Fabindia", "W", "Global Desi", "Anouk", "Libas", "Koovs", "Myntra", "Ajio", "Max", "Pantaloons", "Westside", "Reliance Trends"],
    "home": ["Godrej", "Asian Paints", "Havells", "Crompton", "Bajaj", "Orient", "Philips", "Syska", "Wipro", "Finolex"],
    "sports": ["Nike", "Adidas", "Puma", "Reebok", "Decathlon", "Yonex", "Wilson", "Head", "Slazenger", "Cosco"],
    "beauty": ["Lakme", "Maybelline", "L'Oreal", "Revlon", "MAC", "Clinique", "Nykaa", "Sugar", "Colorbar", "Faces Canada"],
    "books": ["Penguin India", "HarperCollins India", "Rupa Publications", "Westland", "Arihant", "Disha Publications", "McGraw Hill India"],
    "automotive": ["Maruti Suzuki", "Hyundai", "Tata Motors", "Mahindra", "Honda", "Toyota", "Ford", "Volkswagen", "Skoda", "Nissan"],
    "food": ["Amul", "Nestle India", "ITC", "Parle", "Britannia", "Cadbury", "Haldiram's", "Bikanervala", "MTR", "Gits"]
}

INDIAN_STYLE_PREFERENCES = ["traditional", "modern", "fusion", "casual", "formal", "ethnic", "western", "contemporary"]
INDIAN_PRICE_RANGES = ["budget", "mid", "premium", "luxury"]

# Indian names and cultural preferences
INDIAN_FIRST_NAMES = [
    # Male names
    "Arjun", "Raj", "Vikram", "Suresh", "Kumar", "Ravi", "Amit", "Sanjay", "Vishal", "Nitin",
    "Rohit", "Ajay", "Pankaj", "Manish", "Sandeep", "Rakesh", "Vijay", "Ashok", "Dinesh", "Manoj",
    "Suresh", "Ramesh", "Gopal", "Hari", "Krishna", "Ram", "Shiva", "Vishnu", "Ganesh", "Kartik",
    "Rahul", "Aryan", "Kabir", "Arnav", "Vivaan", "Aditya", "Ishaan", "Reyansh", "Atharv", "Advait",
    "Krish", "Shaurya", "Vihaan", "Rudra", "Arush", "Ayaan", "Dhruv", "Veer", "Kiaan", "Aarav",
    # Female names
    "Priya", "Sneha", "Anita", "Deepa", "Sunita", "Pooja", "Kavita", "Meera", "Rekha", "Shilpa",
    "Neha", "Sushma", "Ritu", "Geeta", "Manju", "Kamala", "Indira", "Lakshmi", "Sita", "Radha",
    "Kavya", "Ananya", "Ishita", "Saanvi", "Aadhya", "Diya", "Kiara", "Pari", "Anaya", "Navya",
    "Riya", "Aarohi", "Myra", "Aanya", "Sara", "Ira", "Avni", "Zara", "Inaya", "Prisha",
    "Kavya", "Anika", "Aria", "Mira", "Nora", "Zoya", "Amara", "Trisha", "Kyra", "Isha"
]

INDIAN_LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Gupta", "Agarwal", "Verma", "Jain", "Yadav", "Reddy",
    "Pandey", "Mishra", "Choudhary", "Malhotra", "Arora", "Bansal", "Goyal", "Khanna", "Saxena", "Tiwari",
    "Joshi", "Nair", "Iyer", "Menon", "Nambiar", "Krishnan", "Raman", "Subramanian", "Venkatesh", "Murthy",
    "Desai", "Shah", "Mehta", "Bhatt", "Trivedi", "Pandit", "Dwivedi", "Shukla", "Pathak", "Tripathi",
    "Dubey", "Singhania", "Bajaj", "Goel", "Kapoor", "Chopra", "Ahuja", "Sethi", "Bhatia", "Chadha",
    "Grover", "Sood", "Kohli", "Dhawan", "Raina", "Gambhir", "Sehwag", "Dravid", "Tendulkar", "Ganguly"
]

# Indian states and their major cities
INDIAN_STATES_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur", "Kolhapur", "Amravati", "Nanded"],
    "Delhi": ["New Delhi", "Central Delhi", "East Delhi", "North Delhi", "South Delhi", "West Delhi"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum", "Gulbarga", "Davangere", "Bellary"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Khammam", "Karimnagar", "Ramagundam", "Mahbubnagar"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Erode", "Vellore"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Bardhaman", "Malda", "Habra"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar", "Junagadh", "Gandhinagar"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer", "Bharatpur", "Alwar"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut", "Allahabad", "Bareilly", "Ghaziabad"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot"],
    "Haryana": ["Gurgaon", "Faridabad", "Panipat", "Ambala", "Yamunanagar", "Karnal", "Hisar", "Rohtak"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Palakkad", "Kollam", "Malappuram", "Kannur"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati", "Kadapa", "Anantapur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar", "Dewas", "Satna"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Purnia", "Munger", "Chapra"]
}

# Indian occupations and income levels
INDIAN_OCCUPATIONS = {
    "high_income": ["Software Engineer", "Doctor", "Lawyer", "Investment Banker", "Consultant", "Architect", "Pilot", "Government Officer"],
    "medium_income": ["Teacher", "Accountant", "Sales Manager", "Marketing Executive", "HR Manager", "Bank Manager", "Pharmacist", "Journalist"],
    "budget_conscious": ["Student", "Freelancer", "Small Business Owner", "Driver", "Security Guard", "Retail Worker", "Factory Worker", "Farmer"]
}

# Indian festival preferences
INDIAN_FESTIVALS = ["Diwali", "Holi", "Dussehra", "Eid", "Christmas", "Durga Puja", "Ganesh Chaturthi", "Navratri", "Raksha Bandhan", "Karva Chauth"]

# Indian languages
INDIAN_LANGUAGES = ["Hindi", "English", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati", "Kannada", "Malayalam", "Punjabi", "Odia", "Assamese"]

def generate_indian_preferences(categories: List[str]) -> dict:
    """Generate realistic Indian preferences based on categories"""
    preferred_brands = []
    for category in categories:
        if category in INDIAN_BRAND_CATEGORIES:
            preferred_brands.extend(random.sample(INDIAN_BRAND_CATEGORIES[category], k=min(3, len(INDIAN_BRAND_CATEGORIES[category]))))
    
    return {
        "style": random.choice(INDIAN_STYLE_PREFERENCES),
        "price_range": random.choice(INDIAN_PRICE_RANGES),
        "brands": list(set(preferred_brands))[:5],  # Max 5 unique brands
        "festival_preferences": random.sample(["Diwali", "Holi", "Dussehra", "Eid", "Christmas", "Durga Puja"], k=random.randint(1, 3)),
        "language_preference": random.choice(["Hindi", "English", "Tamil", "Telugu", "Bengali", "Marathi", "Gujarati"])
    }

def generate_indian_phone_number() -> str:
    """Generate Indian phone number"""
    prefixes = ["+91-9", "+91-8", "+91-7", "+91-6"]
    prefix = random.choice(prefixes)
    number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"{prefix}{number}"

def generate_indian_email(name: str) -> str:
    """Generate Indian email"""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "rediffmail.com", "outlook.com"]
    username = name.lower().replace(" ", ".") + str(random.randint(10, 99))
    return f"{username}@{random.choice(domains)}"

def generate_indian_location() -> str:
    """Generate realistic Indian location with state"""
    state = random.choice(list(INDIAN_STATES_CITIES.keys()))
    city = random.choice(INDIAN_STATES_CITIES[state])
    return f"{city}, {state}"

def generate_indian_occupation_and_income() -> tuple:
    """Generate occupation and income level"""
    income_level = random.choices(
        ["high_income", "medium_income", "budget_conscious"],
        weights=[0.15, 0.35, 0.50]  # More budget-conscious customers in India
    )[0]
    occupation = random.choice(INDIAN_OCCUPATIONS[income_level])
    return occupation, income_level

def generate_indian_purchase_patterns(tier: CustomerTier, occupation: str) -> List[str]:
    """Generate realistic Indian purchase patterns"""
    patterns = []
    
    # Base patterns for all tiers
    patterns.extend(["electronics", "fashion"])
    
    # Tier-specific patterns
    if tier in [CustomerTier.GOLD, CustomerTier.PLATINUM]:
        patterns.extend(["home", "beauty", "automotive"])
    elif tier == CustomerTier.SILVER:
        patterns.extend(["sports", "books"])
    else:
        patterns.extend(["food"])  # Budget-conscious customers buy more food items
    
    # Occupation-specific patterns
    if "Engineer" in occupation or "Doctor" in occupation:
        patterns.extend(["electronics", "books"])
    elif "Teacher" in occupation or "Student" in occupation:
        patterns.extend(["books", "fashion"])
    elif "Business" in occupation:
        patterns.extend(["automotive", "home"])
    
    return list(set(patterns))  # Remove duplicates

def generate_synthetic_customers(count: int = 100) -> List[Customer]:
    """Generate synthetic Indian customer profiles for demo purposes"""
    customers = []
    
    # Tier distribution (more realistic for Indian market)
    tier_distribution = {
        CustomerTier.BRONZE: 0.50,  # 50% - Budget conscious
        CustomerTier.SILVER: 0.30,  # 30% - Mid-market
        CustomerTier.GOLD: 0.15,    # 15% - Premium
        CustomerTier.PLATINUM: 0.05 # 5% - Luxury
    }
    
    for i in range(count):
        # Generate Indian name
        first_name = random.choice(INDIAN_FIRST_NAMES)
        last_name = random.choice(INDIAN_LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        # Generate tier based on distribution
        rand = random.random()
        cumulative = 0
        tier = CustomerTier.BRONZE
        for t, prob in tier_distribution.items():
            cumulative += prob
            if rand <= cumulative:
                tier = t
                break
        
        # Generate occupation and income level
        occupation, income_level = generate_indian_occupation_and_income()
        
        # Generate location
        location = generate_indian_location()
        
        # Generate phone and email
        phone = generate_indian_phone_number()
        email = generate_indian_email(full_name)
        
        # Generate age based on occupation
        if "Student" in occupation:
            age = random.randint(18, 25)
        elif "Engineer" in occupation or "Doctor" in occupation:
            age = random.randint(25, 40)
        elif "Manager" in occupation or "Business" in occupation:
            age = random.randint(35, 55)
        else:
            age = random.randint(22, 60)
        
        # Generate purchase history based on tier and occupation
        if tier in [CustomerTier.GOLD, CustomerTier.PLATINUM]:
            num_purchases = random.randint(20, 40)
        elif tier == CustomerTier.SILVER:
            num_purchases = random.randint(10, 25)
        else:
            num_purchases = random.randint(5, 15)
        
        # Generate categories based on Indian preferences and occupation
        categories = generate_indian_purchase_patterns(tier, occupation)
        
        # Generate actual purchase history with product SKUs (sample from Indian products)
        from data.mock_services import PRODUCTS
        purchase_history = []
        for _ in range(num_purchases):
            category_products = [p for p in PRODUCTS if p.category in categories]
            if category_products:
                selected_product = random.choice(category_products)
                purchase_history.append(selected_product.sku)
        
        # Generate preferences
        preferences = generate_indian_preferences(categories)
        preferences.update({
            "occupation": occupation,
            "income_level": income_level,
            "festival_preferences": random.sample(INDIAN_FESTIVALS, k=random.randint(2, 4)),
            "language_preference": random.choice(INDIAN_LANGUAGES),
            "shopping_frequency": random.choice(["weekly", "monthly", "quarterly", "occasional"]),
            "preferred_payment": random.choice(["upi", "credit_card", "cod", "wallet"]),
            "mobile_first": random.choice([True, False])  # Mobile-first shopping behavior
        })
        
        # Generate loyalty points based on tier and purchase history
        base_points = num_purchases * random.randint(15, 75)
        tier_multiplier = {
            CustomerTier.BRONZE: 1.0,
            CustomerTier.SILVER: 1.5,
            CustomerTier.GOLD: 2.0,
            CustomerTier.PLATINUM: 3.0
        }
        loyalty_points = int(base_points * tier_multiplier[tier])
        
        # Generate customer ID
        customer_id = f"customer_{i+1:03d}"
        
        # Generate channel preferences (more mobile-focused in India)
        channel_preferences = []
        if preferences["mobile_first"]:
            channel_preferences.extend([ChannelType.MOBILE, ChannelType.WHATSAPP])
        else:
            channel_preferences.extend([ChannelType.WEB, ChannelType.MOBILE])
        
        # Add additional channels based on tier
        if tier in [CustomerTier.GOLD, CustomerTier.PLATINUM]:
            channel_preferences.extend([ChannelType.TELEGRAM, ChannelType.VOICE_ASSISTANT])
        
        channel_preferences = list(set(channel_preferences))  # Remove duplicates
        
        customer = Customer(
            id=customer_id,
            name=full_name,
            email=email,
            phone=phone,
            age=age,
            location=location,
            tier=tier,
            loyalty_points=loyalty_points,
            purchase_history=purchase_history,
            preferences=preferences,
            channel_preferences=channel_preferences,
            created_at=fake.date_time_between(start_date='-2y', end_date='now'),
            last_active=fake.date_time_between(start_date='-30d', end_date='now')
        )
        
        customers.append(customer)
    
    return customers

# Generate 100 Indian customers
CUSTOMERS = generate_synthetic_customers(100)