from typing import Dict, Any, List
from orchestration import orchestrator
from data.synthetic_customers import CUSTOMERS
from models import ChannelType
import asyncio
import json
from datetime import datetime

class DemoScenarios:
    def __init__(self):
        self.orchestrator = orchestrator
        self.customers = {c.id: c for c in CUSTOMERS}
    
    async def run_scenario(self, scenario_name: str, customer_id: str = "customer_001") -> Dict[str, Any]:
        """Run a specific demo scenario"""
        if scenario_name == "product_search":
            return await self._scenario_product_search(customer_id)
        elif scenario_name == "channel_switch":
            return await self._scenario_channel_switch(customer_id)
        elif scenario_name == "purchase_flow":
            return await self._scenario_purchase_flow(customer_id)
        elif scenario_name == "post_purchase":
            return await self._scenario_post_purchase(customer_id)
        elif scenario_name == "complete_journey":
            return await self._scenario_complete_journey(customer_id)
        else:
            return {"error": f"Unknown scenario: {scenario_name}"}
    
    async def _scenario_product_search(self, customer_id: str) -> Dict[str, Any]:
        """Demo scenario: Product search and recommendations"""
        print("🔍 Starting Product Search Scenario...")
        
        # Step 1: Customer starts conversation
        print("1. Customer starts conversation on mobile app")
        conversation_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "start_conversation",
            "channel": "mobile"
        })
        print(f"   Agent: {conversation_result['message']}")
        
        # Step 2: Customer asks for recommendations
        print("2. Customer: 'I'm looking for a new laptop'")
        message_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "session_id": conversation_result["session_id"],
            "message": "I'm looking for a new laptop",
            "channel": "mobile"
        })
        print(f"   Agent: {message_result['message']}")
        
        # Step 3: Get personalized recommendations
        print("3. Getting personalized recommendations...")
        recommendation_result = await self.orchestrator.worker_agents["recommendation"].execute_task(customer_id, {
            "customer": self.customers[customer_id].dict(),
            "preferences": {"style": "modern", "price_range": "premium"},
            "message": "I'm looking for a new laptop"
        })
        
        print(f"   Found {len(recommendation_result['recommendations'])} recommendations")
        for i, rec in enumerate(recommendation_result["recommendations"][:2], 1):
            print(f"   {i}. {rec['product']['name']} - ${rec['product']['price']} ({rec['reason']})")
        
        # Step 4: Check inventory
        print("4. Checking inventory availability...")
        products = [rec["product"]["sku"] for rec in recommendation_result["recommendations"][:2]]
        inventory_result = await self.orchestrator.worker_agents["inventory"].execute_task(customer_id, {
            "action": "check_availability",
            "products": products,
            "customer_location": self.customers[customer_id].location
        })
        
        available_count = sum(1 for result in inventory_result["availability_results"] if result["available"])
        print(f"   {available_count}/{len(products)} products available")
        
        return {
            "scenario": "product_search",
            "status": "completed",
            "conversation_id": conversation_result["session_id"],
            "recommendations": recommendation_result["recommendations"],
            "inventory": inventory_result,
            "message": "Product search scenario completed successfully"
        }
    
    async def _scenario_channel_switch(self, customer_id: str) -> Dict[str, Any]:
        """Demo scenario: Channel switching"""
        print("🔄 Starting Channel Switch Scenario...")
        
        # Step 1: Start conversation on mobile
        print("1. Customer starts conversation on mobile app")
        mobile_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "start_conversation",
            "channel": "mobile"
        })
        session_id = mobile_result["session_id"]
        print(f"   Agent: {mobile_result['message']}")
        
        # Step 2: Customer asks about products
        print("2. Customer: 'Show me some electronics'")
        mobile_message = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "session_id": session_id,
            "message": "Show me some electronics",
            "channel": "mobile"
        })
        print(f"   Agent: {mobile_message['message']}")
        
        # Step 3: Switch to WhatsApp
        print("3. Customer switches to WhatsApp")
        switch_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "switch_channel",
            "session_id": session_id,
            "new_channel": "whatsapp"
        })
        print(f"   Agent: {switch_result['message']}")
        
        # Step 4: Continue conversation on WhatsApp
        print("4. Customer continues on WhatsApp: 'What about phones?'")
        whatsapp_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "session_id": session_id,
            "message": "What about phones?",
            "channel": "whatsapp"
        })
        print(f"   Agent: {whatsapp_result['message']}")
        
        # Step 5: Switch to in-store kiosk
        print("5. Customer visits store and uses kiosk")
        kiosk_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "switch_channel",
            "session_id": session_id,
            "new_channel": "in_store_kiosk"
        })
        print(f"   Agent: {kiosk_result['message']}")
        
        return {
            "scenario": "channel_switch",
            "status": "completed",
            "session_id": session_id,
            "channels_used": ["mobile", "whatsapp", "in_store_kiosk"],
            "context_preserved": True,
            "message": "Channel switch scenario completed successfully"
        }
    
    async def _scenario_purchase_flow(self, customer_id: str) -> Dict[str, Any]:
        """Demo scenario: Complete purchase flow"""
        print("🛒 Starting Purchase Flow Scenario...")
        
        # Step 1: Start conversation
        print("1. Customer starts conversation")
        conversation_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "start_conversation",
            "channel": "web"
        })
        session_id = conversation_result["session_id"]
        print(f"   Agent: {conversation_result['message']}")
        
        # Step 2: Customer wants to buy
        print("2. Customer: 'I want to buy the MacBook Pro'")
        message_result = await self.orchestrator.sales_agent.execute_task(customer_id, {
            "action": "process_message",
            "session_id": session_id,
            "message": "I want to buy the MacBook Pro",
            "channel": "web"
        })
        print(f"   Agent: {message_result['message']}")
        
        # Step 3: Check inventory
        print("3. Checking inventory...")
        inventory_result = await self.orchestrator.worker_agents["inventory"].execute_task(customer_id, {
            "action": "check_availability",
            "products": [{"sku": "LAPTOP001", "quantity": 1}],
            "customer_location": self.customers[customer_id].location
        })
        print(f"   Inventory: {inventory_result['message']}")
        
        # Step 4: Calculate total with loyalty benefits
        print("4. Calculating total with loyalty benefits...")
        cart_items = [{"sku": "LAPTOP001", "quantity": 1, "price": 2499.99}]
        payment_calculation = await self.orchestrator.worker_agents["payment"].execute_task(customer_id, {
            "action": "calculate_total",
            "cart": cart_items,
            "customer": self.customers[customer_id].dict(),
            "promotions": []
        })
        print(f"   Subtotal: ${payment_calculation['subtotal']:.2f}")
        print(f"   Loyalty discount: ${payment_calculation['loyalty_discount']:.2f}")
        print(f"   Tax: ${payment_calculation['tax_amount']:.2f}")
        print(f"   Total: ${payment_calculation['total']:.2f}")
        
        # Step 5: Process payment
        print("5. Processing payment...")
        payment_result = await self.orchestrator.worker_agents["payment"].execute_task(customer_id, {
            "action": "process_payment",
            "amount": payment_calculation["total"],
            "payment_method": "credit_card",
            "customer": self.customers[customer_id].dict(),
            "cart": cart_items
        })
        
        if payment_result["success"]:
            print(f"   Payment successful! Transaction ID: {payment_result['transaction_id']}")
            print(f"   Amount charged: ${payment_result['amount_charged']:.2f}")
            print(f"   Loyalty points earned: {payment_result['loyalty_points_earned']}")
        else:
            print(f"   Payment failed: {payment_result['error']}")
            return {"error": "Payment failed", "payment_result": payment_result}
        
        # Step 6: Schedule fulfillment
        print("6. Scheduling fulfillment...")
        order_data = {
            "id": f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "customer_id": customer_id,
            "items": cart_items,
            "total_amount": payment_calculation["total"],
            "status": "confirmed",
            "payment_method": "credit_card",
            "fulfillment_method": "ship_to_home"
        }
        
        fulfillment_result = await self.orchestrator.worker_agents["fulfillment"].execute_task(customer_id, {
            "action": "schedule_fulfillment",
            "order": order_data,
            "customer": self.customers[customer_id].dict(),
            "preferences": {"delivery_instructions": "Leave at front door"}
        })
        print(f"   Fulfillment: {fulfillment_result['message']}")
        
        return {
            "scenario": "purchase_flow",
            "status": "completed",
            "order_id": order_data["id"],
            "payment_result": payment_result,
            "fulfillment_result": fulfillment_result,
            "message": "Purchase flow scenario completed successfully"
        }
    
    async def _scenario_post_purchase(self, customer_id: str) -> Dict[str, Any]:
        """Demo scenario: Post-purchase support"""
        print("📞 Starting Post-Purchase Support Scenario...")
        
        # Step 1: Customer has an issue
        print("1. Customer: 'I want to return my laptop'")
        return_result = await self.orchestrator.worker_agents["post_purchase"].execute_task(customer_id, {
            "action": "handle_return",
            "order_id": "ORD_20241201_143022",
            "items": [{"sku": "LAPTOP001", "quantity": 1, "price": 2499.99}],
            "reason": "Changed my mind",
            "customer": self.customers[customer_id].dict()
        })
        print(f"   Return processed: {return_result['return_processed']}")
        if return_result["return_processed"]:
            print(f"   Return ID: {return_result['return_id']}")
            print(f"   Refund amount: ${return_result['refund_amount']:.2f}")
            print(f"   Instructions: {return_result['return_instructions']['return_method']}")
        
        # Step 2: Track another order
        print("2. Customer: 'Track my order'")
        tracking_result = await self.orchestrator.worker_agents["post_purchase"].execute_task(customer_id, {
            "action": "track_shipment",
            "order_id": "ORD_20241201_120000",
            "customer": self.customers[customer_id].dict()
        })
        print(f"   Tracking: {tracking_result['message']}")
        if tracking_result["tracking_found"]:
            print(f"   Status: {tracking_result['tracking_info']['status']}")
            print(f"   Tracking number: {tracking_result['tracking_info']['tracking_number']}")
        
        # Step 3: Solicit feedback
        print("3. Soliciting feedback...")
        feedback_result = await self.orchestrator.worker_agents["post_purchase"].execute_task(customer_id, {
            "action": "solicit_feedback",
            "order_id": "ORD_20241201_120000",
            "customer": self.customers[customer_id].dict(),
            "feedback_type": "product"
        })
        print(f"   Feedback request: {feedback_result['message']}")
        
        return {
            "scenario": "post_purchase",
            "status": "completed",
            "return_result": return_result,
            "tracking_result": tracking_result,
            "feedback_result": feedback_result,
            "message": "Post-purchase support scenario completed successfully"
        }
    
    async def _scenario_complete_journey(self, customer_id: str) -> Dict[str, Any]:
        """Demo scenario: Complete customer journey"""
        print("🌟 Starting Complete Customer Journey Scenario...")
        
        journey_results = {}
        
        # Phase 1: Product Discovery
        print("\n📱 Phase 1: Product Discovery (Mobile App)")
        discovery_result = await self._scenario_product_search(customer_id)
        journey_results["discovery"] = discovery_result
        
        # Phase 2: Channel Switch
        print("\n🔄 Phase 2: Channel Switch (Mobile → WhatsApp)")
        switch_result = await self._scenario_channel_switch(customer_id)
        journey_results["channel_switch"] = switch_result
        
        # Phase 3: Purchase Flow
        print("\n🛒 Phase 3: Purchase Flow (Web)")
        purchase_result = await self._scenario_purchase_flow(customer_id)
        journey_results["purchase"] = purchase_result
        
        # Phase 4: Post-Purchase Support
        print("\n📞 Phase 4: Post-Purchase Support")
        support_result = await self._scenario_post_purchase(customer_id)
        journey_results["support"] = support_result
        
        print("\n✅ Complete Customer Journey Completed!")
        print("   - Product discovery across multiple channels")
        print("   - Seamless channel switching with context preservation")
        print("   - End-to-end purchase flow with loyalty benefits")
        print("   - Comprehensive post-purchase support")
        
        return {
            "scenario": "complete_journey",
            "status": "completed",
            "phases": journey_results,
            "total_phases": 4,
            "message": "Complete customer journey scenario completed successfully"
        }
    
    async def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all demo scenarios"""
        print("🚀 Running All Demo Scenarios...")
        
        scenarios = [
            "product_search",
            "channel_switch", 
            "purchase_flow",
            "post_purchase",
            "complete_journey"
        ]
        
        results = {}
        
        for scenario in scenarios:
            print(f"\n{'='*50}")
            print(f"Running Scenario: {scenario.upper()}")
            print('='*50)
            
            try:
                result = await self.run_scenario(scenario)
                results[scenario] = result
                print(f"✅ {scenario} completed successfully")
            except Exception as e:
                print(f"❌ {scenario} failed: {str(e)}")
                results[scenario] = {"error": str(e)}
        
        print(f"\n{'='*50}")
        print("ALL SCENARIOS COMPLETED")
        print('='*50)
        
        successful = sum(1 for result in results.values() if not result.get("error"))
        total = len(scenarios)
        
        print(f"Successful: {successful}/{total}")
        print(f"Failed: {total - successful}/{total}")
        
        return {
            "status": "completed",
            "scenarios": results,
            "summary": {
                "total": total,
                "successful": successful,
                "failed": total - successful
            }
        }

# Global demo scenarios instance
demo_scenarios = DemoScenarios()
