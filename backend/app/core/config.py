from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o"

    class Config:
        env_file = ".env"

settings = Settings()
