# OPSPECTA — security and privacy gap register

**Assessment date:** 2026-11-09
**Baseline:** `main` commit `21fb5f5`. This is a source review, not a penetration test, legal opinion, certification audit or production database assessment.

## Risk register

| Priority | Finding | Evidence | Required action / release gate |
|---|---|---|---|
| Blocker before multi-customer data | No organization/tenant identifier or membership boundary is present in the baseline user/ticket/equipment models. Lower-role ticket access is owner-scoped, but higher roles are globally scoped; machine and KB queries do not demonstrate customer scope. | `apps/api/app/models/user.py`, `ticket.py`, `machine.py`; `apps/api/app/api/routes/tickets.py`; `apps/api/app/crud/machine.py`; `apps/api/app/services/analyze_service.py` | Implement server-derived tenant scoping across every object/API/blob/retrieval path; add cross-tenant negative tests and independent review before multi-tenant claims or data. |
| High | PR #89 is a large unmerged KB/workspace and migration change (70 commits ahead, 5 behind `main`, dirty merge state). Its CI was green on an older base, but that does not prove PostgreSQL upgrade safety or production restore readiness. | PR #89 description, current branch graph, PR checks | Review the full diff, rebase onto current main, run full current CI and a disposable PostgreSQL migration/data-preservation rehearsal. Require verified backup and restore before production schema changes. |
| High | Production startup executes `Base.metadata.create_all`; ORM `create_all` is not a substitute for schema migrations. SQLite metadata-based tests do not prove PostgreSQL/vector migration behavior. | `apps/api/app/main.py`; `apps/api/tests/`; `apps/api/alembic/versions/` | Confirm deployment order, disable unsafe runtime DDL if appropriate, test migration from each supported baseline on PostgreSQL, exercise downgrade/restore policy. |
| High | Mobile dashboard/equipment pages show hard-coded values; offline queue starts from seed examples; no visible login flow or mobile behavioral test suite. | `apps/mobile/app/index.tsx`, `machines.tsx`, `src/services/offlineTickets.ts`, `package.json`, `.github/workflows/test-mobile.yml` | Keep demo data explicitly labeled; implement auth and tenant-aware API use before customer operations; replace the no-op test script with real behavior tests. |
| Medium/High | Health endpoint returns static `{"status":"ok"}` and no evidence of metrics, tracing, error reporting, alerting or tested disaster recovery was found. | `apps/api/app/main.py`; deployment/docs review | Add separate liveness/readiness semantics, dependency checks, error/latency monitoring, on-call alerts and tested backup restore. |
| Medium/High | Notification delivery includes a development mock; external AI is disabled by default and guarded but provider delivery, retention, deletion and end-to-end audit are not established by code tests alone. | `apps/api/app/api/routes/notifications.py`; `services/rca_advanced.py`; responsible-AI tests | Keep mocks and external calls clearly separated; approve provider/DPA/region/retention and test retries, authenticity, rate limits and data minimization before activation. |
| Medium | Sensitive-data detection is pattern-based and explicitly partial. | `apps/api/app/services/rca_advanced.py`; `docs/security/OPSPECTA_RESPONSIBLE_AI_2026.md` | Do not treat detection as de-identification or legal basis. Minimize inputs, contractually govern processing and perform privacy review. |
| Medium | API analysis previously turned all retrieval exceptions into a no-match result. The audit branch narrows this: absent optional semantic dependencies now produce an explicit 503; other failures propagate. | `apps/api/app/services/analyze_service.py`; `apps/api/app/api/routes/analyze.py`; `apps/api/app/api/routes/tickets.py`; `apps/api/tests/test_clinical_workflows.py` | Merge only after CI; preserve regression coverage and confirm production error monitoring does not log sensitive request content. |
| Medium | Mobile dependency audit policy blocks only critical issues; web/API CI use stricter audit thresholds. | `.github/workflows/test-mobile.yml`; web/API workflows | Align severity policy and document narrowly approved exceptions with expiry and owner. |
| Medium | Regulatory status depends on intended use and market; source copy describes operational/technical assistance, but this assessment does not decide SaMD/CDS classification. | Public product pages and intended-use text; FDA/ANVISA references below | Obtain qualified regulatory advice before expanding to clinical diagnosis, treatment, patient monitoring or safety-critical recommendations. |

## Existing controls observed

- JWT issuer/audience/expiry and server-side account-status/version checks; role-based access and password hashing.
- Production self-registration off by default and allowlist validation when enabled.
- Rate limiting and security headers are configured.
- Ticket attachments are type/size checked and use an S3-compatible storage abstraction.
- Technical conclusions require an explicit qualified human confirmation endpoint; audit log detail is designed to avoid raw narratives.
- External AI processing has a deployment-level opt-in and per-request opt-in; it is disabled by default.
- Automated API tests cover authentication, role boundaries, responsible-AI input checks and human review.

These controls do not address absent organization isolation, operational safeguards, or all possible attack paths.

## Release conditions for real customer data

1. Define and implement tenant ownership and membership authorization for every resource and object storage key.
2. Test same-user/different-tenant, privileged-role/different-tenant, enumeration, bulk export and attachment access paths.
3. Complete threat modeling, dependency review, backup/restore, retention/deletion and incident-response procedures.
4. Verify provider contracts, data residency and subprocessors before any external processing.
5. Rehearse PostgreSQL migrations on a disposable environment using representative synthetic legacy data.
6. Review regulatory intended purpose in each target market.

## References (accessed 2026-11-09)

- OWASP GenAI Security Project / current LLM Top 10: https://genai.owasp.org/llm-top-10/
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Generative AI Profile: https://doi.org/10.6028/NIST.AI.600-1
- FDA Clinical Decision Support Software Guidance (January 2026 page): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
- Brazil RDC 657/2022 (official publication): https://www.in.gov.br/en/web/dou/-/resolucao-rdc-n-657-de-22-de-marco-de-2022-389890649

Framework references guide review; OPSPECTA has not claimed certification or regulatory clearance.
