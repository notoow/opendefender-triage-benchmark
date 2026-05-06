# Baseline Runs

This guide describes reproducible evaluation runs across model and system classes. It is intended to make benchmark comparisons easier to repeat and review.

## Model Classes

Use one of these labels in run configs:

| Model class | Intended use |
| --- | --- |
| `deterministic_heuristic` | Local deterministic smoke tests for the validation and scoring pipeline. |
| `small_general_model` | Lower-cost general language model runs used for quick regression checks. |
| `large_reasoning_model` | Higher-capability model runs used for deeper triage and uncertainty tests. |
| `local_open_weight_model` | Locally hosted or self-managed models where reproducibility depends on runtime details. |
| `tool_assisted_workflow` | Systems that combine a model with retrieval, rules, or analyst workflow helpers. |
| `other` | Runs that do not fit the classes above. |

## Run Config

Each comparable run should have a config matching `evaluation/run_config.schema.json`. The sample config is `examples/run_config.sample.json`.

Validate the sample config with:

```bash
python scripts/validate_run_config.py examples/run_config.sample.json
```

Recommended fields:

- `run_id`: stable lowercase identifier for the run.
- `dataset_version`: version from `DATASET_VERSION`.
- `repo_commit`: commit SHA used for the run, or `local` for unpublished local smoke tests.
- `model_label`: short public model or system label.
- `model_class`: one of the model classes above.
- `prompt_template_path`: prompt template used to create the prompt batch.
- `output_schema_path`: structured output schema expected from the run.
- `generation`: generation settings that affect reproducibility.
- `case_selection`: `all` or an explicit case ID list.
- `output_path`: JSONL output record path.
- `score_report_path`: Markdown score report path.
- `safety_review`: whether outputs were reviewed for safe public sharing.

## Recommended Run Matrix

For early releases, a useful run matrix is small:

| Run | Purpose | Required artifact |
| --- | --- | --- |
| Deterministic heuristic | Checks the pipeline and score report generation. | Output JSONL and score report. |
| Small general model | Catches obvious prompt or schema regressions quickly. | Run config, output JSONL, score report, result card. |
| Large reasoning model | Tests difficult, ambiguous, and known-change cases. | Run config, output JSONL or safe summary, score report, result card. |
| Local open-weight model | Provides a reproducible non-hosted comparison when runtime details are documented. | Run config, runtime notes, output JSONL or safe summary. |

## Workflow

1. Generate prompts:

```bash
python scripts/make_prompt_batch.py data/sample_alerts.jsonl --output .tmp/prompt_batch.jsonl
```

2. Prepare a run config:

```bash
python scripts/validate_run_config.py examples/run_config.sample.json
```

3. Run the model or system and write records matching `evaluation/output_schema.json`.

4. Validate outputs:

```bash
python scripts/validate_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl
```

5. Score outputs:

```bash
python scripts/score_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl --markdown path/to/score_report.md
```

6. Generate a result card:

```bash
python scripts/generate_result_card.py --config path/to/run_config.json --outputs path/to/model_outputs.jsonl --output path/to/result_card.md
```

7. Review `docs/reviewer_notes.md` before interpreting ambiguous, benign, or known-change cases.

8. Summarize public results with `docs/result_card_template.md` when a custom narrative is needed.

## Notes

- Keep private prompts, credentials, proprietary logs, personal data, and unsafe operational details out of public artifacts.
- Treat automated scores as a comparison aid, not a final claim of production readiness.
- Keep generation settings stable across repeated runs when comparing models.
