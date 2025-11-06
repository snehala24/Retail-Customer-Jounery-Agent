# app/services/llm_client.py
import os
import json
import logging
import httpx
from typing import Dict, Any


logger = logging.getLogger("llm_client")

# PASTE YOUR NEW, SECRET KEY HERE (the one that ends in 5coO4)
GEMINI_API_KEY = "AIzaSyDjRoCPqYXtX3lrzdmWmAE9wjr3Wh5coO4" 

if not GEMINI_API_KEY:
    raise ValueError("❌ KEY IS MISSING")

# This is our proof
print("="*60)
print(f"✅ HARDCODED KEY LOADED! Ends with: {GEMINI_API_KEY[-6:]}")
print("="*60)

# --- End of Fix ---

# ✅ NEW URLs
# ✅ FINAL URLs
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
GEMINI_API_URL_FALLBACK = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent"

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a professional conversational sales agent for a retail brand.

Goals:
1️⃣ Understand customer intent (browse, availability, payment, etc.)
2️⃣ Never invent product data.
3️⃣ Always respond with valid JSON only — no markdown or explanation.

Format your response exactly like this:
{
  "reply_text": "<short friendly response to user>",
  "tool_calls": [
    {"tool": "recommend", "args": {"query": "casual shirts", "budget": 1500}}
  ]
}

If no tools are needed, return: { "reply_text": "...", "tool_calls": [] }
"""

# --- Gemini LLM Planner ---
async def plan(user_text: str, session_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Calls Gemini API to convert user input into a structured plan.
    Returns dict: {"reply_text": str, "tool_calls": list}
    """
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": SYSTEM_PROMPT}]},
            {"role": "user", "parts": [{"text": user_text}]}
        ]
    }

    async def call_gemini(endpoint: str) -> Dict[str, Any]:
        """Internal helper to make the HTTP request."""
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{endpoint}?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    try:
        try:
            data = await call_gemini(GEMINI_API_URL)
        except httpx.HTTPStatusError as e:
            # Retry with fallback endpoint if first fails (common on newer keys)
            logger.warning(f"⚠️ Gemini primary endpoint failed ({e.response.status_code}), trying fallback...")
            data = await call_gemini(GEMINI_API_URL_FALLBACK)

        # --- Debug raw response ---
        print("\n🧠 ===== GEMINI RAW RESPONSE START =====")
        print(json.dumps(data, indent=2)[:2000])
        print("===== GEMINI RAW RESPONSE END =====\n")

        # --- Extract model output safely ---
        model_text = ""
        try:
            # Handle different possible field layouts
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts and "text" in parts[0]:
                    model_text = parts[0]["text"]
            elif "output" in data:
                model_text = data["output"]

            model_text = (model_text or "").strip()
        except Exception as parse_error:
            logger.warning(f"⚠️ Unexpected Gemini response structure: {parse_error}")
            model_text = ""

        # --- Try to extract JSON ---
        if model_text.startswith("```"):
            model_text = model_text.strip("```json").strip("```").strip()

        try:
            parsed = json.loads(model_text)
        except json.JSONDecodeError:
            logger.warning("⚠️ Gemini output not valid JSON, fallback to text mode")
            parsed = {"reply_text": model_text or "Let’s continue.", "tool_calls": []}

        # --- Ensure valid shape ---
        parsed.setdefault("reply_text", "I'm here to help you find products!")
        parsed.setdefault("tool_calls", [])

        # --- Return structured plan ---
        logger.info(f"✅ Gemini Parsed Plan: {parsed}")
        return parsed

    except httpx.RequestError as e:
        logger.error(f"❌ Network error while calling Gemini: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ Gemini HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"❌ Unexpected error in llm_client.plan: {e}", exc_info=True)

    # --- Hard fallback (only if API completely unreachable) ---
    return {
        "reply_text": "Hmm, I’m unable to reach the thinking service right now. Let’s try again in a moment.",
        "tool_calls": []
    }
