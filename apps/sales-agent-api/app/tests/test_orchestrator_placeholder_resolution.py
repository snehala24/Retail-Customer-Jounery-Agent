import sys, os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# Allow app imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
@patch("app.services.llm_client.plan", new_callable=AsyncMock)
async def test_orchestrator_placeholder_resolution(mock_plan):
    """
    ✅ Verifies orchestrator correctly handles an LLM plan (mocked).
    Ensures no real API calls are made.
    """

    # Mock the Gemini response
    mock_plan.return_value = {
        "reply_text": "Let's check stock and then recommend similar items.",
        "tool_calls": [
            {"tool": "check_stock", "args": {"sku": "SKU123"}},
            {"tool": "recommend", "args": {"query": "shoes", "budget": 1500}},
        ],
    }

    # Simulate a valid API request (matches ChatRequest model)
    response = client.post(
        "/v1/chat",
        json={
            "channel": "web",
            "text": "show me shirts under 1500",
            "customer_id": "CUST-001"
        }
    )

    # Ensure response succeeded
    assert response.status_code == 200, f"Unexpected status: {response.status_code} - {response.text}"
    data = response.json()

    # Ensure LLM was called once
    mock_plan.assert_called_once()

    # ✅ Check output structure (actual API keys)
    assert "reply" in data, f"Missing 'reply' key. Got: {data.keys()}"
    assert "actions" in data, f"Missing 'actions' key. Got: {data.keys()}"
    assert "tool_results" in data["actions"], f"Missing 'tool_results' in actions. Got: {data['actions'].keys()}"

    print("\n✅ Orchestrator placeholder resolution test passed successfully!")
    print(f"LLM reply: {data['reply']}")
    print(f"Tool results: {data['actions']['tool_results']}")
