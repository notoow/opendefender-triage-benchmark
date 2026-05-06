#!/usr/bin/env python3
"""Check benchmark dataset quality gates and generate a Markdown report."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SEVERITY_ORDER = ["informational", "low", "medium", "high", "critical"]
CONFIDENCE_ORDER = ["low", "medium", "high"]
DIFFICULTY_ORDER = ["easy", "medium", "hard"]

MIN_CASES = 20
MIN_CATEGORIES = 5
MIN_CASES_PER_CATEGORY = 2
MAX_CATEGORY_SHARE = 0.35
MIN_LOW_OR_INFO = 4
MIN_HIGH_OR_CRITICAL = 3
MIN_KNOWN_CHANGE_PRESENT = 4
MIN_KNOWN_CHANGE_ABSENT = 4
MIN_FAILURE_MODES = 8
MIN_CASE_TAGS = 2
MIN_CASE_FAILURE_MODES = 1
MIN_KEY_EVIDENCE = 2
MIN_MISSING_INFORMATION = 1
MIN_SAFE_ACTIONS = 2

SENSITIVE_PATTERNS = [
    ("email address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("private key marker", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("aws access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("jwt-like token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]


@dataclass(frozen=True)
class QualityCheck:
    name: str
    passed: bool
    detail: str


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as dataset_file:
        for line_number, raw_line in enumerate(dataset_file, start=1):
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


def count_array_field(records: list[dict[str, Any]], field_path: tuple[str, ...]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        value: Any = record
        for field in field_path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(field)
        if isinstance(value, list):
            counts.update(str(item) for item in value)
    return counts


def count_known_change(records: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for record in records:
        packet = record.get("alert_packet")
        value = packet.get("known_change_ticket") if isinstance(packet, dict) else None
        counts["present" if value is True else "absent"] += 1
    return counts


def array_length(record: dict[str, Any], field_path: tuple[str, ...]) -> int:
    value: Any = record
    for field in field_path:
        if not isinstance(value, dict):
            return 0
        value = value.get(field)
    return len(value) if isinstance(value, list) else 0


def stable_record_text(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, sort_keys=True)


def find_sensitive_hits(records: list[dict[str, Any]]) -> list[str]:
    hits: list[str] = []
    for record in records:
        case_id = str(record.get("id", "unknown"))
        text = stable_record_text(record)
        for label, pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                hits.append(f"{case_id}: matched {label}")
    return hits


def distribution_lines(counts: Counter[str], order: list[str] | None = None) -> list[str]:
    if order is None:
        items = sorted(counts.items())
    else:
        ordered = [(value, counts[value]) for value in order if value in counts]
        extra = sorted((value, count) for value, count in counts.items() if value not in order)
        items = ordered + extra
    return [f"{value}={count}" for value, count in items]


def build_quality_checks(records: list[dict[str, Any]]) -> list[QualityCheck]:
    categories = count_field(records, ("category",))
    severities = count_field(records, ("expected", "severity"))
    confidence = count_field(records, ("expected", "confidence"))
    difficulty = count_field(records, ("evaluation_metadata", "difficulty"))
    failure_modes = count_array_field(records, ("evaluation_metadata", "failure_modes"))
    known_changes = count_known_change(records)
    sensitive_hits = find_sensitive_hits(records)

    largest_category = max(categories.values(), default=0)
    largest_share = largest_category / len(records) if records else 0
    low_or_info = severities["informational"] + severities["low"]
    high_or_critical = severities["high"] + severities["critical"]

    short_tags = [
        str(record.get("id"))
        for record in records
        if array_length(record, ("evaluation_metadata", "tags")) < MIN_CASE_TAGS
    ]
    missing_failure_modes = [
        str(record.get("id"))
        for record in records
        if array_length(record, ("evaluation_metadata", "failure_modes")) < MIN_CASE_FAILURE_MODES
    ]
    short_evidence = [
        str(record.get("id"))
        for record in records
        if array_length(record, ("expected", "key_evidence")) < MIN_KEY_EVIDENCE
    ]
    short_missing_info = [
        str(record.get("id"))
        for record in records
        if array_length(record, ("expected", "missing_information")) < MIN_MISSING_INFORMATION
    ]
    short_safe_actions = [
        str(record.get("id"))
        for record in records
        if array_length(record, ("expected", "safe_actions")) < MIN_SAFE_ACTIONS
    ]

    return [
        QualityCheck(
            "Minimum case count",
            len(records) >= MIN_CASES,
            f"{len(records)} cases; minimum {MIN_CASES}",
        ),
        QualityCheck(
            "Category breadth",
            len(categories) >= MIN_CATEGORIES,
            f"{len(categories)} categories; minimum {MIN_CATEGORIES}",
        ),
        QualityCheck(
            "Minimum cases per category",
            all(count >= MIN_CASES_PER_CATEGORY for count in categories.values()),
            ", ".join(distribution_lines(categories)),
        ),
        QualityCheck(
            "Largest category share",
            largest_share <= MAX_CATEGORY_SHARE,
            f"{largest_share:.0%}; maximum {MAX_CATEGORY_SHARE:.0%}",
        ),
        QualityCheck(
            "Severity label coverage",
            all(severity in severities for severity in SEVERITY_ORDER),
            ", ".join(distribution_lines(severities, SEVERITY_ORDER)),
        ),
        QualityCheck(
            "Low and informational coverage",
            low_or_info >= MIN_LOW_OR_INFO,
            f"{low_or_info} cases; minimum {MIN_LOW_OR_INFO}",
        ),
        QualityCheck(
            "High and critical coverage",
            high_or_critical >= MIN_HIGH_OR_CRITICAL,
            f"{high_or_critical} cases; minimum {MIN_HIGH_OR_CRITICAL}",
        ),
        QualityCheck(
            "Confidence label coverage",
            all(label in confidence for label in CONFIDENCE_ORDER),
            ", ".join(distribution_lines(confidence, CONFIDENCE_ORDER)),
        ),
        QualityCheck(
            "Difficulty label coverage",
            all(label in difficulty for label in DIFFICULTY_ORDER),
            ", ".join(distribution_lines(difficulty, DIFFICULTY_ORDER)),
        ),
        QualityCheck(
            "Known-change contrast",
            known_changes["present"] >= MIN_KNOWN_CHANGE_PRESENT and known_changes["absent"] >= MIN_KNOWN_CHANGE_ABSENT,
            ", ".join(distribution_lines(known_changes, ["absent", "present"])),
        ),
        QualityCheck(
            "Failure-mode breadth",
            len(failure_modes) >= MIN_FAILURE_MODES,
            f"{len(failure_modes)} unique failure modes; minimum {MIN_FAILURE_MODES}",
        ),
        QualityCheck(
            "Per-case tag depth",
            not short_tags,
            "all cases have enough tags" if not short_tags else "short tags: " + ", ".join(short_tags),
        ),
        QualityCheck(
            "Per-case failure-mode labels",
            not missing_failure_modes,
            (
                "all cases have failure-mode labels"
                if not missing_failure_modes
                else "missing failure modes: " + ", ".join(missing_failure_modes)
            ),
        ),
        QualityCheck(
            "Per-case evidence depth",
            not short_evidence,
            (
                "all cases have enough key evidence"
                if not short_evidence
                else "short evidence: " + ", ".join(short_evidence)
            ),
        ),
        QualityCheck(
            "Per-case missing-information prompts",
            not short_missing_info,
            (
                "all cases identify missing information"
                if not short_missing_info
                else "missing missing-information prompts: " + ", ".join(short_missing_info)
            ),
        ),
        QualityCheck(
            "Per-case safe-action depth",
            not short_safe_actions,
            (
                "all cases have enough safe actions"
                if not short_safe_actions
                else "short safe actions: " + ", ".join(short_safe_actions)
            ),
        ),
        QualityCheck(
            "Sensitive token scan",
            not sensitive_hits,
            "no sensitive-token patterns detected" if not sensitive_hits else "; ".join(sensitive_hits),
        ),
    ]


def format_markdown(records: list[dict[str, Any]], checks: list[QualityCheck], source_path: Path) -> str:
    passed = sum(1 for check in checks if check.passed)
    failed = len(checks) - passed
    categories = count_field(records, ("category",))
    severities = count_field(records, ("expected", "severity"))
    difficulty = count_field(records, ("evaluation_metadata", "difficulty"))

    lines = [
        "# Dataset Quality Report",
        "",
        f"Source: `{source_path.as_posix()}`",
        "",
        "This report is generated from dataset quality gates. Regenerate it with:",
        "",
        "```bash",
        f"python scripts/check_dataset_quality.py {source_path.as_posix()} --output docs/dataset_quality.md",
        "```",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total checks | {len(checks)} |",
        f"| Passed checks | {passed} |",
        f"| Failed checks | {failed} |",
        f"| Cases | {len(records)} |",
        f"| Categories | {len(categories)} |",
        "",
        "## Quality Gates",
        "",
        "| Gate | Status | Detail |",
        "| --- | --- | --- |",
    ]

    for check in checks:
        status = "pass" if check.passed else "fail"
        lines.append(f"| {check.name} | {status} | {check.detail} |")

    lines.extend(
        [
            "",
            "## Snapshot",
            "",
            "| Distribution | Values |",
            "| --- | --- |",
            f"| Category | {', '.join(distribution_lines(categories))} |",
            f"| Severity | {', '.join(distribution_lines(severities, SEVERITY_ORDER))} |",
            f"| Difficulty | {', '.join(distribution_lines(difficulty, DIFFICULTY_ORDER))} |",
            "",
            "## Notes",
            "",
            "- These gates are deliberately lightweight and deterministic so they can run in CI.",
            "- Passing this report does not mean the dataset is complete; it means the public sample keeps minimum breadth, balance, and safety checks.",
            "- New cases should preserve defensive-only scope and avoid real logs, personal data, secrets, and operationally harmful instructions.",
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
    parser = argparse.ArgumentParser(description="Check dataset quality gates.")
    parser.add_argument("dataset", type=Path, help="Dataset JSONL path")
    parser.add_argument("--output", type=Path, help="Write Markdown quality report")
    parser.add_argument("--check", action="store_true", help="Fail if checks fail or --output is out of date")
    args = parser.parse_args(argv[1:])

    try:
        records = load_jsonl(args.dataset)
        checks = build_quality_checks(records)
        report = format_markdown(records, checks, args.dataset)
    except (OSError, ValueError) as exc:
        print(f"Could not check dataset quality: {exc}", file=sys.stderr)
        return 2

    failed_checks = [check for check in checks if not check.passed]
    if failed_checks:
        print(f"Dataset quality checks failed for {args.dataset}:", file=sys.stderr)
        for check in failed_checks:
            print(f"- {check.name}: {check.detail}", file=sys.stderr)
        return 1

    if args.output is None:
        print(report)
        return 0

    if args.check:
        errors = check_file(args.output, report)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print(
                f"Regenerate with: python scripts/check_dataset_quality.py {args.dataset} --output {args.output}",
                file=sys.stderr,
            )
            return 1
        print(f"Dataset quality report is up to date: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote dataset quality report to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
