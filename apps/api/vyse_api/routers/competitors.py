import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import Ctx, current_ctx
from ..db import get_session
from ..models import Competitor, Post
from ..schemas import CompetitorIn, CompetitorOut

router = APIRouter(prefix="/v1/competitors", tags=["scout"])


@router.get("", response_model=list[CompetitorOut])
async def list_competitors(
    platform: str | None = None,
    niche: str | None = None,
    ctx: Ctx = Depends(current_ctx),
    db: AsyncSession = Depends(get_session),
):
    q = select(Competitor).where(Competitor.workspace_id == ctx.workspace.id)
    if platform:
        q = q.where(Competitor.platform == platform)
    if niche:
        q = q.where(Competitor.niche == niche)
    return (await db.execute(q.order_by(Competitor.created_at.desc()))).scalars().all()


@router.post("", response_model=CompetitorOut, status_code=201)
async def add_competitor(
    body: CompetitorIn, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    c = Competitor(
        workspace_id=ctx.workspace.id,
        platform=body.platform,
        handle=body.handle.lstrip("@"),
        niche=body.niche,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    # In prod: enqueue("fetch_profile", c.id) to pull followers/avatar/metrics.
    return c


@router.get("/{cid}", response_model=CompetitorOut)
async def get_competitor(
    cid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    c = await db.get(Competitor, cid)
    if not c or c.workspace_id != ctx.workspace.id:
        raise HTTPException(404)
    return c


@router.get("/{cid}/posts")
async def competitor_posts(
    cid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    q = select(Post).where(Post.competitor_id == cid, Post.workspace_id == ctx.workspace.id)
    return (await db.execute(q.order_by(Post.created_at.desc()))).scalars().all()


@router.delete("/{cid}", status_code=204)
async def delete_competitor(
    cid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    c = await db.get(Competitor, cid)
    if c and c.workspace_id == ctx.workspace.id:
        await db.delete(c)
        await db.commit()
