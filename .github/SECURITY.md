# Security policy — OPSPECTA

## Scope and supported status

OPSPECTA is an early-stage research and product-development repository. The public source code does **not** prove HIPAA, LGPD, GDPR, IEC 62304, ISO 13485, ISO 27001, SOC 2 or medical-device certification. No safety-critical or clinical use should be inferred.

## Report a vulnerability privately

Please **do not publish vulnerabilities, tokens, sensitive logs, patient records or exploit steps in a public issue**. Contact the maintainers privately via the repository owner's contact channel or GitHub private vulnerability reporting if enabled in the repository's Security settings. Availability of that GitHub feature is not asserted.

Include only a minimal non-sensitive description of the problem, affected version/commit, reproduction in a **test environment**, impact and suggested mitigation. Do not test against real healthcare systems, production accounts or third parties without written authorization.

## Release and deployment principles

- No patient data in public demos, tests or incident reports.
- Never commit credentials, patient records, unlicensed manufacturer material or customer logs.
- API-side authorization and organization isolation must be tested before multi-customer processing.
- Human review is mandatory for technical RCA conclusions; synthetic data results must be labelled.
- Roll back and restrict access if authorization, data exposure or unauthorized actions are discovered.
- Coordinate any security-impacting change with code review, tests and migration/rollback plans.

See [OPSPECTA trust dossier](../docs/HEALTHTECH_TRUST.md) and [responsible AI documentation](../docs/security/OPSPECTA_RESPONSIBLE_AI_2026.md).

**No SLA or guaranteed response time is established by this document.**
