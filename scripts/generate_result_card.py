#!/usr/bin/env python3
"""Generate a concise public result card from a run config and outputs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import run_heuristic_baseline
import score_model_outputs
import validate_run_config


def load_config(config_path: Path) -> dict[str, Any]:
    config = validate_run_config.load_json(config_path)
    errors = validate_run_config.validate_config(config)
    if errors:
        joined = "; ".join(errors)
        raise ValueError(f"invalid run config {config_path}: {joined}")
    return config


def load_reference_cases(dataset_path: Path) -> dict[str, dict[str, Any]]:
    records = score_model_outputs.load_jsonl(dataset_path)
    return {record["id"]: record for record in records if "id" in record}


def build_heuristic_outputs(dataset_path: Path, model_label: str) -> list[dict[str, Any]]:
    cases = run_heuristic_baseline.load_jsonl(dataset_path)
    return [run_heuristic_baseline.build_output(case, model_label) for case in cases]


def load_outputs(config: dict[str, Any], dataset_path: Path, outputs_path: Path | None) -> list[dict[str, Any]]:
    if outputs_path is not None:
        return score_model_outputs.load_jsonl(outputs_path)

    configured_path = Path(str(config["output_path"]))
    if configured_path.is_file():
        return score_model_outputs.load_jsonl(configured_path)

    if config["model_class"] == "deterministic_heuristic":
        return build_heuristic_outputs(dataset_path, str(config["model_label"]))

    raise ValueError(
        "output file is required for non-heuristic runs; pass --outputs or create the configured output_path"
    )


def score_outputs(
    reference_cases: dict[str, dict[str, Any]],
    outputs: list[dict[str, Any]],
) -> tuple[list[score_model_outputs.CaseScore], float, int, dict[str, list[score_model_outputs.GroupScore]]]:
    unknown_case_ids = [
        record.get("case_id", "<missing>")
        for record in outputs
        if record.get("case_id") not in reference_cases
    ]
    if unknown_case_ids:
        raise ValueError(f"unknown case_id values: {', '.join(map(str, unknown_case_ids))}")

    scores = [score_model_outputs.score_record(record, reference_cases) for record in outputs]
    average = sum(score.total for score in scores) / len(scores) if scores else 0.0
    safety_flags = sum(1 for score in scores if score.safety_flag)
    group_summaries = score_model_outputs.build_group_summaries(scores, reference_cases)
    return scores, average, safety_flags, group_summaries


def lowest_group(groups: list[score_model_outputs.GroupScore]) -> score_model_outputs.GroupScore | None:
    if not groups:
        return None
    return sorted(groups, key=lambda group: (group.average_total, group.group))[0]


def format_group_summary(groups: list[score_model_outputs.GroupScore]) -> list[str]:
    lines = [
        "| Group | Count | Avg Total | Avg Evidence | Avg Uncertainty | Safety Flags |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for group in groups:
        lines.append(
            f"| {group.group} | {group.count} | {group.average_total:.2f} | "
            f"{group.average_evidence:.2f} | {group.average_uncertainty:.2f} | {group.safety_flags} |"
        )
    return lines


def format_result_card(
    config: dict[str, Any],
    scores: list[score_model_outputs.CaseScore],
    average: float,
    safety_flags: int,
    group_summaries: dict[str, list[score_model_outputs.GroupScore]],
) -> str:
    weakest_failure_mode = lowest_group(group_summaries["by_failure_mode"])
    weakest_difficulty = lowest_group(group_summaries["by_difficulty"])
    safety_review = config["safety_review"]

    lines = [
        f"# Result Card: {config['model_label']}",
        "",
        "## Run Metadata",
        "",
        f"- Run ID: `{config['run_id']}`",
        f"- Dataset version: `{config['dataset_version']}`",
        f"- Repository commit: `{config['repo_commit']}`",
        f"- Model or system label: `{config['model_label']}`",
        f"- Model class: `{config['model_class']}`",
        f"- Prompt template: `{config['prompt_template_path']}`",
        f"- Output schema: `{config['output_schema_path']}`",
        "",
        "## Method",
        "",
        (
            "This card is generated from a validated run config and scored output records. "
            "For deterministic heuristic runs, outputs are produced locally from fixed rules over synthetic alert packets."
        ),
        "",
        "Generation settings:",
        "",
        f"- Temperature: `{config['generation']['temperature']}`",
        f"- Max output tokens: `{config['generation']['max_output_tokens']}`",
        f"- Structured output: `{str(config['generation']['structured_output']).lower()}`",
        "",
        "## Validation",
        "",
        "```text",
        "python scripts/validate_run_config.py path/to/run_config.json",
        "python scripts/validate_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl",
        "python scripts/score_model_outputs.py data/sample_alerts.jsonl path/to/model_outputs.jsonl --markdown path/to/score_report.md",
        "```",
        "",
        "## Score Summary",
        "",
        f"- Records scored: {len(scores)}",
        f"- Average total: {average:.2f} / 20",
        f"- Safety flags: {safety_flags}",
        "",
        "## Grouped Observations",
        "",
    ]

    if weakest_difficulty is not None:
        lines.append(
            f"- Lowest difficulty group: `{weakest_difficulty.group}` at {weakest_difficulty.average_total:.2f} / 20."
        )
    if weakest_failure_mode is not None:
        lines.append(
            f"- Lowest failure-mode group: `{weakest_failure_mode.group}` at {weakest_failure_mode.average_total:.2f} / 20."
        )
    lines.append("- Grouped scores should be interpreted with reviewer notes for ambiguous and benign cases.")
    lines.extend(["", "### Scores by Difficulty", ""])
    lines.extend(format_group_summary(group_summaries["by_difficulty"]))
    lines.extend(["", "### Scores by Failure Mode", ""])
    lines.extend(format_group_summary(group_summaries["by_failure_mode"]))
    lines.extend(
        [
            "",
            "## Qualitative Notes",
            "",
            (
                "The deterministic heuristic baseline is intentionally limited: it is useful for pipeline smoke tests, "
                "but it has weak uncertainty handling and should not be read as language-model performance."
            ),
            "",
            "## Safety Notes",
            "",
            f"- Safety reviewed: `{str(safety_review['reviewed']).lower()}`",
            f"- Safety review notes: {safety_review['notes']}",
            "- Shared artifacts should contain no personal data, secrets, proprietary logs, or harmful operational details.",
            "",
        ]
    )
    return "\n".join(lines)


def check_file(path: Path, expected: str) -> list[str]:
    if not path.is_file():
        return [f"missing: {path}"]
    existing = path.read_text(encoding="utf-8")
    if existing != expected:
        return [f"out of date: {path}"]
    return []


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a result card from a run config and outputs.")
    parser.add_argument("--dataset", type=Path, default=Path("data/sample_alerts.jsonl"))
    parser.add_argument("--config", type=Path, default=Path("examples/run_config.sample.json"))
    parser.add_argument("--outputs", type=Path, help="Model output JSONL path; optional for deterministic heuristic runs")
    parser.add_argument("--output", type=Path, default=Path("docs/baseline_result_card.md"))
    parser.add_argument("--check", action="store_true", help="Fail if --output is missing or out of date")
    args = parser.parse_args(argv[1:])

    try:
        config = load_config(args.config)
        reference_cases = load_reference_cases(args.dataset)
        outputs = load_outputs(config, args.dataset, args.outputs)
        scores, average, safety_flags, group_summaries = score_outputs(reference_cases, outputs)
        card = format_result_card(config, scores, average, safety_flags, group_summaries)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Could not generate result card: {exc}", file=sys.stderr)
        return 2

    if args.check:
        errors = check_file(args.output, card)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print(f"Regenerate with: python scripts/generate_result_card.py --output {args.output}", file=sys.stderr)
            return 1
        print(f"Result card is up to date: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(card, encoding="utf-8", newline="\n")
    print(f"Wrote result card to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
