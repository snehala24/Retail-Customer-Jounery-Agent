# apps/sales-agent-api/app/services/telegram_bot.py

import logging
from typing import Dict, Any
import httpx
from fastapi import APIRouter, Request, BackgroundTasks

logger = logging.getLogger("telegram_bot")
router = APIRouter()

# --- Hardcoded bot token (remove before pushing to GitHub) ---
TELEGRAM_BOT_TOKEN = "8594984778:AAHLlVKiwOVwxHJPZaMXvA_gjl7ueO8Q3kU"
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def _send_message(chat_id: int, text: str) -> Dict[str, Any]:
    """Send a text message to telegram (async)."""
    url = f"{TELEGRAM_API_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)
        try:
            return resp.json()
        except Exception:
            return {"ok": False, "status_code": resp.status_code, "text": resp.text}


@router.post("/v1/telegram/webhook")
async def telegram_webhook(request: Request, background: BackgroundTasks):
    """
    Telegram webhook endpoint. Telegram will POST updates here.
    We extract message.text and chat.id then forward to internal /v1/chat endpoint.
    Finally we send the assistant reply back to the Telegram chat asynchronously (BackgroundTasks).
    """
    body = await request.json()
    logger.debug("Telegram update: %s", body)

    # Telegram sends either "message" or "edited_message"
    message = body.get("message") or body.get("edited_message")
    if not message:
        return {"ok": True}

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "") or message.get("caption", "")
    if not text or chat_id is None:
        return {"ok": True}

    # Build payload for internal chat endpoint
    internal_payload = {
        "channel": "telegram",
        "text": text,
        "customer_id": f"tg-{chat_id}",
    }

    # Call internal orchestrator endpoint
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("http://localhost:8000/v1/chat", json=internal_payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.exception("Error calling internal /v1/chat: %s", e)
        background.add_task(_send_message, chat_id, "⚠️ Sorry, something went wrong on the server.")
        return {"ok": False}

    # --- Smarter reply handling ---
    reply = data.get("actions", {}).get("reply") or data.get("reply_text")
    if not reply or reply.strip().lower() in ["", "sorry, i didn't understand that.", "sorry, i couldn't process that."]:
        reply = ""

    # --- Handle tool results & product details ---
    tool_results = data.get("actions", {}).get("tool_results") or []
    extra_lines = []

    if tool_results:
        for t in tool_results:
            if t.get("result") and t["result"].get("message"):
                extra_lines.append(f"🛠 {t['tool']}: {t['result']['message']}")

                # If tool returns product items, show their details neatly
                items = t["result"].get("items", [])
                if items:
                    for item in items[:3]:  # Show max 3 products
                        extra_lines.append(f"🛍️ <b>{item['name']}</b> — ₹{item['price']}")
            elif t.get("error"):
                extra_lines.append(f"⚠️ {t['tool']} failed: {t['error']}")

    # --- Final message assembly ---
    if not reply:
        reply = "\n".join(extra_lines)
    elif extra_lines:
        reply = f"{reply}\n\n" + "\n".join(extra_lines)

    # --- Send reply back to Telegram ---
    background.add_task(_send_message, chat_id, reply)

    return {"ok": True}
