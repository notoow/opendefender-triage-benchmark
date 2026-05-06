# Examples

This directory contains small example artifacts for exercising the validation and scoring scripts.

## Files

- `model_outputs.sample.jsonl` - sample structured model-output records for two benchmark cases.
- `result_card.sample.md` - sample public result card for the deterministic heuristic baseline.

## Generate Prompt Inputs

Prompt batches are generated rather than committed:

```bash
python scripts/make_prompt_batch.py data/sample_alerts.jsonl --output .tmp/prompt_batch.jsonl
```

The generated prompt batch can be used with any evaluation runner that returns records matching `evaluation/output_schema.json`.
