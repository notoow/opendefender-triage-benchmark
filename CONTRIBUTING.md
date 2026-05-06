# Contributing

Contributions are welcome when they improve defensive evaluation quality and keep the dataset safe to publish.

## Case Requirements

New alert cases should:

- Be synthetic or fully de-identified.
- Avoid personal data, secrets, credentials, tokens, and real customer logs.
- Avoid exploit code, offensive instructions, persistence steps, evasion steps, or credential theft guidance.
- Include enough context for an analyst to understand the expected triage label.
- Include realistic uncertainty when an alert packet is incomplete.
- Follow `schemas/alert_case.schema.json`.

## Review Checklist

Before submitting changes:

1. Run `python scripts/validate_dataset.py data/sample_alerts.jsonl`.
2. Confirm each case has a clear defensive purpose.
3. Confirm recommended actions are proportionate and reviewable by a human analyst.
4. Confirm labels do not depend on facts outside the alert packet.

## Label Guidance

Use `severity` to describe potential operational risk based on the available evidence. Use `confidence` to describe how strongly the alert packet supports the expected classification.

Do not use high confidence when important context is missing.
