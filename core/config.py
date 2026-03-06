from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    CLERK_SECRET_KEY: str
    AUTHORIZED_PARTY: str

    class Config:
        env_file = "../env"

settings = Settings()