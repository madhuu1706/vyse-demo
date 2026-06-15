from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .middleware import RateLimitMiddleware, RequestIdMiddleware
from .routers import billing, competitors, flow, forge, insights, posts, vault, webhooks
from .settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_init_db:
        await init_db()  # idempotent: pgvector extension + tables. Set AUTO_INIT_DB=false to use Alembic
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIdMiddleware)

for r in (competitors, posts, insights, forge, vault, flow, billing, webhooks):
    app.include_router(r.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "vyse-api"}


@app.get("/ready")
async def ready():
    return {"ready": True, "auth_mode": settings.auth_mode, "ai": bool(settings.openai_api_key)}
