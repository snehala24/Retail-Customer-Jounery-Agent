from typing import Dict, Any, List, Optional
from models import Customer, ConversationSession, ChannelType, AgentTask
from agents.base_agent import BaseAgent
from agents.recommendation_agent import RecommendationAgent
from agents.inventory_agent import InventoryAgent
from agents.payment_agent import PaymentAgent
from agents.fulfillment_agent import FulfillmentAgent
from agents.loyalty_agent import LoyaltyAgent
from agents.post_purchase_agent import PostPurchaseAgent
from data.synthetic_customers import CUSTOMERS
from data.mock_services import MockProductService
from utils.gemini_client import get_gemini_client
import asyncio
import uuid
from datetime import datetime
import os

class SalesAgent(BaseAgent):
    def __init__(self):
        super().__init__("sales_agent", "sales")
        self.worker_agents = {
            "recommendation": RecommendationAgent(),
            "inventory": InventoryAgent(),
            "payment": PaymentAgent(),
            "fulfillment": FulfillmentAgent(),
            "loyalty": LoyaltyAgent(),
            "post_purchase": PostPurchaseAgent()
        }
        self.active_sessions: Dict[str, ConversationSession] = {}
        self.customer_database = {c.id: c for c in CUSTOMERS}
        # Initialize Gemini client if API key is available
        self.use_gemini = bool(os.getenv("GEMINI_API_KEY"))
        if self.use_gemini:
            try:
                self.gemini_client = get_gemini_client()
                print("✓ Gemini AI enabled - Enhanced conversational intelligence active")
            except Exception as e:
                print(f"⚠ Warning: Could not initialize Gemini client: {e}")
                print("  System will use rule-based fallback logic")
                self.use_gemini = False
                self.gemini_client = None
        else:
            print("ℹ Gemini AI not configured - Using rule-based conversation logic")
            print("  Set GEMINI_API_KEY environment variable to enable Gemini AI")
            self.gemini_client = None
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Main sales agent task processing"""
        task_data = task.task_data
        action = task_data.get("action")
        customer_id = task.customer_id
        
        if action == "start_conversation":
            return await self._start_conversation(customer_id, task_data)
        elif action == "process_message":
            return await self._process_message(customer_id, task_data)
        elif action == "switch_channel":
            return await self._switch_channel(customer_id, task_data)
        elif action == "get_recommendations":
            return await self._get_recommendations(customer_id, task_data)
        elif action == "check_inventory":
            return await self._check_inventory(customer_id, task_data)
        elif action == "process_payment":
            return await self._process_payment(customer_id, task_data)
        elif action == "handle_fulfillment":
            return await self._handle_fulfillment(customer_id, task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _start_conversation(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new conversation session"""
        channel = ChannelType(task_data.get("channel", "web"))
        customer = self.customer_database.get(customer_id)
        
        if not customer:
            return {"error": "Customer not found"}
        
        session = ConversationSession(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            channel=channel,
            context={
                "customer": customer.model_dump(),
                "conversation_state": "greeting",
                "intent": None,
                "current_products": [],
                "cart": []
            }
        )
        
        self.active_sessions[session.id] = session
        
        # Generate personalized greeting
        greeting = await self._generate_greeting(customer, channel)
        
        return {
            "session_id": session.id,
            "message": greeting,
            "customer": customer.model_dump(),
            "suggested_actions": await self._get_suggested_actions(customer)
        }
    
    async def _process_message(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming customer message"""
        session_id = task_data.get("session_id")
        message = task_data.get("message", "")
        channel = ChannelType(task_data.get("channel", "web"))
        
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Update session with new message
        session.messages.append({
            "role": "customer",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "channel": channel
        })
        session.last_activity = datetime.now()
        
        # Analyze message intent
        intent = await self._analyze_intent(message, session.context)
        session.context["intent"] = intent
        
        # Route to appropriate worker agent based on intent
        response = await self._route_to_worker_agent(session, intent, message)
        
        # Update session with agent response
        session.messages.append({
            "role": "agent",
            "content": response.get("message", ""),
            "timestamp": datetime.now().isoformat(),
            "channel": channel
        })
        
        return response
    
    async def _switch_channel(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle channel switching while maintaining context"""
        session_id = task_data.get("session_id")
        new_channel = ChannelType(task_data.get("new_channel"))
        
        session = self.active_sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Update session channel
        old_channel = session.channel
        session.channel = new_channel
        
        # Generate channel-specific message
        channel_switch_message = await self._generate_channel_switch_message(
            session.context["customer"], old_channel, new_channel
        )
        
        return {
            "message": channel_switch_message,
            "context_preserved": True,
            "previous_channel": old_channel,
            "current_channel": new_channel
        }
    
    async def _get_recommendations(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get product recommendations"""
        session_id = task_data.get("session_id")
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        # Delegate to recommendation agent
        recommendation_task = {
            "customer": session.context["customer"],
            "preferences": session.context.get("preferences", {}),
            "current_products": session.context.get("current_products", [])
        }
        
        result = await self.worker_agents["recommendation"].execute_task(
            customer_id, recommendation_task
        )
        
        return result
    
    async def _check_inventory(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check product inventory"""
        session_id = task_data.get("session_id")
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        # Delegate to inventory agent
        inventory_task = {
            "products": task_data.get("products", []),
            "location": task_data.get("location"),
            "customer_location": session.context["customer"].get("location")
        }
        
        result = await self.worker_agents["inventory"].execute_task(
            customer_id, inventory_task
        )
        
        return result
    
    async def _process_payment(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment"""
        session_id = task_data.get("session_id")
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        # Delegate to payment agent
        payment_task = {
            "amount": task_data.get("amount"),
            "payment_method": task_data.get("payment_method"),
            "customer": session.context["customer"]
        }
        
        result = await self.worker_agents["payment"].execute_task(
            customer_id, payment_task
        )
        
        return result
    
    async def _handle_fulfillment(self, customer_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle order fulfillment"""
        session_id = task_data.get("session_id")
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        # Delegate to fulfillment agent
        fulfillment_task = {
            "order": task_data.get("order"),
            "customer": session.context["customer"],
            "preferences": task_data.get("fulfillment_preferences", {})
        }
        
        result = await self.worker_agents["fulfillment"].execute_task(
            customer_id, fulfillment_task
        )
        
        return result
    
    async def _generate_greeting(self, customer: Customer, channel: ChannelType) -> str:
        """Generate personalized greeting based on customer and channel"""
        return self._get_indian_greeting(customer, channel.value)
    
    async def _get_suggested_actions(self, customer: Customer) -> List[str]:
        """Get suggested actions based on customer profile"""
        return self._get_indian_suggested_actions(customer)
    
    async def _analyze_intent(self, message: str, context: Dict[str, Any]) -> str:
        """Analyze customer message intent using Gemini or fallback"""
        if self.use_gemini and self.gemini_client:
            try:
                intent_result = await self.gemini_client.analyze_intent(message, context)
                return intent_result.get("intent", "general_inquiry")
            except Exception as e:
                print(f"Gemini intent analysis error: {e}")
                # Fall through to fallback
        
        # Fallback intent analysis
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["recommend", "suggest", "what should", "help me find", "show me"]):
            return "recommendation"
        elif any(word in message_lower for word in ["buy", "purchase", "order", "checkout", "add to cart"]):
            return "purchase"
        elif any(word in message_lower for word in ["price", "cost", "how much", "rupee", "₹"]):
            return "pricing"
        elif any(word in message_lower for word in ["stock", "available", "inventory", "in stock"]):
            return "inventory"
        elif any(word in message_lower for word in ["return", "exchange", "refund", "track order"]):
            return "post_purchase"
        elif any(word in message_lower for word in ["upi", "payment", "pay", "cod", "wallet", "credit card"]):
            return "payment"
        else:
            return "general_inquiry"
    
    async def _route_to_worker_agent(self, session: ConversationSession, intent: str, message: str) -> Dict[str, Any]:
        """Route request to appropriate worker agent"""
        customer_id = session.customer_id
        customer = session.context["customer"]
        
        if intent == "recommendation":
            task_data = {
                "customer": customer,
                "preferences": session.context.get("preferences", {}),
                "message": message
            }
            result = await self.worker_agents["recommendation"].execute_task(customer_id, task_data)
            
            # Enhance response with Indian context
            if result.get("recommendations"):
                indian_message = self._enhance_recommendation_message(result, customer)
                result["message"] = indian_message
            
            return result
        
        elif intent == "inventory":
            task_data = {
                "products": session.context.get("current_products", []),
                "customer_location": customer.get("location"),
                "message": message
            }
            result = await self.worker_agents["inventory"].execute_task(customer_id, task_data)
            
            # Enhance with Indian delivery context
            if result.get("availability_results"):
                indian_message = self._enhance_inventory_message(result, customer)
                result["message"] = indian_message
            
            return result
        
        elif intent == "purchase":
            task_data = {
                "cart": session.context.get("cart", []),
                "customer": customer,
                "message": message
            }
            result = await self.worker_agents["payment"].execute_task(customer_id, task_data)
            
            # Enhance with Indian payment context
            if result.get("payment_options"):
                indian_message = self._enhance_payment_message(result, customer)
                result["message"] = indian_message
            
            return result
        
        else:
            # General inquiry - use Gemini for intelligent response if available
            if self.use_gemini and self.gemini_client:
                try:
                    gemini_response = await self.gemini_client.generate_conversation_response(
                        message=message,
                        conversation_history=session.messages,
                        customer_context=customer,
                        agent_type="sales"
                    )
                    return {
                        "message": gemini_response,
                        "suggested_actions": self._get_indian_suggested_actions_from_customer(customer)
                    }
                except Exception as e:
                    print(f"Gemini response generation error: {e}")
                    # Fall through to default
            
            # Fallback response
            return {
                "message": f"Namaste! I'd be happy to help you, {customer['name'].split()[0]}! I can assist you with product recommendations, inventory checks, pricing, and purchases. What would you like to know?",
                "suggested_actions": self._get_indian_suggested_actions_from_customer(customer)
            }
    
    async def _generate_channel_switch_message(self, customer: Dict[str, Any], old_channel: ChannelType, new_channel: ChannelType) -> str:
        """Generate message for channel switching"""
        name = customer["name"].split()[0]
        
        channel_names = {
            ChannelType.WEB: "our website",
            ChannelType.MOBILE: "our mobile app", 
            ChannelType.WHATSAPP: "WhatsApp",
            ChannelType.TELEGRAM: "Telegram",
            ChannelType.INSTORE_KIOSK: "our in-store kiosk",
            ChannelType.VOICE_ASSISTANT: "our voice assistant"
        }
        
        return f"Hi {name}! I see you've switched to {channel_names[new_channel]}. I've maintained our conversation context, so we can continue right where we left off. How can I assist you?"
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get active session by ID"""
        return self.active_sessions.get(session_id)
    
    def get_customer_sessions(self, customer_id: str) -> List[ConversationSession]:
        """Get all active sessions for a customer"""
        return [session for session in self.active_sessions.values() if session.customer_id == customer_id]
    
    def _get_indian_greeting(self, customer: Customer, channel: str) -> str:
        """Generate culturally appropriate Indian greeting"""
        name = customer.name.split()[0]
        tier = customer.tier.value.title()
        location = customer.location.split(',')[0] if customer.location else "India"
        
        # Time-based greetings
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = f"Good morning {name}! Namaste!"
        elif 12 <= current_hour < 17:
            greeting = f"Good afternoon {name}! Namaste!"
        elif 17 <= current_hour < 21:
            greeting = f"Good evening {name}! Namaste!"
        else:
            greeting = f"Hello {name}! Namaste!"
        
        # Channel-specific greetings
        if channel == "whatsapp":
            greeting += f" 👋 I'm your AI sales assistant from {location}."
        elif channel == "mobile":
            greeting += f" 📱 Welcome to our mobile app!"
        elif channel == "voice_assistant":
            greeting += f" 🎤 How can I help you today?"
        else:
            greeting += f" Welcome to our store!"
        
        # Tier-specific messaging
        if customer.tier.value == "platinum":
            greeting += f" As our valued {tier} member, you have exclusive access to our premium collection."
        elif customer.tier.value == "gold":
            greeting += f" Thank you for being a {tier} member!"
        
        return greeting
    
    def _get_indian_suggested_actions(self, customer: Customer) -> List[str]:
        """Generate Indian context-aware suggested actions"""
        actions = []
        
        # Festival-based suggestions
        current_month = datetime.now().month
        if current_month in [10, 11]:  # Diwali season
            actions.extend([
                "🎆 Show me Diwali offers",
                "🪔 Diwali gift suggestions",
                "✨ Festival shopping"
            ])
        elif current_month == 3:  # Holi season
            actions.extend([
                "🌈 Holi special deals",
                "🎨 Color festival offers"
            ])
        
        # Occupation-based suggestions
        occupation = customer.preferences.get("occupation", "")
        if "Engineer" in occupation or "Doctor" in occupation:
            actions.extend([
                "💻 Latest smartphones",
                "📚 Professional books",
                "⚡ Tech gadgets"
            ])
        elif "Student" in occupation:
            actions.extend([
                "📖 Study materials",
                "💻 Budget laptops",
                "🎒 Student essentials"
            ])
        elif "Business" in occupation:
            actions.extend([
                "🚗 Business vehicles",
                "🏠 Office equipment",
                "💼 Professional wear"
            ])
        
        # Location-based suggestions
        location = customer.location.lower()
        if "mumbai" in location:
            actions.extend(["🏙️ Mumbai store offers", "🚚 Same-day delivery"])
        elif "delhi" in location:
            actions.extend(["🏛️ Delhi store deals", "📦 Express delivery"])
        elif "bangalore" in location:
            actions.extend(["💻 Tech hub offers", "🚀 Startup deals"])
        
        # Payment preference suggestions
        preferred_payment = customer.preferences.get("preferred_payment", "")
        if preferred_payment == "upi":
            actions.extend(["💳 UPI payment offers", "📱 Mobile wallet deals"])
        elif preferred_payment == "cod":
            actions.extend(["📦 COD available", "💰 Cash on delivery"])
        
        # Default suggestions
        actions.extend([
            "🛍️ Browse products",
            "🔍 Search items",
            "💬 Ask questions",
            "📞 Contact support"
        ])
        
        return actions[:6]  # Return top 6 suggestions
    
    def _enhance_recommendation_message(self, result: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Enhance recommendation message with Indian context"""
        name = customer["name"].split()[0]
        recommendations = result.get("recommendations", [])
        
        if not recommendations:
            return f"Sorry {name}, I couldn't find any recommendations right now. Let me try a different approach."
        
        # Check for festival context
        current_month = datetime.now().month
        festival_context = ""
        if current_month in [10, 11]:  # Diwali season
            festival_context = " Perfect timing for Diwali shopping! 🪔"
        elif current_month == 3:  # Holi season
            festival_context = " Great for Holi celebrations! 🌈"
        
        # Check for location-based context
        location = customer.get("location", "").lower()
        location_context = ""
        if "mumbai" in location:
            location_context = " I've also checked our Mumbai store availability."
        elif "delhi" in location:
            location_context = " I've verified our Delhi store stock."
        elif "bangalore" in location:
            location_context = " I've confirmed our Bangalore store inventory."
        
        return f"Namaste {name}! I've found {len(recommendations)} great products for you.{festival_context}{location_context} These are personalized based on your {customer.get('tier', 'bronze')} membership and preferences."
    
    def _enhance_inventory_message(self, result: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Enhance inventory message with Indian delivery context"""
        name = customer["name"].split()[0]
        availability_results = result.get("availability_results", [])
        
        if not availability_results:
            return f"Sorry {name}, I'm having trouble checking inventory right now. Please try again."
        
        available_count = sum(1 for r in availability_results if r.get("available"))
        total_count = len(availability_results)
        
        if available_count == 0:
            return f"Sorry {name}, these items are currently out of stock. But don't worry! I can suggest similar products or notify you when they're back in stock."
        elif available_count == total_count:
            return f"Excellent news {name}! All items are available. I can arrange delivery to your location in {customer.get('location', 'India')} within 2-3 business days, or you can pick up from our nearest store."
        else:
            return f"Good news {name}! {available_count} out of {total_count} items are available. I can show you alternatives for the unavailable items and arrange delivery for the available ones."
    
    def _enhance_payment_message(self, result: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Enhance payment message with Indian payment methods"""
        name = customer["name"].split()[0]
        preferred_payment = customer.get("preferences", {}).get("preferred_payment", "")
        
        payment_context = ""
        if preferred_payment == "upi":
            payment_context = " I see you prefer UPI payments - that's perfect! We support PhonePe, Google Pay, and Paytm."
        elif preferred_payment == "cod":
            payment_context = " I can arrange Cash on Delivery for your order - very convenient!"
        elif preferred_payment == "wallet":
            payment_context = " I can process payment through your digital wallet."
        
        return f"Namaste {name}! I'm ready to process your payment.{payment_context} We also accept credit cards, net banking, and UPI. What's your preferred payment method?"
    
    def _get_indian_suggested_actions_from_customer(self, customer: Dict[str, Any]) -> List[str]:
        """Get Indian context-aware suggested actions from customer data"""
        actions = []
        name = customer["name"].split()[0]
        
        # Festival-based suggestions
        current_month = datetime.now().month
        if current_month in [10, 11]:  # Diwali season
            actions.extend([
                "🎆 Show me Diwali offers",
                "🪔 Diwali gift suggestions",
                "✨ Festival shopping"
            ])
        elif current_month == 3:  # Holi season
            actions.extend([
                "🌈 Holi special deals",
                "🎨 Color festival offers"
            ])
        
        # Occupation-based suggestions
        occupation = customer.get("preferences", {}).get("occupation", "")
        if "Engineer" in occupation or "Doctor" in occupation:
            actions.extend([
                "💻 Latest smartphones",
                "📚 Professional books",
                "⚡ Tech gadgets"
            ])
        elif "Student" in occupation:
            actions.extend([
                "📖 Study materials",
                "💻 Budget laptops",
                "🎒 Student essentials"
            ])
        elif "Business" in occupation:
            actions.extend([
                "🚗 Business vehicles",
                "🏠 Office equipment",
                "💼 Professional wear"
            ])
        
        # Location-based suggestions
        location = customer.get("location", "").lower()
        if "mumbai" in location:
            actions.extend(["🏙️ Mumbai store offers", "🚚 Same-day delivery"])
        elif "delhi" in location:
            actions.extend(["🏛️ Delhi store deals", "📦 Express delivery"])
        elif "bangalore" in location:
            actions.extend(["💻 Tech hub offers", "🚀 Startup deals"])
        
        # Payment preference suggestions
        preferred_payment = customer.get("preferences", {}).get("preferred_payment", "")
        if preferred_payment == "upi":
            actions.extend(["💳 UPI payment offers", "📱 Mobile wallet deals"])
        elif preferred_payment == "cod":
            actions.extend(["📦 COD available", "💰 Cash on delivery"])
        
        # Default suggestions
        actions.extend([
            "🛍️ Browse products",
            "🔍 Search items",
            "💬 Ask questions",
            "📞 Contact support"
        ])
        
        return actions[:6]  # Return top 6 suggestions
