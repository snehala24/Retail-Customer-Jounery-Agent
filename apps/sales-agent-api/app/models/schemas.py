# app/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    channel: str
    customer_id: Optional[str] = None
    text: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    actions: Optional[Dict[str, Any]] = None
