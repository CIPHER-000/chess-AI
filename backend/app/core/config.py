import os
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    PROJECT_NAME: str = "Chess Insight AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "chess-insight-files")
    
    # Database connection URL (constructed from Supabase)
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str) and v:
            return v
        # Supabase provides direct PostgreSQL connection
        # Format: postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
        # For now, we'll use Supabase SDK for most operations
        values = info.data if info else {}
        supabase_url = values.get("SUPABASE_URL", "")
        if supabase_url:
            # Extract project ref from Supabase URL
            # URL format: https://[project-ref].supabase.co
            import re
            match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)
            if match:
                project_ref = match.group(1)
                # Note: Direct PostgreSQL connection requires the database password
                # This should be set separately as SUPABASE_DB_PASSWORD
                db_password = os.getenv("SUPABASE_DB_PASSWORD", "")
                if db_password:
                    return f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
        return None
    
    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Chess.com API
    CHESSCOM_API_BASE_URL: str = "https://api.chess.com/pub"
    CHESSCOM_API_RATE_LIMIT: int = 100  # requests per minute
    
    # Stockfish Engine
    STOCKFISH_PATH: str = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")
    STOCKFISH_DEPTH: int = int(os.getenv("STOCKFISH_DEPTH", "15"))
    STOCKFISH_TIME: float = float(os.getenv("STOCKFISH_TIME", "1.0"))
    
    # Background Tasks
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    # File Storage
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "./reports")
    
    # Analysis Settings
    MAX_GAMES_PER_ANALYSIS: int = 50
    ANALYSIS_CACHE_EXPIRE_HOURS: int = 24
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


# Global settings instance
settings = Settings()
