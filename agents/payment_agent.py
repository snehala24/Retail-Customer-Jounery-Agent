from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models import AgentTask
from data.mock_services import MockPaymentService, MockLoyaltyService
from models import PaymentMethod, CustomerTier
import random
import asyncio
from datetime import datetime

class PaymentAgent(BaseAgent):
    def __init__(self):
        super().__init__("payment_agent", "payment")
        self.payment_service = MockPaymentService()
        self.loyalty_service = MockLoyaltyService()
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle payment processing tasks"""
        task_data = task.task_data
        customer_id = task.customer_id
        
        action = task_data.get("action", "process_payment")
        
        if action == "process_payment":
            return await self._process_payment(task_data)
        elif action == "calculate_total":
            return await self._calculate_total(task_data)
        elif action == "apply_promotions":
            return await self._apply_promotions(task_data)
        elif action == "process_refund":
            return await self._process_refund(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _process_payment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process customer payment with real-time support"""
        amount = task_data.get("amount", 0)
        payment_method_str = task_data.get("payment_method", "credit_card")
        payment_method = PaymentMethod(payment_method_str)
        customer = task_data.get("customer", {})
        cart_items = task_data.get("cart", [])
        
        if amount <= 0:
            return {"error": "Invalid payment amount"}
        
        # Calculate loyalty points and discounts
        loyalty_calculation = await self._calculate_loyalty_benefits(amount, customer, cart_items)
        
        # Apply loyalty benefits
        final_amount = loyalty_calculation["final_amount"]
        points_used = loyalty_calculation["points_used"]
        
        # Real-time payment processing with Indian payment methods
        payment_result = await self._process_realtime_payment(
            final_amount, payment_method, customer.get("id", ""), customer
        )
        
        if payment_result["success"]:
            # Calculate new loyalty points
            new_points = self.loyalty_service.calculate_loyalty_points(
                final_amount, customer.get("tier", "bronze")
            )
            
            return {
                "success": True,
                "transaction_id": payment_result["transaction_id"],
                "amount_charged": final_amount,
                "original_amount": amount,
                "payment_method": payment_method.value,
                "payment_method_display": self._get_payment_method_description(payment_method),
                "loyalty_points_earned": new_points,
                "loyalty_points_used": points_used,
                "discount_applied": amount - final_amount,
                "timestamp": payment_result["timestamp"],
                "upi_reference": payment_result.get("upi_reference"),
                "gateway_response": payment_result.get("gateway_response", {}),
                "message": self._generate_payment_success_message(customer, final_amount, new_points, payment_method)
            }
        else:
            return {
                "success": False,
                "error": payment_result["error"],
                "error_code": payment_result.get("error_code"),
                "retry_available": payment_result.get("retry_available", True),
                "message": self._generate_payment_failure_message(payment_result["error"], payment_method)
            }
    
    async def _process_realtime_payment(
        self, 
        amount: float, 
        payment_method: PaymentMethod, 
        customer_id: str,
        customer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process payment in real-time with proper gateway integration simulation"""
        import random
        import time
        
        # Simulate real-time processing delay
        await asyncio.sleep(0.5)  # Simulate network latency
        
        # UPI-specific processing
        if payment_method == PaymentMethod.UPI:
            return await self._process_upi_payment(amount, customer_id, customer)
        elif payment_method == PaymentMethod.COD:
            return await self._process_cod_payment(amount, customer_id)
        elif payment_method == PaymentMethod.WALLET:
            return await self._process_wallet_payment(amount, customer_id, customer)
        else:
            # Card/Net Banking processing
            return self.payment_service.process_payment(amount, payment_method, customer_id)
    
    async def _process_upi_payment(
        self, 
        amount: float, 
        customer_id: str,
        customer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process UPI payment with real-time simulation"""
        import random
        
        # Simulate UPI gateway interaction
        success_rate = 0.92  # 92% success rate for UPI
        
        if random.random() < success_rate:
            # Generate UPI transaction details
            upi_ref = f"UPI{random.randint(100000000, 999999999)}"
            gateway = random.choice(["PhonePe", "Google Pay", "Paytm", "BHIM UPI"])
            
            return {
                "success": True,
                "transaction_id": f"TXN_UPI_{random.randint(100000, 999999)}",
                "amount": amount,
                "payment_method": PaymentMethod.UPI.value,
                "upi_reference": upi_ref,
                "gateway": gateway,
                "gateway_response": {
                    "status": "success",
                    "message": "Payment successful via UPI",
                    "approval_code": f"APP{random.randint(10000, 99999)}"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Simulate UPI failure scenarios
            failure_reasons = [
                "Insufficient funds in bank account",
                "UPI PIN incorrect",
                "Transaction declined by bank",
                "Network timeout - please try again"
            ]
            error_reason = random.choice(failure_reasons)
            
            return {
                "success": False,
                "error": error_reason,
                "error_code": "UPI_PAYMENT_FAILED",
                "retry_available": True,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _process_cod_payment(self, amount: float, customer_id: str) -> Dict[str, Any]:
        """Process Cash on Delivery payment"""
        return {
            "success": True,
            "transaction_id": f"TXN_COD_{random.randint(100000, 999999)}",
            "amount": amount,
            "payment_method": PaymentMethod.COD.value,
            "gateway_response": {
                "status": "confirmed",
                "message": "COD order confirmed. Payment will be collected on delivery."
            },
            "timestamp": datetime.now().isoformat(),
            "cod_instructions": "Please keep exact change ready. Cash will be collected on delivery."
        }
    
    async def _process_wallet_payment(
        self, 
        amount: float, 
        customer_id: str,
        customer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process wallet payment (Paytm, PhonePe wallet)"""
        import random
        
        wallet_type = random.choice(["Paytm", "PhonePe", "Amazon Pay"])
        success_rate = 0.95
        
        if random.random() < success_rate:
            return {
                "success": True,
                "transaction_id": f"TXN_WLT_{random.randint(100000, 999999)}",
                "amount": amount,
                "payment_method": PaymentMethod.WALLET.value,
                "wallet_type": wallet_type,
                "gateway_response": {
                    "status": "success",
                    "message": f"Payment successful via {wallet_type} wallet"
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Insufficient wallet balance",
                "error_code": "WALLET_INSUFFICIENT_BALANCE",
                "retry_available": True,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _calculate_total(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total with taxes, discounts, and loyalty benefits"""
        cart_items = task_data.get("cart", [])
        customer = task_data.get("customer", {})
        promotions = task_data.get("promotions", [])
        
        # Calculate subtotal
        subtotal = sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
        
        # Apply promotions
        promotion_discount = await self._calculate_promotion_discounts(subtotal, promotions, customer)
        
        # Calculate loyalty benefits
        loyalty_calculation = await self._calculate_loyalty_benefits(subtotal, customer, cart_items)
        
        # Calculate tax (mock 8.5% tax rate for India - GST)
        taxable_amount = loyalty_calculation["final_amount"] - promotion_discount["discount_amount"]
        tax_amount = taxable_amount * 0.18  # 18% GST in India
        
        # Final total
        final_total = taxable_amount + tax_amount
        
        return {
            "subtotal": subtotal,
            "promotion_discount": promotion_discount["discount_amount"],
            "loyalty_discount": loyalty_calculation["discount_amount"],
            "tax_amount": tax_amount,
            "total": final_total,
            "breakdown": {
                "items": len(cart_items),
                "subtotal": subtotal,
                "discounts": promotion_discount["discount_amount"] + loyalty_calculation["discount_amount"],
                "tax": tax_amount,
                "final_total": final_total
            },
            "loyalty_points_earned": self.loyalty_service.calculate_loyalty_points(
                subtotal, customer.get("tier", "bronze")
            ),
            "available_promotions": self.loyalty_service.get_available_promotions(
                customer.get("tier", "bronze"), subtotal
            )
        }
    
    async def _apply_promotions(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply promotion codes and calculate discounts"""
        amount = task_data.get("amount", 0)
        promotion_codes = task_data.get("promotion_codes", [])
        customer = task_data.get("customer", {})
        
        if not promotion_codes:
            return {"discount_amount": 0, "applied_promotions": []}
        
        applied_promotions = []
        total_discount = 0
        
        for code in promotion_codes:
            promotion_result = await self._validate_and_apply_promotion(
                code, amount, customer
            )
            
            if promotion_result["valid"]:
                applied_promotions.append(promotion_result)
                total_discount += promotion_result["discount_amount"]
        
        return {
            "discount_amount": total_discount,
            "applied_promotions": applied_promotions,
            "final_amount": amount - total_discount
        }
    
    async def _process_refund(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process refund for returned items"""
        transaction_id = task_data.get("transaction_id")
        refund_amount = task_data.get("refund_amount", 0)
        reason = task_data.get("reason", "return")
        
        if not transaction_id or refund_amount <= 0:
            return {"error": "Invalid refund request"}
        
        # Process refund
        refund_result = self.payment_service.refund_payment(transaction_id, refund_amount)
        
        if refund_result["success"]:
            return {
                "success": True,
                "refund_id": refund_result["refund_id"],
                "refund_amount": refund_amount,
                "timestamp": refund_result["timestamp"],
                "message": f"Refund of ₹{refund_amount:,.2f} has been processed successfully."
            }
        else:
            return {
                "success": False,
                "error": "Refund processing failed",
                "message": "We're having trouble processing your refund. Please contact customer service."
            }
    
    async def _calculate_loyalty_benefits(self, amount: float, customer: Dict[str, Any], cart_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate loyalty points and discounts"""
        customer_tier = customer.get("tier", "bronze")
        current_points = customer.get("loyalty_points", 0)
        
        # Calculate points to earn
        points_to_earn = self.loyalty_service.calculate_loyalty_points(amount, customer_tier)
        
        # Calculate discount from loyalty points
        loyalty_discount = self.loyalty_service.apply_loyalty_discount(
            amount, customer_tier, current_points
        )
        
        return {
            "points_to_earn": points_to_earn,
            "discount_amount": loyalty_discount["discount_amount"],
            "final_amount": loyalty_discount["final_amount"],
            "points_used": loyalty_discount["points_used"],
            "tier_benefits": {
                "tier": customer_tier,
                "points_per_dollar": self.loyalty_service.calculate_loyalty_points(1, customer_tier),
                "discount_rate": 0.15 if customer_tier == "gold" else 0.20 if customer_tier == "platinum" else 0.05
            }
        }
    
    async def _calculate_promotion_discounts(self, amount: float, promotions: List[str], customer: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate discounts from promotion codes"""
        if not promotions:
            return {"discount_amount": 0, "applied_promotions": []}
        
        total_discount = 0
        applied_promotions = []
        
        for promo_code in promotions:
            promo_result = await self._validate_and_apply_promotion(promo_code, amount, customer)
            if promo_result["valid"]:
                total_discount += promo_result["discount_amount"]
                applied_promotions.append(promo_result)
        
        return {
            "discount_amount": total_discount,
            "applied_promotions": applied_promotions
        }
    
    async def _validate_and_apply_promotion(self, code: str, amount: float, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and apply a promotion code"""
        from data.mock_services import PROMOTIONS
        
        promotion = PROMOTIONS.get(code.upper())
        if not promotion:
            return {"valid": False, "error": "Invalid promotion code"}
        
        # Check if promotion is still valid
        if promotion["valid_until"] < datetime.now():
            return {"valid": False, "error": "Promotion has expired"}
        
        # Check minimum amount requirement
        if promotion.get("min_amount") and amount < promotion["min_amount"]:
            return {"valid": False, "error": f"Minimum purchase of ₹{promotion['min_amount']:,.2f} required"}
        
        # Check tier requirement
        if promotion.get("tier_required") and customer.get("tier") != promotion["tier_required"]:
            return {"valid": False, "error": f"Promotion requires {promotion['tier_required']} tier membership"}
        
        # Calculate discount
        discount_amount = amount * promotion["discount"]
        
        return {
            "valid": True,
            "code": code,
            "discount_amount": discount_amount,
            "discount_percentage": promotion["discount"] * 100,
            "description": f"{promotion['discount']*100}% off your purchase"
        }
    
    def _generate_payment_success_message(
        self, 
        customer: Dict[str, Any], 
        amount: float, 
        points_earned: int,
        payment_method: PaymentMethod
    ) -> str:
        """Generate success message for payment"""
        name = customer.get("name", "Customer").split()[0]
        tier = customer.get("tier", "bronze").title()
        
        payment_method_name = self._get_payment_method_description(payment_method)
        
        message = f"Payment successful via {payment_method_name}! Your order for ₹{amount:,.2f} has been processed."
        
        if payment_method == PaymentMethod.UPI:
            message += " Your UPI payment has been confirmed."
        elif payment_method == PaymentMethod.COD:
            message += " Your COD order has been confirmed. Cash will be collected on delivery."
        
        if points_earned > 0:
            message += f" You've earned {points_earned} loyalty points as a {tier} member."
        
        if tier in ["Gold", "Platinum"]:
            message += " Thank you for being a valued member!"
        
        return message
    
    def _generate_payment_failure_message(self, error: str, payment_method: PaymentMethod) -> str:
        """Generate failure message for payment"""
        payment_method_name = self._get_payment_method_description(payment_method)
        
        if "declined" in error.lower():
            return f"Your {payment_method_name} payment was declined. Please check your payment information or try a different payment method."
        elif "insufficient" in error.lower():
            if payment_method == PaymentMethod.UPI:
                return "Insufficient funds in your bank account. Please check your account balance or try a different payment method."
            elif payment_method == PaymentMethod.WALLET:
                return "Insufficient wallet balance. Please recharge your wallet or use a different payment method."
            else:
                return "Insufficient funds. Please try a different payment method or contact your bank."
        elif "pin" in error.lower() or "incorrect" in error.lower():
            return f"Authentication failed. Please check your {payment_method_name} PIN or credentials and try again."
        else:
            return f"We're having trouble processing your {payment_method_name} payment. Please try again or contact customer service."
    
    def _get_payment_method_description(self, method: PaymentMethod) -> str:
        """Get human-readable payment method description (India)"""
        descriptions = {
            PaymentMethod.CREDIT_CARD: "Credit Card",
            PaymentMethod.DEBIT_CARD: "Debit Card", 
            PaymentMethod.UPI: "UPI (Google Pay, PhonePe, Paytm)",
            PaymentMethod.NET_BANKING: "Net Banking",
            PaymentMethod.WALLET: "Digital Wallet (Paytm, PhonePe)",
            PaymentMethod.COD: "Cash on Delivery (COD)",
            PaymentMethod.GIFT_CARD: "Gift Card",
            PaymentMethod.LOYALTY_POINTS: "Loyalty Points"
        }
        return descriptions.get(method, method.value.replace("_", " ").title())
    
    def _calculate_shipping_cost(self, cart_items: List[Dict[str, Any]], customer_location: str) -> float:
        """Calculate shipping cost based on items and location (India - in rupees)"""
        total_weight = sum(item.get("weight", 1) * item.get("quantity", 1) for item in cart_items)
        total_value = sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
        
        # Free shipping over ₹500 in India
        if total_value >= 500:
            return 0.0
        
        # Base shipping cost in rupees
        base_cost = 99.0
        
        # Add weight-based surcharge (₹20 per kg over 5kg)
        if total_weight > 5:
            base_cost += (total_weight - 5) * 20.0
        
        return base_cost
