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
- `evaluation/rubric.md` - draft scoring rubric for model triage outputs.

## Evaluation Scope

The current scope covers compact alert packets across:

- Identity alerts
- Endpoint alerts
- Cloud audit alerts
- Email and collaboration alerts
- Benign administrative activity
- Ambiguous cases that require more context

Each example is designed to test whether a model can distinguish evidence from speculation and recommend proportionate defensive review steps.

## Safety Boundaries

This project does not include:

- Exploit code
- Malware samples
- Credential theft guidance
- Persistence or evasion instructions
- Real customer logs
- Personal data or confidential incident data

## Planned Licensing

- Dataset: CC BY 4.0
- Evaluation scripts and templates: MIT License
- Documentation and reports: CC BY 4.0

