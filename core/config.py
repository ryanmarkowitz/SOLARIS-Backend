from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str
    CLERK_SECRET_KEY: str
    AUTHORIZED_PARTY: str

    class Config:
        env_file = Path(__file__).parent.parent / ".env"

settings = Settings()