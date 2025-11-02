from typing import Dict, Any, List, Optional
from agents.sales_agent import SalesAgent
from agents.recommendation_agent import RecommendationAgent
from agents.inventory_agent import InventoryAgent
from agents.payment_agent import PaymentAgent
from agents.fulfillment_agent import FulfillmentAgent
from agents.loyalty_agent import LoyaltyAgent
from agents.post_purchase_agent import PostPurchaseAgent
from data.synthetic_customers import CUSTOMERS
from data.mock_services import MockProductService, MockInventoryService, MockPaymentService
from models import ChannelType, OrderStatus
import asyncio
import json
from datetime import datetime

class AgentOrchestrator:
    def __init__(self):
        self.sales_agent = SalesAgent()
        self.worker_agents = {
            "recommendation": RecommendationAgent(),
            "inventory": InventoryAgent(),
            "payment": PaymentAgent(),
            "fulfillment": FulfillmentAgent(),
            "loyalty": LoyaltyAgent(),
            "post_purchase": PostPurchaseAgent()
        }
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.customers = {c.id: c for c in CUSTOMERS}
    
    async def execute_workflow(self, workflow_type: str, customer_id: str, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete workflow orchestration"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{customer_id}"
        
        # Initialize workflow
        self.active_workflows[workflow_id] = {
            "type": workflow_type,
            "customer_id": customer_id,
            "status": "running",
            "steps_completed": [],
            "current_step": 0,
            "data": initial_data,
            "results": {},
            "created_at": datetime.now()
        }
        
        try:
            if workflow_type == "product_discovery":
                result = await self._execute_product_discovery_workflow(workflow_id, customer_id, initial_data)
            elif workflow_type == "purchase_flow":
                result = await self._execute_purchase_workflow(workflow_id, customer_id, initial_data)
            elif workflow_type == "channel_switch":
                result = await self._execute_channel_switch_workflow(workflow_id, customer_id, initial_data)
            elif workflow_type == "post_purchase_support":
                result = await self._execute_post_purchase_workflow(workflow_id, customer_id, initial_data)
            else:
                result = {"error": f"Unknown workflow type: {workflow_type}"}
            
            # Mark workflow as completed
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now()
            
            return result
            
        except Exception as e:
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)
            return {"error": str(e)}
    
    async def _execute_product_discovery_workflow(self, workflow_id: str, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute product discovery workflow"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        workflow = self.active_workflows[workflow_id]
        results = {}
        
        # Step 1: Start conversation
        workflow["current_step"] = 1
        workflow["steps_completed"].append("start_conversation")
        
        conversation_result = await self.sales_agent.execute_task(customer_id, {
            "action": "start_conversation",
            "channel": data.get("channel", "web")
        })
        results["conversation"] = conversation_result
        
        # Step 2: Get recommendations
        workflow["current_step"] = 2
        workflow["steps_completed"].append("get_recommendations")
        
        recommendation_result = await self.worker_agents["recommendation"].execute_task(customer_id, {
            "customer": customer.dict(),
            "preferences": data.get("preferences", {}),
            "message": data.get("message", "Show me some products")
        })
        results["recommendations"] = recommendation_result
        
        # Step 3: Check inventory
        if recommendation_result.get("recommendations"):
            workflow["current_step"] = 3
            workflow["steps_completed"].append("check_inventory")
            
            products = [rec["product"]["sku"] for rec in recommendation_result["recommendations"]]
            inventory_result = await self.worker_agents["inventory"].execute_task(customer_id, {
                "action": "check_availability",
                "products": products,
                "customer_location": customer.location
            })
            results["inventory"] = inventory_result
        
        # Step 4: Get loyalty offers
        workflow["current_step"] = 4
        workflow["steps_completed"].append("get_offers")
        
        loyalty_result = await self.worker_agents["loyalty"].execute_task(customer_id, {
            "action": "get_offers",
            "customer": customer.dict(),
            "purchase_amount": data.get("purchase_amount", 0)
        })
        results["loyalty"] = loyalty_result
        
        workflow["results"] = results
        return {
            "workflow_id": workflow_id,
            "workflow_type": "product_discovery",
            "status": "completed",
            "results": results,
            "message": "Product discovery workflow completed successfully"
        }
    
    async def _execute_purchase_workflow(self, workflow_id: str, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute complete purchase workflow"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        workflow = self.active_workflows[workflow_id]
        results = {}
        
        # Step 1: Validate cart
        workflow["current_step"] = 1
        workflow["steps_completed"].append("validate_cart")
        
        cart_items = data.get("cart", [])
        if not cart_items:
            return {"error": "No items in cart"}
        
        # Step 2: Check inventory
        workflow["current_step"] = 2
        workflow["steps_completed"].append("check_inventory")
        
        inventory_result = await self.worker_agents["inventory"].execute_task(customer_id, {
            "action": "check_availability",
            "products": cart_items,
            "customer_location": customer.location
        })
        results["inventory"] = inventory_result
        
        if not inventory_result.get("all_available", False):
            return {
                "error": "Some items are not available",
                "inventory_result": inventory_result
            }
        
        # Step 3: Calculate total with loyalty benefits
        workflow["current_step"] = 3
        workflow["steps_completed"].append("calculate_total")
        
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in cart_items)
        payment_calculation = await self.worker_agents["payment"].execute_task(customer_id, {
            "action": "calculate_total",
            "cart": cart_items,
            "customer": customer.dict(),
            "promotions": data.get("promotions", [])
        })
        results["payment_calculation"] = payment_calculation
        
        # Step 4: Process payment
        workflow["current_step"] = 4
        workflow["steps_completed"].append("process_payment")
        
        payment_result = await self.worker_agents["payment"].execute_task(customer_id, {
            "action": "process_payment",
            "amount": payment_calculation["total"],
            "payment_method": data.get("payment_method", "credit_card"),
            "customer": customer.dict(),
            "cart": cart_items
        })
        results["payment"] = payment_result
        
        if not payment_result.get("success", False):
            return {
                "error": "Payment failed",
                "payment_result": payment_result
            }
        
        # Step 5: Schedule fulfillment
        workflow["current_step"] = 5
        workflow["steps_completed"].append("schedule_fulfillment")
        
        order_data = {
            "id": f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "customer_id": customer_id,
            "items": cart_items,
            "total_amount": payment_calculation["total"],
            "status": "confirmed",
            "payment_method": data.get("payment_method", "credit_card"),
            "fulfillment_method": data.get("fulfillment_method", "ship_to_home")
        }
        
        fulfillment_result = await self.worker_agents["fulfillment"].execute_task(customer_id, {
            "action": "schedule_fulfillment",
            "order": order_data,
            "customer": customer.dict(),
            "preferences": data.get("fulfillment_preferences", {})
        })
        results["fulfillment"] = fulfillment_result
        
        workflow["results"] = results
        return {
            "workflow_id": workflow_id,
            "workflow_type": "purchase_flow",
            "status": "completed",
            "order_id": order_data["id"],
            "results": results,
            "message": "Purchase workflow completed successfully"
        }
    
    async def _execute_channel_switch_workflow(self, workflow_id: str, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute channel switching workflow"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        workflow = self.active_workflows[workflow_id]
        results = {}
        
        # Step 1: Get current session
        workflow["current_step"] = 1
        workflow["steps_completed"].append("get_session")
        
        session_id = data.get("session_id")
        if not session_id:
            return {"error": "Session ID required"}
        
        session = self.sales_agent.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Step 2: Switch channel
        workflow["current_step"] = 2
        workflow["steps_completed"].append("switch_channel")
        
        new_channel = data.get("new_channel", "web")
        channel_switch_result = await self.sales_agent.execute_task(customer_id, {
            "action": "switch_channel",
            "session_id": session_id,
            "new_channel": new_channel
        })
        results["channel_switch"] = channel_switch_result
        
        # Step 3: Transfer context
        workflow["current_step"] = 3
        workflow["steps_completed"].append("transfer_context")
        
        context_transfer = {
            "conversation_history": session.messages,
            "current_context": session.context,
            "active_products": session.context.get("current_products", []),
            "cart": session.context.get("cart", [])
        }
        results["context_transfer"] = context_transfer
        
        # Step 4: Resume conversation
        workflow["current_step"] = 4
        workflow["steps_completed"].append("resume_conversation")
        
        resume_result = await self.sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "session_id": session_id,
            "message": f"Continuing our conversation on {new_channel}",
            "channel": new_channel
        })
        results["resume"] = resume_result
        
        workflow["results"] = results
        return {
            "workflow_id": workflow_id,
            "workflow_type": "channel_switch",
            "status": "completed",
            "results": results,
            "message": "Channel switch workflow completed successfully"
        }
    
    async def _execute_post_purchase_workflow(self, workflow_id: str, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute post-purchase support workflow"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}
        
        workflow = self.active_workflows[workflow_id]
        results = {}
        
        # Step 1: Identify support need
        workflow["current_step"] = 1
        workflow["steps_completed"].append("identify_need")
        
        support_type = data.get("support_type", "general")
        order_id = data.get("order_id")
        
        # Step 2: Route to appropriate agent
        workflow["current_step"] = 2
        workflow["steps_completed"].append("route_support")
        
        if support_type == "return":
            support_result = await self.worker_agents["post_purchase"].execute_task(customer_id, {
                "action": "handle_return",
                "order_id": order_id,
                "items": data.get("items", []),
                "reason": data.get("reason", "No longer needed"),
                "customer": customer.dict()
            })
        elif support_type == "tracking":
            support_result = await self.worker_agents["post_purchase"].execute_task(customer_id, {
                "action": "track_shipment",
                "order_id": order_id,
                "tracking_number": data.get("tracking_number"),
                "customer": customer.dict()
            })
        elif support_type == "feedback":
            support_result = await self.worker_agents["post_purchase"].execute_task(customer_id, {
                "action": "solicit_feedback",
                "order_id": order_id,
                "customer": customer.dict(),
                "feedback_type": data.get("feedback_type", "general")
            })
        else:
            support_result = await self.worker_agents["post_purchase"].execute_task(customer_id, {
                "action": "handle_complaint",
                "complaint_type": support_type,
                "complaint_details": data.get("complaint_details", ""),
                "customer": customer.dict(),
                "order_id": order_id
            })
        
        results["support"] = support_result
        
        # Step 3: Follow-up actions
        workflow["current_step"] = 3
        workflow["steps_completed"].append("follow_up")
        
        follow_up_actions = []
        if support_type == "return" and support_result.get("return_processed"):
            follow_up_actions.append("Schedule return pickup")
            follow_up_actions.append("Process refund")
        elif support_type == "tracking":
            follow_up_actions.append("Send tracking updates")
        elif support_type == "feedback":
            follow_up_actions.append("Send feedback survey")
        
        results["follow_up_actions"] = follow_up_actions
        
        workflow["results"] = results
        return {
            "workflow_id": workflow_id,
            "workflow_type": "post_purchase_support",
            "status": "completed",
            "results": results,
            "message": "Post-purchase support workflow completed successfully"
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow"""
        return self.active_workflows.get(workflow_id)
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """Get all active workflows"""
        return list(self.active_workflows.values())
    
    async def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Cancel an active workflow"""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["status"] = "cancelled"
            self.active_workflows[workflow_id]["cancelled_at"] = datetime.now()
            return {"status": "cancelled", "workflow_id": workflow_id}
        else:
            return {"error": "Workflow not found"}

# Global orchestrator instance
orchestrator = AgentOrchestrator()
