# Intelligent Services

Intelligent Services is a framework for building AI-assisted operational systems that can understand business documentation, project lifecycles, SOPs, governance requirements, compliance constraints, execution readiness, human review escalation, engineering data safety, and last-mile delivery risk.

## Current Focus

The first rule packs establish a data governance, compliance, SOP quality, Legal/SME review, Data/Dev Engineering governance, file mover governance, and governed ticket-building foundation for agents that need to reason across:

- Strategy documents
- SOPs and runbooks
- Gantt charts and project plans
- Jira, ADO, Rally, or Asana work items
- Data maps and system dependencies
- Contracts, SOWs, DPAs, BAAs, and vendor terms
- Excel, CSV, SQL, database tables, views, and pipeline outputs
- Data engineering lifecycle stages from intake through delivery and deletion
- Managed file transfer, SFTP, APIs, cloud storage, portals, report exports, secure email, shared folders, batch jobs, and other file mover or delivery-layer controls
- Access, vendor, privacy, security, and compliance evidence
- Operational readiness and audit-readiness scoring
- Human review routing when AI cannot safely determine an answer

## Product Direction

The repo is moving from static governance documentation toward an agent-ready operating model:

```text
Messy intake
→ Risk scoring
→ Missing information detection
→ Timeline and launch readiness review
→ Ticket hierarchy generation
→ Jira / ADO / Rally / Asana export
→ Evidence packet
→ Human review routing
```

The core value is not generic ticket writing. The differentiated value is preventing bad intake, weak delivery controls, unclear approvals, and last-mile file movement gaps from becoming production or compliance incidents.

## Free Trial Demo Concept

The repo now includes a synthetic free-trial example under:

```text
examples/free_trial/healthcare_file_mover_delivery/
```

This scenario demonstrates how an agent should take a messy healthcare delivery request and generate:

- A governed delivery scorecard
- Missing information questions
- Launch blockers
- A platform-neutral ticket hierarchy
- Jira-ready CSV export
- Evidence packet requirements
- File mover delivery controls

The demo is intentionally vendor-neutral. MOVEit is one possible file mover, but the model applies to any managed file transfer platform, SFTP, API, cloud storage bucket, client portal, reporting export, secure email workflow, shared folder, batch job, or manual upload process.

## Key Differentiator: File Mover and Last-Mile Delivery Governance

A system can be technically correct and still create a compliance event.

The SQL may be correct. The pipeline may run. The file may generate successfully. But the organization can still fail if the final delivery layer sends the wrong file, to the wrong recipient, through the wrong route, with the wrong label, or without evidence.

This repository treats the delivery layer as part of the governed control boundary.

Examples of governed delivery layers include:

| Delivery Layer | Examples |
|---|---|
| Managed file transfer | MOVEit, GoAnywhere MFT, Kiteworks, Cleo, IBM Sterling, Axway |
| SFTP / FTPS | Client SFTP, vendor SFTP, internal secure FTP |
| Cloud storage | AWS S3, Azure Blob, Google Cloud Storage |
| Collaboration storage | SharePoint, OneDrive, Google Drive, Box, Dropbox Business |
| API delivery | REST API, GraphQL API, webhook, partner endpoint |
| Reporting exports | Tableau, Power BI, Looker, CSV download, scheduled reports |
| Portal uploads | Client portal, vendor portal, payer portal, pharmacy portal |
| Email delivery | Secure email, encrypted attachment, manual attachment |
| Batch orchestration | Airflow, Informatica, ActiveBatch, cron, SQL Agent, dbt Cloud |
| Manual transfer | Local upload, ad hoc shared folder, one-off script |

## Data Governance Rule Pack

The repository includes a baseline rule system for operational governance and regulatory awareness.

### Included Rule Areas

| Area | Purpose |
|---|---|
| Baseline data governance | Classify data, map lifecycle, define access, track retention, and collect evidence. |
| Compliance program elements | Data lifecycle management, consent, security controls, policies, training, third-party risk, and ownership. |
| Regulatory overlays | GDPR, CCPA/CPRA, HIPAA, and PCI-DSS trigger logic and required controls. |
| Project lifecycle mapping | Connect initiation, planning, execution, monitoring, and closure to required documents. |
| Document governance | Link SOPs to project tasks, detect contradictions, version artifacts, and enforce source of truth rules. |
| Agent evaluation | Require agents to identify rule IDs, missing evidence, assumptions, and escalation conditions. |

## SOP Quality Scoring System

The repository includes a weighted 100-point SOP scoring model.

### Rating Bands

| Score | Rating | Meaning |
|---:|---|---|
| 90 to 100 | Audit-ready | Clear, controlled, evidence-backed, and ready for normal operational use. |
| 80 to 89 | Controlled but improvable | Operationally usable, but with medium-priority gaps. |
| 70 to 79 | Conditional use | Use only with supervision, compensating controls, or remediation plan. |
| 50 to 69 | Remediation required | Do not use for regulated, production, or high-risk workflows until fixed. |
| 0 to 49 | Uncontrolled or not executable | Rebuild before use. |

### Scored Dimensions

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

### Mandatory Gate Caps

Some findings cap the final score even when the raw score is high.

| Gate | Score Cap |
|---|---:|
| Missing accountable owner | 69 |
| Missing version, effective date, or approval state | 79 |
| Regulated workflow missing control mapping | 69 |
| Missing inputs or outputs | 74 |
| Missing exception or failure path | 79 |
| SOP exposes PHI, PCI, secrets, credentials, tokens, or sensitive records | 49 |

## Legal and SME Review Layer

The repository includes a human review routing layer for situations where AI rules can detect risk, but should not make the final decision.

### Review Philosophy

The AI should:

- Identify the specific project section that requires human judgment.
- Explain why the AI cannot safely determine the answer.
- Route to the minimum necessary reviewers.
- Provide exact decision questions and options.
- Redact sensitive data where possible.
- Track the final decision back to impacted SOPs, tickets, project plans, contracts, data maps, and scores.

The AI should not:

- Provide legal advice.
- Mark unclear regulatory applicability as resolved.
- Hide unresolved assumptions inside polished language.
- Send broad, unfocused review requests when a specific excerpt or section is enough.
- Include unnecessary PHI, PCI, secrets, credentials, or sensitive records in review packets.

### Review Triggers

| Trigger ID | Trigger | Default Reviewers |
|---|---|---|
| `LEGAL-TRIGGER-001` | Regulatory applicability unclear | Legal, Privacy, Compliance |
| `LEGAL-TRIGGER-002` | External-facing claim or customer commitment | Legal, Product Owner, Operational SME |
| `LEGAL-TRIGGER-003` | Contract, SOW, DPA, BAA, or vendor terms ambiguity | Legal, Privacy, Security, Compliance |
| `LEGAL-TRIGGER-004` | Sensitive data handling ambiguity | Privacy, Security, Compliance |
| `LEGAL-TRIGGER-005` | AI limitation or low-confidence classification | Operational SME, Privacy, Compliance |
| `LEGAL-TRIGGER-006` | Cross-border, offshore, or third-party access | Legal, Privacy, Security, Compliance |
| `LEGAL-TRIGGER-007` | Risk acceptance required | Legal, Security, Compliance, Product Owner |

## Data and Dev Engineering Governance Layer

The repository includes a field-level and pipeline-level engineering control model for data submitted through Excel, CSV, SQL, database tables, views, extracts, and delivery files.

### Engineering Rule Areas

| Area | Purpose |
|---|---|
| Data input scoring | Rates whether submitted tabular data is safe, controlled, restricted, or blocked. |
| Field-level classification | Classifies each column as public, internal, confidential, personal data, PHI, PCI, credential, secret, quasi-identifier, derived, aggregate, or free text. |
| Obfuscation and minimization | Defines when to remove, mask, tokenize, hash, generalize, aggregate, or suppress data. |
| Safe enrichment | Checks whether joins, derived fields, risk scores, flags, geocodes, or model features create new sensitivity. |
| Pipeline lifecycle controls | Covers intake, extract, transform, validate, QA/UAT, release, delivery, archive, and deletion. |
| Last-mile delivery controls | Treats file movers, delivery jobs, APIs, shared folders, file names, manifests, recipient lists, and route configs as governed control surfaces. |
| SOC 2 readiness alignment | Maps engineering controls to security, availability, processing integrity, confidentiality, and privacy themes. |

### Data Input Rating Bands

| Score | Rating | Meaning |
|---:|---|---|
| 92 to 100 | Audit-ready input | Dataset is classified, minimized, controlled, validated, and safe for the approved purpose. |
| 85 to 91 | Controlled input | Usable with normal controls, but minor evidence or documentation gaps remain. |
| 75 to 84 | Conditional use | Use only with constraints, remediation, or supervised handling. |
| 50 to 74 | Restricted or remediation required | Do not use broadly in development, testing, AI prompts, shared workspaces, or external delivery. |
| 0 to 49 | Blocked | Uncontrolled sensitive data, unclear ownership, prohibited fields, or unsafe routing risk. |

### Data / Dev Engineering Gate Caps

| Gate | Score Cap |
|---|---:|
| Dataset is unclassified | 74 |
| Sensitive data appears in unmanaged tool, prompt, ticket, screenshot, repo, or email | 49 |
| Missing data owner or system owner | 69 |
| No field minimization review | 79 |
| External delivery lacks outbound controls | 69 |
| Wrong-recipient or wrong-client routing risk | 59 |
| Prohibited fields are present for intended use | 49 |

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── data_dev_engineering_governance_guide.md
│   ├── data_governance_compliance_framework.md
│   ├── file_mover_delivery_governance_guide.md
│   ├── legal_sme_review_guide.md
│   └── sop_quality_scoring_guide.md
├── examples/
│   └── free_trial/
│       └── healthcare_file_mover_delivery/
│           ├── analyzed_scorecard.md
│           ├── evidence_packet.md
│           ├── generated_ticket_hierarchy.md
│           ├── jira_export.csv
│           └── messy_intake.md
├── rules/
│   ├── data_dev_engineering_rules.yaml
│   ├── data_governance_rules.yaml
│   ├── legal_sme_review_rules.yaml
│   └── sop_quality_rules.yaml
└── schemas/
    ├── evidence_packet.schema.json
    ├── governance_rule.schema.json
    ├── intake.schema.json
    ├── scorecard.schema.json
    └── ticket.schema.json
```

## How Agents Should Use These Rules

Agents should not simply summarize documents. They should evaluate whether a workflow is governed, traceable, executable, audit-ready, engineering-safe, and properly routed for human review where needed.

For each project or workflow, agents should ask:

1. What data categories are involved?
2. Which geography, industry, client, vendor, and system context applies?
3. What is the business purpose and approved use?
4. What regulations or contractual controls may be triggered?
5. What documents govern the lifecycle phase of the work?
6. What evidence proves the control is operating?
7. Who owns the decision, system, process, and documentation?
8. Is the SOP executable without tribal knowledge?
9. Does the SOP define failure handling, validation, and audit evidence?
10. What score, gate caps, and remediation actions apply?
11. Is there any issue AI cannot safely decide?
12. Which Legal, Privacy, Security, Compliance, Product, or SME reviewer should receive a review packet?
13. Are submitted data fields classified and minimized?
14. Can the data be safely tracked, enriched, transformed, logged, or delivered?
15. Does the last-mile delivery layer prevent wrong-client or wrong-recipient release?
16. What file mover or delivery layer is being used?
17. Is the destination, recipient allowlist, route, naming convention, manifest, checksum, and delivery evidence validated?
18. Can the request be converted into governed Jira, ADO, Rally, or Asana work items with proper hierarchy, approvals, and evidence requirements?

## Regulatory Overlay Logic

The system separates baseline governance controls from regulatory overlays.

| Overlay | Trigger Examples |
|---|---|
| GDPR | EU/EEA personal data, EU/EEA users, monitoring behavior, cross-border transfer. |
| CCPA/CPRA | California resident personal information, consumer rights, sale/share/opt-out workflows. |
| HIPAA | PHI, claims, eligibility, medication, payer/provider/business associate workflows. |
| PCI-DSS | Cardholder data, payment workflows, cardholder data environment systems. |

## Documentation Governance Logic

The system should enforce the following:

- Strategy documents define scope during initiation.
- Gantt charts and dependency maps guide planning.
- SOPs and runbooks guide execution.
- Audit logs, risk records, and evidence indexes support monitoring.
- Archive manifests and retention records support closure.
- Every execution task should link to an SOP, runbook, policy, or decision record.
- Outdated versions must be archived and marked inactive.
- Contradictions across documents must be logged and resolved by an owner.
- SOPs should receive a raw score, final gated score, rating band, and remediation backlog.
- Legal/SME review packets should be generated for unresolved regulatory, contractual, privacy, security, operational, or risk acceptance questions.
- Data submissions should receive field-level classification, safe-use determination, engineering score, and last-mile delivery review.
- File mover workflows should receive route validation, recipient validation, manifest/checksum review, delivery evidence review, monitoring review, and launch blocker detection.
- Messy intake should be converted into governed ticket hierarchy only when required missing information and launch blockers are visible.

## Important Disclaimer

This repository provides an operational governance framework. It does not provide legal advice and does not replace review by legal, privacy, security, compliance, product, architecture, data engineering, or operational owners.

## Next Recommended Builds

- Add executable rule-engine package for intake, timeline, data, file mover, ticket, and launch readiness scoring.
- Add ticket-builder package for Jira, ADO, Rally, and Asana outputs.
- Add a lightweight CLI that reads synthetic intake and produces scorecard, ticket hierarchy, CSV export, and evidence packet.
- Add a trial demo UI that shows messy intake to governed delivery package in one flow.
- Add a SOC 2 and audit control mapping rule pack.
- Add a project document ingestion workflow.
- Add a contradiction detector for SOPs, Gantt charts, Jira/ADO work items, data maps, and delivery manifests.
- Add example scorecards and review packets for healthcare, finance, retail, SaaS, and public sector workflows.
