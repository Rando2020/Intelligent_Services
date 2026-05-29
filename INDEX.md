# Intelligent Services Index

## Purpose

This index organizes the Intelligent Services repo into its core governance components, executable tools, demo flows, schemas, profiles, and next-build areas.

The repo is designed to help AI agents convert messy operational intake into governed delivery work:

```text
Messy intake
→ risk score
→ platform profile detection
→ launch blockers
→ ticket hierarchy
→ platform exports
→ evidence packet
→ launch readiness summary
```

## 1. Core Framework Components

| Component | Location | Purpose |
|---|---|---|
| Data Governance Framework | `docs/data_governance_compliance_framework.md` | Baseline governance, regulatory overlays, lifecycle controls, and evidence requirements. |
| SOP Quality Scoring | `docs/sop_quality_scoring_guide.md` | Scores SOPs for clarity, ownership, execution readiness, controls, and auditability. |
| Legal / SME Review | `docs/legal_sme_review_guide.md` | Routes unresolved legal, privacy, security, compliance, and SME decisions. |
| Data / Dev Engineering Governance | `docs/data_dev_engineering_governance_guide.md` | Guides engineers through classification, masking, transformation, enrichment, QA, delivery, and deletion. |
| File Mover Governance | `docs/file_mover_delivery_governance_guide.md` | Treats delivery layers as governed control surfaces. |
| CLI Quickstart | `docs/governed_delivery_cli_quickstart.md` | Explains how to run the governed delivery package generator. |

## 2. Executable Tools

| Tool | Location | Purpose |
|---|---|---|
| Governed Delivery CLI | `tools/governed_delivery_cli.py` | Core prototype that creates scorecard, tickets, Jira CSV, evidence packet, and launch summary. |
| Package Generator | `tools/generate_governed_delivery_package.py` | Runs the full package flow, including platform profiles and platform exports. |
| Platform Exporters | `tools/platform_exporters.py` | Creates ADO, Rally, and Asana CSV exports from generated ticket JSON. |
| Platform Profile Detector | `tools/platform_profile_detector.py` | Detects named tools/platforms and creates platform profile report. |
| Platform Profile Augmenter | `tools/platform_profile_augmenter.py` | Injects platform-profile tickets and evidence into the generated package. |

## 3. Demo Paths

### 3.1 Healthcare File Mover Delivery Demo

Location:

```text
examples/free_trial/healthcare_file_mover_delivery/
```

Purpose:

Shows that a technically correct pipeline can still fail governance if the final delivery layer is wrong.

Run:

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

### 3.2 Platform Stack Governance Demo

Location:

```text
examples/free_trial/platform_stack_governance/
```

Purpose:

Shows that engineers can name their normal tools, and the system translates those tools into governance checks, tickets, evidence, and launch blockers.

Stack:

```text
Snowflake → dbt → SFTP / MFT → Tableau / Power BI → API
```

Run:

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/platform_stack_governance/messy_intake.md \
  --output-dir generated/free_trial/platform_stack_governance
```

## 4. Platform Profiles

Platform profiles translate tool names into required governance checks.

| Profile | Location | Purpose |
|---|---|---|
| Snowflake | `platform_profiles/snowflake.profile.json` | Data warehouse controls: classification, masking, row access, roles, sharing, access history, unload/export review. |
| dbt | `platform_profiles/dbt.profile.json` | Transformation controls: model ownership, tests, lineage, documentation, derived-field sensitivity. |
| Generic File Mover | `platform_profiles/generic_file_mover.profile.json` | Vendor-neutral delivery controls: destination, recipient, route, manifest, checksum, test delivery. |
| SFTP / MFT | `platform_profiles/sftp_mft.profile.json` | Host/path, folder permissions, credentials, service accounts, route config, monitoring. |
| Tableau / Power BI | `platform_profiles/tableau_powerbi.profile.json` | Reporting controls: row-level security, dashboard access, exports, subscriptions, refresh validation. |
| API Integration | `platform_profiles/api.profile.json` | API controls: auth, payload schema, logging, secrets, monitoring, endpoint approval. |

## 5. L0-L6 Maturity Model

| Level | Name | Meaning |
|---|---|---|
| L0 | Unknown | Platform is named but governance controls are not identified. |
| L1 | Ad hoc | Controls depend on tribal knowledge. |
| L2 | Documented | Owners, systems, data types, and workflows are documented. |
| L3 | Controlled | Reviews, access controls, QA, and delivery gates exist. |
| L4 | Evidence-backed | Controls have logs, approvals, validation, and evidence. |
| L5 | Automated / enforced | Controls are built into workflows, policies, permissions, jobs, or CI/CD. |
| L6 | Adaptive / org-specific | Organization-specific rules, exceptions, naming conventions, mappings, and monitoring apply. |

## 6. Schemas

| Schema | Location | Purpose |
|---|---|---|
| Governance Rule Schema | `schemas/governance_rule.schema.json` | Machine-readable baseline governance rule structure. |
| Intake Schema | `schemas/intake.schema.json` | Structured messy intake format. |
| Ticket Schema | `schemas/ticket.schema.json` | Generated ticket/work item structure. |
| Scorecard Schema | `schemas/scorecard.schema.json` | Governed delivery risk scorecard output. |
| Evidence Packet Schema | `schemas/evidence_packet.schema.json` | Launch readiness evidence checklist output. |
| Platform Profile Schema | `schemas/platform_profile.schema.json` | Tool/platform-specific governance control profiles. |

## 7. Rule Packs

| Rule Pack | Location | Purpose |
|---|---|---|
| Data Governance Rules | `rules/data_governance_rules.yaml` | Baseline governance and regulatory overlay logic. |
| SOP Quality Rules | `rules/sop_quality_rules.yaml` | SOP quality scoring and mandatory gate caps. |
| Legal / SME Review Rules | `rules/legal_sme_review_rules.yaml` | Review routing and escalation conditions. |
| Data / Dev Engineering Rules | `rules/data_dev_engineering_rules.yaml` | Engineering-safe data use, transformation, enrichment, and delivery controls. |

## 8. Tests

| Test | Location | Purpose |
|---|---|---|
| Governed Delivery Package Test | `tests/test_governed_delivery_package.py` | Verifies core package generation and cross-platform exports. |
| Platform Stack Profile Test | `tests/test_platform_stack_profiles.py` | Verifies multi-platform detection and platform profile augmentation. |

Run:

```bash
python -m pytest tests/test_governed_delivery_package.py tests/test_platform_stack_profiles.py
```

## 9. Current Output Package

The full package generator produces:

```text
normalized_intake.json
scorecard.json
scorecard.md
platform_profile_report.json
platform_profile_report.md
generated_ticket_hierarchy.json
generated_ticket_hierarchy.md
jira_export.csv
ado_export.csv
rally_export.csv
asana_export.csv
evidence_packet.json
evidence_packet.md
launch_readiness_summary.md
```

## 10. Next Recommended Builds

| Priority | Build | Why |
|---:|---|---|
| 1 | YAML-driven rule engine | Moves scoring/blocker logic out of hardcoded Python. |
| 2 | Trial demo UI | Turns CLI output into a no-brainer free trial experience. |
| 3 | More platform profiles | Adds cloud storage, Databricks, GitHub, Airflow, Informatica, Salesforce. |
| 4 | Direct Jira / ADO integration | Moves beyond CSV export once package logic is stable. |
| 5 | SOC 2 control map | Adds stronger audit and enterprise readiness story. |
| 6 | Contradiction detector | Compares SOPs, tickets, timelines, data maps, and manifests for mismatch risk. |
