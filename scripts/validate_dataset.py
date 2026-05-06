#!/usr/bin/env python3
"""Validate OpenDefender JSONL alert cases without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_CATEGORIES = {
    "identity",
    "endpoint",
    "cloud",
    "email",
    "collaboration",
    "network",
    "other",
}

ALLOWED_SEVERITIES = {"informational", "low", "medium", "high", "critical"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
ALLOWED_DIFFICULTY = {"easy", "medium", "hard"}
CASE_ID_PATTERN = re.compile(r"^odtb-[0-9]{4,}$")

TOP_LEVEL_KEYS = {"id", "category", "alert_title", "alert_packet", "expected", "evaluation_metadata"}
ALERT_PACKET_KEYS = {
    "source",
    "signals",
    "asset",
    "business_context",
    "time_window",
    "known_change_ticket",
}
EXPECTED_KEYS = {
    "incident_type",
    "severity",
    "confidence",
    "key_evidence",
    "missing_information",
    "safe_actions",
}
EVALUATION_METADATA_KEYS = {"difficulty", "tags", "failure_modes"}


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


def validate_exact_keys(value: dict[str, Any], expected_keys: set[str], field: str) -> list[str]:
    actual_keys = set(value)
    errors: list[str] = []
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)

    if missing:
        errors.append(f"{field} missing required keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{field} has unexpected keys: {', '.join(extra)}")

    return errors


def validate_case(record: Any, line_number: int, seen_ids: set[str]) -> list[str]:
    prefix = f"line {line_number}"
    errors: list[str] = []

    if not isinstance(record, dict):
        return [f"{prefix}: record must be an object"]

    errors.extend(f"{prefix}: {error}" for error in validate_exact_keys(record, TOP_LEVEL_KEYS, "record"))

    case_id = record.get("id")
    if not is_non_empty_string(case_id) or not CASE_ID_PATTERN.match(case_id):
        errors.append(f"{prefix}: id must match odtb-0000 format")
    elif case_id in seen_ids:
        errors.append(f"{prefix}: duplicate id {case_id}")
    elif isinstance(case_id, str):
        seen_ids.add(case_id)

    category = record.get("category")
    if category not in ALLOWED_CATEGORIES:
        errors.append(f"{prefix}: category must be one of {sorted(ALLOWED_CATEGORIES)}")

    if not is_non_empty_string(record.get("alert_title")):
        errors.append(f"{prefix}: alert_title must be a non-empty string")

    alert_packet = record.get("alert_packet")
    if not isinstance(alert_packet, dict):
        errors.append(f"{prefix}: alert_packet must be an object")
    else:
        errors.extend(
            f"{prefix}: {error}" for error in validate_exact_keys(alert_packet, ALERT_PACKET_KEYS, "alert_packet")
        )
        for field in ("source", "asset", "business_context", "time_window"):
            if not is_non_empty_string(alert_packet.get(field)):
                errors.append(f"{prefix}: alert_packet.{field} must be a non-empty string")
        errors.extend(
            f"{prefix}: {error}"
            for error in validate_string_array(alert_packet.get("signals"), "alert_packet.signals")
        )
        if not isinstance(alert_packet.get("known_change_ticket"), bool):
            errors.append(f"{prefix}: alert_packet.known_change_ticket must be a boolean")

    expected = record.get("expected")
    if not isinstance(expected, dict):
        errors.append(f"{prefix}: expected must be an object")
    else:
        errors.extend(f"{prefix}: {error}" for error in validate_exact_keys(expected, EXPECTED_KEYS, "expected"))
        if not is_non_empty_string(expected.get("incident_type")):
            errors.append(f"{prefix}: expected.incident_type must be a non-empty string")
        if expected.get("severity") not in ALLOWED_SEVERITIES:
            errors.append(f"{prefix}: expected.severity must be one of {sorted(ALLOWED_SEVERITIES)}")
        if expected.get("confidence") not in ALLOWED_CONFIDENCE:
            errors.append(f"{prefix}: expected.confidence must be one of {sorted(ALLOWED_CONFIDENCE)}")
        errors.extend(
            f"{prefix}: {error}" for error in validate_string_array(expected.get("key_evidence"), "expected.key_evidence")
        )
        errors.extend(
            f"{prefix}: {error}"
            for error in validate_string_array(
                expected.get("missing_information"),
                "expected.missing_information",
                allow_empty=True,
            )
        )
        errors.extend(
            f"{prefix}: {error}" for error in validate_string_array(expected.get("safe_actions"), "expected.safe_actions")
        )

    evaluation_metadata = record.get("evaluation_metadata")
    if not isinstance(evaluation_metadata, dict):
        errors.append(f"{prefix}: evaluation_metadata must be an object")
    else:
        errors.extend(
            f"{prefix}: {error}"
            for error in validate_exact_keys(
                evaluation_metadata,
                EVALUATION_METADATA_KEYS,
                "evaluation_metadata",
            )
        )
        if evaluation_metadata.get("difficulty") not in ALLOWED_DIFFICULTY:
            errors.append(f"{prefix}: evaluation_metadata.difficulty must be one of {sorted(ALLOWED_DIFFICULTY)}")
        errors.extend(
            f"{prefix}: {error}"
            for error in validate_string_array(evaluation_metadata.get("tags"), "evaluation_metadata.tags")
        )
        errors.extend(
            f"{prefix}: {error}"
            for error in validate_string_array(
                evaluation_metadata.get("failure_modes"),
                "evaluation_metadata.failure_modes",
            )
        )

    return errors


def validate_dataset(path: Path) -> tuple[int, list[str], set[str]]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    categories: set[str] = set()
    count = 0

    with path.open("r", encoding="utf-8") as dataset_file:
        for line_number, raw_line in enumerate(dataset_file, start=1):
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
            if isinstance(record, dict) and isinstance(record.get("category"), str):
                categories.add(record["category"])
            errors.extend(validate_case(record, line_number, seen_ids))

    return count, errors, categories


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/validate_dataset.py data/sample_alerts.jsonl", file=sys.stderr)
        return 2

    dataset_path = Path(argv[1])
    if not dataset_path.is_file():
        print(f"Dataset file not found: {dataset_path}", file=sys.stderr)
        return 2

    count, errors, categories = validate_dataset(dataset_path)
    if errors:
        print(f"Validation failed for {dataset_path}:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {count} cases from {dataset_path}")
    print(f"Categories: {', '.join(sorted(categories))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
