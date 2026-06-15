-- VYSE schema (reference). In dev the API auto-creates tables from SQLAlchemy models;
-- in prod use Alembic. This file mirrors apps/api/vyse_api/models.py.
create extension if not exists vector;
create extension if not exists pg_trgm;

create table if not exists workspaces (
  id uuid primary key default gen_random_uuid(),
  clerk_org_id text unique not null,
  name text not null,
  plan text not null default 'free',
  created_at timestamptz not null default now()
);
create table if not exists users (
  id uuid primary key default gen_random_uuid(),
  clerk_user_id text unique not null,
  email text not null,
  created_at timestamptz not null default now()
);
create table if not exists memberships (
  workspace_id uuid not null references workspaces(id) on delete cascade,
  user_id uuid not null references users(id) on delete cascade,
  role text not null default 'member',
  primary key (workspace_id, user_id)
);
create table if not exists competitors (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  platform text not null, handle text not null,
  display_name text, avatar_url text, followers bigint,
  engagement_rate numeric(6,4), niche text, niche_cluster int,
  account_avg_eng numeric, last_synced_at timestamptz,
  created_at timestamptz not null default now(),
  unique (workspace_id, platform, handle)
);
create table if not exists posts (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  competitor_id uuid references competitors(id) on delete set null,
  platform text not null, url text not null, external_id text,
  embed_html text, thumbnail_url text, media_type text, caption text,
  hashtags text[], transcript text, metrics jsonb not null default '{}',
  posted_at timestamptz, ingest_status text not null default 'pending',
  created_at timestamptz not null default now(),
  unique (workspace_id, url)
);
create table if not exists metric_snapshots (
  id bigserial primary key,
  post_id uuid not null references posts(id) on delete cascade,
  captured_at timestamptz not null default now(),
  likes bigint, comments bigint, shares bigint, views bigint, saves bigint
);
create table if not exists analyses (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references posts(id) on delete cascade unique,
  hook_type text, cta_type text, emotion text[], story_pattern text,
  content_pillar text, raw jsonb not null default '{}', model text,
  created_at timestamptz not null default now()
);
create table if not exists outliers (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references posts(id) on delete cascade unique,
  score numeric not null, outlier_type text not null,
  components jsonb not null default '{}',
  detected_at timestamptz not null default now()
);
create table if not exists reasonings (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references posts(id) on delete cascade unique,
  why_it_worked text, trigger_type text[], success_factors jsonb,
  replication_insights text, model text,
  created_at timestamptz not null default now()
);
create table if not exists blueprints (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  source_post_id uuid references posts(id) on delete set null,
  target_brand text, target_niche text, output jsonb not null, model text,
  created_at timestamptz not null default now()
);
create table if not exists vault_items (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  post_id uuid references posts(id) on delete cascade,
  board text, tags text[], notes text,
  created_at timestamptz not null default now()
);
create table if not exists flow_tasks (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  blueprint_id uuid references blueprints(id) on delete set null,
  title text not null, status text not null default 'idea',
  assignee_id uuid references users(id), due_date date, position int,
  created_at timestamptz not null default now()
);
create table if not exists embeddings (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid not null references workspaces(id) on delete cascade,
  post_id uuid references posts(id) on delete cascade,
  kind text not null, vector vector(1536) not null,
  created_at timestamptz not null default now()
);
create index if not exists embeddings_hnsw on embeddings using hnsw (vector vector_cosine_ops);
create table if not exists jobs (
  id uuid primary key default gen_random_uuid(),
  workspace_id uuid, type text not null, status text not null default 'queued',
  ref_id uuid, error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
