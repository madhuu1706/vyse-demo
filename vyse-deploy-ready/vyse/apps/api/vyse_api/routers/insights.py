"""PULSE / SPIKE / WHY read endpoints + the outlier leaderboard."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import Ctx, current_ctx
from ..db import get_session
from ..models import Outlier, Post
from ..schemas import AnalysisOut, OutlierOut, ReasoningOut

router = APIRouter(prefix="/v1", tags=["insights"])


async def _own_post(pid, ctx, db) -> Post:
    post = await db.get(Post, pid)
    if not post or post.workspace_id != ctx.workspace.id:
        raise HTTPException(404)
    return post


@router.get("/posts/{pid}/analysis", response_model=AnalysisOut)
async def get_analysis(pid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    post = await _own_post(pid, ctx, db)
    if not post.analysis:
        raise HTTPException(404, "not analyzed yet")
    return post.analysis


@router.get("/posts/{pid}/outlier", response_model=OutlierOut)
async def get_outlier(pid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    post = await _own_post(pid, ctx, db)
    if not post.outlier:
        raise HTTPException(404, "not scored yet")
    return post.outlier


@router.get("/posts/{pid}/why", response_model=ReasoningOut)
async def get_why(pid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    post = await _own_post(pid, ctx, db)
    if not post.reasoning:
        raise HTTPException(404, "no reasoning (post may not be an outlier)")
    return post.reasoning


@router.get("/outliers")
async def leaderboard(
    type: str | None = None,
    platform: str | None = None,
    limit: int = 50,
    ctx: Ctx = Depends(current_ctx),
    db: AsyncSession = Depends(get_session),
):
    q = (
        select(Outlier, Post)
        .join(Post, Post.id == Outlier.post_id)
        .where(Post.workspace_id == ctx.workspace.id)
    )
    if type:
        q = q.where(Outlier.outlier_type == type)
    if platform:
        q = q.where(Post.platform == platform)
    rows = (await db.execute(q.order_by(desc(Outlier.score)).limit(limit))).all()
    return [
        {
            "post_id": str(p.id),
            "url": p.url,
            "platform": p.platform,
            "caption": p.caption,
            "thumbnail_url": p.thumbnail_url,
            "score": float(o.score),
            "outlier_type": o.outlier_type,
            "components": o.components,
        }
        for o, p in rows
    ]
