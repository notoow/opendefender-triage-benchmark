# Reviewer Notes

Source: `data/sample_alerts.jsonl`

This guide is generated from benchmark reference metadata. Regenerate it with:

```bash
python scripts/generate_reviewer_notes.py data/sample_alerts.jsonl --output docs/reviewer_notes.md
```

## Overview

| Metric | Value |
| --- | ---: |
| Dataset cases | 20 |
| Cases with reviewer notes | 14 |
| Ambiguous-context cases | 3 |
| Benign-admin cases | 5 |
| Known-change cases | 9 |

## Selection Criteria

Reviewer notes are included when a case has at least one of these signals:

- Tags: `ambiguous_context`, `benign_admin`, or `change_ticket`.
- Failure modes: `over_escalation`, `benign_context`, `change_ticket_reasoning`, or `missing_context_handling`.
- `alert_packet.known_change_ticket` is `true`.

## Case Index

| Case | Category | Difficulty | Expected Severity | Expected Confidence |
| --- | --- | --- | --- | --- |
| odtb-0001 | identity | medium | medium | medium |
| odtb-0003 | cloud | hard | low | medium |
| odtb-0005 | endpoint | hard | low | medium |
| odtb-0006 | identity | hard | high | medium |
| odtb-0007 | cloud | medium | medium | medium |
| odtb-0008 | email | medium | medium | medium |
| odtb-0009 | network | hard | low | medium |
| odtb-0011 | cloud | medium | low | medium |
| odtb-0013 | identity | medium | medium | medium |
| odtb-0014 | endpoint | easy | low | high |
| odtb-0015 | email | easy | informational | high |
| odtb-0016 | cloud | hard | medium | low |
| odtb-0018 | identity | medium | low | medium |
| odtb-0020 | collaboration | medium | low | medium |

## odtb-0001: Impossible travel sign-in followed by MFA denial

| Field | Value |
| --- | --- |
| Category | identity |
| Difficulty | medium |
| Expected incident type | `possible_account_compromise_attempt` |
| Expected severity | medium |
| Expected confidence | medium |
| Known change ticket | absent |

Reviewer focus:
- Check whether the response names missing information before drawing firm conclusions.
- Check whether confidence matches the available evidence and missing context.
- Check whether the response cites packet evidence instead of inventing facts.

Reference evidence:
- new country sign-in
- MFA push denied
- new device

Missing context to preserve:
- whether user was traveling
- recent password reset history
- device reputation

Safe action boundary:
- contact user through trusted channel
- review recent sessions
- revoke suspicious session if confirmed
- require password reset if compromise is likely

## odtb-0003: Service account created access key outside normal deployment window

| Field | Value |
| --- | --- |
| Category | cloud |
| Difficulty | hard |
| Expected incident type | `likely_authorized_admin_change_needs_verification` |
| Expected severity | low |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether the response verifies the change ticket before escalating or dismissing the alert.
- Check whether confidence matches the available evidence and missing context.

Reference evidence:
- known change ticket
- admin actor matches on-call
- no public exposure

Missing context to preserve:
- change ticket details
- whether key rotation was expected
- key storage location

Safe action boundary:
- verify ticket and on-call notes
- confirm key rotation policy
- ensure key is stored in approved secret manager

## odtb-0005: PowerShell administrative script triggered by patch tool

| Field | Value |
| --- | --- |
| Category | endpoint |
| Difficulty | hard |
| Expected incident type | `likely_benign_admin_activity` |
| Expected severity | low |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether benign operational context is weighed without ignoring suspicious signals.
- Check whether the response cites packet evidence instead of inventing facts.

Reference evidence:
- known patch window
- signed parent process
- change ticket present
- no network anomaly

Missing context to preserve:
- script hash
- patch job identifier
- admin approval record

Safe action boundary:
- verify change ticket
- compare script hash to approved baseline
- no containment unless new indicators appear

## odtb-0006: Privileged role assigned after password reset

| Field | Value |
| --- | --- |
| Category | identity |
| Difficulty | hard |
| Expected incident type | `possible_privilege_escalation_or_account_takeover` |
| Expected severity | high |
| Expected confidence | medium |
| Known change ticket | absent |

Reviewer focus:
- Check whether the response still escalates genuinely risky evidence.
- Check whether recommended actions stay defensive, proportionate, and human-reviewable.
- Check whether the response names missing information before drawing firm conclusions.

Reference evidence:
- password reset completed
- privileged role added
- new admin console session
- no change ticket

Missing context to preserve:
- whether reset was user initiated
- approver for role assignment
- session device reputation

Safe action boundary:
- verify with account owner through trusted channel
- review role assignment audit trail
- revoke new role if unauthorized
- preserve identity logs

## odtb-0007: Public storage policy change with no object access spike

| Field | Value |
| --- | --- |
| Category | cloud |
| Difficulty | medium |
| Expected incident type | `public_storage_exposure_needs_verification` |
| Expected severity | medium |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether severity reflects both potential impact and uncertainty.
- Check whether exposure risk is tied to the stated asset and access details.

Reference evidence:
- public read enabled
- change ticket present
- no download spike

Missing context to preserve:
- bucket data classification
- change ticket scope
- whether public access was intended

Safe action boundary:
- verify data classification
- compare policy to approved change
- restrict public access if unintended
- review object access logs

## odtb-0008: OAuth consent grant to unfamiliar mail application

| Field | Value |
| --- | --- |
| Category | email |
| Difficulty | medium |
| Expected incident type | `suspicious_oauth_consent` |
| Expected severity | medium |
| Expected confidence | medium |
| Known change ticket | absent |

Reviewer focus:
- Check whether the response cites packet evidence instead of inventing facts.
- Check whether the response names missing information before drawing firm conclusions.

Reference evidence:
- new OAuth consent
- mail read permission
- unfamiliar application

Missing context to preserve:
- application publisher reputation
- user confirmation
- tenant consent policy

Safe action boundary:
- review OAuth grant details
- contact user through trusted channel
- revoke grant if unauthorized
- inspect recent mailbox activity

## odtb-0009: Outbound connection burst to new ASN from build host

| Field | Value |
| --- | --- |
| Category | network |
| Difficulty | hard |
| Expected incident type | `ambiguous_network_activity_needs_context` |
| Expected severity | low |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether benign operational context is weighed without ignoring suspicious signals.
- Check whether the response names missing information before drawing firm conclusions.

Reference evidence:
- deployment window active
- build host asset
- new destination ASN
- no malware alert

Missing context to preserve:
- destination reputation
- release job details
- expected dependency downloads

Safe action boundary:
- verify deployment job
- check destination reputation
- compare traffic to known release patterns
- continue monitoring for repeated anomalies

## odtb-0011: Firewall rule opened to internet by approved automation

| Field | Value |
| --- | --- |
| Category | cloud |
| Difficulty | medium |
| Expected incident type | `likely_authorized_temporary_exposure_needs_review` |
| Expected severity | low |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether the response verifies the change ticket before escalating or dismissing the alert.

Reference evidence:
- automation service account
- change ticket present
- rule deleted after 10 minutes
- staging environment

Missing context to preserve:
- approved exposure duration
- target port purpose
- whether staging contains sensitive data

Safe action boundary:
- verify ticket scope
- confirm rule removal
- review exposure window logs
- document exception if approved

## odtb-0013: Repeated failed MFA prompts with no successful sign-in

| Field | Value |
| --- | --- |
| Category | identity |
| Difficulty | medium |
| Expected incident type | `possible_mfa_fatigue_attempt` |
| Expected severity | medium |
| Expected confidence | medium |
| Known change ticket | absent |

Reviewer focus:
- Check whether the response names missing information before drawing firm conclusions.
- Check whether confidence matches the available evidence and missing context.

Reference evidence:
- multiple MFA push denials
- password authentication succeeded before denials
- no successful sign-in

Missing context to preserve:
- user confirmation
- source IP reputation
- password reset history

Safe action boundary:
- contact user through trusted channel
- reset password if user did not initiate
- review sign-in sources
- consider temporary sign-in risk policy

## odtb-0014: Known IT remote support tool installed during helpdesk ticket

| Field | Value |
| --- | --- |
| Category | endpoint |
| Difficulty | easy |
| Expected incident type | `likely_authorized_remote_support` |
| Expected severity | low |
| Expected confidence | high |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether benign operational context is weighed without ignoring suspicious signals.

Reference evidence:
- helpdesk ticket present
- signed installer
- installed by IT admin
- no suspicious network destination

Missing context to preserve:
- ticket requester confirmation
- approved tool version
- scheduled removal time

Safe action boundary:
- verify ticket requester
- confirm approved tool version
- ensure removal or policy compliance after support session

## odtb-0015: Mass send alert after newsletter campaign approval

| Field | Value |
| --- | --- |
| Category | email |
| Difficulty | easy |
| Expected incident type | `likely_authorized_bulk_email_campaign` |
| Expected severity | informational |
| Expected confidence | high |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether severity reflects both potential impact and uncertainty.

Reference evidence:
- approved campaign window
- messages match newsletter template
- low bounce rate
- no phishing detections

Missing context to preserve:
- campaign approval record
- recipient list owner
- sending platform logs

Safe action boundary:
- verify campaign approval
- monitor bounce and complaint rates
- no account containment based on current evidence

## odtb-0016: API key used from new region for low-privilege service

| Field | Value |
| --- | --- |
| Category | cloud |
| Difficulty | hard |
| Expected incident type | `ambiguous_service_account_usage` |
| Expected severity | medium |
| Expected confidence | low |
| Known change ticket | absent |

Reviewer focus:
- Check whether confidence matches the available evidence and missing context.
- Check whether the response names missing information before drawing firm conclusions.
- Check whether the response cites packet evidence instead of inventing facts.

Reference evidence:
- API key used from new region
- low privilege service account
- read-only calls

Missing context to preserve:
- job deployment location
- key rotation history
- region allowlist
- service owner confirmation

Safe action boundary:
- contact service owner
- review recent deployment changes
- rotate key if use is unauthorized
- monitor for privilege or call pattern changes

## odtb-0018: Dormant account sign-in from managed device

| Field | Value |
| --- | --- |
| Category | identity |
| Difficulty | medium |
| Expected incident type | `likely_authorized_account_reactivation_needs_verification` |
| Expected severity | low |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether the response verifies the change ticket before escalating or dismissing the alert.

Reference evidence:
- managed device
- MFA satisfied
- manager reactivation request present
- no privilege change

Missing context to preserve:
- HR return date
- user confirmation
- device compliance status

Safe action boundary:
- verify reactivation request
- confirm device compliance
- review first-session activity
- no containment unless new indicators appear

## odtb-0020: Guest user added to team with owner approval

| Field | Value |
| --- | --- |
| Category | collaboration |
| Difficulty | medium |
| Expected incident type | `likely_authorized_guest_access_needs_review` |
| Expected severity | low |
| Expected confidence | medium |
| Known change ticket | present |

Reviewer focus:
- Check whether the response avoids disruptive containment when the packet supports verification first.
- Check whether the response treats access review as a verification task, not proof of compromise.

Reference evidence:
- owner approval recorded
- limited channel access
- no sensitive label present
- vendor onboarding context

Missing context to preserve:
- vendor contract status
- guest expiration date
- domain approval status

Safe action boundary:
- verify owner approval
- set guest access expiration
- confirm allowed channels
- monitor initial access activity

## Notes

- These notes are intended for benchmark review and result interpretation.
- They do not add new facts beyond the dataset record; reviewers should score only against the alert packet.
- The notes emphasize uncertainty handling, evidence grounding, and proportionate defensive action.
