# OpenDefender Triage Benchmark

OpenDefender Triage Benchmark is a defensive security evaluation project for measuring how well language models handle security alert triage.

The benchmark focuses on a narrow, practical question: given a realistic alert packet, can a model classify the alert, cite the evidence it used, recognize missing information, calibrate severity, and recommend safe next defensive actions?

## Goals

- Provide synthetic, non-sensitive alert examples for reproducible evaluation.
- Measure evidence grounding, uncertainty handling, severity calibration, and operational usefulness.
- Keep all scenarios defensive and public-benefit oriented.
- Avoid confidential data, personal data, secrets, exploit instructions, and offensive playbooks.

## Repository Contents

- `data/sample_alerts.jsonl` - sample alert packets and expected triage metadata.
- `DATASET_VERSION` - current dataset version.
- `CHANGELOG.md` - version history.
- `data/README.md` - dataset format, scope, and safety notes.
- `docs/dataset_card.md` - dataset card with intended use, limitations, and safety notes.
- `docs/dataset_summary.md` - generated summary of category, severity, and confidence coverage.
- `docs/dataset_quality.md` - generated dataset quality-gate report.
- `docs/baseline_results.md` - generated heuristic baseline results report.
- `docs/release_manifest.md` - generated release manifest with artifact hashes.
- `docs/release_manifest.json` - machine-readable release manifest.
- `docs/submitting_results.md` - guidance for sharing reproducible benchmark results.
- `docs/result_card_template.md` - template for public result summaries.
- `examples/README.md` - example artifact descriptions.
- `examples/model_outputs.sample.jsonl` - example model-output records for evaluation runs.
- `examples/result_card.sample.md` - sample result card for the heuristic baseline.
- `evaluation/README.md` - evaluation run format and workflow.
- `evaluation/rubric.md` - draft scoring rubric for model triage outputs.
- `evaluation/output_schema.json` - expected model response shape for structured evaluations.
- `evaluation/prompt_template.md` - defensive triage prompt template for baseline runs.
- `schemas/alert_case.schema.json` - JSON Schema for alert case records.
- `scripts/generate_baseline_report.py` - generated heuristic baseline report.
- `scripts/make_prompt_batch.py` - prompt batch generator for benchmark runs.
- `scripts/generate_release_manifest.py` - deterministic release manifest generator.
- `scripts/check_dataset_quality.py` - deterministic dataset quality-gate checker.
- `scripts/run_heuristic_baseline.py` - deterministic baseline runner for smoke tests.
- `scripts/summarize_dataset.py` - generated dataset coverage summary.
- `scripts/validate_dataset.py` - no-dependency dataset validation script.
- `scripts/validate_model_outputs.py` - no-dependency model-output validation script.
- `scripts/score_model_outputs.py` - lightweight reference scorer for model outputs.
- `tests/` - stdlib unit tests for the validation and scoring scripts.

## Evaluation Scope

The current scope covers compact alert packets across:

- Identity alerts
- Endpoint alerts
- Cloud audit alerts
- Email and collaboration alerts
- Benign administrative activity
- Ambiguous cases that require more context

Each example is designed to test whether a model can distinguish evidence from speculation and recommend proportionate defensive review steps.

Cases include evaluation metadata for difficulty, coverage tags, and target failure modes such as over-escalation, under-escalation, missing-context handling, evidence grounding, and safe action scoping.

## Validation

Validate the sample dataset with:

```bash
python scripts/validate_dataset.py data/sample_alerts.jsonl
```

The validator checks JSONL parsing, required fields, duplicate IDs, controlled severity and confidence labels, and basic schema consistency.

Regenerate the dataset summary:

```bash
python scripts/summarize_dataset.py data/sample_alerts.jsonl --output docs/dataset_summary.md
```

Regenerate the dataset quality report:

```bash
python scripts/check_dataset_quality.py data/sample_alerts.jsonl --output docs/dataset_quality.md
```

Regenerate the release manifest:

```bash
python scripts/generate_release_manifest.py --output-json docs/release_manifest.json --output-md docs/release_manifest.md
```

Regenerate the committed heuristic baseline report:

```bash
python scripts/generate_baseline_report.py --output docs/baseline_results.md
```

Run unit tests:

```bash
python -m unittest discover -s tests
```

Build a prompt batch from the dataset:

```bash
python scripts/make_prompt_batch.py data/sample_alerts.jsonl --output .tmp/prompt_batch.jsonl
```

Run the deterministic baseline:

```bash
python scripts/run_heuristic_baseline.py data/sample_alerts.jsonl --output .tmp/heuristic_outputs.jsonl
```

Validate model output records with:

```bash
python scripts/validate_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl
```

Score sample model output records with:

```bash
python scripts/score_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl
```

The score report includes per-case scores plus grouped averages by category, difficulty, and target failure mode.

Write a Markdown score report:

```bash
python scripts/score_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl --markdown .tmp/score_report.md
```

## Safety Boundaries

This project does not include:

- Exploit code
- Malware samples
- Credential theft guidance
- Persistence or evasion instructions
- Real customer logs
- Personal data or confidential incident data

## Licensing

- Dataset: CC BY 4.0
- Evaluation schemas, scripts, and templates: MIT License
- Documentation and reports: CC BY 4.0

See `LICENSE.md` for the repository license policy.

## Contributing

See `CONTRIBUTING.md` before proposing new cases. Contributions should use synthetic examples, follow the schema, and preserve the defensive-only scope.

For sharing benchmark runs, see `docs/submitting_results.md` and `docs/result_card_template.md`.
