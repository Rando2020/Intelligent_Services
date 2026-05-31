# UI Backend Contract

## Purpose

This document defines what the live demo UI should expect from the backend API.

Claude or any UI builder should use this contract when wiring the live demo.

## Backend URL

Local default:

```text
http://localhost:8787/api/analyze
```

The UI should allow this to be overridden through configuration.

## Request

```http
POST /api/analyze
Content-Type: application/json
```

```json
{
  "title": "Platform Stack Governance Demo",
  "intake": "We use Snowflake, dbt, SFTP, Tableau, and an API. Legal and Security are not confirmed."
}
```

## Response: Required Top-Level Fields

```json
{
  "request_id": "uuid",
  "summary": {},
  "normalized_intake": {},
  "scorecard": {},
  "rule_match_report": {},
  "platform_profile_report": {},
  "tickets": [],
  "prioritized_tickets": [],
  "evidence_packet": {},
  "exports": {},
  "markdown": {},
  "generator_log": "..."
}
```

## Summary Fields

The UI should primarily render from `summary`.

```json
{
  "overall_score": 64,
  "engine_score": 62,
  "display_score_explanation": "Display readiness reflects...",
  "overall_rating": "at_risk",
  "launch_position": "not_launchable",
  "matched_rule_count": 4,
  "detected_platform_count": 2,
  "ticket_count": 22,
  "launch_blocker_count": 8,
  "evidence_item_count": 60
}
```

## Score Rendering Rules

| Condition | UI Treatment |
|---|---|
| `overall_score >= 80` | Show controlled / green styling only if `launch_position` is not blocked. |
| `overall_score >= 65 && overall_score < 80` | Show at-risk / yellow styling. |
| `overall_score < 65` | Show blocked / red styling. |
| `launch_position == not_launchable` | Always show blocked state, even if score looks high. |
| `detected_platform_count == 0` and regulated data exists | Show “platform / architecture unknown” warning. |

## Important UX Rule

Do not display only the first raw `tickets` entries.

Use:

```json
prioritized_tickets
```

first.

Why: baseline tickets are generated first, while dynamic rule and platform tickets are appended later. `prioritized_tickets` is sorted so rule-driven, platform-specific, and launch-blocker work appears first.

## Primary UI Sections

### 1. Readiness Score

Use:

```text
summary.overall_score
summary.launch_position
summary.display_score_explanation
```

Recommended copy:

```text
Readiness: 64 / 100
Launch position: Not launchable
Reason: Display readiness reflects X launch blockers, Y matched rules, Z platform profiles, and N missing evidence items.
```

### 2. Risk/Rule Matches

Use:

```text
rule_match_report.matched_rules
```

Each rule includes:

```json
{
  "id": "GOV-DELIVERY-004",
  "name": "Sparse healthcare product intake requires discovery before readiness",
  "category": "intake_quality",
  "severity": "critical",
  "finding": "...",
  "required_action": "...",
  "launch_blocker": true,
  "required_evidence": [],
  "recommended_ticket": {}
}
```

Recommended UI:

| Column | Field |
|---|---|
| Rule | `id` + `name` |
| Severity | `severity` |
| Finding | `finding` |
| Required Action | `required_action` |
| Launch Blocker | `launch_blocker` |

### 3. Platform Profiles

Use:

```text
platform_profile_report.detected_profiles
```

Each profile includes:

```json
{
  "id": "PLATFORM-SNOWFLAKE",
  "name": "Snowflake Control Profile",
  "platform_type": "data_warehouse",
  "matched_keywords": ["snowflake"],
  "suggested_current_level": "L1",
  "required_checks": [],
  "required_evidence": [],
  "launch_blockers": []
}
```

Recommended UI:

- Profile chip/cards
- Suggested current level
- Required checks count
- Launch blockers count

### 4. Generated Tickets

Use:

```text
prioritized_tickets
```

Important fields:

| Field | Purpose |
|---|---|
| `title` | Ticket summary |
| `work_item_type` | Initiative / epic / story / task |
| `owner_role` | Suggested owner |
| `launch_blocker` | Whether this blocks launch |
| `source_rule_id` | Rule-driven traceability |
| `parent_external_id` | Hierarchy |
| `acceptance_criteria` | Story criteria |
| `evidence_required` | Required artifacts |

Recommended visual ordering:

1. Rule-driven tickets where `source_rule_id` exists.
2. Platform profile tickets where `parent_external_id == EPIC-PLATFORM-001`.
3. Launch-blocker tickets.
4. Other stories/tasks.
5. Epics and initiatives.

### 5. Evidence Packet

Use:

```text
evidence_packet.evidence_items
```

Important fields:

| Field | Purpose |
|---|---|
| `evidence_area` | Rule/profile/baseline evidence area |
| `required_artifact` | What must be attached |
| `owner_role` | Owner |
| `status` | Usually missing in demo |
| `launch_blocker` | Whether missing artifact blocks launch |

### 6. Exports

Use:

```text
exports.jira_csv
exports.ado_csv
exports.rally_csv
exports.asana_csv
```

The UI should download these exact strings as CSV files.

## Sparse Healthcare Intake Expected Behavior

This prompt is a calibration case:

```text
we need to launch a pharmacy product. We are taking in eligibility and claims data
```

Expected behavior:

| Field | Expected |
|---|---|
| `summary.overall_rating` | `at_risk` |
| `summary.launch_position` | `not_launchable` |
| `summary.overall_score` | `<= 64` |
| `rule_match_report.matched_rules` | Includes `GOV-DELIVERY-004` |
| `prioritized_tickets` | Includes `Complete discovery for sparse regulated healthcare product intake` |
| `platform_profile_report.detected_platform_count` | `0` unless a platform is named |

## UX Warnings To Add

### Regulated Data + Sparse Intake

Trigger when:

```text
GOV-DELIVERY-004 is matched
```

Message:

```text
This intake references regulated healthcare data but does not provide enough governance, architecture, approval, QA, or delivery detail to be considered ready for implementation.
```

### No Platform Detected

Trigger when:

```text
detected_platform_count == 0
```

Message:

```text
No platform or delivery architecture was detected. Ask for data source, transformation layer, reporting layer, delivery method, destination, access model, and owner.
```

### Not Launchable

Trigger when:

```text
summary.launch_position == "not_launchable"
```

Message:

```text
This request should not move to production launch until blockers and required evidence are resolved or formally accepted by authorized owners.
```

## Error Handling

If backend is unavailable:

```text
Backend unavailable. Showing local preview only.
```

The live demo should clearly label local preview as non-authoritative.

## Safety Banner

Always show:

```text
Do not paste real PHI, PCI, credentials, secrets, or live client data into this demo. Use synthetic or redacted intake only.
```
