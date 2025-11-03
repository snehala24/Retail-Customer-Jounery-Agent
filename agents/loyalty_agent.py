from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models import AgentTask
from data.mock_services import MockLoyaltyService
from models import CustomerTier
import random
from datetime import datetime, timedelta

class LoyaltyAgent(BaseAgent):
    def __init__(self):
        super().__init__("loyalty_agent", "loyalty")
        self.loyalty_service = MockLoyaltyService()
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle loyalty and offers related tasks"""
        task_data = task.task_data
        customer_id = task.customer_id
        
        action = task_data.get("action", "get_offers")
        
        if action == "get_offers":
            return await self._get_offers(task_data)
        elif action == "apply_promotion":
            return await self._apply_promotion(task_data)
        elif action == "calculate_points":
            return await self._calculate_points(task_data)
        elif action == "redeem_points":
            return await self._redeem_points(task_data)
        elif action == "get_tier_benefits":
            return await self._get_tier_benefits(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _get_offers(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get available offers and promotions for customer"""
        customer = task_data.get("customer", {})
        purchase_amount = task_data.get("purchase_amount", 0)
        customer_tier = customer.get("tier", "bronze")
        
        # Get available promotions
        available_promotions = self.loyalty_service.get_available_promotions(
            customer_tier, purchase_amount
        )
        
        # Get tier-specific benefits
        tier_benefits = self._get_tier_benefits_info(customer_tier)
        
        # Get personalized offers
        personalized_offers = await self._get_personalized_offers(customer, purchase_amount)
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(
            available_promotions, personalized_offers, purchase_amount, customer_tier
        )
        
        return {
            "available_promotions": available_promotions,
            "personalized_offers": personalized_offers,
            "tier_benefits": tier_benefits,
            "potential_savings": potential_savings,
            "message": self._generate_offers_message(customer, available_promotions, tier_benefits)
        }
    
    async def _apply_promotion(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply promotion code to purchase"""
        promotion_code = task_data.get("promotion_code")
        purchase_amount = task_data.get("purchase_amount", 0)
        customer = task_data.get("customer", {})
        
        if not promotion_code:
            return {"error": "Promotion code required"}
        
        # Validate and apply promotion
        promotion_result = await self._validate_promotion(promotion_code, purchase_amount, customer)
        
        if promotion_result["valid"]:
            return {
                "applied": True,
                "promotion_code": promotion_code,
                "discount_amount": promotion_result["discount_amount"],
                "final_amount": purchase_amount - promotion_result["discount_amount"],
                "savings_percentage": promotion_result["discount_percentage"],
                "message": f"Promotion '{promotion_code}' applied! You saved ₹{promotion_result['discount_amount']:,.2f}"
            }
        else:
            return {
                "applied": False,
                "error": promotion_result["error"],
                "message": f"Sorry, promotion '{promotion_code}' could not be applied: {promotion_result['error']}"
            }
    
    async def _calculate_points(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate loyalty points for purchase"""
        purchase_amount = task_data.get("purchase_amount", 0)
        customer = task_data.get("customer", {})
        customer_tier = customer.get("tier", "bronze")
        
        # Calculate base points
        base_points = self.loyalty_service.calculate_loyalty_points(purchase_amount, customer_tier)
        
        # Check for bonus point opportunities
        bonus_points = await self._calculate_bonus_points(purchase_amount, customer)
        
        # Calculate total points
        total_points = base_points + bonus_points
        
        # Calculate points to next tier
        next_tier_info = self._calculate_next_tier(customer.get("loyalty_points", 0), total_points)
        
        return {
            "base_points": base_points,
            "bonus_points": bonus_points,
            "total_points": total_points,
            "current_tier": customer_tier,
            "next_tier": next_tier_info,
            "points_per_dollar": self._get_points_per_dollar(customer_tier),
            "message": self._generate_points_message(customer, total_points, next_tier_info)
        }
    
    async def _redeem_points(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Redeem loyalty points for discount"""
        points_to_redeem = task_data.get("points_to_redeem", 0)
        customer = task_data.get("customer", {})
        current_points = customer.get("loyalty_points", 0)
        
        if points_to_redeem <= 0:
            return {"error": "Invalid points amount"}
        
        if points_to_redeem > current_points:
            return {
                "error": "Insufficient points",
                "available_points": current_points,
                "requested_points": points_to_redeem
            }
        
        # Calculate discount from points
        discount_amount = points_to_redeem * 0.01  # 1 point = $0.01
        
        # Calculate new points balance
        new_balance = current_points - points_to_redeem
        
        return {
            "redeemed": True,
            "points_redeemed": points_to_redeem,
            "discount_amount": discount_amount,
            "new_balance": new_balance,
            "message": f"Successfully redeemed {points_to_redeem} points for ₹{discount_amount:,.2f} discount!"
        }
    
    async def _get_tier_benefits(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer tier benefits"""
        customer = task_data.get("customer", {})
        customer_tier = customer.get("tier", "bronze")
        
        tier_benefits = self._get_tier_benefits_info(customer_tier)
        next_tier_info = self._calculate_next_tier(customer.get("loyalty_points", 0), 0)
        
        return {
            "current_tier": customer_tier,
            "tier_benefits": tier_benefits,
            "next_tier": next_tier_info,
            "message": self._generate_tier_benefits_message(customer, tier_benefits)
        }
    
    async def _get_personalized_offers(self, customer: Dict[str, Any], purchase_amount: float) -> List[Dict[str, Any]]:
        """Get personalized offers based on customer profile"""
        customer_tier = customer.get("tier", "bronze")
        purchase_history = customer.get("purchase_history", [])
        preferences = customer.get("preferences", {})
        
        personalized_offers = []
        
        # Tier-based offers
        if customer_tier in ["gold", "platinum"]:
            personalized_offers.append({
                "type": "exclusive_access",
                "title": "Exclusive Member Access",
                "description": "Early access to new products",
                "discount": 0.0,
                "benefit": "exclusive_access"
            })
        
        # Category-based offers
        if "electronics" in purchase_history:
            personalized_offers.append({
                "type": "category_discount",
                "title": "Electronics Special",
                "description": "15% off electronics",
                "discount": 0.15,
                "category": "electronics"
            })
        
        # Brand-based offers
        preferred_brands = preferences.get("brands", [])
        if "Apple" in preferred_brands:
            personalized_offers.append({
                "type": "brand_discount",
                "title": "Apple Fan Special",
                "description": "10% off Apple products",
                "discount": 0.10,
                "brand": "Apple"
            })
        
        # Purchase amount based offers
        if purchase_amount > 500:
            personalized_offers.append({
                "type": "high_value_purchase",
                "title": "Big Spender Bonus",
                "description": "Extra 5% off your purchase",
                "discount": 0.05,
                "min_amount": 500
            })
        
        return personalized_offers
    
    def _get_tier_benefits_info(self, tier: str) -> Dict[str, Any]:
        """Get tier benefits information"""
        benefits = {
            "bronze": {
                "points_per_dollar": 1,
                "discount_rate": 0.05,
                "free_shipping_threshold": 100,
                "exclusive_access": False,
                "priority_support": False,
                "birthday_discount": 0.10
            },
            "silver": {
                "points_per_dollar": 1.5,
                "discount_rate": 0.10,
                "free_shipping_threshold": 75,
                "exclusive_access": False,
                "priority_support": False,
                "birthday_discount": 0.15
            },
            "gold": {
                "points_per_dollar": 2,
                "discount_rate": 0.15,
                "free_shipping_threshold": 50,
                "exclusive_access": True,
                "priority_support": True,
                "birthday_discount": 0.20
            },
            "platinum": {
                "points_per_dollar": 3,
                "discount_rate": 0.20,
                "free_shipping_threshold": 0,
                "exclusive_access": True,
                "priority_support": True,
                "birthday_discount": 0.25
            }
        }
        
        return benefits.get(tier, benefits["bronze"])
    
    def _calculate_potential_savings(self, promotions: List[Dict[str, Any]], offers: List[Dict[str, Any]], amount: float, tier: str) -> Dict[str, Any]:
        """Calculate potential savings from all offers"""
        total_discount = 0
        applicable_offers = []
        
        # Calculate promotion savings
        for promo in promotions:
            discount = amount * promo.get("discount", 0)
            total_discount += discount
            applicable_offers.append({
                "type": "promotion",
                "name": promo.get("code", "Promotion"),
                "discount": discount
            })
        
        # Calculate offer savings
        for offer in offers:
            if offer.get("discount", 0) > 0:
                discount = amount * offer["discount"]
                total_discount += discount
                applicable_offers.append({
                    "type": "offer",
                    "name": offer.get("title", "Offer"),
                    "discount": discount
                })
        
        # Calculate tier discount
        tier_benefits = self._get_tier_benefits_info(tier)
        tier_discount = amount * tier_benefits["discount_rate"]
        
        return {
            "total_savings": total_discount + tier_discount,
            "promotion_savings": total_discount,
            "tier_savings": tier_discount,
            "applicable_offers": applicable_offers,
            "savings_percentage": ((total_discount + tier_discount) / amount * 100) if amount > 0 else 0
        }
    
    async def _validate_promotion(self, code: str, amount: float, customer: Dict[str, Any]) -> Dict[str, Any]:
        """Validate promotion code"""
        from data.mock_services import PROMOTIONS
        
        promotion = PROMOTIONS.get(code.upper())
        if not promotion:
            return {"valid": False, "error": "Invalid promotion code"}
        
        # Check expiration
        if promotion["valid_until"] < datetime.now():
            return {"valid": False, "error": "Promotion has expired"}
        
        # Check minimum amount
        if promotion.get("min_amount") and amount < promotion["min_amount"]:
            return {"valid": False, "error": f"Minimum purchase of ₹{promotion['min_amount']:,.2f} required"}
        
        # Check tier requirement
        if promotion.get("tier_required") and customer.get("tier") != promotion["tier_required"]:
            return {"valid": False, "error": f"Promotion requires {promotion['tier_required']} tier membership"}
        
        # Calculate discount
        discount_amount = amount * promotion["discount"]
        
        return {
            "valid": True,
            "discount_amount": discount_amount,
            "discount_percentage": promotion["discount"] * 100,
            "description": f"{promotion['discount']*100}% off your purchase"
        }
    
    async def _calculate_bonus_points(self, amount: float, customer: Dict[str, Any]) -> int:
        """Calculate bonus points opportunities"""
        bonus_points = 0
        
        # First purchase bonus
        if not customer.get("purchase_history"):
            bonus_points += 100
        
        # High value purchase bonus
        if amount > 500:
            bonus_points += 50
        
        # Tier bonus
        tier = customer.get("tier", "bronze")
        if tier in ["gold", "platinum"]:
            bonus_points += 25
        
        return bonus_points
    
    def _calculate_next_tier(self, current_points: int, additional_points: int) -> Dict[str, Any]:
        """Calculate points needed for next tier"""
        total_points = current_points + additional_points
        
        tier_thresholds = {
            "bronze": 0,
            "silver": 1000,
            "gold": 2500,
            "platinum": 5000
        }
        
        current_tier = "bronze"
        for tier, threshold in tier_thresholds.items():
            if total_points >= threshold:
                current_tier = tier
        
        # Find next tier
        next_tier = None
        next_threshold = None
        
        for tier, threshold in tier_thresholds.items():
            if threshold > total_points:
                next_tier = tier
                next_threshold = threshold
                break
        
        points_needed = next_threshold - total_points if next_threshold else 0
        
        return {
            "current_tier": current_tier,
            "next_tier": next_tier,
            "points_needed": points_needed,
            "total_points": total_points
        }
    
    def _get_points_per_dollar(self, tier: str) -> float:
        """Get points per dollar for tier"""
        benefits = self._get_tier_benefits_info(tier)
        return benefits["points_per_dollar"]
    
    def _generate_offers_message(self, customer: Dict[str, Any], promotions: List[Dict[str, Any]], tier_benefits: Dict[str, Any]) -> str:
        """Generate offers message"""
        name = customer.get("name", "Customer").split()[0]
        tier = customer.get("tier", "bronze").title()
        
        if promotions:
            return f"Hi {name}! As a {tier} member, you have {len(promotions)} special offers available. Let me show you the best deals!"
        else:
            return f"Hi {name}! As a {tier} member, you enjoy exclusive benefits. Let me show you what's available!"
    
    def _generate_points_message(self, customer: Dict[str, Any], total_points: int, next_tier_info: Dict[str, Any]) -> str:
        """Generate points message"""
        name = customer.get("name", "Customer").split()[0]
        
        if next_tier_info["points_needed"] > 0:
            return f"Great {name}! You'll earn {total_points} points with this purchase. You're {next_tier_info['points_needed']} points away from {next_tier_info['next_tier']} tier!"
        else:
            return f"Excellent {name}! You'll earn {total_points} points with this purchase. You're already at the highest tier!"
    
    def _generate_tier_benefits_message(self, customer: Dict[str, Any], tier_benefits: Dict[str, Any]) -> str:
        """Generate tier benefits message"""
        name = customer.get("name", "Customer").split()[0]
        tier = customer.get("tier", "bronze").title()
        
        benefits_list = []
        if tier_benefits["exclusive_access"]:
            benefits_list.append("exclusive access to new products")
        if tier_benefits["priority_support"]:
            benefits_list.append("priority customer support")
        if tier_benefits["free_shipping_threshold"] == 0:
            benefits_list.append("free shipping on all orders")
        elif tier_benefits["free_shipping_threshold"] < 500:
            benefits_list.append(f"free shipping on orders over ₹{tier_benefits['free_shipping_threshold']}")
        
        benefits_text = ", ".join(benefits_list)
        
        return f"Hi {name}! As a {tier} member, you enjoy: {benefits_text}, {tier_benefits['points_per_dollar']}x points on purchases, and {tier_benefits['discount_rate']*100}% member discount!"
