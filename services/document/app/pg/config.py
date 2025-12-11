from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str

    service_name: str = "document-service"

    class Config:
        env_file = ".env"

# to make the object cached
@lru_cache
def get_settings():
    return Settings()
