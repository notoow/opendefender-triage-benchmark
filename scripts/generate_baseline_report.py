#!/usr/bin/env python3
"""Generate a committed heuristic baseline results report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import run_heuristic_baseline
import score_model_outputs


def generate_report(dataset_path: Path, version_path: Path) -> str:
    cases = run_heuristic_baseline.load_jsonl(dataset_path)
    reference_cases = {case["id"]: case for case in cases}
    outputs = [run_heuristic_baseline.build_output(case, "heuristic-baseline") for case in cases]
    scores = [score_model_outputs.score_record(output, reference_cases) for output in outputs]
    average = sum(score.total for score in scores) / len(scores) if scores else 0.0
    safety_flags = sum(1 for score in scores if score.safety_flag)
    group_summaries = score_model_outputs.build_group_summaries(scores, reference_cases)
    version = version_path.read_text(encoding="utf-8").strip()

    lines = [
        "# Heuristic Baseline Results",
        "",
        f"Dataset version: `{version}`",
        "",
        "This report is generated from the deterministic heuristic baseline. It is intended as an end-to-end smoke test for the dataset, schemas, scoring pipeline, and grouped analysis. It is not intended to represent language model performance.",
        "",
        "Regenerate with:",
        "",
        "```bash",
        "python scripts/generate_baseline_report.py --output docs/baseline_results.md",
        "```",
        "",
    ]
    score_report = score_model_outputs.format_markdown(scores, average, safety_flags, group_summaries)
    lines.extend(score_report.splitlines()[2:])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate heuristic baseline results.")
    parser.add_argument("--dataset", type=Path, default=Path("data/sample_alerts.jsonl"))
    parser.add_argument("--version-file", type=Path, default=Path("DATASET_VERSION"))
    parser.add_argument("--output", type=Path, default=Path("docs/baseline_results.md"))
    parser.add_argument("--check", action="store_true", help="Fail if --output is missing or out of date")
    args = parser.parse_args(argv[1:])

    try:
        report = generate_report(args.dataset, args.version_file)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Could not generate baseline report: {exc}", file=sys.stderr)
        return 2

    if args.check:
        if not args.output.is_file():
            print(f"Baseline report not found: {args.output}", file=sys.stderr)
            return 1
        existing = args.output.read_text(encoding="utf-8")
        if existing != report:
            print(f"Baseline report is out of date: {args.output}", file=sys.stderr)
            print(f"Regenerate with: python scripts/generate_baseline_report.py --output {args.output}")
            return 1
        print(f"Baseline report is up to date: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote baseline report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
