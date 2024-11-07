# core/config.py
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 환경 설정
    ENV: str = "development"
    
    # CORS 설정
    DEV_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    
    PROD_CORS_ORIGINS: List[str] = [
        "https://your-production-domain.com",
    ]
    
    # GCP & NCLOUD 설정
    GCP_HOST: str = ""
    NCLOUD_HOST: str = ""
    
    # MariaDB 설정
    MARIA_DB_HOST: str = "localhost"
    MARIA_DB_PORT: int = 3306
    MARIA_DB_USER: str = ""
    MARIA_DB_PASSWORD: str = ""
    MARIA_DB_NAME: str = ""
    
    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None
    
    # 로그 관련 설정
    LOG_RETENTION_DAYS: int = 30
    LOG_CLEANUP_INTERVAL: int = 86400  # 24시간
    LOG_BACKUP_ENABLED: bool = True
    
    # Add these new fields
    backend_cors_origins: str
    open_ai_key: str
    claude_key: str
    mistral_key: str
    
    # Allow extra fields (alternative approach)
    model_config = ConfigDict(
        extra='allow',
        env_file=".env"
    )
    
    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        if self.ENV == "production":
            return self.PROD_CORS_ORIGINS
        return self.DEV_CORS_ORIGINS

    @property
    def MAIN_DB_URL(self) -> str:
        return f"mysql+aiomysql://{self.MARIA_DB_USER}:{self.MARIA_DB_PASSWORD}@{self.MARIA_DB_HOST}:{self.MARIA_DB_PORT}/{self.MARIA_DB_NAME}"
    
    @property
    def LOG_DB_URL(self) -> str:
        return f"mysql+aiomysql://{self.MARIA_DB_USER}:{self.MARIA_DB_PASSWORD}@{self.MARIA_DB_HOST}:{self.MARIA_DB_PORT}/log_{self.MARIA_DB_NAME}"
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

settings = Settings()