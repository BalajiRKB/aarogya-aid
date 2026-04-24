from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Gemini — embeddings only (free tier)
    GEMINI_API_KEY: str

    # Groq — LLM inference (fast, free tier)
    GROQ_API_KEY: str

    CHROMA_PERSIST_DIR: str = "./chroma_db"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"

    LLM_MODEL: str = "llama-3.3-70b-versatile"
    # text-embedding-004 is not available on the v1beta API endpoint used by
    # langchain-google-genai (deprecated google.generativeai SDK).
    # Use models/embedding-001 which works on v1beta and is stable.
    EMBEDDING_MODEL: str = "models/embedding-001"

    class Config:
        env_file = ".env"

settings = Settings()
