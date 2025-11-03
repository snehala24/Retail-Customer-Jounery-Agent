# Environment Setup Guide

## Google Gemini API Configuration

### Getting Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Setting Up Environment Variables

Create a `.env` file in the project root directory:

```bash
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

**Important Notes:**
- The system works without Gemini API key using intelligent rule-based fallbacks
- Gemini provides enhanced conversational intelligence and intent analysis
- For production, keep your API key secure and never commit it to version control

### Optional Configuration

```bash
# Database Configuration (Optional - SQLite by default)
DATABASE_URL=sqlite:///./sales_agent.db

# Redis Configuration (Optional - for session management)
REDIS_URL=redis://localhost:6379

# Application Settings
DEMO_MODE=True
WS_HOST=localhost
WS_PORT=8000
```

## Testing Payment Methods

The system supports real-time simulation of Indian payment methods:

### Supported Payment Methods:
- **UPI**: Google Pay, PhonePe, Paytm, BHIM UPI
- **Credit/Debit Cards**: Visa, Mastercard, RuPay
- **Net Banking**: All major Indian banks
- **Wallets**: Paytm, PhonePe, Amazon Pay
- **COD**: Cash on Delivery

### Testing UPI Payments:
1. Select a customer from the interface
2. Add items to cart
3. Proceed to checkout
4. Select "UPI" as payment method
5. The system will simulate UPI transaction processing with realistic responses

### Payment Flow:
- Real-time transaction processing simulation
- Success/failure scenarios (92% success rate for UPI)
- Transaction IDs and reference numbers
- Gateway responses
- Retry mechanisms

## Real-Time Features

All features work in real-time:
- ✅ **Inventory Updates**: Stock levels update across online and store locations
- ✅ **Payment Processing**: Simulated real-time payment gateway interactions
- ✅ **Session Management**: WebSocket connections for live updates
- ✅ **Channel Switching**: Seamless context preservation across channels
- ✅ **Order Tracking**: Real-time order status updates

