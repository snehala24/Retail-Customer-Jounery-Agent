# app/api.py
# future: router definitions
from fastapi import APIRouter

router = APIRouter()

@router.get("/v1/info")
async def info():
    return {"service": "sales-agent", "status": "ready"}
