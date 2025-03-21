"""
Application configuration settings.
"""

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API configuration
    API_PREFIX: str = "/api/v1"
    API_VERSION: str = "1.0.0"
    APP_NAME: str = "BobbyApp RPG & Roleplaying Platform"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # AI Services
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")  # mock, openai, anthropic, ollama
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # Media Storage
    MEDIA_BUCKET: str = "media"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB default
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Development/Production mode
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    class Config:
        """Pydantic config"""
        env_prefix = ""
        case_sensitive = True

# Create global settings instance
settings = Settings()
