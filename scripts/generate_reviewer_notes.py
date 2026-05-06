#!/usr/bin/env python3
"""Generate reviewer notes for ambiguous and benign benchmark cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


NOTE_TAGS = {"ambiguous_context", "benign_admin", "change_ticket"}
NOTE_FAILURE_MODES = {
    "benign_context",
    "change_ticket_reasoning",
    "missing_context_handling",
    "over_escalation",
}

FAILURE_MODE_GUIDANCE = {
    "access_review_reasoning": "Check whether the response treats access review as a verification task, not proof of compromise.",
    "benign_context": "Check whether benign operational context is weighed without ignoring suspicious signals.",
    "change_ticket_reasoning": "Check whether the response verifies the change ticket before escalating or dismissing the alert.",
    "confidence_calibration": "Check whether confidence matches the available evidence and missing context.",
    "data_exposure_reasoning": "Check whether exposure risk is tied to the stated asset and access details.",
    "evidence_grounding": "Check whether the response cites packet evidence instead of inventing facts.",
    "missing_context_handling": "Check whether the response names missing information before drawing firm conclusions.",
    "over_escalation": "Check whether the response avoids disruptive containment when the packet supports verification first.",
    "safe_action_scoping": "Check whether recommended actions stay defensive, proportionate, and human-reviewable.",
    "severity_calibration": "Check whether severity reflects both potential impact and uncertainty.",
    "under_escalation": "Check whether the response still escalates genuinely risky evidence.",
}


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


def get_array(record: dict[str, Any], field_path: tuple[str, ...]) -> list[str]:
    value: Any = record
    for field in field_path:
        if not isinstance(value, dict):
            return []
        value = value.get(field)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def get_scalar(record: dict[str, Any], field_path: tuple[str, ...], default: str = "n/a") -> str:
    value: Any = record
    for field in field_path:
        if not isinstance(value, dict):
            return default
        value = value.get(field)
    if value is None:
        return default
    return str(value)


def has_known_change(record: dict[str, Any]) -> bool:
    packet = record.get("alert_packet")
    return isinstance(packet, dict) and packet.get("known_change_ticket") is True


def selected_for_notes(record: dict[str, Any]) -> bool:
    tags = set(get_array(record, ("evaluation_metadata", "tags")))
    failure_modes = set(get_array(record, ("evaluation_metadata", "failure_modes")))
    return bool(tags & NOTE_TAGS) or bool(failure_modes & NOTE_FAILURE_MODES) or has_known_change(record)


def reviewer_focus(failure_modes: list[str]) -> list[str]:
    return [
        FAILURE_MODE_GUIDANCE.get(mode, f"Check whether the response addresses `{mode}`.")
        for mode in failure_modes
    ]


def bullet_lines(items: list[str]) -> list[str]:
    if not items:
        return ["- n/a"]
    return [f"- {item}" for item in items]


def table_cell(value: str) -> str:
    return value.replace("|", "\\|")


def selected_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in records if selected_for_notes(record)]


def format_markdown(records: list[dict[str, Any]], source_path: Path) -> str:
    notes = selected_records(records)
    ambiguous_count = sum(
        1 for record in notes if "ambiguous_context" in get_array(record, ("evaluation_metadata", "tags"))
    )
    benign_count = sum(1 for record in notes if "benign_admin" in get_array(record, ("evaluation_metadata", "tags")))
    known_change_count = sum(1 for record in notes if has_known_change(record))

    lines = [
        "# Reviewer Notes",
        "",
        f"Source: `{source_path.as_posix()}`",
        "",
        "This guide is generated from benchmark reference metadata. Regenerate it with:",
        "",
        "```bash",
        f"python scripts/generate_reviewer_notes.py {source_path.as_posix()} --output docs/reviewer_notes.md",
        "```",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Dataset cases | {len(records)} |",
        f"| Cases with reviewer notes | {len(notes)} |",
        f"| Ambiguous-context cases | {ambiguous_count} |",
        f"| Benign-admin cases | {benign_count} |",
        f"| Known-change cases | {known_change_count} |",
        "",
        "## Selection Criteria",
        "",
        "Reviewer notes are included when a case has at least one of these signals:",
        "",
        "- Tags: `ambiguous_context`, `benign_admin`, or `change_ticket`.",
        "- Failure modes: `over_escalation`, `benign_context`, `change_ticket_reasoning`, or `missing_context_handling`.",
        "- `alert_packet.known_change_ticket` is `true`.",
        "",
        "## Case Index",
        "",
        "| Case | Category | Difficulty | Expected Severity | Expected Confidence |",
        "| --- | --- | --- | --- | --- |",
    ]

    for record in notes:
        lines.append(
            "| {case_id} | {category} | {difficulty} | {severity} | {confidence} |".format(
                case_id=table_cell(get_scalar(record, ("id",))),
                category=table_cell(get_scalar(record, ("category",))),
                difficulty=table_cell(get_scalar(record, ("evaluation_metadata", "difficulty"))),
                severity=table_cell(get_scalar(record, ("expected", "severity"))),
                confidence=table_cell(get_scalar(record, ("expected", "confidence"))),
            )
        )

    for record in notes:
        case_id = get_scalar(record, ("id",))
        title = get_scalar(record, ("alert_title",))
        known_change = "present" if has_known_change(record) else "absent"
        failure_modes = get_array(record, ("evaluation_metadata", "failure_modes"))

        lines.extend(
            [
                "",
                f"## {case_id}: {title}",
                "",
                "| Field | Value |",
                "| --- | --- |",
                f"| Category | {table_cell(get_scalar(record, ('category',)))} |",
                f"| Difficulty | {table_cell(get_scalar(record, ('evaluation_metadata', 'difficulty')))} |",
                f"| Expected incident type | `{table_cell(get_scalar(record, ('expected', 'incident_type')))}` |",
                f"| Expected severity | {table_cell(get_scalar(record, ('expected', 'severity')))} |",
                f"| Expected confidence | {table_cell(get_scalar(record, ('expected', 'confidence')))} |",
                f"| Known change ticket | {known_change} |",
                "",
                "Reviewer focus:",
            ]
        )
        lines.extend(bullet_lines(reviewer_focus(failure_modes)))
        lines.extend(["", "Reference evidence:"])
        lines.extend(bullet_lines(get_array(record, ("expected", "key_evidence"))))
        lines.extend(["", "Missing context to preserve:"])
        lines.extend(bullet_lines(get_array(record, ("expected", "missing_information"))))
        lines.extend(["", "Safe action boundary:"])
        lines.extend(bullet_lines(get_array(record, ("expected", "safe_actions"))))

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- These notes are intended for benchmark review and result interpretation.",
            "- They do not add new facts beyond the dataset record; reviewers should score only against the alert packet.",
            "- The notes emphasize uncertainty handling, evidence grounding, and proportionate defensive action.",
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
    parser = argparse.ArgumentParser(description="Generate reviewer notes for ambiguous and benign cases.")
    parser.add_argument("dataset", type=Path, help="Dataset JSONL path")
    parser.add_argument("--output", type=Path, help="Write reviewer notes Markdown")
    parser.add_argument("--check", action="store_true", help="Fail if --output is missing or out of date")
    args = parser.parse_args(argv[1:])

    try:
        records = load_jsonl(args.dataset)
        report = format_markdown(records, args.dataset)
    except (OSError, ValueError) as exc:
        print(f"Could not generate reviewer notes: {exc}", file=sys.stderr)
        return 2

    if args.output is None:
        print(report)
        return 0

    if args.check:
        errors = check_file(args.output, report)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print(
                f"Regenerate with: python scripts/generate_reviewer_notes.py {args.dataset} --output {args.output}",
                file=sys.stderr,
            )
            return 1
        print(f"Reviewer notes are up to date: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(f"Wrote reviewer notes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
