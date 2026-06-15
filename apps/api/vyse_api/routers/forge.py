import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai import FORGE_SCHEMA, get_ai
from ..auth import Ctx, current_ctx
from ..db import get_session
from ..models import Blueprint, Post
from ..schemas import BlueprintOut, ForgeIn
from ..settings import get_settings

router = APIRouter(prefix="/v1/forge", tags=["forge"])
settings = get_settings()


@router.post("", response_model=BlueprintOut)
async def forge(body: ForgeIn, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    post = await db.get(Post, body.source_post_id)
    if not post or post.workspace_id != ctx.workspace.id:
        raise HTTPException(404, "source post not found")

    a = post.analysis
    context = (
        f"Source caption: {post.caption}\n"
        f"Hook: {getattr(a, 'hook_type', '?')} | CTA: {getattr(a, 'cta_type', '?')} | "
        f"Story: {getattr(a, 'story_pattern', '?')} | Pillar: {getattr(a, 'content_pillar', '?')}\n"
        f"Recreate for brand: {body.target_brand} | niche: {body.target_niche or 'same'}"
    )
    out = await get_ai().structured(
        system="You are an elite short-form content strategist. Produce a production-ready blueprint.",
        user=context,
        schema=FORGE_SCHEMA,
        model=settings.ai_chat_model,
    )
    bp = Blueprint(
        workspace_id=ctx.workspace.id,
        source_post_id=post.id,
        target_brand=body.target_brand,
        target_niche=body.target_niche,
        output=out,
        model=settings.ai_chat_model if settings.openai_api_key else "stub",
    )
    db.add(bp)
    await db.commit()
    await db.refresh(bp)
    return bp


@router.get("/{bid}", response_model=BlueprintOut)
async def get_blueprint(bid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    bp = await db.get(Blueprint, bid)
    if not bp or bp.workspace_id != ctx.workspace.id:
        raise HTTPException(404)
    return bp
