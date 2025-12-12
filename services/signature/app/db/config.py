from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    service_name: str = "signature"
    document_service_url: str = "http://document-service:8000"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()