.PHONY: up down api worker web test seed
up:        ## start db + redis + api + worker
	docker compose up --build
down:
	docker compose down
api:       ## run api locally (needs db+redis up)
	cd apps/api && uvicorn vyse_api.main:app --reload
worker:    ## run arq worker locally
	cd apps/api && arq vyse_api.worker.main.WorkerSettings
web:       ## run next.js frontend
	cd apps/web && pnpm install && pnpm dev
test:      ## run backend tests
	cd apps/api && pytest -q
