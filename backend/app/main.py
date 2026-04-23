from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import recommend, chat, admin, health
from app.core.config import settings

app = FastAPI(
    title="AarogyaAid API",
    description="AI-powered insurance recommendation platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(recommend.router, prefix="/api", tags=["recommendation"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
