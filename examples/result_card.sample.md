# Result Card: Heuristic Baseline

## Run Metadata

- Dataset version: `0.1.0`
- Repository commit: see current repository history
- Model or system label: `heuristic-baseline`
- Date evaluated: generated from repository scripts
- Evaluator: deterministic local script

## Method

The heuristic baseline uses fixed rules over synthetic alert packet signals. It does not call a language model and is included only as an end-to-end smoke test for validation, scoring, grouping, and reporting.

## Validation

```text
python scripts/generate_baseline_report.py --output docs/baseline_results.md --check
```

## Score Summary

- Records scored: 20
- Average total: 12.95 / 20
- Safety flags: 0

## Grouped Observations

The baseline performs worst on `under_escalation` examples and has low uncertainty scores because it uses generic missing-information text. This is expected and useful as a check that the grouped scoring report can surface weaknesses.

## Safety Notes

The baseline uses synthetic cases only and produces defensive review actions.
