"""Typed Arq enqueue helpers + a jobs-table writer for observability/idempotency."""
import uuid

from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Job
from .settings import get_settings

settings = get_settings()
_pool = None


async def pool():
    global _pool
    if _pool is None:
        _pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    return _pool


async def enqueue(
    db: AsyncSession, *, job_type: str, ref_id: uuid.UUID, workspace_id: uuid.UUID, **kwargs
) -> uuid.UUID:
    job = Job(type=job_type, ref_id=ref_id, workspace_id=workspace_id, status="queued")
    db.add(job)
    await db.flush()
    p = await pool()
    await p.enqueue_job(job_type, str(ref_id), job_id_db=str(job.id), **kwargs)
    return job.id
