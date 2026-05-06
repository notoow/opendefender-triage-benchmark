#!/usr/bin/env python3
"""Create prompt JSONL records from OpenDefender alert cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_TEMPLATE = """You are assisting with defensive security alert triage.

Analyze only the alert packet provided. Do not invent facts, indicators, identities, timelines, or root causes that are not present in the packet. If important information is missing, list it under missing_information.

Do not provide exploit code, offensive instructions, credential theft guidance, persistence steps, evasion steps, or instructions for unauthorized access.

Return JSON matching the required schema:

{
  "incident_type": "string",
  "severity": "informational | low | medium | high | critical",
  "confidence": "low | medium | high",
  "evidence": ["string"],
  "missing_information": ["string"],
  "recommended_actions": ["string"],
  "safety_notes": ["string"]
}

Alert packet:
{{ALERT_PACKET_JSON}}
"""


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


def extract_fenced_text(markdown: str) -> str:
    fence = "```"
    start = markdown.find("```text")
    if start == -1:
        return markdown.strip()

    content_start = markdown.find("\n", start)
    if content_start == -1:
        return markdown.strip()

    end = markdown.find(fence, content_start + 1)
    if end == -1:
        return markdown.strip()

    return markdown[content_start + 1 : end].strip()


def load_template(path: Path | None) -> str:
    if path is None:
        return DEFAULT_TEMPLATE.strip()

    template = extract_fenced_text(path.read_text(encoding="utf-8"))
    if "{{ALERT_PACKET_JSON}}" not in template:
        raise ValueError(f"{path} must include {{ALERT_PACKET_JSON}}")
    return template


def make_prompt_record(case: dict[str, Any], template: str) -> dict[str, Any]:
    alert_packet = case.get("alert_packet")
    if not isinstance(alert_packet, dict):
        raise ValueError(f"{case.get('id', '<missing id>')}: alert_packet must be an object")

    alert_json = json.dumps(alert_packet, ensure_ascii=True, sort_keys=True)
    return {
        "case_id": case["id"],
        "category": case["category"],
        "alert_title": case["alert_title"],
        "prompt": template.replace("{{ALERT_PACKET_JSON}}", alert_json),
    }


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output_file:
        for record in records:
            output_file.write(json.dumps(record, ensure_ascii=True, sort_keys=True))
            output_file.write("\n")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create prompt JSONL records from OpenDefender alert cases.")
    parser.add_argument("dataset", type=Path, help="Dataset JSONL path")
    parser.add_argument("--template", type=Path, default=Path("evaluation/prompt_template.md"))
    parser.add_argument("--output", type=Path, required=True, help="Output prompt batch JSONL path")
    args = parser.parse_args(argv[1:])

    try:
        cases = load_jsonl(args.dataset)
        template = load_template(args.template)
        prompt_records = [make_prompt_record(case, template) for case in cases]
        write_jsonl(args.output, prompt_records)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Could not create prompt batch: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {len(prompt_records)} prompt records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
