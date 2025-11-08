# app/services/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# ✅ Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL missing in .env")

# ✅ Engine and Session setup
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# ✅ Base for all SQLAlchemy models
Base = declarative_base()

def get_db():
    """FastAPI dependency generator (for request-based DB sessions)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Helper for direct DB usage outside FastAPI routes."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

# ✅ Lazy import to prevent circular imports with model files
def import_all_models():
    import app.models.order
    import app.models.order_item
    import app.models.product
    import app.models.customer
    import app.models.fulfillment
