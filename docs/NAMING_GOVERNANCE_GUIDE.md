# Naming Governance Guide

## Purpose

Naming conventions are not cosmetic in regulated operational work. They are part of delivery governance, traceability, supportability, and incident prevention.

Bad naming creates avoidable fire alarms:

```text
Wrong client alias
Wrong file route
Wrong folder name
Wrong report label
Wrong Jira label
Wrong table/view name
Wrong program name
```

The key rule:

```text
External contractual names may be locked.
Internal canonical names should be standardized.
Physical delivery names must safely map between both.
```

## Why Naming Becomes Tricky

Many organizations sign BAAs, SOWs, order forms, or client-facing agreements using one set of names. Then internal teams use different names across Jira, Confluence, SQL, SFTP, dashboards, folders, reports, and support processes.

That creates two simultaneous truths:

| Naming Layer | Reality |
|---|---|
| External contract name | May be legally or commercially agreed and cannot be casually changed. |
| External delivery name | May need to match client-required file, folder, report, or route naming. |
| Internal canonical name | Should be clean, consistent, searchable, and operationally useful. |
| System physical name | Must be safe for file transfer, paths, jobs, reports, APIs, and tables. |
| Legacy alias | Must be traceable but should not drive new work. |

## Core Principle

Do not force one name to do every job.

Use a mapping model:

```text
External Contract Name
→ External Delivery Name
→ Internal Canonical Name
→ System Physical Name
→ Legacy Alias
```

The system should preserve each layer and require mapping evidence when names differ.

## External vs Internal Naming

### External Contract Name

Use when referencing:

- BAA
- SOW
- Contract
- Client-facing agreement
- Sales documentation
- Client-facing implementation scope

Governance rule:

```text
Do not change without Legal / Client Success approval.
```

### Internal Canonical Name

Use when referencing:

- Jira / ADO / Rally / Asana work
- Confluence docs
- SOPs
- Runbooks
- Internal reporting
- Data governance records
- Implementation playbooks

Governance rule:

```text
Must follow standard internal naming pattern and map back to external contract name.
```

### External Delivery Name

Use when referencing:

- SFTP/MFT folder
- File name
- Portal upload
- Report title
- API partner-facing label
- Client delivery route

Governance rule:

```text
Must match client requirements if required, while preserving internal mapping and delivery evidence.
```

## Recommended Naming Patterns

Configuration file:

```text
configs/naming_conventions/healthcare_delivery_default.json
```

### Internal Program Name

```text
{client_code}_{program_code}_{line_of_business}_{year}
```

Example:

```text
CENTENE_LAMP_MEDICAID_2026
```

Use for:

- Jira labels
- Confluence pages
- Runbooks
- Internal project references

### Delivery File Name

```text
{external_client_code}_{program_code}_{file_type}_{frequency}_{yyyymmdd}.{extension}
```

Example:

```text
CNC_LAMP_OPPORTUNITY_WEEKLY_20260531.csv
```

Do not include:

- Patient name
- Member ID
- PHI in filename
- Free-text description
- Ambiguous client aliases
- Spaces

### Internal Dataset Name

```text
{domain}_{client_code}_{program_code}_{dataset_purpose}_{grain}
```

Example:

```text
pharmacy_centene_lamp_opportunity_member_week
```

Use for:

- Tables
- Views
- dbt models
- Datasets
- Data marts

### Delivery Route Name

```text
route_{external_client_code}_{program_code}_{direction}_{environment}
```

Example:

```text
route_CNC_LAMP_outbound_prod
```

Use for:

- MFT routes
- SFTP folders
- Scheduled jobs
- Outbound delivery configurations

## Naming Evidence Requirements

When names differ across contract, delivery, internal docs, and systems, require a naming map.

Minimum fields:

| Field | Purpose |
|---|---|
| External Contract Name | Name from BAA/SOW/order form/client agreement. |
| External Delivery Name | Name visible to client or delivery system. |
| Internal Canonical Name | Internal standard name. |
| System Physical Name | File/folder/table/job/report/API path name. |
| Legacy Alias | Prior or alternate name. |
| Owner Role | Who owns the mapping. |
| Approval Source | Who approved the mapping. |
| Effective Date | When it applies. |
| Deprecated Date | If old name should no longer be used. |
| Downstream Impact | What breaks if this changes. |

## Launch Blockers

Naming issues should block launch when:

| Trigger | Why |
|---|---|
| External delivery name does not map to contract/client-approved name | Client confusion or wrong recipient risk. |
| Physical file/folder/route name is ambiguous | Wrong file delivery risk. |
| Naming uses PHI or sensitive values | Privacy/security risk. |
| Prod route includes test naming | Environment confusion risk. |
| Client alias is reused for multiple entities | Wrong-client data exposure risk. |
| Contract-locked name is changed without approval | Legal/client risk. |
| Internal canonical name does not exist | Documentation, support, QA, and reporting drift. |

## Best Practice vs Pragmatic Workaround

### Best Practice

Create a naming registry that tracks every external, internal, physical, and legacy name with owner, approval source, and downstream impact.

### Pragmatic Workaround

For early implementation, require a simple mapping table in the evidence packet:

```text
External Name | Internal Canonical Name | Delivery Name | Physical Name | Owner | Approval
```

This alone prevents many avoidable escalations.

## Where Naming Fits in the System

Naming governance should appear in:

| Module | Role |
|---|---|
| Data Governance App | Classifies names, prevents sensitive naming, creates mapping evidence. |
| Project / Product Planning App | Converts naming gaps into tickets, dependencies, timeline impacts, and Gantt items. |
| Implementation / Documentation App | Updates runbooks, file mover configs, Confluence pages, and delivery evidence. |

## Product Rule

If the system detects words like:

```text
client alias
external name
file name
folder name
route
SFTP
MFT
report name
contract name
SOW
BAA
legacy name
```

It should ask:

1. What is the external contract/client-approved name?
2. What is the internal canonical name?
3. What is the delivery/file/folder/report/API name?
4. What systems use this name?
5. Is the name reused by more than one client/program/entity?
6. Does the name include sensitive values?
7. Who owns the mapping?
8. Who approved the mapping?
9. What breaks if the name changes?
10. Should the old name be deprecated?

## Feedback Loop

Naming failures should feed back into:

| Team | Feedback |
|---|---|
| Sales | Avoid selling or promising inconsistent names without implementation review. |
| Client Success | Maintain client-facing name map and communicate approved delivery names. |
| Product | Define canonical product/program naming. |
| Implementation | Maintain mapping table and delivery evidence. |
| Data Engineering | Ensure physical system names are safe and traceable. |
| QA | Validate files, routes, folders, reports, and API labels match expected naming. |
| Support | Use canonical names and aliases to avoid confusion. |

## Why This Matters

Naming inconsistency is one of the ways organizations manufacture urgency.

The issue looks like a crisis:

```text
The wrong file went to the wrong place.
The client says this is not their program.
The report name does not match the SOW.
The route says one thing, the file says another.
No one knows what this acronym means.
```

But often the root cause is boring:

```text
No one owned the naming map.
External and internal names were mixed.
Legacy names were never deprecated.
Delivery routes were never validated against the contract/client-facing name.
```

This system should make those gaps visible before they become fire alarms.
