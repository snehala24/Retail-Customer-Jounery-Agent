from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models import AgentTask, OrderStatus
import random
from datetime import datetime, timedelta

class PostPurchaseAgent(BaseAgent):
    def __init__(self):
        super().__init__("post_purchase_agent", "post_purchase")
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle post-purchase support tasks"""
        task_data = task.task_data
        customer_id = task.customer_id
        
        action = task_data.get("action", "handle_inquiry")
        
        if action == "handle_return":
            return await self._handle_return(task_data)
        elif action == "handle_exchange":
            return await self._handle_exchange(task_data)
        elif action == "track_shipment":
            return await self._track_shipment(task_data)
        elif action == "solicit_feedback":
            return await self._solicit_feedback(task_data)
        elif action == "handle_complaint":
            return await self._handle_complaint(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _handle_return(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product return request"""
        order_id = task_data.get("order_id")
        items_to_return = task_data.get("items", [])
        reason = task_data.get("reason", "No longer needed")
        customer = task_data.get("customer", {})
        
        if not order_id or not items_to_return:
            return {"error": "Order ID and items required"}
        
        # Validate return eligibility
        return_eligibility = await self._check_return_eligibility(order_id, items_to_return)
        
        if not return_eligibility["eligible"]:
            return {
                "return_processed": False,
                "error": return_eligibility["error"],
                "message": return_eligibility["message"]
            }
        
        # Process return
        return_result = await self._process_return_request(order_id, items_to_return, reason, customer)
        
        # Calculate refund amount
        refund_amount = return_result["refund_amount"]
        
        # Generate return label
        return_label = await self._generate_return_label(return_result["return_id"], customer)
        
        return {
            "return_processed": True,
            "return_id": return_result["return_id"],
            "refund_amount": refund_amount,
            "return_label": return_label,
            "return_instructions": return_result["instructions"],
            "message": self._generate_return_message(customer, refund_amount, return_result["return_id"])
        }
    
    async def _handle_exchange(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product exchange request"""
        order_id = task_data.get("order_id")
        items_to_exchange = task_data.get("items", [])
        new_items = task_data.get("new_items", [])
        reason = task_data.get("reason", "Size/color preference")
        customer = task_data.get("customer", {})
        
        if not order_id or not items_to_exchange or not new_items:
            return {"error": "Order ID, items to exchange, and new items required"}
        
        # Validate exchange eligibility
        exchange_eligibility = await self._check_exchange_eligibility(order_id, items_to_exchange, new_items)
        
        if not exchange_eligibility["eligible"]:
            return {
                "exchange_processed": False,
                "error": exchange_eligibility["error"],
                "message": exchange_eligibility["message"]
            }
        
        # Process exchange
        exchange_result = await self._process_exchange_request(
            order_id, items_to_exchange, new_items, reason, customer
        )
        
        return {
            "exchange_processed": True,
            "exchange_id": exchange_result["exchange_id"],
            "price_difference": exchange_result["price_difference"],
            "exchange_instructions": exchange_result["instructions"],
            "new_order_id": exchange_result.get("new_order_id"),
            "message": self._generate_exchange_message(customer, exchange_result)
        }
    
    async def _track_shipment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track order shipment"""
        order_id = task_data.get("order_id")
        tracking_number = task_data.get("tracking_number")
        customer = task_data.get("customer", {})
        
        if not order_id and not tracking_number:
            return {"error": "Order ID or tracking number required"}
        
        # Get tracking information
        tracking_info = await self._get_tracking_information(order_id, tracking_number)
        
        if not tracking_info:
            return {
                "tracking_found": False,
                "error": "Tracking information not found",
                "message": "I couldn't find tracking information for this order. Please check your order number."
            }
        
        return {
            "tracking_found": True,
            "tracking_info": tracking_info,
            "message": self._generate_tracking_message(customer, tracking_info)
        }
    
    async def _solicit_feedback(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Solicit customer feedback"""
        order_id = task_data.get("order_id")
        customer = task_data.get("customer", {})
        feedback_type = task_data.get("feedback_type", "general")
        
        if not order_id:
            return {"error": "Order ID required"}
        
        # Generate feedback request
        feedback_request = await self._generate_feedback_request(order_id, customer, feedback_type)
        
        return {
            "feedback_requested": True,
            "feedback_request": feedback_request,
            "message": self._generate_feedback_solicitation_message(customer, feedback_type)
        }
    
    async def _handle_complaint(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer complaint"""
        complaint_type = task_data.get("complaint_type", "general")
        complaint_details = task_data.get("complaint_details", "")
        customer = task_data.get("customer", {})
        order_id = task_data.get("order_id")
        
        if not complaint_details:
            return {"error": "Complaint details required"}
        
        # Analyze complaint severity
        severity = await self._analyze_complaint_severity(complaint_type, complaint_details)
        
        # Generate response based on severity
        response = await self._generate_complaint_response(severity, customer, complaint_type)
        
        # Escalate if necessary
        escalation = await self._check_escalation_needed(severity, complaint_type)
        
        return {
            "complaint_received": True,
            "complaint_id": f"COMP_{random.randint(100000, 999999)}",
            "severity": severity,
            "response": response,
            "escalation": escalation,
            "message": self._generate_complaint_response_message(customer, severity, response)
        }
    
    async def _check_return_eligibility(self, order_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if items are eligible for return"""
        # Mock eligibility check
        order_date = datetime.now() - timedelta(days=random.randint(1, 30))
        days_since_order = (datetime.now() - order_date).days
        
        # 30-day return policy
        if days_since_order > 30:
            return {
                "eligible": False,
                "error": "Return period expired",
                "message": "Sorry, the 30-day return period has expired for this order."
            }
        
        # Check item conditions
        for item in items:
            if item.get("condition") == "damaged":
                return {
                    "eligible": False,
                    "error": "Item condition",
                    "message": "This item cannot be returned due to its condition."
                }
        
        return {
            "eligible": True,
            "return_period_days": 30 - days_since_order,
            "message": "Items are eligible for return."
        }
    
    async def _check_exchange_eligibility(self, order_id: str, items_to_exchange: List[Dict[str, Any]], new_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if items are eligible for exchange"""
        # Check return eligibility first
        return_eligibility = await self._check_return_eligibility(order_id, items_to_exchange)
        
        if not return_eligibility["eligible"]:
            return return_eligibility
        
        # Check if new items are available
        for new_item in new_items:
            if not new_item.get("available"):
                return {
                    "eligible": False,
                    "error": "New item unavailable",
                    "message": f"Sorry, the requested exchange item is not available."
                }
        
        return {
            "eligible": True,
            "message": "Exchange is eligible."
        }
    
    async def _process_return_request(self, order_id: str, items: List[Dict[str, Any]], reason: str, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Process return request"""
        return_id = f"RET_{random.randint(100000, 999999)}"
        
        # Calculate refund amount
        refund_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        # Generate return instructions
        instructions = {
            "return_method": "prepaid_label",
            "return_address": "Returns Department, 123 Store St, City, State 12345",
            "packaging_instructions": "Use original packaging if available",
            "return_deadline": (datetime.now() + timedelta(days=14)).isoformat()
        }
        
        return {
            "return_id": return_id,
            "refund_amount": refund_amount,
            "instructions": instructions,
            "processing_time": "3-5 business days"
        }
    
    async def _process_exchange_request(self, order_id: str, items_to_exchange: List[Dict[str, Any]], new_items: List[Dict[str, Any]], reason: str, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Process exchange request"""
        exchange_id = f"EXC_{random.randint(100000, 999999)}"
        
        # Calculate price difference
        original_total = sum(item.get("price", 0) * item.get("quantity", 1) for item in items_to_exchange)
        new_total = sum(item.get("price", 0) * item.get("quantity", 1) for item in new_items)
        price_difference = new_total - original_total
        
        # Generate exchange instructions
        instructions = {
            "return_method": "prepaid_label",
            "new_item_shipping": "free" if price_difference >= 0 else "standard",
            "processing_time": "5-7 business days"
        }
        
        return {
            "exchange_id": exchange_id,
            "price_difference": price_difference,
            "instructions": instructions,
            "new_order_id": f"ORD_{random.randint(100000, 999999)}" if price_difference > 0 else None
        }
    
    async def _get_tracking_information(self, order_id: Optional[str], tracking_number: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get tracking information"""
        # Mock tracking data
        tracking_events = [
            {
                "status": "processing",
                "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
                "location": "Distribution Center",
                "description": "Order is being prepared"
            },
            {
                "status": "shipped",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "location": "Origin Facility",
                "description": "Package has been shipped"
            },
            {
                "status": "in_transit",
                "timestamp": (datetime.now() - timedelta(hours=12)).isoformat(),
                "location": "In Transit",
                "description": "Package is in transit"
            }
        ]
        
        return {
            "tracking_number": tracking_number or f"TRK{random.randint(100000, 999999)}",
            "order_id": order_id,
            "status": "in_transit",
            "events": tracking_events,
            "estimated_delivery": (datetime.now() + timedelta(days=1)).isoformat()
        }
    
    async def _generate_feedback_request(self, order_id: str, customer: Dict[str, Any], feedback_type: str) -> Dict[str, Any]:
        """Generate feedback request"""
        feedback_questions = {
            "general": [
                "How was your overall shopping experience?",
                "How would you rate the product quality?",
                "How satisfied are you with our service?"
            ],
            "product": [
                "How would you rate the product you received?",
                "Did the product meet your expectations?",
                "Would you recommend this product to others?"
            ],
            "service": [
                "How would you rate our customer service?",
                "Was your issue resolved satisfactorily?",
                "How likely are you to shop with us again?"
            ]
        }
        
        return {
            "order_id": order_id,
            "feedback_type": feedback_type,
            "questions": feedback_questions.get(feedback_type, feedback_questions["general"]),
            "feedback_url": f"https://feedback.example.com/{order_id}",
            "expires_in_days": 7
        }
    
    async def _analyze_complaint_severity(self, complaint_type: str, complaint_details: str) -> str:
        """Analyze complaint severity"""
        # Simple severity analysis
        high_severity_keywords = ["terrible", "awful", "worst", "hate", "angry", "furious"]
        medium_severity_keywords = ["disappointed", "unhappy", "frustrated", "concerned"]
        
        complaint_lower = complaint_details.lower()
        
        if any(keyword in complaint_lower for keyword in high_severity_keywords):
            return "high"
        elif any(keyword in complaint_lower for keyword in medium_severity_keywords):
            return "medium"
        else:
            return "low"
    
    async def _generate_complaint_response(self, severity: str, customer: Dict[str, Any], complaint_type: str) -> Dict[str, Any]:
        """Generate complaint response"""
        name = customer.get("name", "Customer").split()[0]
        
        responses = {
            "high": {
                "apology": f"I sincerely apologize for this experience, {name}.",
                "action": "I'm escalating this to our management team immediately.",
                "compensation": "We'd like to offer you a full refund and a 20% discount on your next purchase.",
                "follow_up": "A manager will contact you within 24 hours."
            },
            "medium": {
                "apology": f"I'm sorry to hear about this issue, {name}.",
                "action": "I'm working to resolve this for you right away.",
                "compensation": "We'd like to offer you a 15% discount on your next purchase.",
                "follow_up": "I'll follow up with you in 2-3 business days."
            },
            "low": {
                "apology": f"Thank you for bringing this to our attention, {name}.",
                "action": "I'm looking into this for you.",
                "compensation": "We'd like to offer you a 10% discount on your next purchase.",
                "follow_up": "I'll get back to you within 1-2 business days."
            }
        }
        
        return responses[severity]
    
    async def _check_escalation_needed(self, severity: str, complaint_type: str) -> Dict[str, Any]:
        """Check if complaint needs escalation"""
        needs_escalation = severity == "high" or complaint_type in ["billing", "legal", "safety"]
        
        return {
            "escalation_needed": needs_escalation,
            "escalation_level": "management" if needs_escalation else "standard",
            "escalation_time": "24 hours" if needs_escalation else "48 hours"
        }
    
    async def _generate_return_label(self, return_id: str, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Generate return label"""
        return {
            "return_id": return_id,
            "label_url": f"https://returns.example.com/label/{return_id}",
            "tracking_number": f"RET{random.randint(100000, 999999)}",
            "return_address": "Returns Department, 123 Store St, City, State 12345",
            "instructions": "Print label and attach to package"
        }
    
    def _generate_return_message(self, customer: Dict[str, Any], refund_amount: float, return_id: str) -> str:
        """Generate return confirmation message"""
        name = customer.get("name", "Customer").split()[0]
        return f"I've processed your return request, {name}. Return ID: {return_id}. You'll receive a refund of ₹{refund_amount:,.2f} within 3-5 business days. A prepaid return label has been generated for your convenience."
    
    def _generate_exchange_message(self, customer: Dict[str, Any], exchange_result: Dict[str, Any]) -> str:
        """Generate exchange confirmation message"""
        name = customer.get("name", "Customer").split()[0]
        exchange_id = exchange_result["exchange_id"]
        price_diff = exchange_result["price_difference"]
        
        if price_diff > 0:
            return f"Your exchange has been processed, {name}. Exchange ID: {exchange_id}. You'll be charged an additional ₹{price_diff:,.2f} for the difference. Your new items will be shipped once we receive your return."
        elif price_diff < 0:
            return f"Your exchange has been processed, {name}. Exchange ID: {exchange_id}. You'll receive a refund of ₹{abs(price_diff):,.2f} for the difference. Your new items will be shipped once we receive your return."
        else:
            return f"Your exchange has been processed, {name}. Exchange ID: {exchange_id}. No price difference - it's an even exchange. Your new items will be shipped once we receive your return."
    
    def _generate_tracking_message(self, customer: Dict[str, Any], tracking_info: Dict[str, Any]) -> str:
        """Generate tracking message"""
        name = customer.get("name", "Customer").split()[0]
        status = tracking_info["status"]
        tracking_num = tracking_info["tracking_number"]
        
        if status == "delivered":
            return f"Great news {name}! Your package has been delivered. Tracking: {tracking_num}"
        elif status == "out_for_delivery":
            return f"Your package is out for delivery today, {name}! Tracking: {tracking_num}"
        else:
            return f"Your package is currently {status.replace('_', ' ')}, {name}. Tracking: {tracking_num}"
    
    def _generate_feedback_solicitation_message(self, customer: Dict[str, Any], feedback_type: str) -> str:
        """Generate feedback solicitation message"""
        name = customer.get("name", "Customer").split()[0]
        return f"Hi {name}! We'd love to hear about your recent experience. Your feedback helps us improve our service. Would you mind taking a quick survey?"
    
    def _generate_complaint_response_message(self, customer: Dict[str, Any], severity: str, response: Dict[str, Any]) -> str:
        """Generate complaint response message"""
        name = customer.get("name", "Customer").split()[0]
        return f"{response['apology']} {response['action']} {response['compensation']} {response['follow_up']}"
