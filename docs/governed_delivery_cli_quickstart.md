# Governed Delivery CLI Quickstart

## Purpose

The Governed Delivery CLI is a lightweight prototype that converts messy intake into a governed delivery package.

It now includes a YAML-driven rule engine, platform profile detection, platform-specific ticket/evidence injection, and cross-platform work item exports.

It generates:

- Normalized intake JSON
- YAML rule match report
- Governed delivery scorecard
- Platform profile report
- Generated ticket hierarchy
- Jira CSV export
- ADO CSV export
- Rally CSV export
- Asana CSV export
- Evidence packet
- Launch readiness summary

This is the first executable step toward the governed delivery agent.

## Recommended Demo Command

Use the package generator when you want the full cross-platform demo output.

From the repository root:

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

## Platform Stack Demo Command

Use this when you want to demonstrate platform-aware governance for Snowflake, dbt, SFTP/MFT, Tableau/Power BI, and API controls.

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/platform_stack_governance/messy_intake.md \
  --output-dir generated/free_trial/platform_stack_governance
```

## Core CLI Only

Use the core CLI if you only need the base governed package plus Jira export.

```bash
python tools/governed_delivery_cli.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

## Optional Title Override

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery \
  --title "Centene LAMP Governed File Delivery"
```

## Generated Files

| Output | Purpose |
|---|---|
| `normalized_intake.json` | Structured version of the messy request |
| `rule_match_report.json` | Machine-readable matched YAML rules |
| `rule_match_report.md` | Human-readable matched YAML rules |
| `scorecard.json` | Machine-readable risk scorecard with matched rule IDs |
| `scorecard.md` | Human-readable risk scorecard |
| `platform_profile_report.json` | Machine-readable detected platform profiles |
| `platform_profile_report.md` | Human-readable detected platform profiles |
| `generated_ticket_hierarchy.json` | Machine-readable ticket hierarchy, including rule and platform-generated tickets |
| `generated_ticket_hierarchy.md` | Human-readable ticket hierarchy |
| `jira_export.csv` | Jira import-ready ticket export |
| `ado_export.csv` | Azure DevOps import-friendly ticket export |
| `rally_export.csv` | Rally import-friendly ticket export |
| `asana_export.csv` | Asana import-friendly task export |
| `evidence_packet.json` | Machine-readable evidence checklist |
| `evidence_packet.md` | Human-readable evidence checklist |
| `launch_readiness_summary.md` | Executive launch readiness readout |

## Rule Engine

Rule files live under `rules/`:

| Rule Pack | Purpose |
|---|---|
| `governed_delivery_rules.yaml` | Baseline governed delivery findings and control expectations |
| `launch_blocker_rules.yaml` | Launch-blocking conditions and required resolutions |
| `evidence_rules.yaml` | Evidence requirements for regulated data and delivery workflows |
| `ticket_builder_rules.yaml` | Rule-driven ticket generation logic |

Prototype note: the files use `.yaml` for readability, but currently contain JSON-compatible YAML so the engine can stay dependency-free and use the Python standard library.

## What the Package Generator Currently Detects

| Capability | Current Status |
|---|---|
| Client/program detection | Basic keyword/table detection |
| Launch date detection | Basic text and table detection |
| Sensitive data detection | Keyword-based detection for PHI, PII, PCI, claims, eligibility, medication, credentials |
| YAML rule matching | Dependency-free matching against normalized intake |
| Rule-driven findings | Matched rules are injected into scorecard findings |
| Rule-driven blockers | Launch-blocking rules are injected into scorecard and evidence packet |
| Rule-driven tickets | Recommended rule tickets are injected into generated ticket hierarchy |
| File mover detection | Vendor-neutral delivery layer detection |
| Platform profile detection | Snowflake, dbt, SFTP/MFT, Tableau/Power BI, API, generic file mover |
| Platform-driven tickets/evidence | Detected profiles add tickets and evidence requirements |
| Jira export | CSV export |
| ADO export | CSV export through package generator |
| Rally export | CSV export through package generator |
| Asana export | CSV export through package generator |
| Evidence packet | Rule, platform, and baseline evidence model adapted to detected request |

## Run Tests

```bash
python -m pytest tests/test_governed_delivery_package.py tests/test_platform_stack_profiles.py
```

If pytest is not installed, the code can still be run manually through the package generator command above.

## Safety Rule

Do not use real PHI, PCI, credentials, secrets, or live client data in CLI inputs. Use synthetic, redacted, or generalized intake text.

## Best Next Enhancements

1. Replace JSON-compatible YAML with true YAML parsing if dependencies are acceptable.
2. Add a rule schema and validation tests for every rule pack.
3. Move more hardcoded baseline score logic into YAML rules.
4. Add golden-output snapshots.
5. Add a web demo that wraps this CLI logic.
6. Add a human review packet generator.
7. Add support for source-to-target mapping intake.
8. Add configurable ticket templates by industry and workflow type.
9. Add direct Jira / ADO integration after CSV exports are stable.

## Example Trial Narrative

A user pastes this:

```text
We need to onboard a client for weekly healthcare outbound files. The SQL is mostly done, but Legal approval, final destination, recipient access, and test delivery are not confirmed.
```

The package generator returns:

```text
Governed Delivery Readiness: 62 / 100
Launch Position: Not launchable
YAML Rule Matches: governed delivery, launch blocker, evidence, and ticket builder rules
Detected Profiles: generic file mover and applicable platform controls
Generated Tickets: baseline, rule-driven, and platform-driven work items
Launch Blockers: rule-driven and profile-driven blockers
Required Reviews: Legal, Privacy, Compliance, Data Governance, Security, QA, Platform Operations
Exports: Jira, ADO, Rally, Asana
```

That is the first no-brainer free trial moment.
