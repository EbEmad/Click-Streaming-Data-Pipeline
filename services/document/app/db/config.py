from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str

    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool = False
    minio_bucket_documents: str = "documents"
    
    service_name: str = "document-service"
    MAX_SEND_MESSAGE_LENGTH: int 
    MAX_RECEIVE_MESSAGE_LENGTH: int 

    class Config:
        env_file = ".env"

# to make the object cached
@lru_cache
def get_settings():
    return Settings()
