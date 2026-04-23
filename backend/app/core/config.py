from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Groq — LLM inference (llama-3.3-70b-versatile)
    GROQ_API_KEY: str

    # Gemini — embeddings only (text-embedding-004, free tier)
    GEMINI_API_KEY: str

    CHROMA_PERSIST_DIR: str = "./chroma_db"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"

    LLM_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "models/text-embedding-004"

    class Config:
        env_file = ".env"

settings = Settings()
