# Intelligent Services Index

## Purpose

This index organizes the Intelligent Services repo into its core governance components, executable tools, demo flows, apps, schemas, profiles, rules, tests, and next-build areas.

The repo is designed to help AI agents convert messy operational intake into governed delivery work:

```text
Messy intake
→ normalized intake
→ YAML rule matching
→ risk score
→ platform profile detection
→ launch blockers
→ ticket hierarchy
→ platform exports
→ evidence packet
→ backend API response
→ Jira-native dry-run payloads
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
| Package Generator | `tools/generate_governed_delivery_package.py` | Runs the full package flow: base CLI, YAML rules, platform profiles, package augmentation, and exports. |
| Rule Loader | `tools/rule_loader.py` | Loads JSON-compatible YAML rule packs and matches rules against normalized intake. |
| Rule Match Augmenter | `tools/rule_match_augmenter.py` | Injects matched YAML rules into scorecards, tickets, evidence, and Jira export. |
| Platform Exporters | `tools/platform_exporters.py` | Creates ADO, Rally, and Asana CSV exports from generated ticket JSON. |
| Platform Profile Detector | `tools/platform_profile_detector.py` | Detects named tools/platforms and creates platform profile report. |
| Platform Profile Augmenter | `tools/platform_profile_augmenter.py` | Injects platform-profile tickets and evidence into the generated package. |

## 3. Apps

| App | Location | Purpose |
|---|---|---|
| Backend Demo API | `apps/backend-demo-api/` | HTTP API wrapping the Python package generator with `/health` and `/api/analyze`. |
| Free Trial Demo App | `apps/free-trial-demo/` | Static demo front door for trial-style messy intake analysis. |
| Jira Forge Scaffold | `apps/jira-forge-governed-delivery/` | Atlassian Forge starter with project page, issue panel, backend analysis, issue context, and dry-run Jira payloads. |

### 3.1 Backend Demo API

Run:

```bash
python apps/backend-demo-api/server.py
```

Endpoint:

```text
http://localhost:8787/api/analyze
```

### 3.2 Free Trial Demo App

Run:

```bash
cd apps/free-trial-demo
python -m http.server 4173
```

Open:

```text
http://localhost:4173
```

### 3.3 Jira Forge Scaffold

Location:

```text
apps/jira-forge-governed-delivery/
```

Current behavior:

- Jira project page scaffold
- Jira issue panel scaffold
- Backend analysis resolver
- Jira issue context resolver
- Dry-run Jira payload preparation

Actual Jira issue creation is intentionally not enabled yet. Field mapping, permissions, tenant isolation, and safety controls should be reviewed first.

## 4. Demo Paths

### 4.1 Healthcare File Mover Delivery Demo

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

### 4.2 Platform Stack Governance Demo

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

## 5. YAML Rule Engine

Rule packs are currently `.yaml` files containing JSON-compatible YAML so the engine stays dependency-free.

| Rule Pack | Location | Purpose |
|---|---|---|
| Governed Delivery Rules | `rules/governed_delivery_rules.yaml` | Baseline governed delivery findings, risk triggers, required evidence, and recommended tickets. |
| Launch Blocker Rules | `rules/launch_blocker_rules.yaml` | Launch-blocking conditions, required resolutions, and evidence requirements. |
| Evidence Rules | `rules/evidence_rules.yaml` | Evidence packet requirements for regulated data and file delivery workflows. |
| Ticket Builder Rules | `rules/ticket_builder_rules.yaml` | Rule-driven ticket generation for data governance, file mover validation, and launch approval. |

Supported condition operators:

| Operator | Purpose |
|---|---|
| `equals` | Match exact field value. |
| `not_equals` | Match field value mismatch. |
| `contains_any` | Match one or more values in a string or list. |
| `min_length` | Match list/string length. |
| `all` | All child conditions must match. |
| `any` | At least one child condition must match. |

## 6. Platform Profiles

Platform profiles translate tool names into required governance checks.

| Profile | Location | Purpose |
|---|---|---|
| Snowflake | `platform_profiles/snowflake.profile.json` | Data warehouse controls: classification, masking, row access, roles, sharing, access history, unload/export review. |
| dbt | `platform_profiles/dbt.profile.json` | Transformation controls: model ownership, tests, lineage, documentation, derived-field sensitivity. |
| Generic File Mover | `platform_profiles/generic_file_mover.profile.json` | Vendor-neutral delivery controls: destination, recipient, route, manifest, checksum, test delivery. |
| SFTP / MFT | `platform_profiles/sftp_mft.profile.json` | Host/path, folder permissions, credentials, service accounts, route config, monitoring. |
| Tableau / Power BI | `platform_profiles/tableau_powerbi.profile.json` | Reporting controls: row-level security, dashboard access, exports, subscriptions, refresh validation. |
| API Integration | `platform_profiles/api.profile.json` | API controls: auth, payload schema, logging, secrets, monitoring, endpoint approval. |

## 7. L0-L6 Maturity Model

| Level | Name | Meaning |
|---|---|---|
| L0 | Unknown | Platform is named but governance controls are not identified. |
| L1 | Ad hoc | Controls depend on tribal knowledge. |
| L2 | Documented | Owners, systems, data types, and workflows are documented. |
| L3 | Controlled | Reviews, access controls, QA, and delivery gates exist. |
| L4 | Evidence-backed | Controls have logs, approvals, validation, and evidence. |
| L5 | Automated / enforced | Controls are built into workflows, policies, permissions, jobs, or CI/CD. |
| L6 | Adaptive / org-specific | Organization-specific rules, exceptions, naming conventions, mappings, and monitoring apply. |

## 8. Schemas

| Schema | Location | Purpose |
|---|---|---|
| Governance Rule Schema | `schemas/governance_rule.schema.json` | Machine-readable baseline governance rule structure. |
| Governance Execution Rule Schema | `schemas/governance_execution_rule.schema.json` | Executable rule structure for rule-driven package generation. |
| Intake Schema | `schemas/intake.schema.json` | Structured messy intake format. |
| Ticket Schema | `schemas/ticket.schema.json` | Generated ticket/work item structure. |
| Scorecard Schema | `schemas/scorecard.schema.json` | Governed delivery risk scorecard output. |
| Evidence Packet Schema | `schemas/evidence_packet.schema.json` | Launch readiness evidence checklist output. |
| Platform Profile Schema | `schemas/platform_profile.schema.json` | Tool/platform-specific governance control profiles. |

## 9. Legacy / Supporting Rule Packs

| Rule Pack | Location | Purpose |
|---|---|---|
| Data Governance Rules | `rules/data_governance_rules.yaml` | Baseline governance and regulatory overlay logic. |
| SOP Quality Rules | `rules/sop_quality_rules.yaml` | SOP quality scoring and mandatory gate caps. |
| Legal / SME Review Rules | `rules/legal_sme_review_rules.yaml` | Review routing and escalation conditions. |
| Data / Dev Engineering Rules | `rules/data_dev_engineering_rules.yaml` | Engineering-safe data use, transformation, enrichment, and delivery controls. |

## 10. Tests

| Test | Location | Purpose |
|---|---|---|
| YAML Rule Pack Test | `tests/test_yaml_rule_packs.py` | Validates every YAML pack has IDs and executable packs have valid rule shapes/operators. |
| Governed Delivery Package Test | `tests/test_governed_delivery_package.py` | Verifies core package generation, YAML rule matching, rule injection, and cross-platform exports. |
| Platform Stack Profile Test | `tests/test_platform_stack_profiles.py` | Verifies multi-platform detection, platform profile augmentation, and rule-driven outputs. |
| Backend Demo API Test | `tests/test_backend_demo_api.py` | Verifies backend API analysis returns generated package response. |
| Jira Forge Scaffold Test | `tests/test_jira_forge_scaffold.py` | Verifies Forge scaffold files and dry-run Jira payload behavior. |

Run:

```bash
python -m pytest tests/test_yaml_rule_packs.py tests/test_governed_delivery_package.py tests/test_platform_stack_profiles.py tests/test_backend_demo_api.py tests/test_jira_forge_scaffold.py
```

## 11. Current Output Package

The full package generator produces:

```text
normalized_intake.json
rule_match_report.json
rule_match_report.md
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

## 12. Next Recommended Builds

| Priority | Build | Why |
|---:|---|---|
| 1 | Connect static free-trial UI to backend API | Make the demo use real package generation instead of local simulation. |
| 2 | Enable controlled Jira issue creation | Move Forge scaffold from dry-run payloads to actual issue creation after field mapping review. |
| 3 | True YAML parser / stricter schema validation | Improves authoring experience and catches malformed rules earlier. |
| 4 | More platform profiles | Adds cloud storage, Databricks, GitHub, Airflow, Informatica, Salesforce. |
| 5 | Direct ADO integration | Moves beyond CSV export once package logic is stable. |
| 6 | SOC 2 control map | Adds stronger audit and enterprise readiness story. |
| 7 | Contradiction detector | Compares SOPs, tickets, timelines, data maps, and manifests for mismatch risk. |
