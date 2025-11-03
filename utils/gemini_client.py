"""
Google Gemini API Client for conversational AI
"""
import os
from typing import Dict, Any, List, Optional
import asyncio
from functools import lru_cache

# Try to import Gemini, but allow fallback if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

class GeminiClient:
    """Wrapper for Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client"""
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed. Install it with: pip install google-generativeai")
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in environment variables or .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_response(
        self, 
        prompt: str, 
        context: Optional[List[Dict[str, str]]] = None,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """Generate response using Gemini"""
        try:
            # Build conversation history
            if context:
                # Convert context to Gemini format
                conversation = []
                for msg in context:
                    role = "user" if msg.get("role") == "customer" else "model"
                    conversation.append({
                        "role": role,
                        "parts": [msg.get("content", "")]
                    })
            else:
                conversation = []
            
            # Create generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # Build full prompt
            full_prompt = prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            
            # Generate response in executor to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fallback to simple response
            return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    async def analyze_intent(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze customer intent from message"""
        system_instruction = """You are an AI assistant analyzing customer messages for a retail e-commerce platform.
Analyze the customer's intent and return a JSON response with:
- intent: one of ["recommendation", "purchase", "pricing", "inventory", "post_purchase", "general_inquiry", "payment", "channel_switch"]
- confidence: float between 0 and 1
- entities: dict with extracted entities like product names, categories, etc.
- urgency: one of ["low", "medium", "high"]

Focus on Indian retail context and common Indian customer queries."""
        
        context_info = ""
        if context:
            context_info = f"\nCustomer context: Tier={context.get('tier', 'bronze')}, Location={context.get('location', 'India')}"
        
        prompt = f"""Analyze this customer message and return ONLY valid JSON (no markdown, no explanation):
Message: "{message}"
{context_info}

Return JSON format:
{{
    "intent": "recommendation",
    "confidence": 0.9,
    "entities": {{"category": "electronics", "product": "smartphone"}},
    "urgency": "medium"
}}"""
        
        try:
            response_text = await self.generate_response(
                prompt,
                system_instruction=system_instruction,
                temperature=0.3  # Lower temperature for more consistent intent analysis
            )
            
            # Try to extract JSON from response
            import json
            import re
            
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\n?', '', response_text)
            response_text = re.sub(r'```\n?', '', response_text)
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate structure
            if "intent" not in result:
                raise ValueError("Invalid intent analysis response")
            
            return result
            
        except Exception as e:
            print(f"Intent analysis error: {e}")
            # Fallback to simple rule-based intent
            return self._fallback_intent_analysis(message)
    
    def _fallback_intent_analysis(self, message: str) -> Dict[str, Any]:
        """Fallback intent analysis using simple rules"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["recommend", "suggest", "what should", "help me find"]):
            return {"intent": "recommendation", "confidence": 0.7, "entities": {}, "urgency": "medium"}
        elif any(word in message_lower for word in ["buy", "purchase", "order", "checkout", "add to cart"]):
            return {"intent": "purchase", "confidence": 0.8, "entities": {}, "urgency": "high"}
        elif any(word in message_lower for word in ["price", "cost", "how much"]):
            return {"intent": "pricing", "confidence": 0.7, "entities": {}, "urgency": "medium"}
        elif any(word in message_lower for word in ["stock", "available", "inventory", "in stock"]):
            return {"intent": "inventory", "confidence": 0.8, "entities": {}, "urgency": "medium"}
        elif any(word in message_lower for word in ["return", "exchange", "refund", "track"]):
            return {"intent": "post_purchase", "confidence": 0.8, "entities": {}, "urgency": "medium"}
        elif any(word in message_lower for word in ["upi", "payment", "pay", "cod", "wallet"]):
            return {"intent": "payment", "confidence": 0.8, "entities": {}, "urgency": "high"}
        else:
            return {"intent": "general_inquiry", "confidence": 0.5, "entities": {}, "urgency": "low"}
    
    async def generate_conversation_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        customer_context: Dict[str, Any],
        agent_type: str = "sales"
    ) -> str:
        """Generate conversational response based on context"""
        
        system_instructions = {
            "sales": """You are a helpful AI sales assistant for an Indian retail e-commerce platform. 
Your role is to:
- Greet customers warmly with Indian cultural awareness (use "Namaste" when appropriate)
- Provide personalized product recommendations
- Help customers find products that match their preferences
- Guide them through the purchase process
- Be friendly, professional, and culturally sensitive

Key points:
- Use Indian Rupees (₹) for all prices
- Understand Indian festivals (Diwali, Holi, etc.)
- Support Indian payment methods (UPI, COD, wallets)
- Reference Indian cities and locations
- Be concise but warm in responses""",
            
            "recommendation": """You are a product recommendation specialist for an Indian retail platform.
Provide helpful, personalized product recommendations based on customer preferences and history.""",
            
            "payment": """You are a payment processing assistant. Help customers complete payments using Indian payment methods like UPI, COD, cards, and wallets.""",
            
            "inventory": """You are an inventory specialist. Check product availability across online and store locations in India.""",
            
            "fulfillment": """You are a fulfillment specialist. Help customers choose delivery options (home delivery, store pickup) and track orders.""",
            
            "loyalty": """You are a loyalty program specialist. Help customers understand their tier benefits, points, and available promotions.""",
            
            "post_purchase": """You are a post-purchase support specialist. Help customers with returns, exchanges, tracking, and feedback."""
        }
        
        system_instruction = system_instructions.get(agent_type, system_instructions["sales"])
        
        # Build context string
        context_parts = []
        if customer_context.get("name"):
            context_parts.append(f"Customer name: {customer_context['name']}")
        if customer_context.get("tier"):
            context_parts.append(f"Loyalty tier: {customer_context['tier']}")
        if customer_context.get("location"):
            context_parts.append(f"Location: {customer_context['location']}")
        if customer_context.get("preferences"):
            pref = customer_context['preferences']
            if pref.get("preferred_payment"):
                context_parts.append(f"Preferred payment: {pref['preferred_payment']}")
        
        context_string = "\n".join(context_parts) if context_parts else "No specific context available."
        
        # Build conversation history
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-5:]  # Last 5 messages
            history_text = "\n".join([
                f"{'Customer' if msg.get('role') == 'customer' else 'Assistant'}: {msg.get('content', '')}"
                for msg in recent_history
            ])
        
        prompt = f"""Context:
{context_string}

Recent conversation:
{history_text}

Customer message: "{message}"

Generate a helpful, warm, and culturally appropriate response. Be concise (2-3 sentences max) and actionable."""
        
        try:
            response = await self.generate_response(
                prompt,
                system_instruction=system_instruction,
                temperature=0.8,
                max_tokens=500
            )
            return response
        except Exception as e:
            print(f"Conversation generation error: {e}")
            return "I'm here to help! Could you please tell me more about what you're looking for?"

# Global instance
_gemini_client: Optional[GeminiClient] = None

def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

