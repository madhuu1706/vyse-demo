# VYSE

**AI-powered competitor content intelligence.** Find what works. Know why. Recreate faster.

This is a runnable monorepo foundation for VYSE — the full vertical slice wired end to
end. It boots **with zero external API keys** in dev mode, so you can see the whole loop
(ingest → analyze → score → reason → recreate → organize) working before you plug in
Clerk, OpenAI, Stripe, or platform APIs.

> Honest status: this is the foundation, not a finished commercial product. The pipeline,
> all 8 module APIs, the data model, the scorer, and the UI are real and runnable. The
> things that genuinely need *your* accounts and weeks of iteration (live competitor
> metrics at scale, real LLM output, billing, Clerk orgs, Instagram/LinkedIn) are wired
> behind clean interfaces with working stubs. See **What's wired vs stubbed** below.

---

## Stack

- **Backend:** FastAPI + async SQLAlchemy 2.0 (asyncpg), Arq worker, Redis, Postgres + pgvector
- **Frontend:** Next.js 15 (App Router), Tailwind, TypeScript
- **AI:** provider-agnostic layer — OpenAI when keyed, deterministic offline stub otherwise
- **Auth:** dev mode (seeded workspace) or Clerk JWT verification

The architecture decisions (Arq over BullMQ, pgvector over Pinecone, Postgres over
ClickHouse for MVP, YouTube-first, deterministic SPIKE) are explained in the build
blueprint. `packages/README.md` maps the blueprint's package layout to where each piece
lives in the code.

---

## Quick start (zero keys)

```bash
# 1. Backend + infra (Postgres, Redis, API, worker)
cp .env.example .env
docker compose up --build
#   API  -> http://localhost:8000      (docs at /docs)
#   health -> http://localhost:8000/health

# 2. Frontend (separate terminal)
cd apps/web
cp .env.local.example .env.local
pnpm install && pnpm dev
#   App -> http://localhost:3000
```

Open the app, go to **Posts**, paste a YouTube URL, hit **Analyze**. The post is ingested
via oEmbed, the pipeline runs (analyze → embed → score → reason), and the detail page fills
in the PULSE / SPIKE / WHY panels. In dev mode AI uses the offline stub, so this works with
no OpenAI key.

### Run without Docker

```bash
# Postgres (needs the pgvector extension) + Redis running locally, then:
cd apps/api
pip install -e .            # or: uv pip install -e .
uvicorn vyse_api.main:app --reload          # API
arq vyse_api.worker.main.WorkerSettings     # worker (separate terminal)
```

---

## Tests

```bash
cd apps/api && pytest -q
```

The SPIKE scorer (`vyse_api/scoring.py`) is pure and fully unit-tested
(`tests/test_scoring.py`) — baseline, viral, evergreen, retention cap, and the
missing-metrics safety path all pass.

---

## What's wired vs stubbed

| Area | Status |
|---|---|
| All 8 module REST APIs (SCOUT, SNAP, PULSE, SPIKE, WHY, FORGE, VAULT, FLOW) | **Wired** — 28 endpoints, workspace-scoped |
| Data model (14 tables, multi-tenant, pgvector) | **Wired** — auto-created in dev |
| Ingestion pipeline (Arq: ingest→analyze→embed→score→reason) | **Wired** — idempotent, chained |
| SPIKE outlier scoring | **Wired** — deterministic, tested |
| YouTube / TikTok ingestion (oEmbed) | **Wired** — works keyless for embeds |
| AI (PULSE / WHY / FORGE) | **Wired interface** — real OpenAI when `OPENAI_API_KEY` set; offline stub otherwise |
| Semantic vault search (pgvector cosine) | **Wired** — stub embeddings until OpenAI key added |
| Frontend (all pages + dashboard, kanban, forge studio) | **Wired** — talks to the live API |
| Auth | **Dev mode wired**; Clerk JWT path implemented, needs your keys |
| Competitor metrics at scale | **Stub** — needs YouTube Data API key / licensed provider |
| Instagram / LinkedIn | **Honest placeholder** — need app review / data provider |
| Billing | **Stub** — Stripe checkout/portal/webhook scaffolded, needs keys |
| Transcription, vision, niche clustering, cron resync | **Scaffolded** — hooks in place |

---

## Going to production

1. **Auth:** set `AUTH_MODE=clerk` + `CLERK_JWKS_URL`/`CLERK_ISSUER`; wire the Clerk webhook
   (`/webhooks/clerk`) so orgs/users sync into `workspaces`/`users`/`memberships`.
2. **AI:** set `OPENAI_API_KEY` — PULSE/WHY/FORGE and embeddings switch from stub to real.
3. **Data:** set `YOUTUBE_API_KEY` for durable metrics; add a licensed provider behind
   `ScraperProvider` for IG/LinkedIn (see blueprint §0.3).
4. **Migrations:** swap dev auto-create for Alembic (`packages/db/schema.sql` is the reference).
5. **Billing:** set Stripe keys + price IDs; verify webhook signatures.
6. **Harden:** signature-verify webhooks, per-workspace AI budgets, Sentry, the per-platform
   ingest throttle. Build order is in the blueprint §9.

---

## Layout

```
vyse/
├── apps/
│   ├── api/      FastAPI app + Arq worker (one codebase, two entrypoints)
│   │   └── vyse_api/{models,schemas,scoring,ai,scraper,auth,middleware,enqueue}.py
│   │       ├── routers/   one file per module
│   │       └── worker/    Arq jobs + WorkerSettings + cron
│   └── web/      Next.js 15 app (App Router): all module pages + shared UI
└── packages/     db schema reference + package→module map (see packages/README.md)
```
