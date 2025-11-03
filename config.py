import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = ""
    
    # Database
    database_url: str = "sqlite:///./sales_agent.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Service URLs
    payment_gateway_url: str = "http://localhost:8001"
    inventory_service_url: str = "http://localhost:8002"
    loyalty_service_url: str = "http://localhost:8003"
    
    # WebSocket
    ws_host: str = "localhost"
    ws_port: int = 8000
    
    # Demo mode
    demo_mode: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
