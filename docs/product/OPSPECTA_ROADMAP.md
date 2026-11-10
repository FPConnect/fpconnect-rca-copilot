# OPSPECTA — evidence-based roadmap

**Updated:** 2026-11-09
**Planning status:** prioritized proposal; dates and staffing are not commitments.

## Prioritization method

Score work by customer value, safety/privacy risk, evidence, cost and dependencies. Security boundaries and data integrity outrank model novelty. Do not pursue high-cost features until a bounded customer pilot demonstrates demand.

## Cycle A — stabilize before customer data (P0)

1. **Tenant/security architecture:** define organization and membership semantics and scope every customer-owned resource. Add negative cross-tenant tests. No multi-tenant claim until independently reviewed.
2. **Reconcile PR #89:** base is stale (70 commits ahead, 5 behind `main`) and GitHub reports a dirty merge state. Review its migration/authorization diff, rebase in a separate branch, run current CI and PostgreSQL migration/data-preservation/restore rehearsal. Do not run migration in production without verified backup and separate approval.
3. **Accurate failure states:** surfaced retrieval/database/model failures as errors instead of false “no match” results; first patch in this audit branch makes both analysis routes return localized HTTP 503 only when the optional local model package is absent and lets other errors propagate.
4. **Mobile readiness:** implement sign-in/session expiry, tenant-safe API-backed equipment/dashboard, demo labeling, loading/error states and real unit/integration tests. Until then, label the mobile UI prototype.
5. **Operations:** readiness checks, error monitoring, alerting, deployment rollback, backups and restoration evidence.
6. **Dependency policy:** reconcile mobile/web/API advisory thresholds and create time-bounded documented exceptions.

## Cycle B — paid pilot value (P1)

- Authorized CSV/XLSX/JSON import with mapping preview, validation report, duplicate handling and source lineage.
- Descriptive metrics with exact definitions, missingness and reproducible calculations.
- Recurrence view using asset identity, symptom, dates and outcome; distinguish candidate similarity from confirmed recurrence.
- Human-reviewed RCA evidence panel with approved-source references and version tracking.
- Transparent report export, preserving source and calculation provenance.
- Measure review effort and outcome during a scoped pilot before claiming savings.

## Cycle C — evaluated intelligence (P2)

- Improve KB curation, retrieval evaluation and tenant/corpus scoping.
- Add model-agnostic inference contracts with bounded tools and human approval.
- Evaluate anomaly detection and survival analysis only if sample size, labels and temporal coverage support them.
- Consider graph projections or digital-twin terminology only after a relational prototype demonstrates a gap. Current code is not a physical sensor twin.

## Cycle D — global expansion (P3)

- Add standard-based integrations only for named customer systems and authorized endpoints.
- Evaluate FHIR `Device`, `Provenance`, `AuditEvent`; DICOMweb only for authorized imaging use cases.
- Expand localization and accessibility with WCAG 2.2 AA as a target and assistive-technology testing.
- Explore aggregate benchmarking only with explicit consent, lawful basis and re-identification risk analysis.

## Gates before moving cycles

- P0: organization isolation tests and restore/migration proof.
- P1: pilot acceptance criteria signed off before data arrives; sample and outputs independently reconciled.
- P2: evaluation protocol, dataset version, baselines and false-alert reporting.
- P3: legal, security, vendor and support requirements agreed for each integration/region.

## Current blockers

- No organization/tenant fields in the baseline API models.
- PR #89 remains open, stale relative to `main`, and requires migration rehearsal/backup evidence.
- Mobile test command is a successful placeholder; key screens remain seeded/static.
- No production readiness/restore or prospective model validation evidence was reviewed.
