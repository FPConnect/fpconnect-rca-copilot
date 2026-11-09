# OPSPECTA — AI and analytics evaluation plan

**Assessment date:** 2026-11-09
**Status:** design and code-path review only. No customer data, validated clinical dataset, model benchmark, or external provider was used in this assessment.

## What exists

| Capability | Verified code behavior | Maturity / limitation |
|---|---|---|
| Local RCA retrieval | `apps/api/app/services/analyze_service.py` loads `paraphrase-multilingual-MiniLM-L12-v2`, queries up to three KB rows with embeddings above a fixed similarity cutoff. | Retrieval prototype; model and threshold are not calibrated for RCA quality. Current schema does not demonstrate tenant/source approval filters. |
| External LLM helper | `apps/api/app/services/rca_advanced.py` has explicit deployment/request opt-ins, common-pattern screening and draft-only output. | Guarded prototype; pattern screening is partial; no provider governance or production evaluation evidence. |
| Priority index | `apps/api/app/services/predictive.py` computes a transparent weighted heuristic, labels it unvalidated and returns no predicted failure days. | Exploratory triage only; not a predictive model or failure probability. |
| Human review | `/analyze/{ticket_id}/confirm` persists only after explicit reviewer attestation and records a metadata-only audit event. | Safety workflow exists; organizational reviewer governance and evidence truth are not independently validated. |
| Public demonstrations | Some dashboards/metrics and the public demonstration page use illustrative/synthetic data and disclose the limits. | Marketing/demo only, not a customer benchmark or live model result. |

## Evaluation datasets and cases

Start with synthetic data and authorized, minimized historical examples whose outcomes have been independently adjudicated by qualified reviewers. Keep tenant-separated evaluation fixtures. Include:

- Recurrences with the same asset vs similar symptoms on different assets.
- Missing timestamps, codes, model identifiers and interventions.
- Ambiguous/contradictory failure codes and conflicting documents.
- Unsuccessful interventions, censored histories and no-evidence cases.
- Duplicate imports, malformed rows, unit/timezone inconsistencies.
- Cross-organization retrieval and object access attempts.
- Prompt injection embedded in documents and user context.
- Invalid/missing model packages, DB outages, timeouts and provider errors.
- Cases where the safe answer is “insufficient evidence.”

Do not use synthetic labels as evidence of real-world accuracy.

## Metrics and protocol

| Component | Baselines and measurements |
|---|---|
| Data quality/import | Duplicate rate, required-field completeness, rejected-row precision, source-to-normalized reconciliation, deterministic replay. |
| Retrieval | Recall@k, MRR/nDCG on reviewer-labeled query–evidence pairs; citation/source ID fidelity; unauthorized result count (must be zero). |
| Hypothesis assistance | Blinded reviewer agreement, unsupported-claim rate, abstention rate, severity-weighted false positives/negatives; do not reduce to a single “accuracy” number. |
| Risk prioritization | Compare to transparent rules and expert baseline; temporal holdout; top-k workload yield; false alert rate, recall/coverage and calibration only if a probability model is actually trained. |
| Reliability | MTTR definition and missingness, recurrence by asset/service window, event-time leakage checks, sensitivity analyses. |
| Operations | p50/p95 latency, timeout/error rate, cost per completed analysis, audit completeness and availability. |
| Privacy/security | Cross-tenant deny rate, prompt-injection policy adherence, sensitive-data leakage tests, access-log completeness. |

Split by time and, where possible, by asset/customer to prevent leakage. Freeze code/model/configuration and dataset version. Report sample size, confidence intervals, class balance, exclusions and adjudication method. Avoid random row splits when repeated incidents from one asset can leak across train and test.

## Stop conditions

- Do not describe similarity as confidence or causality.
- No probability of failure or days-to-failure claim without reliable labels, temporal evaluation, calibration and approval.
- Do not send customer data to an external model without explicit contract, privacy/security review, tenant controls and authorization.
- Do not let agents execute equipment commands, modify safety settings or turn hypotheses into maintenance instructions.
- If intended use shifts toward clinical diagnosis/treatment or safety-critical recommendations, pause release for specialist regulatory review.

## References

- NIST AI RMF (voluntary): https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Generative AI Profile (AI 600-1, 2024): https://doi.org/10.6028/NIST.AI.600-1
- NIST SP 800-226, differential privacy evaluation (2025): https://doi.org/10.6028/NIST.SP.800-226
- OWASP GenAI Security Project: https://genai.owasp.org/llm-top-10/

## Results actually measured in this assessment

- API test suite after the error-handling change: **67 passed**.
- Ruff on modified API files: passed.
- No retrieval-quality, prediction-quality, bias, privacy-risk or customer outcome metric was measured.
