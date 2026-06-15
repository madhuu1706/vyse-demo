import time
import uuid

import redis.asyncio as aioredis
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .settings import get_settings

settings = get_settings()
_redis = aioredis.from_url(settings.redis_url, decode_responses=True)


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = rid
        try:
            response = await call_next(request)
        except Exception as exc:  # noqa: BLE001
            return JSONResponse(
                status_code=500,
                content={"type": "about:blank", "title": "internal_error",
                         "detail": str(exc), "request_id": rid},
            )
        response.headers["x-request-id"] = rid
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window limiter keyed by client IP (swap to workspace_id post-auth)."""

    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/ready"):
            return await call_next(request)
        key = f"rl:{request.client.host}:{int(time.time() // 60)}"
        try:
            n = await _redis.incr(key)
            if n == 1:
                await _redis.expire(key, 60)
            if n > settings.rate_limit_per_min:
                return JSONResponse(status_code=429, content={"title": "rate_limited"})
        except Exception:  # noqa: BLE001 — never fail open->closed on redis hiccup
            pass
        return await call_next(request)
