#!/usr/bin/env python3
"""
Test script for AI Sales Agent Demo
Run this script to test all components and scenarios
"""

import asyncio
import sys
import json
from datetime import datetime
from demo_scenarios import demo_scenarios
from orchestration import orchestrator
from data.synthetic_customers import CUSTOMERS
from data.mock_services import MockProductService, MockInventoryService, MockPaymentService

async def test_basic_components():
    """Test basic components"""
    print("🧪 Testing Basic Components...")
    
    # Test customer data
    print("1. Testing customer data...")
    assert len(CUSTOMERS) >= 10, "Should have at least 10 customers"
    print(f"   ✅ Found {len(CUSTOMERS)} customers")
    
    # Test product service
    print("2. Testing product service...")
    product_service = MockProductService()
    products = product_service.get_products(limit=5)
    assert len(products) > 0, "Should have products"
    print(f"   ✅ Found {len(products)} products")
    
    # Test inventory service
    print("3. Testing inventory service...")
    inventory_service = MockInventoryService()
    inventory = inventory_service.check_inventory("LAPTOP001")
    assert len(inventory) > 0, "Should have inventory data"
    print(f"   ✅ Found inventory for {len(inventory)} locations")
    
    # Test payment service
    print("4. Testing payment service...")
    payment_service = MockPaymentService()
    payment_result = payment_service.process_payment(100.0, "credit_card", "customer_001")
    assert "success" in payment_result, "Should have success field"
    print(f"   ✅ Payment test: {payment_result['success']}")
    
    print("✅ All basic components working correctly\n")

async def test_agents():
    """Test individual agents"""
    print("🤖 Testing Individual Agents...")
    
    # Test Sales Agent
    print("1. Testing Sales Agent...")
    sales_agent = orchestrator.sales_agent
    conversation_result = await sales_agent.execute_task("customer_001", {
        "action": "start_conversation",
        "channel": "web"
    })
    assert "session_id" in conversation_result, "Should return session ID"
    print(f"   ✅ Sales Agent conversation started: {conversation_result['session_id']}")
    
    # Test Recommendation Agent
    print("2. Testing Recommendation Agent...")
    rec_agent = orchestrator.worker_agents["recommendation"]
    rec_result = await rec_agent.execute_task("customer_001", {
        "customer": CUSTOMERS[0].dict(),
        "preferences": {"style": "modern"},
        "message": "Show me electronics"
    })
    assert "recommendations" in rec_result, "Should return recommendations"
    print(f"   ✅ Found {len(rec_result['recommendations'])} recommendations")
    
    # Test Inventory Agent
    print("3. Testing Inventory Agent...")
    inv_agent = orchestrator.worker_agents["inventory"]
    inv_result = await inv_agent.execute_task("customer_001", {
        "action": "check_availability",
        "products": ["LAPTOP001", "PHONE001"],
        "customer_location": "New York, NY"
    })
    assert "availability_results" in inv_result, "Should return availability results"
    print(f"   ✅ Checked availability for {len(inv_result['availability_results'])} products")
    
    # Test Payment Agent
    print("4. Testing Payment Agent...")
    pay_agent = orchestrator.worker_agents["payment"]
    pay_result = await pay_agent.execute_task("customer_001", {
        "action": "calculate_total",
        "cart": [{"sku": "LAPTOP001", "quantity": 1, "price": 2499.99}],
        "customer": CUSTOMERS[0].dict()
    })
    assert "total" in pay_result, "Should return total"
    print(f"   ✅ Calculated total: ${pay_result['total']:.2f}")
    
    # Test Fulfillment Agent
    print("5. Testing Fulfillment Agent...")
    ful_agent = orchestrator.worker_agents["fulfillment"]
    ful_result = await ful_agent.execute_task("customer_001", {
        "action": "schedule_fulfillment",
        "order": {
            "id": "TEST_ORDER",
            "items": [{"sku": "LAPTOP001", "quantity": 1}],
            "fulfillment_method": "ship_to_home"
        },
        "customer": CUSTOMERS[0].dict()
    })
    assert "fulfillment_scheduled" in ful_result, "Should schedule fulfillment"
    print(f"   ✅ Fulfillment scheduled: {ful_result['fulfillment_scheduled']}")
    
    # Test Loyalty Agent
    print("6. Testing Loyalty Agent...")
    loy_agent = orchestrator.worker_agents["loyalty"]
    loy_result = await loy_agent.execute_task("customer_001", {
        "action": "get_offers",
        "customer": CUSTOMERS[0].dict(),
        "purchase_amount": 100.0
    })
    assert "available_promotions" in loy_result, "Should return promotions"
    print(f"   ✅ Found {len(loy_result['available_promotions'])} promotions")
    
    # Test Post-Purchase Agent
    print("7. Testing Post-Purchase Agent...")
    pp_agent = orchestrator.worker_agents["post_purchase"]
    pp_result = await pp_agent.execute_task("customer_001", {
        "action": "handle_return",
        "order_id": "TEST_ORDER",
        "items": [{"sku": "LAPTOP001", "quantity": 1, "price": 2499.99}],
        "reason": "Test return",
        "customer": CUSTOMERS[0].dict()
    })
    assert "return_processed" in pp_result, "Should process return"
    print(f"   ✅ Return processed: {pp_result['return_processed']}")
    
    print("✅ All agents working correctly\n")

async def test_scenarios():
    """Test demo scenarios"""
    print("🎬 Testing Demo Scenarios...")
    
    scenarios = [
        "product_search",
        "channel_switch",
        "purchase_flow",
        "post_purchase"
    ]
    
    for scenario in scenarios:
        print(f"Testing scenario: {scenario}")
        try:
            result = await demo_scenarios.run_scenario(scenario, "customer_001")
            assert result.get("status") == "completed", f"Scenario {scenario} should complete"
            print(f"   ✅ {scenario} completed successfully")
        except Exception as e:
            print(f"   ❌ {scenario} failed: {str(e)}")
            return False
    
    print("✅ All scenarios working correctly\n")
    return True

async def test_workflows():
    """Test workflow orchestration"""
    print("🔄 Testing Workflow Orchestration...")
    
    # Test product discovery workflow
    print("1. Testing product discovery workflow...")
    discovery_result = await orchestrator.execute_workflow(
        "product_discovery",
        "customer_001",
        {
            "channel": "web",
            "message": "I'm looking for a laptop",
            "preferences": {"style": "modern"}
        }
    )
    assert "workflow_id" in discovery_result, "Should return workflow ID"
    print(f"   ✅ Product discovery workflow: {discovery_result['workflow_id']}")
    
    # Test purchase workflow
    print("2. Testing purchase workflow...")
    purchase_result = await orchestrator.execute_workflow(
        "purchase_flow",
        "customer_001",
        {
            "cart": [{"sku": "LAPTOP001", "quantity": 1, "price": 2499.99}],
            "payment_method": "credit_card",
            "fulfillment_method": "ship_to_home"
        }
    )
    assert "order_id" in purchase_result, "Should return order ID"
    print(f"   ✅ Purchase workflow: {purchase_result['order_id']}")
    
    # Test channel switch workflow
    print("3. Testing channel switch workflow...")
    switch_result = await orchestrator.execute_workflow(
        "channel_switch",
        "customer_001",
        {
            "session_id": discovery_result.get("results", {}).get("conversation", {}).get("session_id"),
            "new_channel": "whatsapp"
        }
    )
    assert "workflow_id" in switch_result, "Should return workflow ID"
    print(f"   ✅ Channel switch workflow: {switch_result['workflow_id']}")
    
    print("✅ All workflows working correctly\n")

async def run_performance_test():
    """Run performance test"""
    print("⚡ Running Performance Test...")
    
    start_time = datetime.now()
    
    # Test concurrent agent execution
    tasks = []
    for i in range(5):
        task = orchestrator.worker_agents["recommendation"].execute_task(
            f"customer_{i+1:03d}",
            {
                "customer": CUSTOMERS[i % len(CUSTOMERS)].dict(),
                "preferences": {"style": "modern"},
                "message": "Show me products"
            }
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    end_time = datetime.now()
    
    duration = (end_time - start_time).total_seconds()
    print(f"   ✅ Executed {len(tasks)} concurrent recommendations in {duration:.2f}s")
    print(f"   ✅ Average time per request: {duration/len(tasks):.2f}s")
    
    print("✅ Performance test completed\n")

async def main():
    """Main test function"""
    print("🚀 AI Sales Agent Demo - Test Suite")
    print("=" * 50)
    
    try:
        # Test basic components
        await test_basic_components()
        
        # Test individual agents
        await test_agents()
        
        # Test scenarios
        scenarios_ok = await test_scenarios()
        if not scenarios_ok:
            print("❌ Some scenarios failed")
            return False
        
        # Test workflows
        await test_workflows()
        
        # Performance test
        await run_performance_test()
        
        print("🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("The AI Sales Agent system is ready for demo!")
        print("\nTo start the demo:")
        print("1. Run: python main.py")
        print("2. Open: http://localhost:8000")
        print("3. Select a customer and start chatting!")
        print("\nMobile interface: http://localhost:8000/mobile")
        print("API documentation: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
