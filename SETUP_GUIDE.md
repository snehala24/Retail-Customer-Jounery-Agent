# Retail Customer Journey Agent - Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or navigate to the project directory**
```bash
cd Retail-Customer-Jounery-Agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python main.py
```

4. **Access the demo interface**
- Web Interface: http://localhost:8000
- Mobile Interface: http://localhost:8000/mobile
- API Documentation: http://localhost:8000/docs

## 📋 Features Overview

### Multi-Channel Support
- **Web Chat**: Browser-based chat interface
- **Mobile App**: Responsive mobile interface
- **WhatsApp**: WhatsApp integration (webhook-ready)
- **Telegram**: Telegram bot integration
- **In-Store Kiosk**: Physical store kiosk interface
- **Voice Assistant**: Voice command processing

### Indian-Specific Features
- **Payment Methods**: UPI, Credit/Debit Cards, Net Banking, Wallets (Paytm, PhonePe), COD
- **Currency**: All prices in Indian Rupees (₹)
- **Shipping**: Blue Dart, 3-5 day delivery
- **Stores**: Mumbai, Delhi, Bangalore store locations
- **Festivals**: Diwali, Holi, Dussehra promotions
- **Tax**: 18% GST calculation
- **Free Shipping**: Orders over ₹500

### Agent System
1. **Sales Agent**: Main orchestrator, handles conversations
2. **Recommendation Agent**: Personalized product suggestions
3. **Inventory Agent**: Real-time stock checking
4. **Payment Agent**: Payment processing with Indian gateways
5. **Fulfillment Agent**: Order scheduling and delivery
6. **Loyalty Agent**: Points, tier benefits, promotions
7. **Post-Purchase Agent**: Returns, tracking, feedback

## 🎯 Demo Scenarios

### Scenario 1: Product Discovery
1. Select a customer from the sidebar
2. Ask: "I'm looking for a smartphone"
3. Agent provides personalized recommendations
4. Check inventory availability

### Scenario 2: Channel Switching
1. Start conversation on mobile app
2. Switch to WhatsApp via channel selector
3. Continue conversation seamlessly
4. Context is preserved across channels

### Scenario 3: Complete Purchase Flow
1. Add products to cart
2. Check inventory for your location
3. Apply loyalty points and promotions
4. Process payment via UPI/COD/Card
5. Schedule fulfillment (ship-to-home or pickup)
6. Receive order confirmation

### Scenario 4: Post-Purchase Support
1. Request return for an order
2. Track shipment status
3. Provide feedback
4. Handle complaints with escalation

## 📊 Indian Dataset

The system includes:
- **100+ Synthetic Indian Customers** with:
  - Indian names (Arjun, Priya, etc.)
  - Locations across major Indian cities
  - Tier-based loyalty (Bronze, Silver, Gold, Platinum)
  - Purchase history with Indian products
  - Festival preferences (Diwali, Holi, etc.)
  - Payment preferences (UPI, COD, etc.)

- **60+ Indian Products** across categories:
  - Electronics (Samsung, OnePlus, Xiaomi, etc.)
  - Fashion (Fabindia, W, Manyavar, etc.)
  - Home (LG, Samsung, Preethi, etc.)
  - Sports (Cricket equipment, Nike, Adidas)
  - Beauty (Lakme, Maybelline, Nykaa)
  - Books (Indian authors)
  - Food (Haldiram's, Bikanervala, MTR)

- **Store Locations**:
  - Mumbai Store - Andheri
  - Delhi Store - Connaught Place
  - Bangalore Store - MG Road

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file for customization:
```
OPENAI_API_KEY=your_key_here (if using OpenAI)
DEMO_MODE=true
```

### Indian Payment Gateways
- **UPI**: Razorpay
- **Cards**: Razorpay
- **Wallets**: Paytm

## 🧪 Testing

### Run Test Scenarios
```bash
python test_demo.py
```

### Manual Testing
1. Select a customer (e.g., customer_001)
2. Start a conversation
3. Try different intents:
   - "Show me phones"
   - "Check stock for PHONE001"
   - "I want to buy this"
   - "Track my order"
   - "Return my item"

## 📱 API Endpoints

### Customer Management
- `GET /api/customers` - List all customers
- `POST /api/start-conversation` - Start new conversation

### Messaging
- `POST /api/send-message` - Send message to agent
- `POST /api/switch-channel` - Switch conversation channel
- `WebSocket /ws/{customer_id}` - Real-time chat

### Products
- `GET /api/products` - List products
- `GET /api/products/search?q=query` - Search products

### Workflows
- `POST /api/execute-workflow` - Execute complete workflow
- `GET /api/workflow-status/{workflow_id}` - Check workflow status

## 🌟 Key Highlights

### Indian Market Optimization
- ✅ All prices in ₹ (Rupees)
- ✅ GST calculation (18%)
- ✅ UPI payment support
- ✅ COD (Cash on Delivery)
- ✅ Indian cities and store locations
- ✅ Blue Dart shipping
- ✅ Festival-based promotions
- ✅ Mobile-first customer profiles

### Agent Orchestration
- ✅ Multi-agent coordination
- ✅ Context preservation
- ✅ Channel switching
- ✅ Real-time inventory
- ✅ Personalized recommendations
- ✅ End-to-end purchase flow

## 📞 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review `PROJECT_SUMMARY.md`
3. Check `DEMO_GUIDE.md` for detailed scenarios

## 🎉 Ready to Demo!

The system is now ready for live demonstration. Start the server and begin testing the multi-agent retail customer journey system!

