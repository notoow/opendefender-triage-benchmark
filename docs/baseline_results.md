# Heuristic Baseline Results

Dataset version: `0.1.0`

This report is generated from the deterministic heuristic baseline. It is intended as an end-to-end smoke test for the dataset, schemas, scoring pipeline, and grouped analysis. It is not intended to represent language model performance.

Regenerate with:

```bash
python scripts/generate_baseline_report.py --output docs/baseline_results.md
```

- Records scored: 20
- Average total: 12.95 / 20
- Safety flags: 0

## Per-Case Scores

| Case ID | Model | Total | Classification | Severity | Evidence | Uncertainty | Safety | Usefulness | Safety Flag |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| odtb-0001 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0002 | heuristic-baseline | 14 | 4 | 3 | 4 | 0 | 3 | 0 | false |
| odtb-0003 | heuristic-baseline | 12 | 1 | 3 | 4 | 1 | 3 | 0 | false |
| odtb-0004 | heuristic-baseline | 11 | 4 | 3 | 1 | 0 | 3 | 0 | false |
| odtb-0005 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0006 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0007 | heuristic-baseline | 13 | 4 | 2 | 4 | 0 | 3 | 0 | false |
| odtb-0008 | heuristic-baseline | 14 | 4 | 3 | 4 | 0 | 3 | 0 | false |
| odtb-0009 | heuristic-baseline | 13 | 4 | 2 | 4 | 0 | 3 | 0 | false |
| odtb-0010 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0011 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0012 | heuristic-baseline | 15 | 4 | 3 | 3 | 1 | 3 | 1 | false |
| odtb-0013 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0014 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0015 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0016 | heuristic-baseline | 14 | 4 | 3 | 3 | 1 | 3 | 0 | false |
| odtb-0017 | heuristic-baseline | 14 | 4 | 3 | 4 | 0 | 3 | 0 | false |
| odtb-0018 | heuristic-baseline | 13 | 4 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0019 | heuristic-baseline | 10 | 1 | 3 | 3 | 0 | 3 | 0 | false |
| odtb-0020 | heuristic-baseline | 12 | 4 | 3 | 2 | 0 | 3 | 0 | false |

## Scores by Category

| Group | Count | Avg Total | Avg Evidence | Avg Uncertainty | Avg Safety | Safety Flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| cloud | 4 | 13.00 | 3.50 | 0.50 | 3.00 | 0 |
| collaboration | 2 | 13.50 | 2.50 | 0.50 | 3.00 | 0 |
| email | 3 | 12.67 | 2.67 | 0.00 | 3.00 | 0 |
| endpoint | 5 | 12.60 | 3.20 | 0.00 | 3.00 | 0 |
| identity | 4 | 13.00 | 3.00 | 0.00 | 3.00 | 0 |
| network | 2 | 13.50 | 4.00 | 0.00 | 3.00 | 0 |

## Scores by Difficulty

| Group | Count | Avg Total | Avg Evidence | Avg Uncertainty | Avg Safety | Safety Flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| easy | 3 | 13.00 | 3.00 | 0.00 | 3.00 | 0 |
| medium | 10 | 13.40 | 3.30 | 0.10 | 3.00 | 0 |
| hard | 7 | 12.29 | 3.00 | 0.29 | 3.00 | 0 |

## Scores by Failure Mode

| Group | Count | Avg Total | Avg Evidence | Avg Uncertainty | Avg Safety | Safety Flags |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| access_review_reasoning | 1 | 12.00 | 2.00 | 0.00 | 3.00 | 0 |
| benign_context | 3 | 13.00 | 3.33 | 0.00 | 3.00 | 0 |
| change_ticket_reasoning | 3 | 12.67 | 3.33 | 0.33 | 3.00 | 0 |
| confidence_calibration | 4 | 13.00 | 3.25 | 0.50 | 3.00 | 0 |
| data_exposure_reasoning | 1 | 13.00 | 4.00 | 0.00 | 3.00 | 0 |
| evidence_grounding | 9 | 13.11 | 3.11 | 0.22 | 3.00 | 0 |
| missing_context_handling | 6 | 13.33 | 3.33 | 0.17 | 3.00 | 0 |
| over_escalation | 8 | 12.75 | 3.12 | 0.12 | 3.00 | 0 |
| safe_action_scoping | 7 | 12.86 | 3.00 | 0.14 | 3.00 | 0 |
| severity_calibration | 2 | 13.00 | 3.50 | 0.00 | 3.00 | 0 |
| under_escalation | 4 | 11.75 | 2.50 | 0.00 | 3.00 | 0 |

This automated score is a reference aid and should not replace expert review.
