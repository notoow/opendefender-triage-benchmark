# Release Manifest

| Field | Value |
| --- | --- |
| Dataset name | OpenDefender Triage Benchmark |
| Dataset version | 0.1.0 |
| Dataset path | `data/sample_alerts.jsonl` |
| Case count | 20 |
| First case ID | odtb-0001 |
| Last case ID | odtb-0020 |

## Category Counts

| Category | Count |
| --- | ---: |
| cloud | 4 |
| collaboration | 2 |
| email | 3 |
| endpoint | 5 |
| identity | 4 |
| network | 2 |

## Severity Counts

| Severity | Count |
| --- | ---: |
| informational | 1 |
| low | 7 |
| medium | 8 |
| high | 3 |
| critical | 1 |

## Confidence Counts

| Confidence | Count |
| --- | ---: |
| low | 1 |
| medium | 15 |
| high | 4 |

## Artifact Hashes

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `DATASET_VERSION` | 6 | `e9dd8507f4bf0c6f42458e41aea833ad0bd3f6127272335eee9bf4d58541ed67` |
| `data/sample_alerts.jsonl` | 17598 | `7c8f0f66eeb8628e300292ac3f2ccda95e955e2d1853b49567e33dda41386d02` |
| `schemas/alert_case.schema.json` | 2667 | `a61fbd11bc7dc417184fa8d7c6e43cf1bc4d2086aaf676f54f9a12572f83da99` |
| `evaluation/output_schema.json` | 1292 | `399be156a31d4485a3d0ce1707586f37a5f321d3c991257b9e8375936208c299` |
| `evaluation/rubric.md` | 2648 | `0f1c316778d28283bac3872cb2102b1a438f22eb6487d4ccf81ca7b3e723d7d3` |
| `evaluation/prompt_template.md` | 1248 | `329f163959955e91424de4e5f973db3cd30b84bb44f5dd16f44ca2b874b8a7eb` |

Regenerate with:

```bash
python scripts/generate_release_manifest.py --output-json docs/release_manifest.json --output-md docs/release_manifest.md
```
