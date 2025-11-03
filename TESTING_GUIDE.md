# Testing Guide

## Complete End-to-End Testing

### Prerequisites
1. Install dependencies: `pip install -r requirements.txt`
2. (Optional) Set up Gemini API key in `.env` file
3. Start the server: `python main.py`

### Test Scenario 1: Complete Purchase Flow with UPI

1. **Start the application**
   - Open http://localhost:8000
   - Select a customer (e.g., "Arjun Sharma from Mumbai")

2. **Product Discovery**
   - Message: "I'm looking for a smartphone"
   - Expected: Personalized recommendations with Indian brands

3. **Check Inventory**
   - Message: "Is PHONE001 available in Mumbai?"
   - Expected: Real-time inventory check across stores

4. **Add to Cart**
   - Message: "Add PHONE001 to cart"
   - Expected: Item added, cart total shown

5. **Apply Promotions**
   - Message: "Apply DIWALI20 promo code"
   - Expected: Discount applied, updated total

6. **Process UPI Payment**
   - Message: "Pay via UPI"
   - Expected: UPI transaction processing simulation with:
     - Transaction ID
     - UPI reference number
     - Gateway confirmation
     - Success/failure handling

7. **Order Confirmation**
   - Expected: Order ID, tracking number, delivery date

### Test Scenario 2: Channel Switching

1. Start conversation on Web
2. Switch channel to WhatsApp
3. Continue conversation: "Show me laptops"
4. Expected: Context preserved, seamless transition

### Test Scenario 3: Real-Time Inventory

1. Check product availability: "Check stock for LAPTOP001"
2. Expected: Real-time stock levels across:
   - Online warehouse
   - Mumbai store
   - Delhi store
   - Bangalore store

### Test Scenario 4: Payment Methods Testing

Test all Indian payment methods:

#### UPI Payment
- Message: "Pay ₹5000 via UPI"
- Expected: UPI transaction simulation with gateway response

#### COD Payment
- Message: "Pay via COD"
- Expected: COD confirmation with delivery instructions

#### Wallet Payment
- Message: "Pay via Paytm wallet"
- Expected: Wallet transaction processing

#### Credit Card
- Message: "Pay via credit card"
- Expected: Card payment processing

### Test Scenario 5: Post-Purchase Support

1. **Track Order**
   - Message: "Track my order ORD_123456"
   - Expected: Real-time tracking information

2. **Return Request**
   - Message: "I want to return order ORD_123456"
   - Expected: Return processing with refund calculation

3. **Feedback**
   - Message: "I want to give feedback"
   - Expected: Feedback solicitation with survey

## API Testing

### Using curl

```bash
# Start conversation
curl -X POST http://localhost:8000/api/start-conversation \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "customer_001", "channel": "web"}'

# Send message
curl -X POST http://localhost:8000/api/send-message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID",
    "message": "Show me smartphones",
    "customer_id": "customer_001",
    "channel": "web"
  }'
```

### Using Python

```python
import requests

# Start conversation
response = requests.post(
    "http://localhost:8000/api/start-conversation",
    json={"customer_id": "customer_001", "channel": "web"}
)
session_id = response.json()["session_id"]

# Send message
response = requests.post(
    "http://localhost:8000/api/send-message",
    json={
        "session_id": session_id,
        "message": "Pay ₹5000 via UPI",
        "customer_id": "customer_001",
        "channel": "web"
    }
)
print(response.json())
```

## Expected Behaviors

### Real-Time Features
✅ All inventory checks happen in real-time  
✅ Payment processing simulates gateway delays  
✅ Session state persists across channel switches  
✅ WebSocket updates in real-time  

### Indian Market Features
✅ Prices in Indian Rupees (₹)  
✅ Indian payment methods (UPI, COD, Wallets)  
✅ Indian cities and locations  
✅ Festival-based promotions  
✅ Indian customer names and profiles  

### Error Handling
✅ Graceful fallback if Gemini API unavailable  
✅ Payment retry mechanisms  
✅ Clear error messages for failed payments  
✅ Validation of all inputs  

## Troubleshooting

### Gemini API Errors
- If you see "GEMINI_API_KEY not found": System will use rule-based fallback
- If you see "google-generativeai not installed": Run `pip install google-generativeai`
- API errors are logged but don't crash the system

### Payment Processing
- UPI payments simulate 92% success rate
- Failed payments can be retried
- All payment methods return proper transaction IDs

### Inventory Issues
- Inventory updates in real-time
- Stock levels decrement when items reserved
- Store locations checked across all Indian stores

