import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/astratrade"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    DEBUG: bool = False

    class Config:
        env_file = ".env"