from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models import AgentTask
from data.mock_services import MockPaymentService, MockLoyaltyService
from models import PaymentMethod, CustomerTier
import random
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
        """Process customer payment"""
        amount = task_data.get("amount", 0)
        payment_method = PaymentMethod(task_data.get("payment_method", "credit_card"))
        customer = task_data.get("customer", {})
        cart_items = task_data.get("cart", [])
        
        if amount <= 0:
            return {"error": "Invalid payment amount"}
        
        # Calculate loyalty points and discounts
        loyalty_calculation = await self._calculate_loyalty_benefits(amount, customer, cart_items)
        
        # Apply loyalty benefits
        final_amount = loyalty_calculation["final_amount"]
        points_used = loyalty_calculation["points_used"]
        
        # Process payment
        payment_result = self.payment_service.process_payment(
            final_amount, payment_method, customer.get("id", "")
        )
        
        if payment_result["success"]:
            # Calculate new loyalty points
            new_points = self.loyalty_service.calculate_loyalty_points(
                amount, customer.get("tier", "bronze")
            )
            
            return {
                "success": True,
                "transaction_id": payment_result["transaction_id"],
                "amount_charged": final_amount,
                "original_amount": amount,
                "payment_method": payment_method,
                "loyalty_points_earned": new_points,
                "loyalty_points_used": points_used,
                "discount_applied": amount - final_amount,
                "timestamp": payment_result["timestamp"],
                "message": self._generate_payment_success_message(customer, final_amount, new_points)
            }
        else:
            return {
                "success": False,
                "error": payment_result["error"],
                "error_code": payment_result.get("error_code"),
                "message": self._generate_payment_failure_message(payment_result["error"])
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
        
        # Calculate tax (mock 8.5% tax rate)
        taxable_amount = loyalty_calculation["final_amount"] - promotion_discount["discount_amount"]
        tax_amount = taxable_amount * 0.085
        
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
                "message": f"Refund of ${refund_amount:.2f} has been processed successfully."
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
            return {"valid": False, "error": f"Minimum purchase of ${promotion['min_amount']} required"}
        
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
    
    def _generate_payment_success_message(self, customer: Dict[str, Any], amount: float, points_earned: int) -> str:
        """Generate success message for payment"""
        name = customer.get("name", "Customer").split()[0]
        tier = customer.get("tier", "bronze").title()
        
        message = f"Payment successful! Your order for ${amount:.2f} has been processed."
        
        if points_earned > 0:
            message += f" You've earned {points_earned} loyalty points as a {tier} member."
        
        if tier in ["Gold", "Platinum"]:
            message += " Thank you for being a valued member!"
        
        return message
    
    def _generate_payment_failure_message(self, error: str) -> str:
        """Generate failure message for payment"""
        if "declined" in error.lower():
            return "Your payment was declined. Please check your payment information or try a different payment method."
        elif "insufficient" in error.lower():
            return "Insufficient funds. Please try a different payment method or contact your bank."
        else:
            return "We're having trouble processing your payment. Please try again or contact customer service."
    
    def _get_payment_method_description(self, method: PaymentMethod) -> str:
        """Get human-readable payment method description"""
        descriptions = {
            PaymentMethod.CREDIT_CARD: "Credit Card",
            PaymentMethod.DEBIT_CARD: "Debit Card", 
            PaymentMethod.UPI: "UPI Payment",
            PaymentMethod.GIFT_CARD: "Gift Card",
            PaymentMethod.CASH: "Cash",
            PaymentMethod.LOYALTY_POINTS: "Loyalty Points"
        }
        return descriptions.get(method, method.value.replace("_", " ").title())
    
    def _calculate_shipping_cost(self, cart_items: List[Dict[str, Any]], customer_location: str) -> float:
        """Calculate shipping cost based on items and location"""
        total_weight = sum(item.get("weight", 1) * item.get("quantity", 1) for item in cart_items)
        total_value = sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
        
        # Free shipping over $100
        if total_value >= 100:
            return 0.0
        
        # Base shipping cost
        base_cost = 9.99
        
        # Add weight-based surcharge
        if total_weight > 10:
            base_cost += (total_weight - 10) * 2.0
        
        return base_cost
