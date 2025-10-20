from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import os

from .config import settings

# PostgreSQL/Supabase Database
# Use SQLite in-memory for testing if Supabase not configured
database_url = str(settings.SQLALCHEMY_DATABASE_URI) if settings.SQLALCHEMY_DATABASE_URI else None

if not database_url or database_url == "None":
    # Development/Testing mode - use SQLite in-memory
    database_url = "sqlite:///:memory:"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.LOG_LEVEL == "DEBUG"
    )
else:
    # Production mode - use Supabase/PostgreSQL
    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        echo=settings.LOG_LEVEL == "DEBUG"
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Redis connection (optional for development)
try:
    redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
    # Test connection
    redis_client.ping()
except (redis.ConnectionError, Exception) as e:
    # Redis not available - create a mock client for development
    print(f"⚠️ Redis not available: {e}. Using mock client for development.")
    redis_client = None


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """Dependency for getting Redis connection."""
    return redis_client
