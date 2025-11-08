# app/services/tool_router.py

import logging
from app.agents import recommendation_agent, inventory_agent, payment_agent

logger = logging.getLogger("tool_router")

# Define mapping of tool name → function
TOOL_MAP = {
    "recommend": recommendation_agent.recommend_products_sync,
    "check_stock": inventory_agent.check_stock_sync,
    "authorize_payment": payment_agent.authorize_payment_sync
}

async def execute(tool_name: str, args: dict):
    """
    Executes a given tool asynchronously.
    """
    if tool_name not in TOOL_MAP:
        logger.warning(f"⚠️ Unknown tool requested: {tool_name}")
        raise ValueError(f"Unknown tool: {tool_name}")

    tool_func = TOOL_MAP[tool_name]
    logger.info(f"🔧 Executing tool '{tool_name}' with args: {args}")

    try:
        # Run tool (even if it’s sync)
        result = await _run_async(tool_func, **args)
        logger.info(f"✅ Tool '{tool_name}' completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Tool '{tool_name}' failed: {e}")
        raise

async def _run_async(func, **kwargs):
    """
    Helper to run sync functions asynchronously (thread offload).
    """
    import asyncio
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(**kwargs))
