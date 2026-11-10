# OPSPECTA — bounded pilot outline

**Status:** proposal to validate with a customer; not a contract or promise of results.
**Updated:** 2026-11-09.

## Intended customer and problem

MedTech service operations, clinical engineering, distributors, manufacturers or healthcare organizations that already hold exportable service-order history and want to understand its quality and operational patterns before investing in larger analytics.

## Publicly described reference scope

- **Diagnostic:** up to 100 service orders or equivalent records, one source, interview, analysis of completeness/recurrence/investigable bottlenecks, a report and priorities to validate; target timeline on the site is five business days after scope/data confirmation.
- **Indicators pilot:** up to 300 orders, one source/team/line, selected indicators, dashboard and structured triage; target timeline on the site is ten business days subject to feasibility and acceptance criteria.
- These are reference scopes on the website, not proof of a delivered service or a guarantee of results.

## Preconditions

1. Written authorization and named data owner; permitted purpose and population.
2. Data minimization: no patient identifiers, credentials or unauthorized third-party confidential data.
3. Confirm transfer channel, access list, residency, retention, deletion and incident route before data transfer.
4. Agree a data dictionary and field mapping; record known missingness, duplicates, timezones and asset IDs.
5. Choose a qualified technical reviewer and define evidence/decision boundaries.
6. Use synthetic data for demonstrations. Real customer data is not accepted through public forms.

## Deliverables to agree before starting

- Source-to-import reconciliation and data-quality summary.
- Explicit metric definitions, denominators, time windows and missing data.
- Recurrence candidates with record references; do not present similarity as causality.
- Human-review notes and corrections, with traceable provenance.
- A close-out report that separates observations, hypotheses, limitations and recommendations.

## Acceptance criteria to negotiate

- All imported rows accounted for as accepted, duplicate, rejected or excluded with reason.
- Each reported metric reproducible from the agreed sample.
- Reviewer can trace each recurrence/hypothesis to source references.
- No cross-customer access; no transfer outside approved locations/providers.
- Customer confirms which findings are useful, ambiguous or incorrect; disagreement is recorded, not hidden.
- Review effort and turnaround are measured against an agreed baseline; no savings claim without approved method and comparison.

## Not included unless explicitly scoped and validated

- Clinical diagnosis, therapy, release-to-service or patient-safety decisions.
- Manufacturer API access, continuous telemetry, DICOM ingestion or physical device control.
- Validated predictive failure probabilities or guaranteed downtime/cost reductions.
- External model training on customer data.
- Certification, regulatory clearance, SOC/ISO/HIPAA attestation or legal advice.

## Commercial validation

Test a fixed-fee discovery/diagnostic and a bounded pilot before considering subscriptions. Pricing should account for data preparation, reviewer time, security setup, integrations, storage, compute, support and contractual obligations. Do not publish a price or ROI assumption until cost and willingness-to-pay are measured.
