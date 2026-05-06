# Dataset Quality Report

Source: `data/sample_alerts.jsonl`

This report is generated from dataset quality gates. Regenerate it with:

```bash
python scripts/check_dataset_quality.py data/sample_alerts.jsonl --output docs/dataset_quality.md
```

## Overview

| Metric | Value |
| --- | ---: |
| Total checks | 17 |
| Passed checks | 17 |
| Failed checks | 0 |
| Cases | 20 |
| Categories | 6 |

## Quality Gates

| Gate | Status | Detail |
| --- | --- | --- |
| Minimum case count | pass | 20 cases; minimum 20 |
| Category breadth | pass | 6 categories; minimum 5 |
| Minimum cases per category | pass | cloud=4, collaboration=2, email=3, endpoint=5, identity=4, network=2 |
| Largest category share | pass | 25%; maximum 35% |
| Severity label coverage | pass | informational=1, low=7, medium=8, high=3, critical=1 |
| Low and informational coverage | pass | 8 cases; minimum 4 |
| High and critical coverage | pass | 4 cases; minimum 3 |
| Confidence label coverage | pass | low=1, medium=15, high=4 |
| Difficulty label coverage | pass | easy=3, medium=10, hard=7 |
| Known-change contrast | pass | absent=11, present=9 |
| Failure-mode breadth | pass | 11 unique failure modes; minimum 8 |
| Per-case tag depth | pass | all cases have enough tags |
| Per-case failure-mode labels | pass | all cases have failure-mode labels |
| Per-case evidence depth | pass | all cases have enough key evidence |
| Per-case missing-information prompts | pass | all cases identify missing information |
| Per-case safe-action depth | pass | all cases have enough safe actions |
| Sensitive token scan | pass | no sensitive-token patterns detected |

## Snapshot

| Distribution | Values |
| --- | --- |
| Category | cloud=4, collaboration=2, email=3, endpoint=5, identity=4, network=2 |
| Severity | informational=1, low=7, medium=8, high=3, critical=1 |
| Difficulty | easy=3, medium=10, hard=7 |

## Notes

- These gates are deliberately lightweight and deterministic so they can run in CI.
- Passing this report does not mean the dataset is complete; it means the public sample keeps minimum breadth, balance, and safety checks.
- New cases should preserve defensive-only scope and avoid real logs, personal data, secrets, and operationally harmful instructions.
