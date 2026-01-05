from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuration for Data Quality Service."""

    # Service Settings
    service_name: str = "data-quality"
    
    # LLM Provider Settings
    llm_provider: str 
    openai_api_key: str 
    gemini_api_key: str
    openai_model: str 
    gemini_model: str


    # Quality Thresholds
    min_quality_score: float = 50.0  # 0-100 scale
    block_low_quality: bool = False  # If True, don't publish low-quality docs
    
    # Kafka Settings
    kafka_bootstrap_servers: str
    kafka_consumer_group: str
    cdc_documents_topic: str 
    quality_checks_topic: str

    # MinIO Settings (for fetching document content)
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_secure: bool = False
    minio_bucket_documents: str 


    class Config:
        env_file=".env"

@lru_cache
def get_settings():
    return Settings()