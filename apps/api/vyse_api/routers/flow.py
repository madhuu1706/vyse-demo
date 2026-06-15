import uuid
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import Ctx, current_ctx
from ..db import get_session
from ..models import FlowTask
from ..schemas import FLOW_STATUSES, FlowIn, FlowOut, FlowPatch

router = APIRouter(prefix="/v1/flow", tags=["flow"])


@router.get("")
async def board(ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    rows = (
        await db.execute(
            select(FlowTask)
            .where(FlowTask.workspace_id == ctx.workspace.id)
            .order_by(FlowTask.position.asc().nulls_last())
        )
    ).scalars().all()
    grouped: dict[str, list] = defaultdict(list)
    for t in rows:
        grouped[t.status].append(FlowOut.model_validate(t).model_dump())
    return {s: grouped.get(s, []) for s in FLOW_STATUSES}


@router.post("", response_model=FlowOut, status_code=201)
async def create(body: FlowIn, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    if body.status not in FLOW_STATUSES:
        raise HTTPException(422, "invalid status")
    t = FlowTask(
        workspace_id=ctx.workspace.id,
        title=body.title,
        blueprint_id=body.blueprint_id,
        status=body.status,
        due_date=body.due_date,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return t


@router.patch("/{tid}", response_model=FlowOut)
async def patch(tid: uuid.UUID, body: FlowPatch, ctx: Ctx = Depends(current_ctx), db: AsyncSession = Depends(get_session)):
    t = await db.get(FlowTask, tid)
    if not t or t.workspace_id != ctx.workspace.id:
        raise HTTPException(404)
    if body.status and body.status not in FLOW_STATUSES:
        raise HTTPException(422, "invalid status")
    for field, val in body.model_dump(exclude_unset=True).items():
        setattr(t, field, val)
    await db.commit()
    await db.refresh(t)
    return t
