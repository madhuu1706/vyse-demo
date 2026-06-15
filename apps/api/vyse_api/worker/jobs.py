"""Arq jobs implementing the ingestion + analysis pipeline.

ingest_post -> analyze_post -> embed_post -> score_post -> (if outlier) reason_post
Each job is idempotent and updates the jobs audit row.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from ..ai import PULSE_SCHEMA, WHY_SCHEMA, get_ai
from ..db import SessionLocal
from ..models import (
    Analysis,
    Embedding,
    Job,
    MetricSnapshot,
    Outlier,
    Post,
    Reasoning,
)
from ..scoring import Snapshot, outlier_score
from ..scraper import get_scraper
from ..settings import get_settings

settings = get_settings()


async def _mark(db, job_id_db, status, error=None):
    if not job_id_db:
        return
    job = await db.get(Job, uuid.UUID(job_id_db))
    if job:
        job.status = status
        job.error = error


async def ingest_post(ctx, post_id: str, job_id_db: str | None = None):
    async with SessionLocal() as db:
        await _mark(db, job_id_db, "running")
        post = await db.get(Post, uuid.UUID(post_id))
        if not post:
            return
        try:
            data = await get_scraper(post.platform).fetch(post.url)
            post.embed_html = data.get("embed_html")
            post.thumbnail_url = data.get("thumbnail_url")
            post.caption = data.get("caption") or post.caption
            post.media_type = data.get("media_type")
            post.external_id = data.get("external_id")
            post.metrics = data.get("metrics") or {}
            post.ingest_status = "fetched"
            db.add(MetricSnapshot(post_id=post.id, **{k: post.metrics.get(k) for k in
                   ("likes", "comments", "shares", "views", "saves")}))
            await _mark(db, job_id_db, "done")
            await db.commit()
        except Exception as e:  # noqa: BLE001
            post.ingest_status = "failed"
            await _mark(db, job_id_db, "failed", str(e))
            await db.commit()
            raise
    await ctx["redis"].enqueue_job("analyze_post", post_id)


async def analyze_post(ctx, post_id: str, job_id_db: str | None = None):
    async with SessionLocal() as db:
        post = await db.get(Post, uuid.UUID(post_id))
        if not post:
            return
        ai = get_ai()
        out = await ai.structured(
            system="Analyze this social post. Return hook_type, cta_type, emotion[], "
                   "story_pattern, content_pillar.",
            user=f"Caption: {post.caption}\nTranscript: {post.transcript or ''}",
            schema=PULSE_SCHEMA,
            model=settings.ai_chat_model,
        )
        existing = (await db.execute(select(Analysis).where(Analysis.post_id == post.id))).scalar_one_or_none()
        a = existing or Analysis(post_id=post.id)
        a.hook_type, a.cta_type = out.get("hook_type"), out.get("cta_type")
        a.emotion, a.story_pattern = out.get("emotion"), out.get("story_pattern")
        a.content_pillar, a.raw = out.get("content_pillar"), out
        a.model = settings.ai_chat_model if settings.openai_api_key else "stub"
        if not existing:
            db.add(a)
        await db.commit()
    await ctx["redis"].enqueue_job("embed_post", post_id)
    await ctx["redis"].enqueue_job("score_post", post_id)


async def embed_post(ctx, post_id: str, job_id_db: str | None = None):
    async with SessionLocal() as db:
        post = await db.get(Post, uuid.UUID(post_id))
        if not post:
            return
        text_blob = " ".join(filter(None, [post.caption, post.transcript]))
        if not text_blob.strip():
            return
        vec = (await get_ai().embed(texts=[text_blob], model=settings.ai_embed_model))[0]
        db.add(Embedding(workspace_id=post.workspace_id, post_id=post.id, kind="composite", vector=vec))
        await db.commit()


async def score_post(ctx, post_id: str, job_id_db: str | None = None):
    async with SessionLocal() as db:
        post = await db.get(Post, uuid.UUID(post_id))
        if not post:
            return
        avg = float(post.competitor.account_avg_eng) if post.competitor and post.competitor.account_avg_eng else None
        snaps = (await db.execute(
            select(MetricSnapshot).where(MetricSnapshot.post_id == post.id).order_by(MetricSnapshot.captured_at)
        )).scalars().all()
        snapshots = [Snapshot(
            captured_at=s.captured_at, likes=s.likes or 0, comments=s.comments or 0,
            shares=s.shares or 0, views=s.views or 0, saves=s.saves or 0) for s in snaps]
        result = outlier_score(post.metrics, avg, snapshots)
        existing = (await db.execute(select(Outlier).where(Outlier.post_id == post.id))).scalar_one_or_none()
        o = existing or Outlier(post_id=post.id)
        o.score, o.outlier_type, o.components = result["score"], result["outlier_type"], result["components"]
        o.detected_at = datetime.now(timezone.utc)
        if not existing:
            db.add(o)
        await db.commit()
        is_outlier = result["outlier_type"] != "none"
    if is_outlier:
        await ctx["redis"].enqueue_job("reason_post", post_id)


async def reason_post(ctx, post_id: str, job_id_db: str | None = None):
    async with SessionLocal() as db:
        post = await db.get(Post, uuid.UUID(post_id))
        if not post or not post.analysis or not post.outlier:
            return
        out = await get_ai().structured(
            system="Explain why this content outperformed. Return why_it_worked, "
                   "trigger_type[], success_factors{}, replication_insights.",
            user=f"Caption: {post.caption}\nAnalysis: {post.analysis.raw}\n"
                 f"Outlier score: {post.outlier.score} ({post.outlier.outlier_type})\n"
                 f"Components: {post.outlier.components}",
            schema=WHY_SCHEMA,
            model=settings.ai_chat_model,
        )
        existing = (await db.execute(select(Reasoning).where(Reasoning.post_id == post.id))).scalar_one_or_none()
        r = existing or Reasoning(post_id=post.id)
        r.why_it_worked = out.get("why_it_worked")
        r.trigger_type = out.get("trigger_type")
        r.success_factors = out.get("success_factors")
        r.replication_insights = out.get("replication_insights")
        r.model = settings.ai_chat_model if settings.openai_api_key else "stub"
        if not existing:
            db.add(r)
        await db.commit()
