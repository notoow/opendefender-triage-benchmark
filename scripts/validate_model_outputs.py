#!/usr/bin/env python3
"""Validate model-output JSONL records for OpenDefender evaluations."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_SEVERITIES = {"informational", "low", "medium", "high", "critical"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
OUTPUT_KEYS = {
    "incident_type",
    "severity",
    "confidence",
    "evidence",
    "missing_information",
    "recommended_actions",
    "safety_notes",
}
RECORD_KEYS = {"case_id", "model", "output"}


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_string_array(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, list):
        return [f"{field} must be an array"]
    if not allow_empty and not value:
        errors.append(f"{field} must not be empty")
    for index, item in enumerate(value):
        if not is_non_empty_string(item):
            errors.append(f"{field}[{index}] must be a non-empty string")
    return errors


def load_case_ids(dataset_path: Path) -> set[str]:
    case_ids: set[str] = set()
    with dataset_path.open("r", encoding="utf-8") as dataset_file:
        for line_number, raw_line in enumerate(dataset_file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{dataset_path}:{line_number}: invalid JSON: {exc.msg}") from exc
            case_id = record.get("id") if isinstance(record, dict) else None
            if not is_non_empty_string(case_id):
                raise ValueError(f"{dataset_path}:{line_number}: missing case id")
            case_ids.add(case_id)
    return case_ids


def validate_record(record: Any, line_number: int, known_case_ids: set[str], seen_case_ids: set[str]) -> list[str]:
    prefix = f"line {line_number}"
    errors: list[str] = []

    if not isinstance(record, dict):
        return [f"{prefix}: record must be an object"]

    actual_keys = set(record)
    missing = sorted(RECORD_KEYS - actual_keys)
    extra = sorted(actual_keys - RECORD_KEYS)
    if missing:
        errors.append(f"{prefix}: record missing required keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{prefix}: record has unexpected keys: {', '.join(extra)}")

    case_id = record.get("case_id")
    if not is_non_empty_string(case_id):
        errors.append(f"{prefix}: case_id must be a non-empty string")
    elif case_id not in known_case_ids:
        errors.append(f"{prefix}: unknown case_id {case_id}")
    elif case_id in seen_case_ids:
        errors.append(f"{prefix}: duplicate output for case_id {case_id}")
    elif isinstance(case_id, str):
        seen_case_ids.add(case_id)

    if not is_non_empty_string(record.get("model")):
        errors.append(f"{prefix}: model must be a non-empty string")

    output = record.get("output")
    if not isinstance(output, dict):
        errors.append(f"{prefix}: output must be an object")
        return errors

    actual_output_keys = set(output)
    missing_output = sorted(OUTPUT_KEYS - actual_output_keys)
    extra_output = sorted(actual_output_keys - OUTPUT_KEYS)
    if missing_output:
        errors.append(f"{prefix}: output missing required keys: {', '.join(missing_output)}")
    if extra_output:
        errors.append(f"{prefix}: output has unexpected keys: {', '.join(extra_output)}")

    if not is_non_empty_string(output.get("incident_type")):
        errors.append(f"{prefix}: output.incident_type must be a non-empty string")
    if output.get("severity") not in ALLOWED_SEVERITIES:
        errors.append(f"{prefix}: output.severity must be one of {sorted(ALLOWED_SEVERITIES)}")
    if output.get("confidence") not in ALLOWED_CONFIDENCE:
        errors.append(f"{prefix}: output.confidence must be one of {sorted(ALLOWED_CONFIDENCE)}")

    errors.extend(f"{prefix}: {error}" for error in validate_string_array(output.get("evidence"), "output.evidence"))
    errors.extend(
        f"{prefix}: {error}"
        for error in validate_string_array(
            output.get("missing_information"),
            "output.missing_information",
            allow_empty=True,
        )
    )
    errors.extend(
        f"{prefix}: {error}"
        for error in validate_string_array(output.get("recommended_actions"), "output.recommended_actions")
    )
    errors.extend(
        f"{prefix}: {error}"
        for error in validate_string_array(output.get("safety_notes"), "output.safety_notes", allow_empty=True)
    )

    return errors


def validate_outputs(dataset_path: Path, outputs_path: Path) -> tuple[int, list[str]]:
    known_case_ids = load_case_ids(dataset_path)
    seen_case_ids: set[str] = set()
    errors: list[str] = []
    count = 0

    with outputs_path.open("r", encoding="utf-8") as outputs_file:
        for line_number, raw_line in enumerate(outputs_file, start=1):
            line = raw_line.strip()
            if not line:
                errors.append(f"line {line_number}: blank lines are not allowed")
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
                continue
            count += 1
            errors.extend(validate_record(record, line_number, known_case_ids, seen_case_ids))

    return count, errors


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(
            "Usage: python scripts/validate_model_outputs.py data/sample_alerts.jsonl outputs.jsonl",
            file=sys.stderr,
        )
        return 2

    dataset_path = Path(argv[1])
    outputs_path = Path(argv[2])
    if not dataset_path.is_file():
        print(f"Dataset file not found: {dataset_path}", file=sys.stderr)
        return 2
    if not outputs_path.is_file():
        print(f"Outputs file not found: {outputs_path}", file=sys.stderr)
        return 2

    try:
        count, errors = validate_outputs(dataset_path, outputs_path)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if errors:
        print(f"Validation failed for {outputs_path}:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {count} model output records from {outputs_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
