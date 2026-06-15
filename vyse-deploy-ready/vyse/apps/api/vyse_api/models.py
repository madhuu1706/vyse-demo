import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base
from .settings import get_settings

PK = lambda: mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # noqa: E731
NOW = lambda: mapped_column(DateTime(timezone=True), server_default=func.now())  # noqa: E731


class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[uuid.UUID] = PK()
    clerk_org_id: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    plan: Mapped[str] = mapped_column(String, default="free")
    created_at: Mapped[datetime] = NOW()


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = PK()
    clerk_user_id: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = NOW()


class Membership(Base):
    __tablename__ = "memberships"
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String, default="member")


class Competitor(Base):
    __tablename__ = "competitors"
    __table_args__ = (UniqueConstraint("workspace_id", "platform", "handle"),)
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    platform: Mapped[str] = mapped_column(String)
    handle: Mapped[str] = mapped_column(String)
    display_name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    followers: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    engagement_rate: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    niche: Mapped[str | None] = mapped_column(String, nullable=True)
    niche_cluster: Mapped[int | None] = mapped_column(Integer, nullable=True)
    account_avg_eng: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = NOW()


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("workspace_id", "url"),)
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    competitor_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("competitors.id", ondelete="SET NULL"), nullable=True
    )
    platform: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    embed_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String, nullable=True)
    media_type: Mapped[str | None] = mapped_column(String, nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSONB, default=dict)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ingest_status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = NOW()

    analysis: Mapped["Analysis"] = relationship(backref="post", uselist=False, lazy="selectin")
    outlier: Mapped["Outlier"] = relationship(backref="post", uselist=False, lazy="selectin")
    reasoning: Mapped["Reasoning"] = relationship(backref="post", uselist=False, lazy="selectin")
    competitor: Mapped["Competitor"] = relationship(lazy="selectin")


class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), index=True
    )
    captured_at: Mapped[datetime] = NOW()
    likes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    comments: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    shares: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    views: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    saves: Mapped[int | None] = mapped_column(BigInteger, nullable=True)


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[uuid.UUID] = PK()
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), unique=True
    )
    hook_type: Mapped[str | None] = mapped_column(String, nullable=True)
    cta_type: Mapped[str | None] = mapped_column(String, nullable=True)
    emotion: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    story_pattern: Mapped[str | None] = mapped_column(String, nullable=True)
    content_pillar: Mapped[str | None] = mapped_column(String, nullable=True)
    raw: Mapped[dict] = mapped_column(JSONB, default=dict)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = NOW()


class Outlier(Base):
    __tablename__ = "outliers"
    id: Mapped[uuid.UUID] = PK()
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), unique=True
    )
    score: Mapped[float] = mapped_column(Numeric)
    outlier_type: Mapped[str] = mapped_column(String)
    components: Mapped[dict] = mapped_column(JSONB, default=dict)
    detected_at: Mapped[datetime] = NOW()


class Reasoning(Base):
    __tablename__ = "reasonings"
    id: Mapped[uuid.UUID] = PK()
    post_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), unique=True
    )
    why_it_worked: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger_type: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    success_factors: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    replication_insights: Mapped[str | None] = mapped_column(Text, nullable=True)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = NOW()


class Blueprint(Base):
    __tablename__ = "blueprints"
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    source_post_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("posts.id", ondelete="SET NULL"), nullable=True
    )
    target_brand: Mapped[str | None] = mapped_column(String, nullable=True)
    target_niche: Mapped[str | None] = mapped_column(String, nullable=True)
    output: Mapped[dict] = mapped_column(JSONB)
    model: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = NOW()


class VaultItem(Base):
    __tablename__ = "vault_items"
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=True
    )
    board: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = NOW()


class FlowTask(Base):
    __tablename__ = "flow_tasks"
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    blueprint_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("blueprints.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="idea")
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = NOW()


class Embedding(Base):
    __tablename__ = "embeddings"
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), index=True
    )
    post_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String)
    vector: Mapped[list[float]] = mapped_column(Vector(get_settings().embed_dim))
    created_at: Mapped[datetime] = NOW()


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[uuid.UUID] = PK()
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    type: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="queued")
    ref_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = NOW()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
