# Data and Dev Engineering Governance Guide

## Purpose

This guide helps Data Engineers, Dev Engineers, Architects, Product Owners, and Implementation teams evaluate whether tabular data, SQL extracts, Excel files, pipelines, transformations, enrichment logic, and outbound delivery jobs are safe to use.

The goal is practical: engineers should not need to be compliance experts to know when data is safe, restricted, or blocked.

## Core Concept

A system can be technically correct and still create a compliance event.

The pipeline may transform the data correctly, the SQL may be right, and the job may run successfully. But if the final file is labeled incorrectly, routed to the wrong recipient, delivered to the wrong MOVEit folder, or approved against the wrong client ID, the organization still has a compliance incident.

That is why this framework treats **last-mile delivery** as part of the control boundary.

## What Data Engineers Need to Know

### What can usually be used safely

| Data Type | Typical Use | Notes |
|---|---|---|
| Synthetic data | Development, demos, tests, AI prompts | Best default for non-production work. |
| Schema-only examples | Design, documentation, mapping, validation | Use fake values. |
| Aggregated metadata | Monitoring, quality checks, delivery tracking | Watch for small-cell risk. |
| Row counts and control totals | Reconciliation and QA | Preferred over sample records. |
| Batch IDs and run IDs | Lineage and troubleshooting | Should not encode sensitive values. |
| File hashes/checksums | Delivery validation | Preferred for file integrity checks. |
| Canonical client IDs | Routing and control matching | Safer than free-text client names. |

### What can be used only with controls

| Data Type | Required Controls |
|---|---|
| Production data | Approved purpose, access control, logging, environment restrictions. |
| PHI | HIPAA review, minimum necessary, access logging, BAA/vendor review when applicable. |
| Personal data | Privacy review, permitted use, retention, minimization, rights/notice review where applicable. |
| PCI/cardholder data | PCI-scoped environment, masking/tokenization, strict access, no unmanaged exports. |
| Client confidential data | Contract coverage, access control, retention, secure transfer. |
| Tokenized or pseudonymized data | Lookup table protection, re-identification review, purpose restriction. |
| Derived risk scores or flags | Source field lineage, permitted use, sensitivity review. |

### What should be blocked by default

| Data Type | Why Blocked |
|---|---|
| CVV, PIN, full magnetic stripe data | Sensitive authentication data should not be stored or used outside approved payment controls. |
| Passwords, API keys, private keys, secrets, tokens | Credential exposure risk. |
| Full PAN/card numbers outside PCI-controlled systems | PCI scope and exposure risk. |
| Live PHI or PCI in public repos, AI prompts, screenshots, tickets, email, or chat | Unmanaged disclosure risk. |
| Free-text clinical notes or ticket comments without review | Often contain unexpected sensitive data. |
| Unknown-source datasets | Cannot verify rights, owner, permitted use, or controls. |

## Data Input Scoring Model

Data submissions are scored on a 100-point scale.

| Dimension | Weight |
|---|---:|
| Dataset ownership, source, and purpose | 10 |
| Field-level classification and sensitivity | 14 |
| Data minimization and permitted tracking | 12 |
| Obfuscation, masking, tokenization, and de-identification controls | 12 |
| Data quality, schema, and validation controls | 10 |
| Environment separation and safe test data | 10 |
| Pipeline lineage, transformation, and reproducibility | 10 |
| Access, logging, and operational monitoring | 10 |
| External delivery and last-mile release controls | 14 |
| Retention, archive, deletion, and incident rollback | 8 |
| **Total** | **100** |

## Rating Bands

| Score | Rating | Meaning |
|---:|---|---|
| 92 to 100 | Audit-ready input | Dataset is classified, minimized, controlled, validated, and safe for the approved purpose. |
| 85 to 91 | Controlled input | Usable with normal controls, but minor evidence or documentation gaps remain. |
| 75 to 84 | Conditional use | Use only with constraints, remediation, or supervised handling. |
| 50 to 74 | Restricted or remediation required | Do not use broadly in development, testing, AI prompts, shared workspaces, or external delivery. |
| 0 to 49 | Blocked | Uncontrolled sensitive data, unclear ownership, prohibited fields, or unsafe routing risk. |

## Mandatory Gate Caps

| Gate | Condition | Final Score Cap |
|---|---|---:|
| Dataset unclassified | No sensitivity, owner, source, intended use, or regulatory overlay status. | 74 |
| Sensitive data in unmanaged tool | PHI, PCI, secrets, credentials, sensitive personal data, or client confidential data in unmanaged contexts. | 49 |
| Missing data owner | No accountable owner or steward. | 69 |
| No minimization review | More fields than needed and no justification. | 79 |
| No outbound delivery control | External delivery lacks allowlist, manifest, checksum, approval, or route validation. | 69 |
| Wrong-recipient risk | Routing depends on manual labels, free-text names, copied folders, or human-selected destinations. | 59 |
| Prohibited fields present | CVV, passwords, tokens, private keys, or unnecessary direct identifiers are present. | 49 |

## Field-Level Handling Rules

| Field Type | Examples | Default Handling |
|---|---|---|
| Direct identifiers | Name, email, phone, address, SSN, MRN, member ID | Remove, mask, tokenize, or replace with surrogate key unless required. |
| Quasi-identifiers | DOB, ZIP, rare condition, facility, small employer group | Generalize, aggregate, or suppress small cells. |
| Free text | Notes, comments, clinical narrative, ticket comments | Avoid, redact, or replace with synthetic text. |
| Credentials/secrets | API keys, passwords, tokens, private keys | Block, remove, rotate if exposed, escalate. |
| PCI sensitive authentication data | CVV, PIN, magnetic stripe data | Block by default. |
| Derived fields | Risk score, adherence flag, SDoH indicator | Review source lineage, permitted use, and new sensitivity. |
| Aggregates | Counts, rates, totals, averages | Usually safe, but check small-cell and re-identification risk. |

## Obfuscation Guidance

### Better patterns

| Need | Preferred Pattern |
|---|---|
| Join across datasets without exposing identity | Approved tokenization or keyed hashing with controlled salt/pepper. |
| Demo realistic data | Synthetic data generator. |
| Troubleshoot row movement | Batch ID, run ID, row count, file hash, and exception code. |
| Validate file delivery | Manifest, checksum, recipient allowlist, route validation. |
| Share sample schema | Fake values, no live records. |

### Risky patterns

| Pattern | Risk |
|---|---|
| Unsalted hash of email, SSN, MRN, or member ID | Often reversible through dictionary attack. |
| Masking only part of a unique identifier | May still allow re-identification. |
| Joining de-identified data with granular date and geography | Can recreate identity risk. |
| Using real screenshots in tickets | Can expose PHI, PCI, credentials, or customer data. |
| Free-text notes in AI prompts | May expose sensitive or privileged information. |

## Pipeline Lifecycle Stages

### 1. Intake and Source Approval

Required controls:

- Data owner
- System owner
- Source system
- Intended use
- Field classification
- Regulatory overlay review
- Intake manifest

Architect guidance:

Do not let ad hoc spreadsheets become production sources without ownership, schema, validation, and retention controls.

### 2. Extract and Landing

Required controls:

- Approved extract path
- Encrypted transfer
- Controlled landing zone
- Access logging
- Raw zone handling
- Reject/temp file controls

Architect guidance:

Never land sensitive extracts in personal folders, unmanaged shared drives, or local machines unless explicitly approved.

### 3. Transform, Enrich, and Join

Required controls:

- Transformation spec
- Code version
- Join logic
- Lineage
- Enrichment purpose
- Derived field sensitivity review

Architect guidance:

Enrichment can create new sensitivity. A harmless field can become risky when joined with member, patient, transaction, location, or behavior data.

### 4. Validate and Reconcile

Required controls:

- Row counts
- Control totals
- Schema validation
- Null thresholds
- Referential integrity
- Duplicate checks
- Exception reports

Architect guidance:

Prefer metadata validation over reviewing raw sensitive records.

### 5. QA and UAT

Required controls:

- Environment separation
- Test data strategy
- Production data exception approval where needed
- Role-based access
- QA evidence

Architect guidance:

Synthetic, masked, tokenized, or minimum-necessary data should be the default for testing.

### 6. Release and Deployment

Required controls:

- Code review
- Change ticket
- Deployment approval
- Rollback plan
- Runtime configuration review
- Environment validation

Architect guidance:

Configuration is code-adjacent. A pipeline can fail governance because a runtime config, recipient table, route, or folder is wrong even if the code is correct.

### 7. Outbound Delivery and Last-Mile Transfer

Required controls:

- Canonical client ID
- Approved recipient allowlist
- Delivery manifest
- Checksum/file hash
- Route validation
- Outbound quarantine
- Release approval
- Post-delivery confirmation
- Wrong-recipient stop condition

Architect guidance:

MOVEit, SFTP, shared folders, APIs, file labels, routing configs, and recipient lists are production control surfaces. They must be governed like code.

### 8. Archive, Retention, and Deletion

Required controls:

- Retention rule
- Archive process
- Deletion/purge process
- Legal hold rule
- Recall/rollback process
- Incident escalation path

Architect guidance:

Temporary files, rejects, logs, debug outputs, staging tables, and delivered files all need retention handling.

## Last-Mile Delivery Control Example

Weak process:

> Generate file, name it with the client name, manually upload to MOVEit folder.

Controlled process:

1. Generate file from approved run ID.
2. Create delivery manifest with canonical client ID, recipient ID, row count, control totals, checksum, and route ID.
3. Land file in outbound quarantine.
4. Validate file metadata against recipient allowlist.
5. Confirm file label matches canonical metadata.
6. Require release approval or automated release gate.
7. Deliver through approved route.
8. Capture delivery confirmation, timestamp, destination, and checksum.
9. Alert and stop if client ID, file label, destination, or route conflicts.

## SOC 2 Readiness Alignment

This guide is not a SOC 2 audit framework, but these controls support common SOC 2 readiness themes.

| Trust Services Category | Engineering Relevance |
|---|---|
| Security | Access control, secure transfer, encryption, logging, secrets management. |
| Availability | Job monitoring, failure handling, retry logic, rollback, delivery confirmation. |
| Processing Integrity | Completeness, accuracy, timeliness, schema checks, reconciliation, route validation. |
| Confidentiality | Data minimization, masking, tokenization, controlled delivery, retention/disposal. |
| Privacy | Permitted use, notice/consent alignment, minimization, de-identification, retention. |

The AICPA describes SOC 2 as reporting on controls relevant to security, availability, processing integrity, confidentiality, or privacy. HIPAA’s Security Rule also requires administrative, physical, and technical safeguards for electronic protected health information, while PCI DSS is the global standard for securing payment account data. These sources support why engineering controls cannot stop at code and must include access, transmission, validation, monitoring, and delivery controls. 

## Data / Dev Engineering Review Scorecard Template

```markdown
## Data / Dev Engineering Review Scorecard

### Summary
- Dataset / pipeline reviewed:
- Source system:
- Intended use:
- Environment:
- Raw score:
- Final gated score:
- Rating:
- Go/No-Go:

### Failed Gates
| Gate ID | Finding | Cap Applied | Required Action |
|---|---|---:|---|

### Field Classification
| Field | Classification | Use Allowed? | Required Handling |
|---|---|---|---|

### Dimension Scores
| Dimension | Weight | Score | Finding | Missing Evidence |
|---|---:|---:|---|---|

### Pipeline Stage Controls
| Stage | Control Status | Risk | Required Action |
|---|---|---|---|

### Last-Mile Delivery Review
| Control | Status | Evidence | Gap |
|---|---|---|---|

### Remediation Backlog
| Priority | Action | Owner | Due Date | Acceptance Criteria |
|---|---|---|---|---|
```

## Practical Engineering Rule

When in doubt, track the operation, not the person.

Better:

- `batch_id`
- `run_id`
- `row_count`
- `checksum`
- `route_id`
- `canonical_client_id`
- `validation_status`
- `exception_count`

Riskier:

- patient/member name
- full member ID in logs
- raw claim details in ticket comments
- screenshots of production records
- manually typed client labels
- free-text notes

## Related Files

- `rules/data_dev_engineering_rules.yaml`
- `rules/data_governance_rules.yaml`
- `rules/legal_sme_review_rules.yaml`
- `rules/sop_quality_rules.yaml`
