#!/usr/bin/env python3
"""Run a simple deterministic baseline over OpenDefender alert cases."""

from __future__ import annotations

import argparse
import json
import sys
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


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output_file:
        for record in records:
            output_file.write(json.dumps(record, ensure_ascii=True, sort_keys=True))
            output_file.write("\n")


def signal_set(case: dict[str, Any]) -> set[str]:
    packet = case.get("alert_packet", {})
    signals = packet.get("signals", []) if isinstance(packet, dict) else []
    return {str(signal) for signal in signals}


def choose_severity(signals: set[str], known_change_ticket: bool, category: str) -> str:
    if "credential_dumping_behavior_blocked" in signals:
        return "critical"
    if {"new_inbox_forwarding_rule", "risky_sign_in_same_hour"} <= signals:
        return "high"
    if "privileged_role_added" in signals and not known_change_ticket:
        return "high"
    if "unusual_child_process" in signals and "file_from_email_attachment" in signals:
        return "high"
    if "approved_campaign_window" in signals and "no_phishing_detections" in signals:
        return "informational"
    if known_change_ticket and category in {"endpoint", "identity", "cloud", "collaboration"}:
        return "low"
    return "medium"


def choose_incident_type(case: dict[str, Any], signals: set[str], severity: str) -> str:
    category = case.get("category")
    known_change_ticket = bool(case.get("alert_packet", {}).get("known_change_ticket"))

    if "credential_dumping_behavior_blocked" in signals:
        return "possible_credential_access_attempt"
    if "new_inbox_forwarding_rule" in signals:
        return "possible_business_email_compromise"
    if "new_oauth_consent" in signals:
        return "suspicious_oauth_consent"
    if "multiple_mfa_push_denials" in signals:
        return "possible_mfa_fatigue_attempt"
    if "privileged_role_added" in signals:
        return "possible_privilege_escalation_or_account_takeover"
    if "dormant_account_sign_in" in signals and known_change_ticket:
        return "likely_authorized_account_reactivation_needs_verification"
    if "successful_password_auth_from_new_country" in signals:
        return "possible_account_compromise_attempt"
    if "public_read_enabled" in signals:
        return "public_storage_exposure_needs_verification"
    if "firewall_rule_created" in signals and known_change_ticket:
        return "likely_authorized_temporary_exposure_needs_review"
    if "api_key_used_from_new_region" in signals:
        return "ambiguous_service_account_usage"
    if "external_share_created" in signals:
        return "possible_unauthorized_external_sharing"
    if "guest_user_added" in signals and known_change_ticket:
        return "likely_authorized_guest_access_needs_review"
    if "remote_access_tool_installed" in signals and known_change_ticket:
        return "likely_authorized_remote_support"
    if "powershell_execution" in signals and known_change_ticket:
        return "likely_benign_admin_activity"
    if "unsigned_binary" in signals:
        return "suspicious_endpoint_execution"
    if "new_destination_asn" in signals:
        return "ambiguous_network_activity_needs_context"
    if "newly_observed_domain" in signals:
        return "possible_malicious_or_unwanted_domain_resolution"
    if "high_volume_outbound_email" in signals and known_change_ticket:
        return "likely_authorized_bulk_email_campaign"

    if severity in {"informational", "low"}:
        return f"likely_authorized_{category}_activity_needs_review"
    return f"suspicious_{category}_activity"


def choose_confidence(signals: set[str], known_change_ticket: bool, severity: str) -> str:
    if severity in {"critical", "informational"}:
        return "high"
    if "api_key_used_from_new_region" in signals:
        return "low"
    if known_change_ticket:
        return "medium"
    return "medium"


def humanize_signal(signal: str) -> str:
    return signal.replace("_", " ")


def build_output(case: dict[str, Any], model_name: str) -> dict[str, Any]:
    packet = case.get("alert_packet", {})
    category = str(case.get("category"))
    signals = signal_set(case)
    known_change_ticket = bool(packet.get("known_change_ticket")) if isinstance(packet, dict) else False
    severity = choose_severity(signals, known_change_ticket, category)
    incident_type = choose_incident_type(case, signals, severity)
    confidence = choose_confidence(signals, known_change_ticket, severity)

    evidence = [humanize_signal(signal) for signal in sorted(signals)[:4]]
    if known_change_ticket:
        evidence.append("known change ticket is present")

    missing_information = [
        "asset owner confirmation",
        "recent related activity",
        "approved change details" if known_change_ticket else "business justification",
    ]

    recommended_actions = [
        "verify the activity with the accountable owner",
        "review related audit and telemetry records",
        "preserve relevant logs for analyst review",
    ]
    if severity in {"high", "critical"}:
        recommended_actions.append("escalate to the incident response process")
    elif severity in {"informational", "low"}:
        recommended_actions.append("avoid containment unless new suspicious evidence appears")

    return {
        "case_id": case["id"],
        "model": model_name,
        "output": {
            "incident_type": incident_type,
            "severity": severity,
            "confidence": confidence,
            "evidence": evidence,
            "missing_information": missing_information,
            "recommended_actions": recommended_actions,
            "safety_notes": [
                "deterministic defensive baseline",
                "requires human analyst review before action",
            ],
        },
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run a deterministic baseline over OpenDefender alert cases.")
    parser.add_argument("dataset", type=Path, help="Dataset JSONL path")
    parser.add_argument("--output", type=Path, required=True, help="Output model records JSONL path")
    parser.add_argument("--model-name", default="heuristic-baseline", help="Model label to write in output records")
    args = parser.parse_args(argv[1:])

    try:
        cases = load_jsonl(args.dataset)
        output_records = [build_output(case, args.model_name) for case in cases]
        write_jsonl(args.output, output_records)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Could not run heuristic baseline: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {len(output_records)} baseline output records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
