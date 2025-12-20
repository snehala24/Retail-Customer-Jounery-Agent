
# Agentic Sales (Agentic AI) 


## Project overview

Agentic Sales is an Agentic AI assistant for retail: it accepts chat requests, queries an LLM (Gemini) to plan actions, executes tools (recommend, check_stock, authorize_payment), and returns results. The project includes a FastAPI backend, a React + Vite frontend, and uses Redis + Postgres for persistence.

---

## Backend directory (canonical)

```
agentic-sales/
├─ apps/
│  ├─ clients/
│  └─ sales-agent-api/
│     ├─ .pytest_cache/
│     ├─ app/
│     │  ├─ __init__.py
│     │  ├─ api.py
│     │  ├─ main.py
│     │  ├─ agents/
│     │  │  ├─ fulfillment_agent.py
│     │  │  ├─ inventory_agent.py
│     │  │  ├─ loyalty_agent.py
│     │  │  ├─ order_agent.py
│     │  │  ├─ payment_agent.py
│     │  │  └─ recommendation_agent.py
│     │  ├─ models/
│     │  │  ├─ __init__.py
│     │  │  ├─ all_models.py
│     │  │  ├─ customer.py
│     │  │  ├─ fulfillement.py
│     │  │  ├─ inventory.py
│     │  │  ├─ loyalty.py
│     │  │  ├─ order_item.py
│     │  │  ├─ order.py
│     │  │  ├─ product.py
│     │  │  └─ schemas.py
│     │  ├─ services/
│     │  │  ├─ __init__.py
│     │  │  ├─ db.py
│     │  │  ├─ inventory_service.py
│     │  │  ├─ llm_client.py
│     │  │  ├─ metrics_tracker.py
│     │  │  ├─ orchestrator.py
│     │  │  ├─ order_service.py
│     │  │  ├─ recommendation_service.py
│     │  │  ├─ seed_data.py
│     │  │  ├─ session_store.py
│     │  │  └─ tool_router.py
│     │  ├─ tests/
│     │  │  ├─ test_orchestration.py
│     │  │  └─ test_request.py
│     │  └─ workflows/
│     │     └─ order_workflow.py
│     ├─ Dockerfile
│     └─ requirements.txt
├─ .env
├─ docker-compose.yml
├─ alembic.ini
└─ README.md
```

> **Note:** This README now reflects the actual backend layout. If your repo differs, update these paths accordingly.

---

## Tech stack

- Backend: Python 3.10+, FastAPI, httpx, aioredis (or redis client), SQLAlchemy / Alembic
- Frontend: React (Vite), Tailwind CSS
- LLM: Gemini (via REST generateContent)
- DB + cache: PostgreSQL, Redis (via Docker)
- Tunnel for webhooks: Cloudflared (recommended) or ngrok
- Testing: pytest, pytest-asyncio

---

## Environment & secrets

Create a `.env` in the repository root (do **not** commit). Example `.env`:

```
# .env (DO NOT COMMIT)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:postgres@db:5432/sales
REDIS_URL=redis://redis:6379/0
```

Your Docker Compose will load these variables. If you used hardcoded keys (like in `llm_client.py`) — **remove them immediately** and replace with `os.getenv`.

---

## Docker (required)

A sample `docker-compose.yml` (place in repo root):

```yaml
version: "3.8"
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: sales
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./apps/sales-agent-api
    env_file:
      - .env
    volumes:
      - ./apps/sales-agent-api/app:/app/app
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

volumes:
  pgdata:
```

**Run** (from repo root):

```powershell
docker compose up --build
```

> If Docker Desktop is closed, `docker`/`docker compose` commands will fail — you must start Docker.

---

## Local dev (without Docker) — not recommended for full stack


Typical steps (when using Docker recommended above):

1. Start Docker services:
   ```powershell
   docker compose up -d
   ```
2. Install Python deps inside venv:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r apps/sales-agent-api/requirements.txt
   ```
3. Run migrations (alembic) and seed:
   ```powershell
   alembic upgrade head
   python apps/sales-agent-api/app/services/seed_data.py
   ```
4. Run backend:
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```

---

## Frontend

In `frontend/sales-dashboard`:

```powershell
cd frontend/sales-dashboard
npm install
npm run dev
```

Your Vite app will run at `http://localhost:5173` by default. Ensure CORS is configured on the FastAPI backend (it already is in this project).

---

## Webhook (Telegram) + tunneling

You tried ngrok and had antivirus issues — that's fine. Cloudflared worked for you.

**Quick Tunnel (cloudflared)**
```powershell
cloudflared tunnel --url http://localhost:8000
# the CLI prints a public URL; use that to set Telegram webhook
```

Once you have the public URL `https://<something>.trycloudflare.com`, set the webhook (PowerShell):

```powershell
Invoke-WebRequest -Uri "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" `
  -Method POST -Body @{ url = "https://<your-tunnel>/v1/telegram/webhook" }
```

---

## Running everything (recommended)

1. Start Docker (Docker Desktop).
2. From repo root:
   ```powershell
   docker compose up --build
   ```
3. In a separate terminal, start frontend:
   ```powershell
   cd frontend/sales-dashboard
   npm install
   npm run dev
   ```
4. Start cloudflared:
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
   copy the public URL and set Telegram webhook as shown above.

---

## Troubleshooting (common issues)

- **Tailwind / PostCSS errors**: Install `@tailwindcss/postcss` and ensure `postcss.config.cjs` uses CommonJS when `type: "module"` is set.
- **ngrok antivirus deleting exe**: Use cloudflared as an alternative.
- **'ngrok' not recognized**: Ensure the global npm bin is in PATH. Prefer installing official ngrok binary from website and unblock it, or use cloudflared.
- **Docker Desktop closed**: Start Docker Desktop or use WSL/docker engine.

---

## Tests

Run tests from repo root (ensure services are available):

```powershell
# activate venv or use docker compose test setup
pytest -q
```
