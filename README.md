# Intelligent Services

Intelligent Services is a framework and executable prototype for building AI-assisted operational systems that understand business documentation, project lifecycles, SOPs, governance requirements, compliance constraints, execution readiness, human review escalation, engineering data safety, platform-specific controls, and last-mile delivery risk.

## What This Repo Is Building

This repo is moving from static governance documentation toward an agent-ready operating model:

```text
Messy intake
→ Risk scoring
→ Platform/tool detection
→ Missing information detection
→ Timeline and launch readiness review
→ Ticket hierarchy generation
→ Jira / ADO / Rally / Asana export
→ Evidence packet
→ Human review routing
```

The core value is not generic ticket writing. The differentiated value is preventing bad intake, weak platform controls, unclear approvals, and last-mile delivery gaps from becoming production or compliance incidents.

## Current Product Spine

| Component | Purpose |
|---|---|
| Governed Delivery CLI | Converts messy intake into scorecards, tickets, evidence, and exports. |
| Platform Profile Engine | Detects named tools like Snowflake, dbt, SFTP, Tableau, APIs, and maps them to governance checks. |
| File Mover Governance | Treats delivery layers as governed control surfaces, not operational afterthoughts. |
| Ticket Exporters | Generates Jira, ADO, Rally, and Asana-friendly CSVs. |
| Evidence Packet Generator | Converts risks and controls into launch readiness evidence requirements. |
| Human Review Layer | Routes unresolved legal, privacy, security, compliance, product, and SME decisions. |

## Demo Paths

### Demo 1: Healthcare File Mover Delivery

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

Use this demo to show the last-mile delivery risk story:

```text
A technically correct pipeline can still create a compliance event if the file is mislabeled, routed to the wrong recipient, sent to the wrong destination, or launched without evidence.
```

### Demo 2: Platform Stack Governance

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/platform_stack_governance/messy_intake.md \
  --output-dir generated/free_trial/platform_stack_governance
```

Use this demo to show the platform-aware governance story:

```text
Engineers describe the tools they use.
The system translates those tools into required controls, tickets, evidence, and launch blockers.
```

Example platform stack:

```text
Snowflake → dbt → SFTP / MFT → Tableau / Power BI → API
```

## Generated Package Outputs

The package generator creates:

| Output | Purpose |
|---|---|
| `normalized_intake.json` | Structured version of the messy intake. |
| `scorecard.json` / `scorecard.md` | Governed delivery scorecard and launch readiness status. |
| `platform_profile_report.json` / `platform_profile_report.md` | Detected platforms, L0-L6 maturity scale, checks, evidence, and blockers. |
| `generated_ticket_hierarchy.json` / `generated_ticket_hierarchy.md` | Generated initiative, epic, story, and task hierarchy. |
| `jira_export.csv` | Jira import-friendly work items. |
| `ado_export.csv` | Azure DevOps import-friendly work items. |
| `rally_export.csv` | Rally import-friendly work items. |
| `asana_export.csv` | Asana import-friendly tasks. |
| `evidence_packet.json` / `evidence_packet.md` | Required launch evidence and missing approvals. |
| `launch_readiness_summary.md` | Executive go/no-go summary. |

## Platform Control Profiles

The platform profile engine supports L0-L6 maturity because different organizations have different governance depth.

| Level | Name | Meaning |
|---|---|---|
| L0 | Unknown | System/platform is named but governance controls are not identified. |
| L1 | Ad hoc | Engineers use the platform, but controls depend on tribal knowledge. |
| L2 | Documented | Basic owners, systems, data types, and workflows are documented. |
| L3 | Controlled | Required reviews, access controls, QA, and delivery gates exist. |
| L4 | Evidence-backed | Controls are documented with evidence, logs, approvals, and validation. |
| L5 | Automated / enforced | Controls are built into workflows, permissions, CI/CD, jobs, or platform policies. |
| L6 | Adaptive / org-specific | Organization-specific rules, control mappings, exception logic, and continuous monitoring apply. |

Current profiles:

| Profile | Detects | Governance Focus |
|---|---|---|
| Snowflake | Snowflake, warehouse, schema, stage, Snowpipe, COPY INTO, data share | Classification, tags, masking, row access, role access, access history, lineage, unload/export review. |
| dbt | dbt, models, seeds, snapshots, exposures, lineage | Model ownership, tests, lineage, documentation, derived field sensitivity, downstream exposure. |
| Generic File Mover | File transfer, outbound delivery, recipient, route, portal, shared folder | Destination validation, recipient allowlist, manifest, checksum, test delivery. |
| SFTP / MFT | SFTP, FTPS, MOVEit, GoAnywhere, MFT, folder paths | Host/path validation, folder permissions, keys, service accounts, route config. |
| Tableau / Power BI | Tableau, Power BI, dashboard, report, extract, RLS | Row-level security, report access, export permissions, subscriptions, refresh validation. |
| API Integration | API, REST, GraphQL, webhook, endpoint, payload, token | Auth, payload schema, secret handling, logging, monitoring, external endpoint approval. |

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

## Rule and Governance Layers

| Layer | Purpose |
|---|---|
| Data Governance Rule Pack | Classify data, map lifecycle, define access, track retention, and collect evidence. |
| SOP Quality Scoring | Score SOPs for ownership, reproducibility, controls, evidence, QA, and change impact. |
| Legal and SME Review | Route unclear legal, privacy, security, compliance, and risk acceptance questions. |
| Data / Dev Engineering Governance | Guide engineers through classification, masking, enrichment, QA, lineage, delivery, and deletion. |
| File Mover Governance | Validate destinations, recipients, routes, manifests, checksums, delivery logs, and monitoring. |
| Platform Profiles | Translate named tools into platform-specific checks, evidence, tickets, and launch blockers. |
| Ticket Builder / Export | Convert governed intake into Jira, ADO, Rally, and Asana-ready work. |

## Repository Structure

```text
.
├── README.md
├── INDEX.md
├── docs/
│   ├── data_dev_engineering_governance_guide.md
│   ├── data_governance_compliance_framework.md
│   ├── file_mover_delivery_governance_guide.md
│   ├── governed_delivery_cli_quickstart.md
│   ├── legal_sme_review_guide.md
│   └── sop_quality_scoring_guide.md
├── examples/
│   └── free_trial/
│       ├── healthcare_file_mover_delivery/
│       │   ├── analyzed_scorecard.md
│       │   ├── evidence_packet.md
│       │   ├── generated_ticket_hierarchy.md
│       │   ├── jira_export.csv
│       │   └── messy_intake.md
│       └── platform_stack_governance/
│           └── messy_intake.md
├── platform_profiles/
│   ├── api.profile.json
│   ├── dbt.profile.json
│   ├── generic_file_mover.profile.json
│   ├── sftp_mft.profile.json
│   ├── snowflake.profile.json
│   └── tableau_powerbi.profile.json
├── rules/
│   ├── data_dev_engineering_rules.yaml
│   ├── data_governance_rules.yaml
│   ├── legal_sme_review_rules.yaml
│   └── sop_quality_rules.yaml
├── schemas/
│   ├── evidence_packet.schema.json
│   ├── governance_rule.schema.json
│   ├── intake.schema.json
│   ├── platform_profile.schema.json
│   ├── scorecard.schema.json
│   └── ticket.schema.json
├── tests/
│   ├── test_governed_delivery_package.py
│   └── test_platform_stack_profiles.py
└── tools/
    ├── generate_governed_delivery_package.py
    ├── governed_delivery_cli.py
    ├── platform_exporters.py
    ├── platform_profile_augmenter.py
    └── platform_profile_detector.py
```

## How Agents Should Use These Rules

Agents should not simply summarize documents. They should evaluate whether a workflow is governed, traceable, executable, audit-ready, engineering-safe, platform-aware, and properly routed for human review where needed.

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
18. Which platforms/tools are named, such as Snowflake, dbt, SFTP, Tableau, Power BI, APIs, cloud storage, or orchestration tools?
19. What platform-specific checks, evidence, and launch blockers apply?
20. Can the request be converted into governed Jira, ADO, Rally, or Asana work items with proper hierarchy, approvals, and evidence requirements?

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
- Platform profiles should inject additional tickets and evidence requirements for named tools and systems.
- Messy intake should be converted into governed ticket hierarchy only when required missing information and launch blockers are visible.

## Run Tests

```bash
python -m pytest tests/test_governed_delivery_package.py tests/test_platform_stack_profiles.py
```

## Important Disclaimer

This repository provides an operational governance framework. It does not provide legal advice and does not replace review by legal, privacy, security, compliance, product, architecture, data engineering, or operational owners.

## Next Recommended Builds

- Move scoring and blocker logic into YAML-driven rule packs.
- Add direct Jira / ADO integration after CSV exports stabilize.
- Add a trial demo UI that shows messy intake to governed delivery package in one flow.
- Add a SOC 2 and audit control mapping rule pack.
- Add cloud storage, Databricks, GitHub, Airflow, Informatica, and Salesforce platform profiles.
- Add a contradiction detector for SOPs, Gantt charts, Jira/ADO work items, data maps, and delivery manifests.
