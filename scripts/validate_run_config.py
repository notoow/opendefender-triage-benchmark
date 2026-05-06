#!/usr/bin/env python3
"""Validate an evaluation run configuration without external dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_KEYS = {
    "run_id",
    "dataset_version",
    "repo_commit",
    "model_label",
    "model_class",
    "prompt_template_path",
    "output_schema_path",
    "generation",
    "case_selection",
    "output_path",
    "score_report_path",
    "safety_review",
}
REQUIRED_GENERATION_KEYS = {"temperature", "max_output_tokens", "structured_output"}
ALLOWED_GENERATION_KEYS = REQUIRED_GENERATION_KEYS | {"notes"}
SAFETY_REVIEW_KEYS = {"reviewed", "notes"}
MODEL_CLASSES = {
    "deterministic_heuristic",
    "small_general_model",
    "large_reasoning_model",
    "local_open_weight_model",
    "tool_assisted_workflow",
    "other",
}
RUN_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
CASE_ID_PATTERN = re.compile(r"^odtb-[0-9]{4,}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_exact_keys(value: dict[str, Any], expected_keys: set[str], field: str) -> list[str]:
    errors: list[str] = []
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        errors.append(f"{field} missing required keys: {', '.join(missing)}")
    if extra:
        errors.append(f"{field} has unexpected keys: {', '.join(extra)}")
    return errors


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: config must be an object")
    return value


def validate_generation(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["generation must be an object"]

    missing = sorted(REQUIRED_GENERATION_KEYS - set(value))
    if missing:
        errors.append(f"generation missing required keys: {', '.join(missing)}")
    extra = sorted(set(value) - ALLOWED_GENERATION_KEYS)
    if extra:
        errors.append(f"generation has unexpected keys: {', '.join(extra)}")
    temperature = value.get("temperature")
    if not isinstance(temperature, (int, float)) or isinstance(temperature, bool):
        errors.append("generation.temperature must be a number")
    elif temperature < 0 or temperature > 2:
        errors.append("generation.temperature must be between 0 and 2")

    max_output_tokens = value.get("max_output_tokens")
    if not isinstance(max_output_tokens, int) or isinstance(max_output_tokens, bool):
        errors.append("generation.max_output_tokens must be an integer")
    elif max_output_tokens < 1:
        errors.append("generation.max_output_tokens must be positive")

    if not isinstance(value.get("structured_output"), bool):
        errors.append("generation.structured_output must be a boolean")

    if "notes" in value and not isinstance(value.get("notes"), str):
        errors.append("generation.notes must be a string")

    return errors


def validate_case_selection(value: Any) -> list[str]:
    if value == "all":
        return []
    if not isinstance(value, list) or not value:
        return ["case_selection must be 'all' or a non-empty array of case IDs"]

    errors: list[str] = []
    seen: set[str] = set()
    for index, case_id in enumerate(value):
        if not isinstance(case_id, str) or not CASE_ID_PATTERN.match(case_id):
            errors.append(f"case_selection[{index}] must match odtb-0000 format")
        elif case_id in seen:
            errors.append(f"case_selection[{index}] duplicates {case_id}")
        else:
            seen.add(case_id)
    return errors


def validate_safety_review(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["safety_review must be an object"]

    errors.extend(validate_exact_keys(value, SAFETY_REVIEW_KEYS, "safety_review"))
    if not isinstance(value.get("reviewed"), bool):
        errors.append("safety_review.reviewed must be a boolean")
    if not isinstance(value.get("notes"), str):
        errors.append("safety_review.notes must be a string")
    return errors


def validate_config(config: dict[str, Any]) -> list[str]:
    errors = validate_exact_keys(config, REQUIRED_KEYS, "config")

    run_id = config.get("run_id")
    if not isinstance(run_id, str) or not RUN_ID_PATTERN.match(run_id):
        errors.append("run_id must be 3-64 lowercase letters, numbers, dots, underscores, or hyphens")

    for field in (
        "dataset_version",
        "model_label",
        "prompt_template_path",
        "output_schema_path",
        "output_path",
        "score_report_path",
    ):
        if not is_non_empty_string(config.get(field)):
            errors.append(f"{field} must be a non-empty string")

    repo_commit = config.get("repo_commit")
    if not isinstance(repo_commit, str) or (repo_commit != "local" and not COMMIT_PATTERN.match(repo_commit)):
        errors.append("repo_commit must be 'local' or a 7-40 character lowercase hex commit")

    if config.get("model_class") not in MODEL_CLASSES:
        errors.append(f"model_class must be one of {sorted(MODEL_CLASSES)}")

    errors.extend(validate_generation(config.get("generation")))
    errors.extend(validate_case_selection(config.get("case_selection")))
    errors.extend(validate_safety_review(config.get("safety_review")))
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate an evaluation run config.")
    parser.add_argument("config", type=Path, help="Run config JSON path")
    args = parser.parse_args(argv[1:])

    if not args.config.is_file():
        print(f"Run config not found: {args.config}", file=sys.stderr)
        return 2

    try:
        config = load_json(args.config)
    except (OSError, ValueError) as exc:
        print(f"Could not validate run config: {exc}", file=sys.stderr)
        return 2

    errors = validate_config(config)
    if errors:
        print(f"Validation failed for {args.config}:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated run config: {args.config}")
    print(f"Run ID: {config['run_id']}")
    print(f"Model class: {config['model_class']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
