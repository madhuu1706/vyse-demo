import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- SCOUT ----------
class CompetitorIn(BaseModel):
    platform: str
    handle: str
    niche: str | None = None


class CompetitorOut(ORM):
    id: uuid.UUID
    platform: str
    handle: str
    display_name: str | None = None
    avatar_url: str | None = None
    followers: int | None = None
    engagement_rate: float | None = None
    niche: str | None = None
    account_avg_eng: float | None = None
    last_synced_at: datetime | None = None
    created_at: datetime


# ---------- SNAP ----------
class IngestIn(BaseModel):
    url: str
    competitor_id: uuid.UUID | None = None


class IngestOut(BaseModel):
    post_id: uuid.UUID
    job_id: uuid.UUID
    platform: str
    status: str


class PostOut(ORM):
    id: uuid.UUID
    competitor_id: uuid.UUID | None = None
    platform: str
    url: str
    embed_html: str | None = None
    thumbnail_url: str | None = None
    media_type: str | None = None
    caption: str | None = None
    hashtags: list[str] | None = None
    metrics: dict = {}
    posted_at: datetime | None = None
    ingest_status: str
    created_at: datetime


# ---------- PULSE ----------
class AnalysisOut(ORM):
    hook_type: str | None = None
    cta_type: str | None = None
    emotion: list[str] | None = None
    story_pattern: str | None = None
    content_pillar: str | None = None
    raw: dict = {}


# ---------- SPIKE ----------
class OutlierOut(ORM):
    score: float
    outlier_type: str
    components: dict = {}
    detected_at: datetime


# ---------- WHY ----------
class ReasoningOut(ORM):
    why_it_worked: str | None = None
    trigger_type: list[str] | None = None
    success_factors: dict | None = None
    replication_insights: str | None = None


class PostDetail(PostOut):
    analysis: AnalysisOut | None = None
    outlier: OutlierOut | None = None
    reasoning: ReasoningOut | None = None


# ---------- FORGE ----------
class ForgeIn(BaseModel):
    source_post_id: uuid.UUID
    target_brand: str
    target_niche: str | None = None


class BlueprintOut(ORM):
    id: uuid.UUID
    source_post_id: uuid.UUID | None = None
    target_brand: str | None = None
    target_niche: str | None = None
    output: dict
    created_at: datetime


# ---------- VAULT ----------
class VaultIn(BaseModel):
    post_id: uuid.UUID | None = None
    board: str | None = None
    tags: list[str] = []
    notes: str | None = None


class VaultOut(ORM):
    id: uuid.UUID
    post_id: uuid.UUID | None = None
    board: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    created_at: datetime


class VaultSearchIn(BaseModel):
    query: str
    limit: int = 20


# ---------- FLOW ----------
FLOW_STATUSES = ["idea", "script", "shoot", "edit", "review", "posted"]


class FlowIn(BaseModel):
    title: str
    blueprint_id: uuid.UUID | None = None
    status: str = "idea"
    due_date: date | None = None


class FlowPatch(BaseModel):
    status: str | None = None
    position: int | None = None
    assignee_id: uuid.UUID | None = None
    title: str | None = None


class FlowOut(ORM):
    id: uuid.UUID
    blueprint_id: uuid.UUID | None = None
    title: str
    status: str
    assignee_id: uuid.UUID | None = None
    due_date: date | None = None
    position: int | None = None
    created_at: datetime


class Page(BaseModel):
    items: list
    next_cursor: str | None = None
