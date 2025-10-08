import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration for the Agentic AI System"""
    
    # ====================
    # API Configuration
    # ====================
    
    # Base URL of your IT Analytics Platform backend
    IT_ANALYTICS_BASE_URL = os.getenv("IT_ANALYTICS_BASE_URL", "http://localhost:8000")
    
    # API version prefix
    API_V1_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
    
    # Agentic AI server port
    AGENTIC_AI_PORT = int(os.getenv("AGENTIC_AI_PORT", "8001"))
    
    # ====================
    # Gemini AI Configuration
    # ====================
    
    # Your Google Gemini API Key (Required for AI features)
    # Get it from: https://aistudio.google.com/app/apikey
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Gemini model to use
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Alternative models you can use:
    # GEMINI_MODEL=gemini-1.5-pro
    # GEMINI_MODEL=gemini-1.0-pro
    
    # ====================
    # Agent Configuration
    # ====================
    
    # Agent timeout in seconds
    AGENT_TIMEOUT = int(os.getenv("AGENT_TIMEOUT", "30"))
    
    # Maximum retries for API calls
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    
    # Enable/disable specific agents
    ENABLE_RISK_ANALYST = os.getenv("ENABLE_RISK_ANALYST", "true").lower() == "true"
    ENABLE_RESOURCE_OPTIMIZER = os.getenv("ENABLE_RESOURCE_OPTIMIZER", "true").lower() == "true"
    ENABLE_COST_FORECASTER = os.getenv("ENABLE_COST_FORECASTER", "true").lower() == "true"
    ENABLE_ANOMALY_DETECTOR = os.getenv("ENABLE_ANOMALY_DETECTOR", "true").lower() == "true"
    
    # ====================
    # Memory & Caching
    # ====================
    
    # Conversation memory TTL (seconds)
    CONVERSATION_TTL = int(os.getenv("CONVERSATION_TTL", "3600"))
    
    # Enable conversation memory
    ENABLE_MEMORY = os.getenv("ENABLE_MEMORY", "true").lower() == "true"
    
    # Maximum conversation history length
    MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
    
    # ====================
    # Logging Configuration
    # ====================
    
    # Log level (DEBUG, INFO, WARNING, ERROR)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Enable verbose logging for development
    VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "true").lower() == "true"
    
    # Log file path
    LOG_FILE = os.getenv("LOG_FILE", "logs/agentic_ai.log")
    
    # ====================
    # Security Configuration
    # ====================
    
    # API rate limiting (requests per minute)
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Enable CORS origins (comma-separated)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    
    # API key for external access (optional)
    AGENTIC_AI_API_KEY = os.getenv("AGENTIC_AI_API_KEY", "")
    
    # ====================
    # Performance Configuration
    # ====================
    
    # Maximum concurrent requests
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    
    # Request timeout in seconds
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Enable response caching
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    
    # Cache TTL in seconds
    CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
    
    # ====================
    # Tool Configuration
    # ====================
    
    # Enabled tools (comma-separated)
    ENABLED_TOOLS = os.getenv("ENABLED_TOOLS", "project_search,risk_prediction,risk_dashboard,team_performance,utilization_analysis,cost_forecast,anomaly_detection").split(",")
    
    # Tool timeout in seconds
    TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "25"))
    
    # Maximum tools per agent execution
    MAX_TOOLS_PER_AGENT = int(os.getenv("MAX_TOOLS_PER_AGENT", "5"))
    
    # ====================
    # Development Settings
    # ====================
    
    # Environment
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    
    # Enable hot reload
    HOT_RELOAD = os.getenv("HOT_RELOAD", "true").lower() == "true"
    
    # Test mode (uses mock data if true)
    TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
    
    # ====================
    # Monitoring & Observability
    # ====================
    
    # Enable Prometheus metrics
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    
    # Enable health checks
    ENABLE_HEALTH_CHECKS = os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true"
    
    # Enable request tracing
    ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"
    
    # ====================
    # Database (Optional - for conversation storage)
    # ====================
    
    # Database URL (SQLite by default)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentic_ai.db")
    
    # Enable database persistence
    ENABLE_DB_PERSISTENCE = os.getenv("ENABLE_DB_PERSISTENCE", "false").lower() == "true"
    
    # ====================
    # Validation Methods
    # ====================
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings"""
        errors = []
        
        # Check required settings
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required but not set")
        
        if not cls.IT_ANALYTICS_BASE_URL:
            errors.append("IT_ANALYTICS_BASE_URL is required but not set")
        
        # Check URL format
        if cls.IT_ANALYTICS_BASE_URL and not cls.IT_ANALYTICS_BASE_URL.startswith(('http://', 'https://')):
            errors.append("IT_ANALYTICS_BASE_URL must start with http:// or https://")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """Get full API URL for endpoint"""
        return f"{cls.IT_ANALYTICS_BASE_URL}{cls.API_V1_PREFIX}{endpoint}"
    
    @classmethod
    def get_available_agents(cls) -> List[str]:
        """Get list of available agents based on configuration"""
        agents = []
        if cls.ENABLE_RISK_ANALYST:
            agents.append("risk_analyst")
        if cls.ENABLE_RESOURCE_OPTIMIZER:
            agents.append("resource_optimizer")
        if cls.ENABLE_COST_FORECASTER:
            agents.append("cost_forecaster")
        if cls.ENABLE_ANOMALY_DETECTOR:
            agents.append("anomaly_detector")
        return agents

# Single global instance
config = Config()

# Validate configuration on import
try:
    config.validate_config()
    print("✅ Configuration validated successfully")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    if config.DEBUG:
        print("⚠️  Continuing in development mode, but some features may not work")