"""Auth context. Two modes:
  dev   -> inject a seeded workspace/user (run with zero external keys)
  clerk -> verify Clerk-issued JWTs via JWKS
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .models import Membership, User, Workspace
from .settings import get_settings

settings = get_settings()
DEV_ORG = "org_dev"
DEV_USER = "user_dev"
_jwks_cache: dict | None = None


@dataclass
class Ctx:
    user: User
    workspace: Workspace


async def _ensure_dev(db: AsyncSession) -> Ctx:
    ws = (await db.execute(select(Workspace).where(Workspace.clerk_org_id == DEV_ORG))).scalar_one_or_none()
    if not ws:
        ws = Workspace(clerk_org_id=DEV_ORG, name="Dev Workspace", plan="agency")
        db.add(ws)
    user = (await db.execute(select(User).where(User.clerk_user_id == DEV_USER))).scalar_one_or_none()
    if not user:
        user = User(clerk_user_id=DEV_USER, email="dev@vyse.local")
        db.add(user)
    await db.flush()
    link = await db.get(Membership, (ws.id, user.id))
    if not link:
        db.add(Membership(workspace_id=ws.id, user_id=user.id, role="owner"))
    await db.commit()
    await db.refresh(ws)
    await db.refresh(user)
    return Ctx(user=user, workspace=ws)


async def _jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as c:
            _jwks_cache = (await c.get(settings.clerk_jwks_url)).json()
    return _jwks_cache


async def current_ctx(
    request: Request, db: AsyncSession = Depends(get_session)
) -> Ctx:
    if settings.auth_mode == "dev":
        return await _ensure_dev(db)

    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    token = auth.removeprefix("Bearer ")
    from jose import jwt  # lazy: only needed in clerk mode

    try:
        claims = jwt.decode(
            token, await _jwks(), algorithms=["RS256"], issuer=settings.clerk_issuer,
            options={"verify_aud": False},
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(401, f"invalid token: {e}") from e

    org_id = claims.get("org_id") or claims.get("o", {}).get("id")
    if not org_id:
        raise HTTPException(403, "no active organization")
    ws = (await db.execute(select(Workspace).where(Workspace.clerk_org_id == org_id))).scalar_one_or_none()
    user = (await db.execute(select(User).where(User.clerk_user_id == claims["sub"]))).scalar_one_or_none()
    if not ws or not user:
        raise HTTPException(403, "workspace/user not provisioned — check Clerk webhook")
    return Ctx(user=user, workspace=ws)
