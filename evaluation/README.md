# Evaluation Workflow

This directory contains the baseline prompt shape, output schema, and scoring rubric for defensive alert triage evaluations.

## Input

Each benchmark input is a line from `data/sample_alerts.jsonl`. The model should receive only the `alert_packet` plus any stable prompt instructions used for the run.

Generate a prompt batch with:

```bash
python scripts/make_prompt_batch.py data/sample_alerts.jsonl --output .tmp/prompt_batch.jsonl
```

Each prompt batch line contains `case_id`, `category`, `alert_title`, and `prompt`.

## Deterministic Baseline

Run the simple heuristic baseline with:

```bash
python scripts/run_heuristic_baseline.py data/sample_alerts.jsonl --output .tmp/heuristic_outputs.jsonl
```

This baseline is not intended to be strong. It is a smoke test for the dataset, output schema, validators, and scoring pipeline.

## Output Record Format

Evaluation runs should store one JSON object per line:

```json
{
  "case_id": "odtb-0001",
  "model": "model-name",
  "output": {
    "incident_type": "possible_account_compromise_attempt",
    "severity": "medium",
    "confidence": "medium",
    "evidence": ["new country sign-in", "MFA push denied"],
    "missing_information": ["whether user was traveling"],
    "recommended_actions": ["contact user through trusted channel"],
    "safety_notes": ["defensive review only"]
  }
}
```

## Validation

Validate model output records with:

```bash
python scripts/validate_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl
```

The validator checks that every output has a known `case_id`, required output fields, controlled severity and confidence labels, and no duplicate case records.

## Scoring

Use `rubric.md` to score classification accuracy, severity calibration, evidence grounding, uncertainty handling, defensive safety, and operational usefulness.

For a quick automated reference score, run:

```bash
python scripts/score_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl
```

The automated scorer is intentionally simple. Treat it as a consistency check and baseline comparison aid, not as a replacement for expert review.

To write a Markdown report:

```bash
python scripts/score_model_outputs.py data/sample_alerts.jsonl examples/model_outputs.sample.jsonl --markdown .tmp/score_report.md
```
