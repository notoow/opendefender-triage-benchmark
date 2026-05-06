# Summary

Describe the dataset, evaluation, or documentation change.

# Safety Checklist

- [ ] No personal data, secrets, credentials, or real customer logs.
- [ ] No exploit code, offensive instructions, persistence steps, or evasion steps.
- [ ] Recommended actions are defensive and proportionate.
- [ ] Labels are supported by evidence in the alert packet.
- [ ] Dataset validation passes.

# Validation

```text
python scripts/validate_dataset.py data/sample_alerts.jsonl
python scripts/validate_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl
python scripts/score_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl
```
