"""Arq worker entrypoint:  arq vyse_api.worker.main.WorkerSettings"""
from arq import cron
from arq.connections import RedisSettings

from ..settings import get_settings
from . import jobs

settings = get_settings()


async def resync_metrics(ctx):
    """Every 6h: refetch metrics + append snapshots (feeds SPIKE velocity)."""
    # Walkthrough left as an exercise: iterate fetched posts, re-fetch, snapshot, re-score.
    return


async def nightly_aggregates(ctx):
    """Recompute account_avg_eng, engagement_rate, niche clusters."""
    return


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [
        jobs.ingest_post,
        jobs.analyze_post,
        jobs.embed_post,
        jobs.score_post,
        jobs.reason_post,
    ]
    cron_jobs = [
        cron(resync_metrics, hour={0, 6, 12, 18}, minute=0),
        cron(nightly_aggregates, hour=3, minute=0),
    ]
    max_jobs = 10
