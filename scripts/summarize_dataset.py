#!/usr/bin/env python3
"""Generate a Markdown summary for OpenDefender alert cases."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as jsonl_file:
        for line_number, raw_line in enumerate(jsonl_file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            records.append(record)
    return records


def count_field(records: list[dict[str, Any]], field_path: tuple[str, ...]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        value: Any = record
        for field in field_path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(field)
        counts[str(value)] += 1
    return counts


def count_known_change(records: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        packet = record.get("alert_packet")
        value = packet.get("known_change_ticket") if isinstance(packet, dict) else None
        counts["present" if value is True else "absent"] += 1
    return counts


def ordered_items(counts: Counter[str], order: list[str] | None) -> list[tuple[str, int]]:
    if order is None:
        return sorted(counts.items())

    known = [(value, counts[value]) for value in order if value in counts]
    unknown = sorted((value, count) for value, count in counts.items() if value not in order)
    return known + unknown


def format_count_table(title: str, counts: Counter[str], order: list[str] | None = None) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Value | Count |",
        "| --- | ---: |",
    ]
    for value, count in ordered_items(counts, order):
        lines.append(f"| {value} | {count} |")
    lines.append("")
    return lines


def generate_summary(records: list[dict[str, Any]], source_path: Path) -> str:
    categories = count_field(records, ("category",))
    severities = count_field(records, ("expected", "severity"))
    confidence = count_field(records, ("expected", "confidence"))
    known_changes = count_known_change(records)

    case_ids = [str(record.get("id")) for record in records]
    first_case = min(case_ids) if case_ids else "n/a"
    last_case = max(case_ids) if case_ids else "n/a"

    lines = [
        "# Dataset Summary",
        "",
        f"Source: `{source_path.as_posix()}`",
        "",
        "This summary is generated from the dataset JSONL file. Regenerate it with:",
        "",
        "```bash",
        f"python scripts/summarize_dataset.py {source_path.as_posix()} --output docs/dataset_summary.md",
        "```",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total cases | {len(records)} |",
        f"| First case ID | {first_case} |",
        f"| Last case ID | {last_case} |",
        f"| Categories | {len(categories)} |",
        "",
    ]

    lines.extend(format_count_table("Category Distribution", categories))
    lines.extend(
        format_count_table(
            "Expected Severity Distribution",
            severities,
            ["informational", "low", "medium", "high", "critical"],
        )
    )
    lines.extend(format_count_table("Expected Confidence Distribution", confidence, ["low", "medium", "high"]))
    lines.extend(format_count_table("Known Change Ticket Distribution", known_changes, ["absent", "present"]))

    lines.extend(
        [
            "## Notes",
            "",
            "- Counts describe the current sample dataset, not a production incident distribution.",
            "- Cases are synthetic and defensive-only.",
            "- Low and informational examples are included so benchmarks can measure over-escalation.",
            "- Ambiguous examples are included so benchmarks can measure uncertainty handling.",
            "",
        ]
    )

    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a Markdown dataset summary.")
    parser.add_argument("dataset", type=Path, help="Dataset JSONL path")
    parser.add_argument("--output", type=Path, help="Write summary Markdown to this path")
    parser.add_argument("--check", action="store_true", help="Fail if --output exists and differs")
    args = parser.parse_args(argv[1:])

    try:
        records = load_jsonl(args.dataset)
        summary = generate_summary(records, args.dataset)
    except (OSError, ValueError) as exc:
        print(f"Could not summarize dataset: {exc}", file=sys.stderr)
        return 2

    if args.output is None:
        print(summary)
        return 0

    if args.check:
        if not args.output.is_file():
            print(f"Summary file not found: {args.output}", file=sys.stderr)
            return 1
        existing = args.output.read_text(encoding="utf-8")
        if existing != summary:
            print(f"Summary is out of date: {args.output}", file=sys.stderr)
            print(f"Regenerate with: python scripts/summarize_dataset.py {args.dataset} --output {args.output}")
            return 1
        print(f"Summary is up to date: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(summary, encoding="utf-8", newline="\n")
    print(f"Wrote dataset summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
