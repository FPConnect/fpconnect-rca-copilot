# OPSPECTA — current system state

**Assessment date:** 2026-11-09
**Repository baseline:** `main` at `21fb5f536bacf23a202830b18133e4fbedbb000b` (PR #91).
**Scope:** source, tests, configuration and GitHub workflow metadata accessible during this assessment. No production database, customer environment, Vercel secrets, or authenticated customer account was accessed.

## Executive assessment

OPSPECTA is a working monorepo with a Next.js public/product web app, FastAPI API, and Expo mobile app. The API has meaningful authenticated ticket, equipment, attachment, account, notification, playbook, contract, and analysis routes. Authentication, role checks, human confirmation of technical conclusions, and several privacy controls have automated tests.

This does **not** establish production readiness as a multi-customer SaaS. The API models contain no organization/tenant identifier or membership boundary. Regular users are scoped to tickets they created, but level 3+ users have global ticket visibility; equipment, knowledge articles and other resources do not demonstrate customer-level isolation. The current mobile dashboard and equipment screen are static examples, and the mobile test script exits successfully while printing “No tests yet.”

| Area | Observed state | Maturity |
|---|---|---|
| Public web | Landing, solutions, diagnostic, resources, demonstration and responsible-AI pages are implemented; localized home page and crawler endpoints are live. Some pages intentionally contain illustrative content. | Implemented; production route check passed in prior deployment |
| Authenticated web | API client, server session validation, route screens and test coverage exist. Some preview data paths remain configurable. | Partially validated; not a substitute for end-to-end customer acceptance |
| API | FastAPI routes and SQLAlchemy CRUD for tickets, machines, users, contracts, playbooks, notifications, attachments and RCA exist. | Implemented; test suite passed locally |
| Authentication | JWT validation against current account state, token versioning, password hashing and RBAC exist. | Implemented; automated coverage present |
| Authorization / tenancy | Per-user ticket ownership for lower access levels and role-based global access for higher levels; no organization model/foreign keys found in the baseline API models. | **Insufficient for multi-tenant customer data** |
| Database | PostgreSQL is configurable; SQLite is used for many tests. Alembic history on `main` ends at revision `007`; local tests commonly create schema from ORM metadata rather than replaying the full production migration chain. | Implemented, migration/production compatibility not fully demonstrated |
| Attachments | S3-compatible upload and expiring download URL helpers exist. | Implemented; tenant authorization and live provider operations require further validation |
| Knowledge retrieval | Optional local sentence-transformer embeddings, top-three KB retrieval and a similarity threshold are present. External LLM processing is disabled by default. | Prototype/limited; no validated retrieval-quality benchmark or tenant-scoped corpus |
| Predictive scoring | An explainable weighted triage heuristic exists and explicitly says it is not calibrated or a failure probability. | Exploratory only; not predictive maintenance |
| Mobile | Expo app, local ticket queue and token-aware synchronization exist. Dashboard/equipment views are hard-coded; no complete sign-in lifecycle or automated behavioral tests were found. | Prototype; not a production-ready fleet client |
| Observability | Structured request logging and a `/health` endpoint exist. `/health` returns a static `ok`; comprehensive readiness, tracing, metrics, alerting and recovery evidence were not found. | Basic |
| CI/CD | GitHub workflows test web/API/mobile and deploy API/web through Vercel from `main`. PR #91's merge deployment completed successfully. | Implemented; a green pipeline does not prove customer-data isolation or database recovery |
| External services | S3-compatible storage, Redis and OpenAI-related configuration/dependencies exist; notifications include a development mock and external AI has explicit gates. | Some adapters/configuration exist; each provider's production delivery and operational controls need proof |

## Evidence and validation

- Baseline code: `apps/api/app/api/routes/`, `apps/api/app/models/`, `apps/web/src/`, `apps/mobile/app/`.
- Database and migrations: `apps/api/app/core/database.py`, `apps/api/app/models/`, `apps/api/alembic/versions/001_initial_schema.py` through `007_user_status.py`.
- ML dependencies are optional in `apps/api/requirements-ml.txt`; the standard API requirements omit `sentence-transformers`.
- The baseline API suite passed **65** tests during audit; after the first safe fix on this branch, **67** API tests passed and Ruff passed.
- Mobile `npm run typecheck` passed. `npm test` printed `No tests yet` and exited 0; this is not evidence of mobile behavioral tests.
- The production deploy workflow for commit `21fb5f5` completed successfully on 2026-11-09; its Test Web, Test API, Deploy API and Deploy Web jobs succeeded.
- The audit worktree's first change is not yet merged or deployed.

## Branch and integration status

The local audit branch starts at current `main`. The existing PR #89 branch, `opspecta-improvements-1104`, is **70 commits ahead and 5 behind** `main` in the fetched history. PR #89 is open with a dirty merge state; its last visible CI checks passed against an older base, while required PostgreSQL migration rehearsal and verified backup/restore gates remain explicit release conditions. Do not merge it by simply resolving conflicts or running its migration against production.

## High-impact findings

1. Establish organization membership and enforce a server-derived tenant boundary before storing or retrieving multiple customers' records.
2. Review and rebase PR #89 onto current `main`; re-run the entire suite and a disposable PostgreSQL Alembic upgrade/rollback/data-preservation rehearsal.
3. Treat the mobile application as a prototype until real authentication, API-backed screens, clear demo labeling, and meaningful automated tests are implemented.
4. Ensure analysis infrastructure failures are not represented as a successful “no similar cause” result. This audit branch now returns an explicit HTTP 503 when optional semantic-search dependencies are missing and lets other retrieval errors surface; tests cover both API analysis routes.
5. Add operational readiness checks, alerting, error monitoring, verified backups/restores and customer-appropriate retention/deletion controls.

## Explicit non-claims

This assessment does not establish a completed multi-tenant SaaS, predictive maintenance, validated causal diagnosis, full FHIR/DICOM integration, regulatory clearance, ISO certification, production mobile readiness, or customer-measured ROI.
