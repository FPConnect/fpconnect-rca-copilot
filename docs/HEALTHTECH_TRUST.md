# OPSPECTA | HealthTech engineering trust dossier

**Version:** 09 November 2026 · **Classification:** Public technical overview, not an audit or a certification.

## Product thesis

Distributed medical-technology service operations generate technical tickets, work orders and logs across different service desks and teams. OPSPECTA investigates the quality, traceability and operational interpretation of those **authorized records**. The project is **not** a device-control platform, clinical diagnostic system, clinical decision support certification, or an established predictive-maintenance product.

**Initial target:** technically authorized equipment-maintenance teams, distributors and MedTech service operations. All customer-fit hypotheses must be validated with the intended buyer. No named manufacturer/hospital is represented as a customer or partner.

## Current demonstrable assets

1. [GitHub monorepo](../README.md): Next.js web, FastAPI backend, Expo mobile prototype and engineering documentation. Do not infer deployment readiness from source-code presence.
2. [Synthetic work-order experiment](research/2026-11-python-synthetic-service-orders/README.md), with [reproducible Python generator](research/2026-11-python-synthetic-service-orders/analise_logs_sinteticos.py).
3. [Responsible AI limitations and gates](security/OPSPECTA_RESPONSIBLE_AI_2026.md).
4. [Commercial service validation hypotheses](business/OPSPECTA_SERVICE_VALIDATION_2026-11.md).

## Evidence standard — every claim needs a source

| Claim | Required evidence before publishing |
| --- | --- |
| Reduced downtime / cost | Real baseline, evaluation window, authorized dataset, metric definition and independently reviewable calculations |
| Improved incident recurrence detection | Labelled holdout set, expert adjudication, precision, recall and false-positive/false-negative analysis |
| Root-cause accuracy | Qualified technician review with cited source and ground-truth protocol |
| Enterprise security | Threat model, tested tenant isolation, data-retention and incident response, independent security assessment as appropriate |
| Clinical or regulatory compliance | Written regulatory scope determination by qualified reviewer and required approvals/certifications (where applicable) |
| Customer traction | Traceable engagement/contract evidence and permission to disclose |
| AI reliability | Clearly specified model/version, evaluation dataset, failure modes and monitoring |

**Do not label simulated metrics as field outcomes.**

## Secure handling of source data

Before accepting real records: confirm legal authority and scope; exclude patient-identifying data; contract confidentiality, permitted use, geography and retention; isolate organization data throughout API, exports, storage, caches, analytics and retrieval; restrict user access; audit access without logging sensitive payloads; define deletion and breach handling. International transfers and subcontractors need jurisdiction-specific review. Never ask customers for credentials or unrestricted device access.

Repository changes under review (especially security and tenancy) are **not delivered product capability**. Validate security changes in an isolated environment, complete migration rehearsal/rollback and obtain approval before promotion. See active pull requests and issue history.

## Roadmap — proposals, not shipped promises

- **QualiOS:** missing-field/quality audit of work orders.
- **RecurTrace:** candidate repeated incidents linked to source record IDs and human review.
- **ServiceFlow:** measurable intervals/hand-offs with stated limitations.
- **Evidence-Led RCA:** reviewable technical hypotheses, no autonomous physical interventions.
- **Service Intelligence:** aggregated reporting *after* organization isolation and privacy controls pass validation.

## How to evaluate a pilot

Agree upon one de-identified authorized dataset, 100 work orders maximum for the initial reference diagnosis, a fixed deliverable, a verification/review protocol and signed scope/pricing. Compare pre-agreed operational measures without inferring causality. Do not retain datasets beyond documented permission.

## Research and governance

Public synthetic studies are labelled as such. A GitHub technical note is not a peer-reviewed journal paper. The OPSPECTA branding is in transition from FPConnect; legal name, trademarks and third-party relationships should not be inferred from a display name.

For private security findings, contact the repository owner through a private channel; do not publish exploit details or credentials in issues.
