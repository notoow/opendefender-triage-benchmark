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
2. Run `python scripts/summarize_dataset.py data/sample_alerts.jsonl --output docs/dataset_summary.md --check`.
3. Run `python scripts/check_dataset_quality.py data/sample_alerts.jsonl --output docs/dataset_quality.md --check`.
4. Run `python scripts/generate_reviewer_notes.py data/sample_alerts.jsonl --output docs/reviewer_notes.md --check`.
5. Run `python scripts/validate_run_config.py examples/run_config.sample.json`.
6. Run `python scripts/generate_baseline_report.py --output docs/baseline_results.md --check`.
7. Run `python scripts/generate_result_card.py --output docs/baseline_result_card.md --check`.
8. Run `python scripts/generate_release_manifest.py --output-json docs/release_manifest.json --output-md docs/release_manifest.md --check`.
9. Confirm each case has a clear defensive purpose.
10. Confirm recommended actions are proportionate and reviewable by a human analyst.
11. Confirm labels do not depend on facts outside the alert packet.

## Label Guidance

Use `severity` to describe potential operational risk based on the available evidence. Use `confidence` to describe how strongly the alert packet supports the expected classification.

Do not use high confidence when important context is missing.

## Result Submissions

Use `docs/submitting_results.md` for benchmark run submissions. Public results should include the dataset version, repository commit, model or system label, validation command, score report, and any notable safety or failure-mode observations.

Use `docs/result_card_template.md` for concise public summaries.
