# app/services/metrics_tracker.py
import json
import time
from datetime import datetime
from app.services.session_store import create_session_store

class MetricsTracker:
    """Tracks performance and reliability metrics for each tool."""

    def __init__(self):
        self.redis = None

    async def init(self):
        if not self.redis:
            self.redis = await create_session_store()

    async def update(self, tool_name: str, success: bool, exec_time: float):
        """Update metrics for a specific tool."""
        await self.init()
        key = f"metrics:{tool_name}"

        data = await self.redis.get(key)

        # Decode JSON safely if Redis returned bytes or string
        if isinstance(data, (bytes, str)):
            try:
                metrics = json.loads(data)
            except Exception:
                metrics = None
        elif isinstance(data, dict):
            metrics = data
        else:
            metrics = None

        # Initialize if new
        if not metrics:
            metrics = {
                "calls": 0,
                "avg_exec_time": 0.0,
                "success_count": 0,
                "error_count": 0,
                "last_used": None
            }

        # Update counters
        metrics["calls"] += 1
        if success:
            metrics["success_count"] += 1
        else:
            metrics["error_count"] += 1

        # Compute running average for execution time
        total_time = metrics["avg_exec_time"] * (metrics["calls"] - 1)
        metrics["avg_exec_time"] = round((total_time + exec_time) / metrics["calls"], 3)
        metrics["last_used"] = datetime.now().isoformat()

        # ✅ Save as JSON string (this fixes your error!)
        await self.redis.set(key, json.dumps(metrics))

    async def get_metrics(self, tool_name: str):
        """Fetch stored metrics for a tool."""
        await self.init()
        data = await self.redis.get(f"metrics:{tool_name}")

        if not data:
            return None

        if isinstance(data, (bytes, str)):
            try:
                return json.loads(data)
            except Exception:
                return None
        elif isinstance(data, dict):
            return data
        return None


# --- Singleton instance ---
metrics_tracker = MetricsTracker()
