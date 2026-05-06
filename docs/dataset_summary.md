# Dataset Summary

Source: `data/sample_alerts.jsonl`

This summary is generated from the dataset JSONL file. Regenerate it with:

```bash
python scripts/summarize_dataset.py data/sample_alerts.jsonl --output docs/dataset_summary.md
```

## Overview

| Metric | Value |
| --- | ---: |
| Total cases | 20 |
| First case ID | odtb-0001 |
| Last case ID | odtb-0020 |
| Categories | 6 |

## Category Distribution

| Value | Count |
| --- | ---: |
| cloud | 4 |
| collaboration | 2 |
| email | 3 |
| endpoint | 5 |
| identity | 4 |
| network | 2 |

## Expected Severity Distribution

| Value | Count |
| --- | ---: |
| informational | 1 |
| low | 7 |
| medium | 8 |
| high | 3 |
| critical | 1 |

## Expected Confidence Distribution

| Value | Count |
| --- | ---: |
| low | 1 |
| medium | 15 |
| high | 4 |

## Known Change Ticket Distribution

| Value | Count |
| --- | ---: |
| absent | 11 |
| present | 9 |

## Notes

- Counts describe the current sample dataset, not a production incident distribution.
- Cases are synthetic and defensive-only.
- Low and informational examples are included so benchmarks can measure over-escalation.
- Ambiguous examples are included so benchmarks can measure uncertainty handling.
