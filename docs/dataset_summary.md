# Dataset Summary

Source: `data/sample_alerts.jsonl`

This summary is generated from the dataset JSONL file. Regenerate it with:

```bash
python scripts/summarize_dataset.py data/sample_alerts.jsonl --output docs/dataset_summary.md
```

## Overview

| Metric | Value |
| --- | ---: |
| Total cases | 20 |
| First case ID | odtb-0001 |
| Last case ID | odtb-0020 |
| Categories | 6 |

## Category Distribution

| Value | Count |
| --- | ---: |
| cloud | 4 |
| collaboration | 2 |
| email | 3 |
| endpoint | 5 |
| identity | 4 |
| network | 2 |

## Expected Severity Distribution

| Value | Count |
| --- | ---: |
| informational | 1 |
| low | 7 |
| medium | 8 |
| high | 3 |
| critical | 1 |

## Expected Confidence Distribution

| Value | Count |
| --- | ---: |
| low | 1 |
| medium | 15 |
| high | 4 |

## Known Change Ticket Distribution

| Value | Count |
| --- | ---: |
| absent | 11 |
| present | 9 |

## Difficulty Distribution

| Value | Count |
| --- | ---: |
| easy | 3 |
| medium | 10 |
| hard | 7 |

## Tag Coverage

| Value | Count |
| --- | ---: |
| account_compromise | 2 |
| admin_account | 1 |
| ambiguous_context | 3 |
| api_key | 1 |
| bec | 1 |
| benign_admin | 5 |
| blocked_domain | 1 |
| build_system | 1 |
| bulk_email | 1 |
| change_ticket | 5 |
| cloud | 4 |
| collaboration | 2 |
| credential_access | 1 |
| critical_asset | 1 |
| data_access | 1 |
| deployment_window | 1 |
| dns | 1 |
| dormant_account | 1 |
| email | 3 |
| email_attachment | 1 |
| endpoint | 5 |
| execution | 1 |
| external_sharing | 1 |
| firewall_rule | 1 |
| forwarding_rule | 1 |
| guest_access | 1 |
| helpdesk | 1 |
| high_value_account | 1 |
| identity | 4 |
| mailbox_access | 1 |
| mfa | 2 |
| network | 2 |
| network_blocked | 1 |
| oauth | 1 |
| powershell | 1 |
| privilege_change | 1 |
| process_anomaly | 1 |
| remote_access_tool | 1 |
| service_account | 2 |
| staging | 1 |
| storage_exposure | 1 |
| vendor_onboarding | 1 |

## Failure Mode Coverage

| Value | Count |
| --- | ---: |
| access_review_reasoning | 1 |
| benign_context | 3 |
| change_ticket_reasoning | 3 |
| confidence_calibration | 4 |
| data_exposure_reasoning | 1 |
| evidence_grounding | 9 |
| missing_context_handling | 6 |
| over_escalation | 8 |
| safe_action_scoping | 7 |
| severity_calibration | 2 |
| under_escalation | 4 |

## Notes

- Counts describe the current sample dataset, not a production incident distribution.
- Cases are synthetic and defensive-only.
- Low and informational examples are included so benchmarks can measure over-escalation.
- Ambiguous examples are included so benchmarks can measure uncertainty handling.
