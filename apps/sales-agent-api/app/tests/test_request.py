# app/tests/test_request.py

import json
from fastapi.testclient import TestClient
from app.main import app

def test_end_to_end():
    # Simulate user request
    user_input = {
        "channel": "web",
        "text": "Show me shirts under ₹1500, then check stock for the first one",
        "customer_id": "CUST-001"
    }
    
    # Use TestClient to simulate the request to the API
    client = TestClient(app)
    response = client.post("/v1/chat", json=user_input)
    
    # Assert response status is 200 (OK)
    assert response.status_code == 200
    
    response_json = response.json()
    
    # ✅ Check for expected wording in the reply (relaxed match)
    reply = response_json["reply"].lower()
    assert "find some shirts" in reply
    assert "under ₹1500" in reply
    assert "check the stock" in reply
    
    # ✅ Check that tool results are being executed (expecting two tools)
    assert "actions" in response_json
    assert "tool_results" in response_json["actions"]
    assert len(response_json["actions"]["tool_results"]) == 2
    
    # Validate the tool names
    tools = [t["tool"] for t in response_json["actions"]["tool_results"]]
    assert "recommend" in tools
    assert "check_stock" in tools

    # ✅ Check stock info correctness
    stock_result = response_json["actions"]["tool_results"][1]["result"]
    assert stock_result["found"] is True
    assert stock_result["total_stock"] > 0
