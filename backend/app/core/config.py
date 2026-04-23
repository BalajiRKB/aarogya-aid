from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Groq — used for the LLM (chat/reasoning)
    GROQ_API_KEY: str

    # OpenAI — used ONLY for text-embedding-3-small (Groq has no embedding API)
    OPENAI_API_KEY: str

    CHROMA_PERSIST_DIR: str = "./chroma_db"
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    SECRET_KEY: str = "changeme-use-a-real-secret-in-production"

    # Groq model for chat/reasoning
    LLM_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI model for embeddings only
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"

settings = Settings()
