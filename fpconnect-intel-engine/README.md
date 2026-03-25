# FPConnect Intel Engine (MVP) — RSS/APIs Públicas + Postgres

This project is a **ready-to-run** Market/Tech Intelligence engine for FPConnect.
It ingests **trusted RSS feeds** (cybersecurity, research, interoperability), stores items in **PostgreSQL**, and exposes a simple **FastAPI** to query content.

✅ **Bilingual-ready (PT/EN):** the DB stores `summary_pt` and `summary_en`.
- Without an LLM key, it uses simple heuristics (both summaries may be the same).
- With an LLM provider key, you can generate high-quality bilingual summaries.

✅ **Agentic workflow-ready:** each new item can run a 3-step flow:
- **Research Agent:** enriches short content with public page context.
- **Triage Agent:** infers `topic`, `severity`, and recommended action.
- **RCA Agent:** proposes root-cause hypothesis and action plan using semantic memory (RAG-like behavior).

---

## IMPORTANT (LinkedIn)
- **LinkedIn Premium is not an API.**
- **Do not scrape or automate login-based monitoring of LinkedIn**, as it can violate the platform's Terms.
- If you have an approved **official LinkedIn API** (Marketing/Community), you can add a connector module later.
- For now, use RSS/public APIs and (optionally) manually export LinkedIn data you own.

---

## Quickstart (Docker)

### 1) Copy env
```bash
cp .env.example .env
```

### 2) Start services
```bash
docker compose up -d --build
```
This starts:
- Postgres (pgvector-ready)
- API on http://localhost:8000
- Background `ingest_loop` container polling sources every 15 minutes

### 3) Test
Open:
- http://localhost:8000/  (built-in test UI)
- http://localhost:8000/health
- http://localhost:8000/items

---

## Run ingestion manually (optional)
```bash
docker compose run --rm api python -m app.scripts.ingest_once
```

---

## Configure sources
Edit `sources.yaml`.
Each source must be a direct RSS URL.

---

## API endpoints
- `GET /health`
- `GET /items?topic=cybersecurity&limit=50`
- `POST /ingest/once` (manual ingestion)

`GET /items` now also returns:
- `severity`
- `rca`

---

## Next upgrades (recommended)
1) Add pgvector embeddings for semantic search
2) Add a "feature suggestion" generator that opens GitHub Issues (optional)
3) Add official API connectors (only where authorized)
4) Add a small web dashboard (Next.js) for browsing insights and exporting weekly reports
