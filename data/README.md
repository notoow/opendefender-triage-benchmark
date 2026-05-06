# Dataset

`sample_alerts.jsonl` contains 20 synthetic defensive security alert examples. Each line is one JSON object.

The sample data is intentionally compact. It is meant to illustrate the benchmark format, not to represent a complete production corpus.

See `../docs/dataset_summary.md` for generated category, severity, confidence, difficulty, failure-mode, and known-change coverage.
See `../docs/dataset_quality.md` for deterministic quality gates covering breadth, balance, per-case metadata depth, and sensitive-token scans.

## Record Format

Each alert case contains:

- `id`: stable benchmark case identifier.
- `category`: alert category such as `identity`, `endpoint`, `cloud`, or `email`.
- `alert_title`: short human-readable alert title.
- `alert_packet`: normalized alert context provided to the model.
- `expected`: reference triage metadata used for evaluation.
- `evaluation_metadata`: tags for difficulty, coverage, and target failure modes.

## Safety Rules

Dataset records should not include:

- Real customer logs
- Personal data
- Secrets, credentials, or tokens
- Malware samples
- Exploit code or exploit instructions
- Offensive playbooks

## Current Categories

- `identity`
- `endpoint`
- `cloud`
- `email`
- `collaboration`
- `network`

Additional categories should keep the same defensive-only scope and follow `schemas/alert_case.schema.json`.
