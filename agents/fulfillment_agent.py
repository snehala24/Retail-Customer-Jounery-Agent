from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
from models import AgentTask, Order, OrderStatus
import random
from datetime import datetime, timedelta

class FulfillmentAgent(BaseAgent):
    def __init__(self):
        super().__init__("fulfillment_agent", "fulfillment")
    
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle fulfillment-related tasks"""
        task_data = task.task_data
        customer_id = task.customer_id
        
        action = task_data.get("action", "schedule_fulfillment")
        
        if action == "schedule_fulfillment":
            return await self._schedule_fulfillment(task_data)
        elif action == "track_order":
            return await self._track_order(task_data)
        elif action == "update_fulfillment":
            return await self._update_fulfillment(task_data)
        elif action == "get_fulfillment_options":
            return await self._get_fulfillment_options(task_data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    async def _schedule_fulfillment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule order fulfillment"""
        order = task_data.get("order", {})
        customer = task_data.get("customer", {})
        preferences = task_data.get("preferences", {})
        
        if not order:
            return {"error": "No order provided"}
        
        fulfillment_method = order.get("fulfillment_method", "ship_to_home")
        items = order.get("items", [])
        
        # Generate fulfillment schedule
        if fulfillment_method == "ship_to_home":
            return await self._schedule_shipping(order, customer, preferences)
        elif fulfillment_method == "click_and_collect":
            return await self._schedule_click_collect(order, customer, preferences)
        elif fulfillment_method == "in_store_pickup":
            return await self._schedule_in_store_pickup(order, customer, preferences)
        else:
            return {"error": f"Unknown fulfillment method: {fulfillment_method}"}
    
    async def _schedule_shipping(self, order: Dict[str, Any], customer: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule shipping fulfillment"""
        order_id = order.get("id")
        items = order.get("items", [])
        customer_location = customer.get("location")
        
        # Calculate shipping time based on location
        shipping_time = self._calculate_shipping_time(customer_location)
        
        # Generate tracking information
        tracking_number = f"TRK{random.randint(100000, 999999)}"
        
        # Schedule pickup and delivery
        pickup_date = datetime.now() + timedelta(hours=2)  # Pickup in 2 hours
        delivery_date = pickup_date + timedelta(days=shipping_time)
        
        # Generate shipping details
        shipping_details = {
            "tracking_number": tracking_number,
            "carrier": "FedEx",
            "service_type": "Standard Ground",
            "pickup_date": pickup_date.isoformat(),
            "estimated_delivery": delivery_date.isoformat(),
            "shipping_time_days": shipping_time,
            "delivery_address": customer.get("address", "Customer Address"),
            "special_instructions": preferences.get("delivery_instructions", "")
        }
        
        # Notify logistics
        logistics_notification = await self._notify_logistics(order_id, items, shipping_details)
        
        return {
            "fulfillment_scheduled": True,
            "method": "ship_to_home",
            "tracking_number": tracking_number,
            "shipping_details": shipping_details,
            "logistics_notified": logistics_notification,
            "message": self._generate_shipping_message(shipping_details, customer)
        }
    
    async def _schedule_click_collect(self, order: Dict[str, Any], customer: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule click and collect fulfillment"""
        order_id = order.get("id")
        items = order.get("items", [])
        store_location = preferences.get("store_location", "store_001")
        
        # Calculate preparation time
        preparation_time = self._calculate_preparation_time(items)
        
        # Schedule store preparation
        ready_time = datetime.now() + timedelta(hours=preparation_time)
        pickup_window = {
            "start": ready_time,
            "end": ready_time + timedelta(hours=4)  # 4-hour pickup window
        }
        
        # Generate store details
        store_details = {
            "store_location": store_location,
            "store_name": self._get_store_name(store_location),
            "store_address": self._get_store_address(store_location),
            "ready_time": ready_time.isoformat(),
            "pickup_window": {
                "start": pickup_window["start"].isoformat(),
                "end": pickup_window["end"].isoformat()
            },
            "preparation_time_hours": preparation_time
        }
        
        # Notify store staff
        store_notification = await self._notify_store_staff(order_id, items, store_details)
        
        return {
            "fulfillment_scheduled": True,
            "method": "click_and_collect",
            "store_details": store_details,
            "store_notified": store_notification,
            "message": self._generate_click_collect_message(store_details, customer)
        }
    
    async def _schedule_in_store_pickup(self, order: Dict[str, Any], customer: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule in-store pickup fulfillment"""
        order_id = order.get("id")
        items = order.get("items", [])
        store_location = preferences.get("store_location", "store_001")
        
        # Items are immediately available
        available_time = datetime.now() + timedelta(minutes=30)  # 30 minutes for staff preparation
        
        # Generate store details
        store_details = {
            "store_location": store_location,
            "store_name": self._get_store_name(store_location),
            "store_address": self._get_store_address(store_location),
            "available_time": available_time.isoformat(),
            "pickup_instructions": "Items are ready for immediate pickup"
        }
        
        # Notify store staff
        store_notification = await self._notify_store_staff(order_id, items, store_details)
        
        return {
            "fulfillment_scheduled": True,
            "method": "in_store_pickup",
            "store_details": store_details,
            "store_notified": store_notification,
            "message": self._generate_in_store_pickup_message(store_details, customer)
        }
    
    async def _track_order(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track order fulfillment status"""
        order_id = task_data.get("order_id")
        tracking_number = task_data.get("tracking_number")
        
        if not order_id and not tracking_number:
            return {"error": "Order ID or tracking number required"}
        
        # Generate mock tracking information
        tracking_info = self._generate_tracking_info(order_id, tracking_number)
        
        return {
            "order_id": order_id,
            "tracking_number": tracking_number,
            "status": tracking_info["status"],
            "tracking_info": tracking_info,
            "message": self._generate_tracking_message(tracking_info)
        }
    
    async def _update_fulfillment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update fulfillment status"""
        order_id = task_data.get("order_id")
        new_status = task_data.get("status")
        update_reason = task_data.get("reason", "Status update")
        
        if not order_id or not new_status:
            return {"error": "Order ID and status required"}
        
        # Update fulfillment status
        update_result = await self._process_fulfillment_update(order_id, new_status, update_reason)
        
        return {
            "order_id": order_id,
            "status_updated": True,
            "new_status": new_status,
            "update_reason": update_reason,
            "timestamp": datetime.now().isoformat(),
            "message": f"Order status updated to {new_status}"
        }
    
    async def _get_fulfillment_options(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get available fulfillment options"""
        items = task_data.get("items", [])
        customer_location = task_data.get("customer_location")
        
        if not items:
            return {"error": "No items provided"}
        
        # Calculate fulfillment options
        options = []
        
        # Shipping option
        shipping_time = self._calculate_shipping_time(customer_location)
        shipping_cost = self._calculate_shipping_cost(items, customer_location)
        
        options.append({
            "method": "ship_to_home",
            "description": "Ship directly to your home",
            "estimated_delivery": f"{shipping_time} business days",
            "cost": shipping_cost,
            "available": True
        })
        
        # Store pickup options
        store_options = self._get_store_pickup_options(customer_location)
        options.extend(store_options)
        
        return {
            "fulfillment_options": options,
            "recommended_option": self._get_recommended_option(options),
            "message": "Here are your fulfillment options"
        }
    
    def _calculate_shipping_time(self, customer_location: Optional[str]) -> int:
        """Calculate shipping time based on location"""
        if not customer_location:
            return 3  # Default 3 days
        
        # Mock shipping time calculation
        location_times = {
            "New York, NY": 1,
            "Los Angeles, CA": 2,
            "Miami, FL": 3,
            "Seattle, WA": 4,
            "Beverly Hills, CA": 1
        }
        
        return location_times.get(customer_location, 3)
    
    def _calculate_preparation_time(self, items: List[Dict[str, Any]]) -> int:
        """Calculate store preparation time"""
        # Base time: 1 hour
        base_time = 1
        
        # Add time based on number of items
        item_count = len(items)
        additional_time = min(item_count * 0.1, 2)  # Max 2 additional hours
        
        return int(base_time + additional_time)
    
    def _calculate_shipping_cost(self, items: List[Dict[str, Any]], customer_location: Optional[str]) -> float:
        """Calculate shipping cost"""
        total_value = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        # Free shipping over $100
        if total_value >= 100:
            return 0.0
        
        # Base shipping cost
        return 9.99
    
    def _get_store_pickup_options(self, customer_location: Optional[str]) -> List[Dict[str, Any]]:
        """Get store pickup options"""
        stores = [
            {"id": "store_001", "name": "Downtown Store", "distance": 2.1},
            {"id": "store_002", "name": "Mall Location", "distance": 4.5}
        ]
        
        options = []
        for store in stores:
            options.append({
                "method": "click_and_collect",
                "description": f"Pick up at {store['name']}",
                "store_id": store["id"],
                "store_name": store["name"],
                "distance": f"{store['distance']} miles",
                "estimated_ready": "1-2 hours",
                "cost": 0.0,
                "available": True
            })
        
        return options
    
    def _get_recommended_option(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get recommended fulfillment option"""
        if not options:
            return {}
        
        # Prefer free options
        free_options = [opt for opt in options if opt.get("cost", 0) == 0]
        if free_options:
            return free_options[0]
        
        # Otherwise return first option
        return options[0]
    
    def _get_store_name(self, store_location: str) -> str:
        """Get store name from location"""
        store_names = {
            "store_001": "Downtown Store",
            "store_002": "Mall Location",
            "store_003": "Airport Store"
        }
        return store_names.get(store_location, store_location)
    
    def _get_store_address(self, store_location: str) -> str:
        """Get store address from location"""
        store_addresses = {
            "store_001": "123 Main St, Downtown",
            "store_002": "456 Mall Dr, Shopping Center",
            "store_003": "789 Airport Blvd, Terminal 2"
        }
        return store_addresses.get(store_location, "Store Address")
    
    def _generate_tracking_info(self, order_id: Optional[str], tracking_number: Optional[str]) -> Dict[str, Any]:
        """Generate mock tracking information"""
        # Mock tracking status progression
        statuses = ["processing", "shipped", "in_transit", "out_for_delivery", "delivered"]
        current_status = random.choice(statuses)
        
        tracking_events = []
        base_time = datetime.now() - timedelta(days=2)
        
        for i, status in enumerate(statuses[:statuses.index(current_status) + 1]):
            event_time = base_time + timedelta(hours=i * 12)
            tracking_events.append({
                "status": status,
                "timestamp": event_time.isoformat(),
                "location": self._get_tracking_location(status),
                "description": self._get_tracking_description(status)
            })
        
        return {
            "status": current_status,
            "events": tracking_events,
            "estimated_delivery": (datetime.now() + timedelta(days=1)).isoformat()
        }
    
    def _get_tracking_location(self, status: str) -> str:
        """Get location for tracking status"""
        locations = {
            "processing": "Distribution Center",
            "shipped": "Origin Facility",
            "in_transit": "In Transit",
            "out_for_delivery": "Local Facility",
            "delivered": "Customer Address"
        }
        return locations.get(status, "Unknown")
    
    def _get_tracking_description(self, status: str) -> str:
        """Get description for tracking status"""
        descriptions = {
            "processing": "Order is being prepared for shipment",
            "shipped": "Package has been shipped",
            "in_transit": "Package is in transit to destination",
            "out_for_delivery": "Package is out for delivery",
            "delivered": "Package has been delivered"
        }
        return descriptions.get(status, "Status update")
    
    async def _notify_logistics(self, order_id: str, items: List[Dict[str, Any]], shipping_details: Dict[str, Any]) -> bool:
        """Notify logistics team about shipment"""
        # Mock notification
        print(f"LOGISTICS NOTIFICATION: Order {order_id} ready for pickup")
        print(f"Items: {len(items)} items")
        print(f"Tracking: {shipping_details['tracking_number']}")
        return True
    
    async def _notify_store_staff(self, order_id: str, items: List[Dict[str, Any]], store_details: Dict[str, Any]) -> bool:
        """Notify store staff about pickup order"""
        # Mock notification
        print(f"STORE NOTIFICATION: Order {order_id} ready for pickup at {store_details['store_name']}")
        print(f"Items: {len(items)} items")
        return True
    
    async def _process_fulfillment_update(self, order_id: str, status: str, reason: str) -> bool:
        """Process fulfillment status update"""
        # Mock status update
        print(f"FULFILLMENT UPDATE: Order {order_id} status changed to {status}")
        print(f"Reason: {reason}")
        return True
    
    def _generate_shipping_message(self, shipping_details: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Generate shipping confirmation message"""
        name = customer.get("name", "Customer").split()[0]
        tracking = shipping_details["tracking_number"]
        delivery_date = shipping_details["estimated_delivery"][:10]  # Date only
        
        return f"Great news {name}! Your order has been scheduled for shipping. Tracking number: {tracking}. Estimated delivery: {delivery_date}. You'll receive updates as your package moves through our network."
    
    def _generate_click_collect_message(self, store_details: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Generate click and collect confirmation message"""
        name = customer.get("name", "Customer").split()[0]
        store_name = store_details["store_name"]
        ready_time = store_details["ready_time"][:16]  # Date and time
        
        return f"Perfect {name}! Your order will be ready for pickup at {store_name} by {ready_time}. You'll receive a notification when it's ready. Please bring a valid ID for pickup."
    
    def _generate_in_store_pickup_message(self, store_details: Dict[str, Any], customer: Dict[str, Any]) -> str:
        """Generate in-store pickup confirmation message"""
        name = customer.get("name", "Customer").split()[0]
        store_name = store_details["store_name"]
        
        return f"Excellent {name}! Your items are available for immediate pickup at {store_name}. Please visit the customer service desk with your order confirmation."
    
    def _generate_tracking_message(self, tracking_info: Dict[str, Any]) -> str:
        """Generate tracking status message"""
        status = tracking_info["status"]
        events = tracking_info["events"]
        
        if status == "delivered":
            return "Your package has been delivered! Thank you for your order."
        elif status == "out_for_delivery":
            return "Your package is out for delivery and should arrive today!"
        elif status == "in_transit":
            return "Your package is in transit and on its way to you."
        else:
            return f"Your order status is: {status.replace('_', ' ').title()}"
