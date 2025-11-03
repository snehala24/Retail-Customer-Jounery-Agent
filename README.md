# AI-Driven Retail Customer Journey Agent

A comprehensive **end-to-end functional** multi-agent system that revolutionizes retail sales experience by providing seamless, personalized customer interactions across online and physical channels, specifically optimized for the **Indian market**.

## 🎯 Problem Statement

Customers face fragmented experiences when moving between online browsing, mobile app shopping, messaging apps, and in-store interactions. This system provides a unified, human-like conversational journey that anticipates needs, provides tailored recommendations, and facilitates sales across all channels.

## 🏗️ System Architecture

### Core Components
- **Sales Agent**: Main orchestrator managing multi-channel conversations
- **Worker Agents**: Specialized agents handling specific tasks
  - Recommendation Agent (Personalized product suggestions)
  - Inventory Agent (Real-time stock across warehouses and stores)
  - Payment Agent (UPI, Cards, COD, Wallets)
  - Fulfillment Agent (Ship-to-home, Click & Collect, In-store pickup)
  - Loyalty and Offers Agent (Points, promotions, tier benefits)
  - Post-Purchase Support Agent (Returns, tracking, feedback)

### Features
- ✅ **Multi-channel support**: Web, Mobile, WhatsApp, Telegram, In-Store Kiosk, Voice Assistant
- ✅ **Real-time inventory**: Check stock across online and multiple Indian store locations
- ✅ **Personalized recommendations**: Based on customer tier, purchase history, preferences
- ✅ **Indian payment methods**: UPI, Credit/Debit Cards, Net Banking, Wallets, COD
- ✅ **Cross-channel session continuity**: Seamless switching with context preservation
- ✅ **End-to-end purchase flow**: Recommendation → Inventory → Payment → Fulfillment → Follow-up
- ✅ **Post-purchase support**: Returns, exchanges, tracking, feedback collection

## 🇮🇳 Indian Market Features

- **Currency**: All prices in Indian Rupees (₹)
- **Payment Methods**: UPI (Google Pay, PhonePe), Credit/Debit Cards, Net Banking, Wallets (Paytm), COD
- **Tax**: 18% GST automatically calculated
- **Shipping**: Blue Dart, free shipping over ₹500, 3-5 day delivery
- **Stores**: Mumbai (Andheri), Delhi (Connaught Place), Bangalore (MG Road)
- **Festivals**: Diwali, Holi, Dussehra promotions
- **Products**: Indian brands (Samsung, OnePlus, Fabindia, Lakme, etc.)
- **Customers**: 100+ synthetic Indian customer profiles

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up Gemini API key:**
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   - **Note:** The system works without Gemini API key using rule-based fallbacks, but Gemini provides better conversational intelligence.

3. **Run the application:**
```bash
python main.py
```

4. **Access the demo:**
- Web Interface: http://localhost:8000
- Mobile Interface: http://localhost:8000/mobile
- API Documentation: http://localhost:8000/docs

## 🤖 Gemini AI Integration

This system uses **Google Gemini** for intelligent conversation handling:
- **Intent Analysis**: Understands customer queries with high accuracy
- **Natural Conversations**: Generates context-aware, culturally sensitive responses
- **Indian Market Optimization**: Understands Indian context, festivals, payment methods
- **Fallback Support**: Works even without API key using rule-based logic

## 📋 Demo Scenarios

### Scenario 1: Product Discovery & Recommendation
1. Select an Indian customer (e.g., "Arjun Sharma from Mumbai")
2. Ask: "I'm looking for a smartphone"
3. Agent provides personalized recommendations based on tier and preferences
4. Check real-time inventory across Mumbai, Delhi, Bangalore stores

### Scenario 2: Channel Switching
1. Start conversation on mobile app
2. Switch to WhatsApp via channel selector
3. Continue seamlessly: "What about laptops?"
4. Switch to in-store kiosk
5. Context preserved throughout - cart, conversation, preferences intact

### Scenario 3: Complete Purchase Flow
1. Add product to cart: "Add PHONE001 to cart"
2. Check inventory: "Is it available in Mumbai?"
3. Apply loyalty points and Diwali promotion
4. Process payment via UPI: "Pay via UPI"
5. Schedule fulfillment: "Ship to my home" or "Pickup at Mumbai store"
6. Receive order confirmation with tracking number

### Scenario 4: Post-Purchase Support
1. Request return: "I want to return my order"
2. Track shipment: "Track my order"
3. Provide feedback: "Rate my experience"
4. Handle complaints with automatic escalation

## 📊 Dataset

- **100+ Indian Customers**: Realistic profiles with:
  - Indian names (Arjun, Priya, Vikram, Sneha, etc.)
  - Locations across 50+ Indian cities
  - Tier-based loyalty (Bronze, Silver, Gold, Platinum)
  - Purchase history with Indian products
  - Festival preferences (Diwali, Holi, etc.)
  - Payment preferences (UPI, COD, Wallet)

- **60+ Indian Products**:
  - Electronics: Samsung Galaxy, OnePlus, Xiaomi, Realme
  - Fashion: Fabindia, W, Manyavar, Libas
  - Home: LG, Samsung, Preethi, Godrej
  - Sports: Cricket equipment, Nike, Adidas
  - Beauty: Lakme, Maybelline, Nykaa
  - Books: Indian authors
  - Food: Haldiram's, Bikanervala, MTR

## 🔧 Technical Stack

- **Backend**: FastAPI (Python) with async/await
- **Real-time**: WebSocket connections
- **Data Models**: Pydantic with validation
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Architecture**: Multi-agent system with orchestration

## 📖 Documentation

- **Setup Guide**: See `SETUP_GUIDE.md`
- **Implementation Notes**: See `IMPLEMENTATION_NOTES.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`
- **Demo Guide**: See `DEMO_GUIDE.md`
- **API Docs**: http://localhost:8000/docs

## 🎯 Key Deliverables

✅ **Multi-channel engagement**: Web, mobile, WhatsApp, Telegram, in-store, voice  
✅ **Context preservation**: Seamless channel switching with conversation history  
✅ **End-to-end orchestration**: Recommendation → Inventory → Payment → Fulfillment → Follow-up  
✅ **Indian market optimization**: UPI, COD, GST, Indian cities, festivals  
✅ **Fully functional**: Not just examples - complete working system  

## 🎉 Ready for Demo!

The system is **fully functional** and ready for live demonstration. Start the server and experience the complete retail customer journey!

---

**Built for the Indian retail market with love ❤️**
