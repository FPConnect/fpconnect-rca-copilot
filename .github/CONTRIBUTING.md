# Contributing to OPSPECTA

Thank you for considering a contribution to evidence-led MedTech service intelligence.

## Scope

Contributions should improve source-code quality, reproducible research, documentation, accessibility and the safety and reliability of assistive technical workflows. No customer-specific or clinical information belongs in this public repository.

## Pull-request checklist

- [ ] Describe the problem and intended outcome with an issue or reproducible scenario.
- [ ] Add regression tests and include actual commands/results; do not claim CI passed without checking it.
- [ ] Label any artificial data prominently. Supply script, seed, schema and limitations.
- [ ] Avoid invented customer results, patient data, vendor intellectual property and medical safety instructions.
- [ ] Protect authentication, authorization and cross-customer separation; test negative cases.
- [ ] Keep analysis as reviewable *hypotheses*, not definitive repair orders or medical advice.
- [ ] Explain deployment risk, migration/rollback needs and compatibility with historical FPConnect identifiers.
- [ ] Add accessible documentation in English where the change is intended for global readers.

## Developer setup

See the [README](../README.md) for API/web/mobile setup and test commands. Before running any tests that modify data, use an isolated development database. Never use production credentials.

## Reporting security issues

Refer to [SECURITY.md](SECURITY.md), rather than a public issue.
