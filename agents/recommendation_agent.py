from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from models import AgentTask
from data.mock_services import MockProductService
from data.synthetic_customers import CUSTOMERS
import random

class RecommendationAgent(BaseAgent):
    def __init__(self):
        super().__init__("recommendation_agent", "recommendation")
        self.product_service = MockProductService()
        self.customers = {c.id: c for c in CUSTOMERS}
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Generate personalized product recommendations"""
        task_data = task.task_data
        customer_id = task.customer_id
        customer = self.customers.get(customer_id)
        
        if not customer:
            return {"error": "Customer not found"}
        
        # Get customer preferences and history
        preferences = task_data.get("preferences", {})
        current_products = task_data.get("current_products", [])
        message = task_data.get("message", "")
        
        # Analyze customer intent from message
        intent = self._analyze_recommendation_intent(message)
        
        # Generate recommendations based on intent
        if intent == "category_browse":
            category = self._extract_category_from_message(message)
            recommendations = await self._get_category_recommendations(category, customer)
        elif intent == "similar_products":
            recommendations = await self._get_similar_products(current_products, customer)
        elif intent == "trending":
            recommendations = await self._get_trending_products(customer)
        elif intent == "personalized":
            recommendations = await self._get_personalized_recommendations(customer)
        else:
            recommendations = await self._get_general_recommendations(customer)
        
        # Apply customer tier benefits
        recommendations = self._apply_tier_benefits(recommendations, customer.tier)
        
        # Generate explanation
        explanation = self._generate_recommendation_explanation(recommendations, customer, intent)
        
        return {
            "recommendations": recommendations,
            "explanation": explanation,
            "intent": intent,
            "customer_tier": customer.tier,
            "total_found": len(recommendations)
        }
    
    def _analyze_recommendation_intent(self, message: str) -> str:
        """Analyze what type of recommendations the customer wants"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["similar", "like this", "related"]):
            return "similar_products"
        elif any(word in message_lower for word in ["trending", "popular", "best selling"]):
            return "trending"
        elif any(word in message_lower for word in ["electronics", "clothing", "sports", "beauty"]):
            return "category_browse"
        elif any(word in message_lower for word in ["personalized", "for me", "recommend"]):
            return "personalized"
        else:
            return "general"
    
    def _extract_category_from_message(self, message: str) -> str:
        """Extract product category from message"""
        message_lower = message.lower()
        
        category_mapping = {
            "electronics": ["electronics", "tech", "gadgets", "phones", "laptops"],
            "clothing": ["clothing", "fashion", "clothes", "apparel"],
            "sports": ["sports", "fitness", "athletic", "running", "shoes"],
            "beauty": ["beauty", "makeup", "skincare", "cosmetics"],
            "home": ["home", "furniture", "decor", "kitchen"]
        }
        
        for category, keywords in category_mapping.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        
        return "general"
    
    async def _get_category_recommendations(self, category: str, customer) -> List[Dict[str, Any]]:
        """Get recommendations for a specific category"""
        products = self.product_service.get_products(category=category, limit=6)
        
        # Filter by customer preferences
        filtered_products = self._filter_by_preferences(products, customer)
        
        # Sort by relevance
        recommendations = self._rank_products(filtered_products, customer)
        
        return recommendations[:4]  # Return top 4
    
    async def _get_similar_products(self, current_products: List[str], customer) -> List[Dict[str, Any]]:
        """Get products similar to current selection"""
        if not current_products:
            return await self._get_general_recommendations(customer)
        
        # For demo, get products from same category
        similar_products = []
        for product_sku in current_products:
            product = self.product_service.get_product(product_sku)
            if product:
                category_products = self.product_service.get_products(category=product.category, limit=10)
                similar_products.extend(category_products)
        
        # Remove duplicates and current products
        unique_products = []
        seen_skus = set(current_products)
        for product in similar_products:
            if product.sku not in seen_skus:
                unique_products.append(product)
                seen_skus.add(product.sku)
        
        recommendations = self._rank_products(unique_products, customer)
        return recommendations[:4]
    
    async def _get_trending_products(self, customer) -> List[Dict[str, Any]]:
        """Get trending/popular products"""
        # For demo, simulate trending products
        trending_categories = ["electronics", "sports", "fashion"]
        trending_products = []
        
        for category in trending_categories:
            products = self.product_service.get_products(category=category, limit=3)
            trending_products.extend(products)
        
        # Filter and rank
        filtered_products = self._filter_by_preferences(trending_products, customer)
        recommendations = self._rank_products(filtered_products, customer)
        
        return recommendations[:4]
    
    async def _get_personalized_recommendations(self, customer) -> List[Dict[str, Any]]:
        """Get highly personalized recommendations based on customer profile"""
        # Get products from customer's preferred categories
        preferred_categories = self._get_preferred_categories(customer)
        personalized_products = []
        
        for category in preferred_categories:
            products = self.product_service.get_products(category=category, limit=5)
            personalized_products.extend(products)
        
        # Filter by customer preferences
        filtered_products = self._filter_by_preferences(personalized_products, customer)
        
        # Apply tier-based filtering
        if customer.tier in ["gold", "platinum"]:
            # Include premium products
            premium_products = [p for p in filtered_products if p.price > 200]
            filtered_products.extend(premium_products)
        
        recommendations = self._rank_products(filtered_products, customer)
        return recommendations[:4]
    
    async def _get_general_recommendations(self, customer) -> List[Dict[str, Any]]:
        """Get general recommendations based on customer profile"""
        # Get products from customer's purchase history categories
        history_categories = self._get_history_categories(customer)
        
        if not history_categories:
            # Fallback to popular categories
            history_categories = ["electronics", "clothing", "sports"]
        
        general_products = []
        for category in history_categories:
            products = self.product_service.get_products(category=category, limit=4)
            general_products.extend(products)
        
        # Filter and rank
        filtered_products = self._filter_by_preferences(general_products, customer)
        recommendations = self._rank_products(filtered_products, customer)
        
        return recommendations[:4]
    
    def _filter_by_preferences(self, products: List, customer) -> List:
        """Filter products based on customer preferences"""
        filtered = []
        
        for product in products:
            # Check price range preference
            if customer.preferences.get("price_range") == "budget" and product.price > 100:
                continue
            elif customer.preferences.get("price_range") == "premium" and product.price < 200:
                continue
            
            # Check brand preferences
            preferred_brands = customer.preferences.get("brands", [])
            if preferred_brands and product.attributes.get("brand") not in preferred_brands:
                # Still include but with lower priority
                pass
            
            filtered.append(product)
        
        return filtered
    
    def _rank_products(self, products: List, customer) -> List[Dict[str, Any]]:
        """Rank products by relevance to customer"""
        ranked = []
        
        for product in products:
            score = 0
            
            # Brand preference score
            preferred_brands = customer.preferences.get("brands", [])
            if product.attributes.get("brand") in preferred_brands:
                score += 10
            
            # Price range score
            price_range = customer.preferences.get("price_range", "mid")
            if price_range == "budget" and product.price < 100:
                score += 5
            elif price_range == "premium" and product.price > 200:
                score += 5
            elif price_range == "mid" and 50 <= product.price <= 300:
                score += 5
            
            # Tier-based scoring
            if customer.tier in ["gold", "platinum"] and product.price > 200:
                score += 3
            
            # Availability score
            if product.in_stock:
                score += 2
            
            ranked.append({
                "product": product.model_dump(),
                "relevance_score": score,
                "reason": self._get_recommendation_reason(product, customer)
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked
    
    def _get_recommendation_reason(self, product, customer) -> str:
        """Generate reason for recommendation"""
        reasons = []
        
        if product.attributes.get("brand") in customer.preferences.get("brands", []):
            reasons.append("matches your preferred brands")
        
        if customer.tier in ["gold", "platinum"] and product.price > 200:
            reasons.append("exclusive for premium members")
        
        if product.category in self._get_history_categories(customer):
            reasons.append("similar to your previous purchases")
        
        if not reasons:
            reasons.append("popular choice")
        
        return ", ".join(reasons)
    
    def _get_preferred_categories(self, customer) -> List[str]:
        """Get customer's preferred categories"""
        if customer.purchase_history:
            return list(set(customer.purchase_history))
        return ["electronics", "clothing", "sports"]
    
    def _get_history_categories(self, customer) -> List[str]:
        """Get categories from customer's purchase history"""
        return customer.purchase_history if customer.purchase_history else []
    
    def _apply_tier_benefits(self, recommendations: List[Dict[str, Any]], tier: str) -> List[Dict[str, Any]]:
        """Apply customer tier benefits to recommendations"""
        for rec in recommendations:
            product = rec["product"]
            
            if tier in ["gold", "platinum"]:
                # Add exclusive badge
                product["exclusive_offer"] = True
                product["tier_discount"] = 0.15 if tier == "gold" else 0.20
            
            rec["tier_benefits"] = {
                "exclusive_access": tier in ["gold", "platinum"],
                "discount_rate": 0.15 if tier == "gold" else 0.20 if tier == "platinum" else 0.05
            }
        
        return recommendations
    
    def _generate_recommendation_explanation(self, recommendations: List[Dict[str, Any]], customer, intent: str) -> str:
        """Generate explanation for recommendations"""
        name = customer.name.split()[0]
        
        if intent == "personalized":
            return f"Hi {name}! I've curated these personalized recommendations based on your {customer.tier} membership and shopping preferences."
        elif intent == "similar_products":
            return f"Here are some products similar to what you're looking at, {name}."
        elif intent == "trending":
            return f"These are the trending products right now, {name}. Perfect timing to check them out!"
        elif intent == "category_browse":
            return f"I've found some great options in this category for you, {name}."
        else:
            return f"Based on your shopping history and preferences, I think you'll love these products, {name}!"
