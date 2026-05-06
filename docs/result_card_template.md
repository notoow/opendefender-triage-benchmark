# Result Card Template

## Run Metadata

- Dataset version:
- Repository commit:
- Model or system label:
- Date evaluated:
- Evaluator:

## Method

Describe the prompt, structured-output format, model settings, retrieval or policy context, and any routing or post-processing.

## Validation

```text
python scripts/validate_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl
```

## Score Summary

- Records scored:
- Average total:
- Safety flags:

## Grouped Observations

Summarize notable results by:

- Category
- Difficulty
- Failure mode

## Qualitative Notes

Describe recurring strengths, recurring failures, calibration issues, missing-context behavior, unsafe or overly broad actions, and examples that need human review.

## Safety Notes

Confirm that shared artifacts contain no personal data, secrets, proprietary logs, or harmful operational details.
