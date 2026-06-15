# Deploying VYSE as a web application

VYSE has four runtime pieces: a **frontend**, a **FastAPI API**, a **background worker**,
and **Postgres + Redis**. No single platform hosts all of it well, so the live app is:

- **Frontend → Vercel**
- **API + worker + Redis + Postgres → Render** (one Blueprint = `render.yaml`)

Total time: ~15 minutes. You need a GitHub account, a Render account, and a Vercel account.

---

## Step 1 — Put the code on GitHub

```bash
cd vyse
git init && git add . && git commit -m "VYSE initial"
git branch -M main
git remote add origin https://github.com/<you>/vyse.git
git push -u origin main
```

Vercel and Render both deploy from this repo and redeploy automatically on every push.

## Step 2 — Backend stack on Render (one Blueprint)

1. Render dashboard → **New** → **Blueprint**.
2. Connect your GitHub repo. Render reads `render.yaml` and proposes four resources:
   `vyse-api` (web), `vyse-worker`, `vyse-redis`, `vyse-db`.
3. Click **Apply**. The API and worker build from `apps/api/Dockerfile`; Postgres and
   Redis are provisioned and wired automatically.
4. When it's up, open `vyse-api` and copy its URL, e.g. `https://vyse-api.onrender.com`.
   Hit `https://vyse-api.onrender.com/health` — you should get `{"status":"ok"}`.

The API self-bootstraps the schema (pgvector extension + tables) on first boot, so there's
no separate migration step to get started.

> Database note: Render's free Postgres is time-limited. Since you already use Supabase,
> a sturdier option is to delete the `databases:` block in `render.yaml` and instead set
> `DATABASE_URL` (as a secret env var on both services) to your Supabase connection string
> — pgvector is built in. The app accepts a plain `postgresql://` URL and adapts it.

## Step 3 — Frontend on Vercel

1. Vercel → **Add New** → **Project** → import the same repo.
2. **Root Directory → `apps/web`** (this is the one setting that matters for a monorepo).
3. Environment Variables → add `NEXT_PUBLIC_API_URL = https://vyse-api.onrender.com`
   (your Step 2 URL). The app proxies `/api/*` to it, so the browser stays same-origin.
4. **Deploy.** You get a URL like `https://vyse.vercel.app` — that's your web app.

## Step 4 — Close the loop

1. Back on Render, set `vyse-api`'s `CORS_ORIGINS` to your Vercel domain.
2. Open the Vercel URL → **Posts** → paste a YouTube link → **Analyze**. The worker runs
   the pipeline and the PULSE / SPIKE / WHY panels fill in.

That's a live web application. It runs on the offline AI stub until you add a key.

---

## Turning on the real features

| Want | Set (on the Render services) |
|---|---|
| Real AI (PULSE/WHY/FORGE) | `OPENAI_API_KEY` |
| Durable YouTube metrics | `YOUTUBE_API_KEY` |
| Real multi-user accounts | `AUTH_MODE=clerk`, `CLERK_JWKS_URL`, `CLERK_ISSUER`; wire the Clerk webhook |
| Billing | `STRIPE_SECRET_KEY` + price IDs |

## Alternatives

- **Everything on Railway instead of Render:** create a project, add services from the repo
  (API start `uvicorn vyse_api.main:app --host 0.0.0.0 --port $PORT`, worker start
  `arq vyse_api.worker.main.WorkerSettings`), plus the Postgres and Redis templates. No
  Blueprint file; you wire it in the dashboard. Frontend can still go to Vercel.
- **Frontend on Render too** (single platform): add a Node web service for `apps/web`
  (build `corepack enable && pnpm install && pnpm build`, start `pnpm start`).
- **API on Vercel:** possible via Vercel's Python runtime, but the worker still can't run
  there, so you'd split anyway — not worth it for this app.
