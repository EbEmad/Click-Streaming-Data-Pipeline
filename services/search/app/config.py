from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    elasticsearch_url:str
    elasticsearch_index:str
    service_name:str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()