import os
import json
import logging
import re  # Regular expression import
from typing import Any, Dict, List

import httpx

logger = logging.getLogger("llm_client")

# --- System prompt (keep your existing prompt text here) ---
SYSTEM_PROMPT = """ 
You are a helpful retail AI sales assistant connected to multiple internal tools.

You can use one or more of these tools in each response:
- recommend: suggest products based on a query and optional budget.
  args → { "query": string, "budget": number }
- check_stock: verify availability of a product in inventory.
  args → { "sku": string, "location": optional string }
- authorize_payment: confirm payment for an order.
  args → { "order_id": string, "amount": number, "payment_method": object }

🎯 Output Format:
Always return **valid JSON only** (inside triple backticks).
The JSON must include these fields:
{
  "reply_text": "short friendly message to user",
  "tool_calls": [
    { "tool": "...", "args": { ... } },
    ...
  ]
}

💡 Multi-step reasoning rules:
- You may chain tools if it makes sense.
- Later tool_calls can refer to results of earlier ones using placeholders like:
    "${tool_results[0].result.items[0].sku}"
- If no tool is required, return an empty list: "tool_calls": [].
- Keep messages concise and polite. Prices are in ₹.
"""

# --- Helper utilities ---
_CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*([\s\S]+?)\s*```$", flags=re.MULTILINE)

def _strip_code_fence(text: str) -> str:
    """Strip triple backticks if present."""
    m = _CODE_FENCE_RE.search(text.strip())
    if m:
        return m.group(1).strip()
    # if not fenced, try to find a JSON object inside the text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1]
    return text.strip()

def _safe_parse_json(s: str) -> Dict[str, Any]:
    try:
        return json.loads(s)
    except Exception as e:
        logger.debug("JSON parse failed: %s\nSTRING:\n%s", e, s)
        return {}

# --- Main client ---
# This function is used by your main.py: plan(user_text, session)
async def plan(user_text: str, session: Dict[str, Any], max_history: int = 20) -> Dict[str, Any]:
    """
    Build a prompt that includes system prompt + recent session messages + current user text,
    call the LLM (Gemini) and return the parsed plan:
      { "reply_text": str, "tool_calls": [ { "tool": name, "args": {...}}, ... ] }

    session param is expected to be the object stored in Redis (dict with "messages" list
    and optionally previous "tool_results" entries).
    """
    # build messages list (system + conversation)
    messages: List[Dict[str, str]] = []
    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # include recent conversation history from session["messages"]
    history = session.get("messages", []) if session else []
    # keep only last `max_history` entries
    pruned = history[-max_history:]

    # Normalize session messages into a textual block the LLM can understand.
    convo_blocks = []
    for m in pruned:
        role = m.get("role", "user")
        chan = m.get("channel")
        txt = m.get("text", "")
        if chan:
            convo_blocks.append(f"[{role}] ({chan}): {txt}")
        else:
            convo_blocks.append(f"[{role}]: {txt}")

    # Also include previous tool results (if any) so LLM can reference them
    tool_results = session.get("tool_results", [])
    if tool_results:
        # convert to readable JSON block but keep it compact
        try:
            tool_block = json.dumps(tool_results, indent=2, ensure_ascii=False)
        except Exception:
            tool_block = str(tool_results)
        convo_blocks.append(f"[tool_results]: {tool_block}")

    # Finally add the current user instruction
    convo_blocks.append(f"[user] (current): {user_text}")

    # Single string for context
    conversation_context = "\n".join(convo_blocks)

    # Ask model to produce JSON only (we already instruct in SYSTEM_PROMPT, repeat briefly)
    user_prompt = (
        "You are given the conversation context below. Produce **valid JSON only** inside triple backticks "
        "with fields: reply_text (string) and tool_calls (list). Do not output any commentary.\n\n"
        "Conversation context:\n"
        f"{conversation_context}\n\n"
        "Return the JSON now."
    )

    messages.append({"role": "user", "content": user_prompt})

    # --- Hardcoded API Key (instead of reading from .env) ---
    api_key = "AIzaSyDjRoCPqYXtX3lrzdmWmAE9wjr3Wh5coO4"  # Replace this with your own key

    # --- Build the request to Gemini (FIXED) ---

    # 1. Convert your 'messages' list (which has system + user prompts)
    #    into the 'contents' format the API expects.
    #    The API maps the 'system' role to 'user'.
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "system" else "user" # API only accepts "user" or "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # 2. Build the request body with the CORRECT fields
    #    - "contents": not "messages"
    #    - "generationConfig": for settings
    #    - "maxOutputTokens": is camelCase
    request_body = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 512
        }
    }

    # 3. Your URL is correct (it includes the key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    # --- End of Fix ---

    # async HTTP call
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=request_body)
            text = resp.text
            if resp.status_code != 200:
                logger.error("Gemini HTTP error: %s - %s", resp.status_code, text)
                return {"reply_text": "Hmm, I’m unable to reach the thinking service right now. Let’s try again in a moment.", "tool_calls": []}

            # Try to extract model text from the response payload.
            data = resp.json()
            # Typical shape: { "candidates": [ { "content": { "parts": [ { "text": "```json\n{...}\n```" } ] } } ] }
            candidate_text = None
            if isinstance(data, dict):
                cands = data.get("candidates") or []
                if cands and isinstance(cands, list):
                    first = cands[0]
                    content = first.get("content") or {}
                    parts = content.get("parts") or []
                    if parts:
                        candidate_text = parts[0].get("text")
                # fallback: top-level "output" or similar
                if candidate_text is None:
                    # try to find any string in response
                    candidate_text = json.dumps(data)

            if not candidate_text:
                logger.error("No text candidate in Gemini response: %s", data)
                return {"reply_text": "Thinking service returned unexpected data.", "tool_calls": []}

            # strip backticks and extract JSON
            stripped = _strip_code_fence(candidate_text)
            parsed = _safe_parse_json(stripped)
            if not parsed:
                # Last attempt: search for first {...} and parse
                first_brace = stripped.find("{")
                last_brace = stripped.rfind("}")
                if first_brace != -1 and last_brace != -1:
                    maybe = stripped[first_brace:last_brace+1]
                    parsed = _safe_parse_json(maybe)

            if not parsed:
                logger.error("Failed to parse JSON plan from LLM. raw: %s", candidate_text[:1000])
                return {"reply_text": "I received an answer but couldn't parse the plan. Please try rephrasing.", "tool_calls": []}

            # Ensure keys exist
            reply_text = parsed.get("reply_text", "").strip()
            tool_calls = parsed.get("tool_calls", []) or []

            # normalize tool_calls to expected shape
            normalized = []
            for t in tool_calls:
                if isinstance(t, dict) and "tool" in t and "args" in t:
                    normalized.append({"tool": t["tool"], "args": t["args"]})
                else:
                    logger.debug("Skipping malformed tool_call entry: %s", t)

            return {"reply_text": reply_text, "tool_calls": normalized}

    except Exception as e:
        logger.exception("Exception calling Gemini: %s", e)
        return {"reply_text": "Hmm, I ran into an error while thinking. Try again.", "tool_calls": []}
