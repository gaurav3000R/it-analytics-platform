import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./it_analytics.db")
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "IT Analytics Platform"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ML Model Settings
    RISK_MODEL_PATH: str = "models/risk_prediction_model.pkl"
    ANOMALY_MODEL_PATH: str = "models/anomaly_detection_model.pkl"
    
    # Redis (for caching)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Gemini AI Settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_PRIMARY_MODEL: str = "gemini-2.0-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-1.5-flash"
    GEMINI_MAX_RETRIES: int = 3
    
    # CSV Data Settings
    DEFAULT_CSV_PATH: str = "app/data/project_risk_dataset.csv"
    MAX_CSV_SIZE_MB: int = 10
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env (like NEXT_PUBLIC_* variables)

settings = Settings()