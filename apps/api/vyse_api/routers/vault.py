import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai import get_ai
from ..auth import Ctx, current_ctx
from ..db import get_session
from ..models import VaultItem
from ..schemas import VaultIn, VaultOut, VaultSearchIn
from ..settings import get_settings

router = APIRouter(prefix="/v1/vault", tags=["vault"])
settings = get_settings()


@router.post("", response_model=VaultOut, status_code=201)
async def save(body: VaultIn, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    item = VaultItem(
        workspace_id=ctx.workspace.id,
        post_id=body.post_id,
        board=body.board,
        tags=body.tags,
        notes=body.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("", response_model=list[VaultOut])
async def list_items(
    board: str | None = None,
    tag: str | None = None,
    ctx: Ctx = Depends(current_ctx),
    db: AsyncSession = Depends(get_session),
):
    q = select(VaultItem).where(VaultItem.workspace_id == ctx.workspace.id)
    if board:
        q = q.where(VaultItem.board == board)
    if tag:
        q = q.where(VaultItem.tags.any(tag))
    return (await db.execute(q.order_by(VaultItem.created_at.desc()))).scalars().all()


@router.post("/search")
async def semantic_search(
    body: VaultSearchIn, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)
):
    """Embed the query, cosine-search the embeddings table (pgvector)."""
    vec = (await get_ai().embed(texts=[body.query], model=settings.ai_embed_model))[0]
    rows = (
        await db.execute(
            text(
                """
                SELECT e.post_id, p.url, p.caption, p.thumbnail_url,
                       1 - (e.vector <=> :qvec) AS similarity
                FROM embeddings e JOIN posts p ON p.id = e.post_id
                WHERE e.workspace_id = :ws AND e.post_id IS NOT NULL
                ORDER BY e.vector <=> :qvec ASC
                LIMIT :lim
                """
            ),
            {"qvec": str(vec), "ws": str(ctx.workspace.id), "lim": body.limit},
        )
    ).mappings().all()
    return [dict(r) for r in rows]


@router.delete("/{vid}", status_code=204)
async def delete_item(vid: uuid.UUID, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    item = await db.get(VaultItem, vid)
    if item and item.workspace_id == ctx.workspace.id:
        await db.delete(item)
        await db.commit()
