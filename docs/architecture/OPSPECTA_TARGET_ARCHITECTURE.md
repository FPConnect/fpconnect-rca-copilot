# OPSPECTA — incremental target architecture

**Status:** proposed; not a description of already delivered capability.
**Updated:** 2026-11-09.

## Design constraint

First make one customer's authorized service history safe, traceable and useful. Do not introduce microservices, a graph database, autonomous agents, or continuous device telemetry until a measured use case justifies their cost and risk.

## Target flow

```text
Authorized source
  -> validated import/API
  -> canonical asset and service-event records
  -> tenant-scoped storage and audit
  -> deterministic metrics and retrieval
  -> optional bounded hypothesis generation
  -> human review and recorded decision
  -> evaluation and outcome measurement
```

## Incremental components

1. **Tenant foundation (release blocker for multi-customer use):** add organization and membership records, server-resolved organization context, and organization ownership on every customer-scoped record. Apply the same boundary to list, detail, update, delete, upload/download, audit, exports and knowledge retrieval. Add database constraints/indexes and tests that try cross-tenant access for every resource. Never trust a client-supplied tenant ID as authorization.
2. **Canonical domain model:** retain SQLAlchemy/PostgreSQL and extend equipment, service order, observed symptom, intervention, evidence reference, hypothesis and human-reviewed outcome with explicit source/version/timestamps. Use existing relational joins first; add graph projection only if query complexity or a measured product need warrants it.
3. **Import boundary:** start with authorized CSV/XLSX/JSON and documented REST contracts. Validate schema, size, content type, row counts, duplicates, timezone and units; provide a preview and rejection report before persistence. Record source and mapping version. Avoid PHI and credentials; quarantine uncertain data.
4. **Knowledge/RCA:** retrieve only approved, authorized, tenant-visible material. Return source IDs/snippets and retrieval scores as retrieval metadata, never calibrated confidence. Keep documents as untrusted input; do not allow document instructions to alter system policy or tools. External model processing stays disabled unless separately approved.
5. **Analysis contracts:** define provider-neutral inputs/outputs and typed failure modes (`insufficient evidence`, `feature unavailable`, `provider failure`, `candidate hypotheses`). Apply request, time and cost limits. Human review remains mandatory; no equipment commands or safety-critical action.
6. **Reliability metrics:** begin with transparent descriptive statistics and recurrence summaries over validated data. Require data completeness checks and time-window definitions before metrics such as MTTR. Keep an uncalibrated triage heuristic clearly distinct from failure probability.
7. **Audit/observability:** emit metadata-only audit events with actor, tenant, action, resource ID, source/model/config versions and outcome. Keep sensitive narratives, credentials and raw payloads out of general logs. Add readiness probes for dependencies, latency/error metrics and alerts.
8. **Interoperability:** use manual import first. Evaluate HL7 FHIR `Device`, `Provenance` and `AuditEvent` where a concrete client integration requires them; use DICOMweb only for explicitly authorized imaging workflows. Do not assume a vendor exposes open APIs.
9. **Client apps:** after server-side tenancy and auth are proven, make web and mobile consume the same authorized API contract. Replace static mobile dashboard/equipment lists with explicit loading, empty, error and live states; visibly label any demo dataset.

## Release gates

- Tenant boundary demonstrated in tests for every customer-owned table and blob path.
- Migration tested on disposable PostgreSQL against a copy of representative synthetic legacy data; backup/restore evidence recorded before any production schema change.
- Security and privacy review for imports, retention, access, exports and external providers.
- Evaluation suite has fixed synthetic cases and manually adjudicated authorized samples before any predictive claim.
- Rollback plan and production approval are separate from code merge.

## External standards and references

- HL7 FHIR R4 Device: https://www.hl7.org/fhir/R4/device.html
- HL7 FHIR R4 Provenance: https://www.hl7.org/fhir/R4/provenance.html
- HL7 FHIR R4 AuditEvent: https://www.hl7.org/fhir/R4/auditevent.html
- DICOMweb overview: https://www.dicomstandard.org/using/dicomweb
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- NIST Generative AI Profile (AI 600-1): https://doi.org/10.6028/NIST.AI.600-1

These are references for design, not proof of conformance or certification.
