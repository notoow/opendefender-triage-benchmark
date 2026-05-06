# Dataset Card

## Dataset Name

OpenDefender Triage Benchmark

## Summary

This dataset contains synthetic defensive security alert cases for evaluating language model behavior in alert triage tasks. Each case provides a compact alert packet and reference triage metadata.

The dataset is designed to test whether a model can identify likely incident type, calibrate severity and confidence, cite relevant evidence, recognize missing information, and recommend safe defensive next actions.

## Intended Use

Appropriate uses include:

- Evaluating defensive security alert triage responses.
- Testing evidence grounding and uncertainty handling.
- Comparing structured model outputs across prompt or model variants.
- Developing safer evaluation practices for security operations support.

## Out-of-Scope Use

The dataset is not intended for:

- Offensive security training.
- Exploit development.
- Automated containment decisions without human review.
- Production incident classification without additional validation.

## Data Composition

Each JSONL record includes:

- A stable case ID.
- A high-level alert category.
- A normalized alert packet.
- Reference labels for expected triage behavior.
- Safe defensive next actions.
- Evaluation metadata for difficulty, coverage tags, and target model failure modes.

The initial sample covers identity, endpoint, cloud, email, collaboration, and network alerts. Future versions may include additional benign, ambiguous, and reviewer-challenging cases.

See `dataset_summary.md` for generated coverage counts.

See `release_manifest.md` for the current dataset version and artifact hashes.

## Data Collection and Creation

The sample records are synthetic. They are written to resemble common defensive alert patterns without using real customer logs, personal data, secrets, credentials, or proprietary incident material.

## Labeling

Reference labels are intended to support evaluation, not to replace human analyst judgment. Labels should be reviewed for:

- Correctness of incident type.
- Severity calibration.
- Confidence calibration.
- Evidence support.
- Missing-information notes.
- Safety of recommended actions.

## Known Limitations

- The current dataset is small and illustrative.
- Synthetic cases may not capture the full messiness of production environments.
- Labels are reference judgments and may need review by multiple analysts for larger releases.
- The benchmark does not measure live tool use, containment execution, or long-running incident response.

## Safety and Privacy

Records should not contain:

- Personal data
- Real customer logs
- Secrets or credentials
- Malware samples
- Exploit code
- Offensive playbooks

Any future contribution should preserve this defensive-only scope.
