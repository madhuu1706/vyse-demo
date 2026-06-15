import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import Ctx, current_ctx
from ..db import get_session
from ..enqueue import enqueue
from ..models import Post
from ..schemas import IngestIn, IngestOut, PostDetail, PostOut
from ..scraper import detect_platform

router = APIRouter(prefix="/v1/posts", tags=["snap"])


@router.post("/ingest", response_model=IngestOut)
async def ingest(
    body: IngestIn, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    platform = detect_platform(body.url)
    if platform == "unknown":
        raise HTTPException(422, "unsupported or unrecognised URL")

    existing = (
        await db.execute(
            select(Post).where(Post.workspace_id == ctx.workspace.id, Post.url == body.url)
        )
    ).scalar_one_or_none()
    post = existing or Post(
        workspace_id=ctx.workspace.id,
        competitor_id=body.competitor_id,
        platform=platform,
        url=body.url,
        ingest_status="pending",
    )
    if not existing:
        db.add(post)
        await db.flush()

    job_id = await enqueue(
        db, job_type="ingest_post", ref_id=post.id, workspace_id=ctx.workspace.id
    )
    await db.commit()
    return IngestOut(post_id=post.id, job_id=job_id, platform=platform, status="queued")


@router.get("", response_model=list[PostOut])
async def list_posts(
    platform: str | None = None,
    ctx: Ctx = Depends(current_ctx),
    db: AsyncSession = Depends(get_session),
):
    q = select(Post).where(Post.workspace_id == ctx.workspace.id)
    if platform:
        q = q.where(Post.platform == platform)
    return (await db.execute(q.order_by(Post.created_at.desc()).limit(100))).scalars().all()


@router.get("/{pid}", response_model=PostDetail)
async def get_post(
    pid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    post = await db.get(Post, pid)
    if not post or post.workspace_id != ctx.workspace.id:
        raise HTTPException(404)
    return PostDetail(
        **PostOut.model_validate(post).model_dump(),
        analysis=post.analysis,
        outlier=post.outlier,
        reasoning=post.reasoning,
    )


@router.post("/{pid}/reanalyze", response_model=IngestOut)
async def reanalyze(
    pid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    post = await db.get(Post, pid)
    if not post or post.workspace_id != ctx.workspace.id:
        raise HTTPException(404)
    job_id = await enqueue(db, job_type="analyze_post", ref_id=post.id, workspace_id=ctx.workspace.id)
    await db.commit()
    return IngestOut(post_id=post.id, job_id=job_id, platform=post.platform, status="queued")
