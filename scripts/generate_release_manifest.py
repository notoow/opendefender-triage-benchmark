#!/usr/bin/env python3
"""Generate deterministic release manifests for OpenDefender artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_ARTIFACTS = [
    "DATASET_VERSION",
    "data/sample_alerts.jsonl",
    "schemas/alert_case.schema.json",
    "evaluation/output_schema.json",
    "evaluation/rubric.md",
    "evaluation/prompt_template.md",
    "docs/baseline_results.md",
]


def stable_text_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(stable_text_bytes(path)).hexdigest()


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


def count_field(records: list[dict[str, Any]], field_path: tuple[str, ...]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for record in records:
        value: Any = record
        for field in field_path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(field)
        counts[str(value)] += 1
    return dict(sorted(counts.items()))


def count_array_field(records: list[dict[str, Any]], field_path: tuple[str, ...]) -> dict[str, int]:
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
    return dict(sorted(counts.items()))


def build_manifest(repo_root: Path, dataset_path: Path, version_path: Path, artifact_paths: list[Path]) -> dict[str, Any]:
    records = load_jsonl(repo_root / dataset_path)
    version = (repo_root / version_path).read_text(encoding="utf-8").strip()

    artifacts = []
    for artifact_path in artifact_paths:
        full_path = repo_root / artifact_path
        if not full_path.is_file():
            raise ValueError(f"artifact not found: {artifact_path.as_posix()}")
        artifacts.append(
            {
                "path": artifact_path.as_posix(),
                "bytes": len(stable_text_bytes(full_path)),
                "sha256": sha256_file(full_path),
            }
        )

    case_ids = [str(record.get("id")) for record in records]
    return {
        "manifest_version": 1,
        "dataset_name": "OpenDefender Triage Benchmark",
        "dataset_version": version,
        "dataset_path": dataset_path.as_posix(),
        "case_count": len(records),
        "first_case_id": min(case_ids) if case_ids else None,
        "last_case_id": max(case_ids) if case_ids else None,
        "category_counts": count_field(records, ("category",)),
        "severity_counts": count_field(records, ("expected", "severity")),
        "confidence_counts": count_field(records, ("expected", "confidence")),
        "difficulty_counts": count_field(records, ("evaluation_metadata", "difficulty")),
        "failure_mode_counts": count_array_field(records, ("evaluation_metadata", "failure_modes")),
        "artifacts": artifacts,
    }


def format_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Release Manifest",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Dataset name | {manifest['dataset_name']} |",
        f"| Dataset version | {manifest['dataset_version']} |",
        f"| Dataset path | `{manifest['dataset_path']}` |",
        f"| Case count | {manifest['case_count']} |",
        f"| First case ID | {manifest['first_case_id']} |",
        f"| Last case ID | {manifest['last_case_id']} |",
        "",
        "## Category Counts",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]

    for category, count in manifest["category_counts"].items():
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            "## Severity Counts",
            "",
            "| Severity | Count |",
            "| --- | ---: |",
        ]
    )
    for severity, count in ordered_counts(
        manifest["severity_counts"],
        ["informational", "low", "medium", "high", "critical"],
    ):
        lines.append(f"| {severity} | {count} |")

    lines.extend(
        [
            "",
            "## Confidence Counts",
            "",
            "| Confidence | Count |",
            "| --- | ---: |",
        ]
    )
    for confidence, count in ordered_counts(manifest["confidence_counts"], ["low", "medium", "high"]):
        lines.append(f"| {confidence} | {count} |")

    lines.extend(
        [
            "",
            "## Difficulty Counts",
            "",
            "| Difficulty | Count |",
            "| --- | ---: |",
        ]
    )
    for difficulty, count in ordered_counts(manifest["difficulty_counts"], ["easy", "medium", "hard"]):
        lines.append(f"| {difficulty} | {count} |")

    lines.extend(
        [
            "",
            "## Failure Mode Counts",
            "",
            "| Failure Mode | Count |",
            "| --- | ---: |",
        ]
    )
    for failure_mode, count in manifest["failure_mode_counts"].items():
        lines.append(f"| {failure_mode} | {count} |")

    lines.extend(
        [
            "",
            "## Artifact Hashes",
            "",
            "| Path | Bytes | SHA-256 |",
            "| --- | ---: | --- |",
        ]
    )
    for artifact in manifest["artifacts"]:
        lines.append(f"| `{artifact['path']}` | {artifact['bytes']} | `{artifact['sha256']}` |")

    lines.extend(
        [
            "",
            "Regenerate with:",
            "",
            "```bash",
            "python scripts/generate_release_manifest.py --output-json docs/release_manifest.json --output-md docs/release_manifest.md",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def ordered_counts(counts: dict[str, int], order: list[str]) -> list[tuple[str, int]]:
    known = [(value, counts[value]) for value in order if value in counts]
    unknown = sorted((value, count) for value, count in counts.items() if value not in order)
    return known + unknown


def write_json(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(format_markdown(manifest), encoding="utf-8", newline="\n")


def check_file(path: Path, expected: str) -> list[str]:
    if not path.is_file():
        return [f"missing: {path}"]
    existing = path.read_text(encoding="utf-8")
    if existing != expected:
        return [f"out of date: {path}"]
    return []


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate release manifests for OpenDefender artifacts.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--dataset", type=Path, default=Path("data/sample_alerts.jsonl"))
    parser.add_argument("--version-file", type=Path, default=Path("DATASET_VERSION"))
    parser.add_argument("--output-json", type=Path, default=Path("docs/release_manifest.json"))
    parser.add_argument("--output-md", type=Path, default=Path("docs/release_manifest.md"))
    parser.add_argument("--check", action="store_true", help="Fail if output files are missing or out of date")
    args = parser.parse_args(argv[1:])

    repo_root = args.repo_root.resolve()
    dataset_path = args.dataset
    version_path = args.version_file
    artifact_paths = [Path(path) for path in DEFAULT_ARTIFACTS]

    try:
        manifest = build_manifest(repo_root, dataset_path, version_path, artifact_paths)
    except (OSError, ValueError) as exc:
        print(f"Could not generate release manifest: {exc}", file=sys.stderr)
        return 2

    expected_json = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    expected_md = format_markdown(manifest)

    if args.check:
        errors = check_file(args.output_json, expected_json)
        errors.extend(check_file(args.output_md, expected_md))
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            print(
                "Regenerate with: python scripts/generate_release_manifest.py "
                "--output-json docs/release_manifest.json --output-md docs/release_manifest.md",
                file=sys.stderr,
            )
            return 1
        print("Release manifest files are up to date")
        return 0

    write_json(args.output_json, manifest)
    write_markdown(args.output_md, manifest)
    print(f"Wrote release manifest JSON to {args.output_json}")
    print(f"Wrote release manifest Markdown to {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
