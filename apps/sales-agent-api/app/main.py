import os, logging, asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from app.services import telegram_bot

load_dotenv()

from app.services.session_store import create_session_store

# ✅ Load .env safely no matter where Uvicorn is launched from
env_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(env_path)

# ✅ Logging setup
logger = logging.getLogger("sales_agent")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# ✅ FastAPI app instance
app = FastAPI(title="Sales Agent (Conductor)", version="0.2.1")


# ✅ CORS (for React/Telegram frontends)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For now allow all origins (safe for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telegram_bot.router)

# ----- Models -----
class ChatRequest(BaseModel):
    session_id: str | None = None
    channel: str
    customer_id: str | None = None
    text: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    actions: dict | None = None

# ----- Global State -----
session_store = None  # Global variable to store session store instance

# ----- Routes -----
@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
@app.get("/v1/metrics/{tool_name}")
async def get_tool_metrics(tool_name: str):
    """View performance metrics for a specific tool."""
    from app.services.metrics_tracker import metrics_tracker
    await metrics_tracker.init()
    metrics = await metrics_tracker.get_metrics(tool_name)
    return metrics or {"message": f"No metrics yet for tool '{tool_name}'"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    """
    Intelligent chat flow:
    - Load session from Redis
    - Call Gemini planner (intent + tool_calls)
    - Optionally call Worker Agents (mock for now)
    - Save context back to Redis
    """
    from app.services import llm_client, tool_router

    global session_store

    # Ensure session store is initialized before accessing it
    if session_store is None:
        session_store = await create_session_store()  # Ensure Redis connection is established

    session_id = req.session_id or f"sid-{os.urandom(6).hex()}"
    session = await session_store.get(session_id) or {"messages": [], "customer_id": req.customer_id}

    # 1️⃣ Append user message
    session["messages"].append({"role": "user", "text": req.text, "channel": req.channel})

    # 2️⃣ Call Gemini planner
    plan = await llm_client.plan(req.text, session)
    logger.info(f"🧠 Gemini plan output: {plan}")

    reply_text = plan.get("reply_text", "")
    tool_calls = plan.get("tool_calls", [])

    # 3️⃣ Execute tool calls via orchestrator
    from app.services.orchestrator import execute_plan
    orchestration_result = await execute_plan({"reply_text": reply_text, "tool_calls": tool_calls}, session_id, session)
    results = orchestration_result.get("tool_results", [])
    # optionally update reply_text from orchestrator.plan reply (same as we already have)
    reply_text = orchestration_result.get("reply_text", reply_text)

    # 4️⃣ Append assistant message
    session["messages"].append({
        "role": "assistant",
        "text": reply_text,
        "tools_used": tool_calls
    })

    # 5️⃣ Persist to Redis
    await session_store.set(session_id, session)

    # 6️⃣ Return structured response
    return ChatResponse(
        session_id=session_id,
        reply=reply_text,
        actions={"tool_results": results} if results else None
    )

# ----- Lifecycle -----
@app.on_event("startup")
async def startup_event():
    global session_store
    logger.info("🚀 Starting Sales Agent API (connecting to Redis)...")
    session_store = await create_session_store()  # Initialize session_store at startup
    logger.info("✅ Redis session store initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Sales Agent API shutting down")
