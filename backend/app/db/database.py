"""
Database configuration and connection management
"""
from typing import Generator
from sqlmodel import Session, create_engine, SQLModel
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session


# Supabase client configuration
try:
    from supabase import create_client, Client
    
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
except Exception as e:
    print(f"Warning: Supabase client initialization failed: {e}")
    supabase = None
