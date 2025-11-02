from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models import AgentTask
from data.mock_services import MockInventoryService, MockProductService
from models import InventoryItem
import random

class InventoryAgent(BaseAgent):
    def __init__(self):
        super().__init__("inventory_agent", "inventory")
        self.inventory_service = MockInventoryService()
        self.product_service = MockProductService()
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle inventory-related tasks"""
        task_data = task.task_data
        customer_id = task.customer_id
        
        action = task_data.get("action", "check_availability")
        
        if action == "check_availability":
            return await self._check_availability(task_data)
        elif action == "reserve_items":
            return await self._reserve_items(task_data)
        elif action == "release_reservation":
            return await self._release_reservation(task_data)
        elif action == "get_fulfillment_options":
            return await self._get_fulfillment_options(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _check_availability(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check product availability across locations"""
        products = task_data.get("products", [])
        customer_location = task_data.get("customer_location")
        message = task_data.get("message", "")
        
        if not products:
            return {"error": "No products specified"}
        
        availability_results = []
        total_available = 0
        
        for product_info in products:
            sku = product_info.get("sku") if isinstance(product_info, dict) else product_info
            quantity = product_info.get("quantity", 1) if isinstance(product_info, dict) else 1
            
            # Get product details
            product = self.product_service.get_product(sku)
            if not product:
                availability_results.append({
                    "sku": sku,
                    "available": False,
                    "error": "Product not found"
                })
                continue
            
            # Check inventory across all locations
            inventory_items = self.inventory_service.check_inventory(sku)
            
            # Calculate total availability
            total_stock = sum(item.quantity - item.reserved for item in inventory_items)
            available = total_stock >= quantity
            
            # Find best fulfillment options
            fulfillment_options = self._find_fulfillment_options(inventory_items, quantity, customer_location)
            
            availability_results.append({
                "sku": sku,
                "product": product.model_dump(),
                "available": available,
                "total_stock": total_stock,
                "requested_quantity": quantity,
                "fulfillment_options": fulfillment_options,
                "locations": [
                    {
                        "location": item.location,
                        "available": item.quantity - item.reserved,
                        "reserved": item.reserved
                    }
                    for item in inventory_items
                ]
            })
            
            if available:
                total_available += 1
        
        # Generate response message
        response_message = self._generate_availability_message(availability_results, message)
        
        return {
            "availability_results": availability_results,
            "message": response_message,
            "total_products": len(products),
            "available_products": total_available,
            "all_available": total_available == len(products)
        }
    
    async def _reserve_items(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reserve items for customer"""
        reservations = task_data.get("reservations", [])
        customer_id = task_data.get("customer_id")
        
        if not reservations:
            return {"error": "No reservations specified"}
        
        reservation_results = []
        successful_reservations = 0
        
        for reservation in reservations:
            sku = reservation.get("sku")
            location = reservation.get("location")
            quantity = reservation.get("quantity", 1)
            
            # Attempt to reserve
            success = self.inventory_service.reserve_item(sku, location, quantity)
            
            reservation_results.append({
                "sku": sku,
                "location": location,
                "quantity": quantity,
                "success": success,
                "reservation_id": f"RES_{random.randint(100000, 999999)}" if success else None
            })
            
            if success:
                successful_reservations += 1
        
        return {
            "reservation_results": reservation_results,
            "successful_reservations": successful_reservations,
            "total_reservations": len(reservations),
            "all_successful": successful_reservations == len(reservations)
        }
    
    async def _release_reservation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Release reserved items"""
        reservations = task_data.get("reservations", [])
        
        if not reservations:
            return {"error": "No reservations specified"}
        
        release_results = []
        successful_releases = 0
        
        for reservation in reservations:
            sku = reservation.get("sku")
            location = reservation.get("location")
            quantity = reservation.get("quantity", 1)
            
            # Attempt to release
            success = self.inventory_service.release_reservation(sku, location, quantity)
            
            release_results.append({
                "sku": sku,
                "location": location,
                "quantity": quantity,
                "success": success
            })
            
            if success:
                successful_releases += 1
        
        return {
            "release_results": release_results,
            "successful_releases": successful_releases,
            "total_releases": len(reservations)
        }
    
    async def _get_fulfillment_options(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get available fulfillment options for products"""
        products = task_data.get("products", [])
        customer_location = task_data.get("customer_location")
        
        if not products:
            return {"error": "No products specified"}
        
        fulfillment_options = []
        
        for product_info in products:
            sku = product_info.get("sku") if isinstance(product_info, dict) else product_info
            quantity = product_info.get("quantity", 1) if isinstance(product_info, dict) else 1
            
            # Check inventory
            inventory_items = self.inventory_service.check_inventory(sku)
            options = self._find_fulfillment_options(inventory_items, quantity, customer_location)
            
            fulfillment_options.append({
                "sku": sku,
                "options": options
            })
        
        return {
            "fulfillment_options": fulfillment_options,
            "recommended_option": self._get_recommended_fulfillment_option(fulfillment_options)
        }
    
    def _find_fulfillment_options(self, inventory_items: List[InventoryItem], quantity: int, customer_location: Optional[str]) -> List[Dict[str, Any]]:
        """Find available fulfillment options for a product"""
        options = []
        
        # Check online availability
        online_item = next((item for item in inventory_items if item.location == "online"), None)
        if online_item and (online_item.quantity - online_item.reserved) >= quantity:
            options.append({
                "type": "ship_to_home",
                "location": "online",
                "available": True,
                "quantity": online_item.quantity - online_item.reserved,
                "estimated_delivery": "2-3 business days",
                "shipping_cost": 9.99 if quantity * 50 < 100 else 0,  # Free shipping over $100
                "description": "Ship directly to your home"
            })
        
        # Check store availability
        store_items = [item for item in inventory_items if item.location.startswith("store_")]
        for store_item in store_items:
            if (store_item.quantity - store_item.reserved) >= quantity:
                store_name = self._get_store_name(store_item.location)
                distance = self._calculate_distance(customer_location, store_item.location)
                
                options.append({
                    "type": "click_and_collect",
                    "location": store_item.location,
                    "store_name": store_name,
                    "available": True,
                    "quantity": store_item.quantity - store_item.reserved,
                    "pickup_time": "Ready in 1-2 hours",
                    "distance": distance,
                    "description": f"Pick up at {store_name}"
                })
                
                options.append({
                    "type": "in_store_pickup",
                    "location": store_item.location,
                    "store_name": store_name,
                    "available": True,
                    "quantity": store_item.quantity - store_item.reserved,
                    "pickup_time": "Available now",
                    "distance": distance,
                    "description": f"Available now at {store_name}"
                })
        
        # Sort by preference (online first, then by distance)
        options.sort(key=lambda x: (x["type"] != "ship_to_home", x.get("distance", 999)))
        
        return options
    
    def _get_store_name(self, location: str) -> str:
        """Get human-readable store name"""
        store_mapping = {
            "store_001": "Downtown Store",
            "store_002": "Mall Location",
            "store_003": "Airport Store"
        }
        return store_mapping.get(location, location.replace("_", " ").title())
    
    def _calculate_distance(self, customer_location: Optional[str], store_location: str) -> float:
        """Calculate distance from customer to store (mock)"""
        if not customer_location:
            return 5.0  # Default distance
        
        # Mock distance calculation
        distance_mapping = {
            "New York, NY": {"store_001": 2.1, "store_002": 4.5},
            "Los Angeles, CA": {"store_001": 3.2, "store_002": 1.8},
            "Miami, FL": {"store_001": 1.5, "store_002": 6.2},
            "Seattle, WA": {"store_001": 4.1, "store_002": 2.8},
            "Beverly Hills, CA": {"store_001": 0.8, "store_002": 3.4}
        }
        
        return distance_mapping.get(customer_location, {}).get(store_location, 5.0)
    
    def _get_recommended_fulfillment_option(self, fulfillment_options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get recommended fulfillment option"""
        if not fulfillment_options:
            return {}
        
        # Find the option with the most availability
        best_option = None
        max_availability = 0
        
        for product_options in fulfillment_options:
            for option in product_options.get("options", []):
                if option.get("available") and option.get("quantity", 0) > max_availability:
                    max_availability = option.get("quantity", 0)
                    best_option = option
        
        return best_option or {}
    
    def _generate_availability_message(self, availability_results: List[Dict[str, Any]], message: str) -> str:
        """Generate human-readable availability message"""
        total_products = len(availability_results)
        available_products = sum(1 for result in availability_results if result.get("available"))
        
        if available_products == 0:
            return "I'm sorry, but none of the requested products are currently available. Let me suggest some alternatives."
        elif available_products == total_products:
            return "Great news! All the products you're looking for are available. I can show you the best fulfillment options."
        else:
            return f"Good news! {available_products} out of {total_products} products are available. Let me show you what's in stock and suggest alternatives for the others."
    
    def _generate_fulfillment_message(self, fulfillment_options: List[Dict[str, Any]]) -> str:
        """Generate message about fulfillment options"""
        if not fulfillment_options:
            return "I'm checking fulfillment options for you..."
        
        online_available = any(
            option.get("type") == "ship_to_home" and option.get("available")
            for product_options in fulfillment_options
            for option in product_options.get("options", [])
        )
        
        store_available = any(
            option.get("type") in ["click_and_collect", "in_store_pickup"] and option.get("available")
            for product_options in fulfillment_options
            for option in product_options.get("options", [])
        )
        
        if online_available and store_available:
            return "Perfect! You have multiple fulfillment options - I can ship to your home or you can pick up at a nearby store."
        elif online_available:
            return "I can ship these items directly to your home. Would you like me to proceed with shipping?"
        elif store_available:
            return "These items are available for pickup at nearby stores. I can show you the closest locations."
        else:
            return "I'm checking all fulfillment options for you. Let me find the best way to get these items to you."
