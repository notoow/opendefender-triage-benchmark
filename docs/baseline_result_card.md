# Result Card: heuristic-baseline

## Run Metadata

- Run ID: `heuristic-baseline-sample`
- Dataset version: `0.1.0`
- Repository commit: `local`
- Model or system label: `heuristic-baseline`
- Model class: `deterministic_heuristic`
- Prompt template: `evaluation/prompt_template.md`
- Output schema: `evaluation/output_schema.json`

## Method

This card is generated from a validated run config and scored output records. For deterministic heuristic runs, outputs are produced locally from fixed rules over synthetic alert packets.

Generation settings:

- Temperature: `0`
- Max output tokens: `800`
- Structured output: `true`

## Validation

```text
python scripts/validate_run_config.py path/to/run_config.json
python scripts/validate_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl
python scripts/score_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl --markdown path/to/score_report.md
```

## Score Summary

- Records scored: 20
- Average total: 12.95 / 20
- Safety flags: 0

## Grouped Observations

- Lowest difficulty group: `hard` at 12.29 / 20.
- Lowest failure-mode group: `under_escalation` at 11.75 / 20.
- Grouped scores should be interpreted with reviewer notes for ambiguous and benign cases.

### Scores by Difficulty

| Group | Count | Avg Total | Avg Evidence | Avg Uncertainty | Safety Flags |
| --- | ---: | ---: | ---: | ---: | ---: |
| easy | 3 | 13.00 | 3.00 | 0.00 | 0 |
| medium | 10 | 13.40 | 3.30 | 0.10 | 0 |
| hard | 7 | 12.29 | 3.00 | 0.29 | 0 |

### Scores by Failure Mode

| Group | Count | Avg Total | Avg Evidence | Avg Uncertainty | Safety Flags |
| --- | ---: | ---: | ---: | ---: | ---: |
| access_review_reasoning | 1 | 12.00 | 2.00 | 0.00 | 0 |
| benign_context | 3 | 13.00 | 3.33 | 0.00 | 0 |
| change_ticket_reasoning | 3 | 12.67 | 3.33 | 0.33 | 0 |
| confidence_calibration | 4 | 13.00 | 3.25 | 0.50 | 0 |
| data_exposure_reasoning | 1 | 13.00 | 4.00 | 0.00 | 0 |
| evidence_grounding | 9 | 13.11 | 3.11 | 0.22 | 0 |
| missing_context_handling | 6 | 13.33 | 3.33 | 0.17 | 0 |
| over_escalation | 8 | 12.75 | 3.12 | 0.12 | 0 |
| safe_action_scoping | 7 | 12.86 | 3.00 | 0.14 | 0 |
| severity_calibration | 2 | 13.00 | 3.50 | 0.00 | 0 |
| under_escalation | 4 | 11.75 | 2.50 | 0.00 | 0 |

## Qualitative Notes

The deterministic heuristic baseline is intentionally limited: it is useful for pipeline smoke tests, but it has weak uncertainty handling and should not be read as language-model performance.

## Safety Notes

- Safety reviewed: `true`
- Safety review notes: Outputs contain defensive triage labels only and are checked by the scorer safety flag.
- Shared artifacts should contain no personal data, secrets, proprietary logs, or harmful operational details.
