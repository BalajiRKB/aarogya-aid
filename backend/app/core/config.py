from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Gemini — used for embeddings via new google-genai SDK
    GEMINI_API_KEY: str

    # Groq — LLM inference
    GROQ_API_KEY: str

    CHROMA_PERSIST_DIR: str = "./chroma_db"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"

    LLM_MODEL: str = "llama-3.3-70b-versatile"
    # Uses new google-genai SDK (v1 API) — NOT langchain_google_genai
    EMBEDDING_MODEL: str = "gemini-embedding-004"

    class Config:
        env_file = ".env"

settings = Settings()
