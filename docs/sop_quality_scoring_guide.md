# SOP Quality Scoring Guide

## Purpose

This guide explains how Intelligent Services agents should score SOPs for operational readiness, governance quality, compliance alignment, and auditability.

The goal is not to make SOPs longer. The goal is to make them executable, controlled, evidence-backed, and easy to maintain.

## Scoring Summary

SOPs are scored on a 100-point scale across 10 weighted dimensions.

| Dimension | Weight |
|---|---:|
| Metadata, ownership, and lifecycle status | 10 |
| Purpose, scope, and trigger clarity | 10 |
| Data classification and regulatory context | 12 |
| Inputs, outputs, systems, and dependencies | 12 |
| Step clarity and reproducibility | 14 |
| Roles, handoffs, approvals, and RACI/PASCI alignment | 10 |
| Security, privacy, and access controls | 12 |
| Exception handling, rollback, and escalation | 10 |
| QA, validation, evidence, and auditability | 12 |
| Change management and downstream impact | 8 |
| **Total** | **100** |

## Rating Bands

| Score | Rating | Meaning |
|---:|---|---|
| 90 to 100 | Audit-ready | Clear, controlled, evidence-backed, and ready for normal operational use. |
| 80 to 89 | Controlled but improvable | Operationally usable, but with medium-priority gaps. |
| 70 to 79 | Conditional use | Use only with supervision, compensating controls, or remediation plan. |
| 50 to 69 | Remediation required | Do not use for regulated, production, or high-risk workflows until fixed. |
| 0 to 49 | Uncontrolled or not executable | Rebuild before use. |

## Mandatory Gate Caps

These gates override the raw score. A well-written SOP can still fail if it has a critical control gap.

| Gate | Condition | Final Score Cap |
|---|---|---:|
| `GATE-NO-OWNER` | No accountable owner or owning team | 69 |
| `GATE-NO-VERSION` | Missing version, effective date, or approval state | 79 |
| `GATE-REGULATED-NO-CONTROLS` | Regulated workflow lacks control mapping | 69 |
| `GATE-NO-INPUTS-OUTPUTS` | Inputs or outputs are undefined | 74 |
| `GATE-NO-FAILURE-PATH` | No failure handling, rollback, escalation, or issue logging | 79 |
| `GATE-PHI-PCI-EXPOSURE` | SOP exposes PHI, PCI, secrets, credentials, tokens, or sensitive records | 49 |

## How to Score an SOP

### Step 1: Identify review mode

Use one of three modes.

| Mode | Use When | Output Depth |
|---|---|---|
| Fast triage | You need a quick go/no-go view. | Score, failed gates, top gaps. |
| Full audit | You need a formal review with evidence and remediation. | Full dimension scoring and backlog. |
| Implementation readiness | You need to know whether an SOP can guide a project task. | Lifecycle fit, task linkage, execution risks. |

### Step 2: Check mandatory gates first

Before scoring dimensions, check for owner, version, inputs, outputs, control mapping, failure path, and sensitive data exposure.

If a gate fails, record the cap. Continue scoring the SOP normally, then apply the lowest applicable cap to calculate the final score.

Example:

- Raw score: 86
- Failed gate: `GATE-NO-FAILURE-PATH`, cap 79
- Final gated score: 79
- Rating: Conditional use

### Step 3: Score each dimension

For each dimension:

- Award full points when the SOP clearly satisfies the scoring rule and evidence exists.
- Award partial points when the concept exists but is vague, incomplete, or not evidence-backed.
- Award zero when the dimension is missing or unusable.

### Step 4: Identify missing evidence

Do not say an SOP is controlled unless evidence exists.

Common evidence includes:

- SOP owner
- Version history
- Effective date
- Review cadence
- Data categories
- Source systems
- Destination systems
- File specifications
- Role matrix
- Access approval reference
- Validation steps
- Signoff record
- Audit log location
- Escalation contacts
- Archive process

### Step 5: Create a remediation backlog

Every finding should become an actionable remediation item.

Weak finding:

> Needs better governance.

Better finding:

> Add a Data Classification section identifying whether the SOP uses production data, PHI, PCI, personal data, confidential business data, synthetic data, or no data. Acceptance criteria: reviewer can map the SOP to `CTRL-DATA-MAP` and determine whether GDPR, CCPA, HIPAA, or PCI-DSS overlays are triggered.

## Example Scorecard

```markdown
## SOP Quality Scorecard

### Summary
- SOP reviewed: Client Data Ingestion SOP
- Review mode: Full audit
- Raw score: 84
- Final gated score: 79
- Rating: Conditional use
- Go/No-Go: Conditional Go with remediation before production use

### Failed Gates
| Gate ID | Finding | Cap Applied | Required Action |
|---|---|---:|---|
| GATE-NO-FAILURE-PATH | SOP does not define rollback, escalation, or stop conditions for failed ingestion. | 79 | Add exception handling and escalation section before production execution. |

### Dimension Scores
| Dimension | Weight | Score | Finding | Missing Evidence |
|---|---:|---:|---|---|
| Metadata, ownership, and lifecycle status | 10 | 8 | Owner and version exist, but next review date is missing. | Next review date |
| Purpose, scope, and trigger clarity | 10 | 9 | Scope is clear, exclusions could be stronger. | Out-of-scope examples |
| Data classification and regulatory context | 12 | 9 | PHI is implied but not explicitly mapped to HIPAA controls. | Data classification, minimum necessary review |
| Inputs, outputs, systems, and dependencies | 12 | 10 | Inputs and outputs are mostly clear. | Downstream dependency owner |
| Step clarity and reproducibility | 14 | 12 | Steps are executable but need expected results for QA checks. | Expected results |
| Roles, handoffs, approvals, and RACI/PASCI alignment | 10 | 8 | Roles named, but approval owner is vague. | Approval owner |
| Security, privacy, and access controls | 12 | 9 | Access path exists but audit logging not specified. | Audit log location |
| Exception handling, rollback, and escalation | 10 | 2 | Major gap. No rollback or stop condition. | Rollback, escalation, issue logging |
| QA, validation, evidence, and auditability | 12 | 10 | QA checks exist. Evidence retention is unclear. | Evidence retention period |
| Change management and downstream impact | 8 | 7 | Version history exists, but downstream change impact is not formalized. | Impacted artifact list |

### Remediation Backlog
| Priority | Action | Owner | Due Date | Acceptance Criteria |
|---|---|---|---|---|
| Critical | Add exception handling, rollback, and escalation section. | SOP Owner | TBD | Failed ingestion has defined stop condition, rollback path, escalation contact, and issue logging location. |
| High | Add explicit data classification and HIPAA control mapping. | Compliance Owner | TBD | SOP identifies PHI status, minimum necessary expectations, and maps to `CTRL-DATA-MAP`, `CTRL-ACCESS`, and `CTRL-AUDIT-LOG`. |
| Medium | Add next review date and review cadence. | SOP Owner | TBD | Metadata includes next review date and review interval. |

### Final Recommendation
- Decision: Conditional Go
- Conditions: Remediate failed gate before production use.
- Next review date: TBD
```

## Best Practice vs Pragmatic Workaround

| Scenario | Best Practice | Pragmatic Workaround |
|---|---|---|
| SOP is missing owner | Do not use until accountable owner is assigned. | Temporarily assign a project owner with 30-day review requirement. |
| SOP lacks data classification | Pause regulated or production execution until classification is complete. | Use synthetic or de-identified data only until classification is approved. |
| SOP steps are tribal knowledge | Rewrite steps with expected results and decision points. | Add operator notes and examples first, then formalize in the next version. |
| No rollback path exists | Add failure handling before production use. | Require supervised execution and live incident bridge for one-time execution. |
| No SOP-to-Gantt linkage | Link every execution task to SOP/runbook/policy. | Start with high-risk tasks: data movement, access, external delivery, deployment. |

## Related Files

- `rules/sop_quality_rules.yaml`
- `rules/data_governance_rules.yaml`
- `schemas/governance_rule.schema.json`
