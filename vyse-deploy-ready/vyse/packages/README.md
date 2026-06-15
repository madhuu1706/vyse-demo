# packages/

The architecture blueprint describes these as separate Python packages. In this
runnable scaffold the logic lives as focused modules inside `apps/api/vyse_api/`
so the service installs and runs as one unit (the cleanest path to "it runs").
The boundaries are still real — splitting them into installable packages later is
mechanical.

| Blueprint package | Implemented as |
|---|---|
| `packages/db` | `vyse_api/models.py` (+ `schema.sql` here for reference) |
| `packages/ai` | `vyse_api/ai.py` (AIProvider protocol, OpenAI + offline stub) |
| `packages/scraper` | `vyse_api/scraper.py` (ScraperProvider, YouTube/TikTok oEmbed) |
| `packages/queue` | `vyse_api/enqueue.py` + `vyse_api/worker/` (Arq) |
| `packages/analytics` | `vyse_api/scoring.py` (SPIKE) + worker cron aggregates |
| `packages/embeddings` | pgvector via `Embedding` model + `/v1/vault/search` |
| `packages/ui` | shared React primitives currently in `apps/web/components/ui` |
