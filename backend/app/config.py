from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://lens:lens@db:5432/lens"
    redis_url: str = "redis://redis:6379/0"
    api_token: str = "local-development-token"
    data_dir: str = "/data"
    max_log_bytes: int = 5 * 1024 * 1024
    max_image_bytes: int = 512 * 1024 * 1024

settings = Settings()
