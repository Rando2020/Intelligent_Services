# Governed Delivery CLI Quickstart

## Purpose

The Governed Delivery CLI is a lightweight prototype that converts messy intake into a governed delivery package.

It generates:

- Normalized intake JSON
- Governed delivery scorecard
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
| `scorecard.json` | Machine-readable risk scorecard |
| `scorecard.md` | Human-readable risk scorecard |
| `generated_ticket_hierarchy.json` | Machine-readable ticket hierarchy |
| `generated_ticket_hierarchy.md` | Human-readable ticket hierarchy |
| `jira_export.csv` | Jira import-ready ticket export |
| `ado_export.csv` | Azure DevOps import-friendly ticket export |
| `rally_export.csv` | Rally import-friendly ticket export |
| `asana_export.csv` | Asana import-friendly task export |
| `evidence_packet.json` | Machine-readable evidence checklist |
| `evidence_packet.md` | Human-readable evidence checklist |
| `launch_readiness_summary.md` | Executive launch readiness readout |

## What the CLI Currently Detects

| Capability | Current Status |
|---|---|
| Client/program detection | Basic keyword/table detection |
| Launch date detection | Basic text and table detection |
| Sensitive data detection | Keyword-based detection for PHI, PII, PCI, claims, eligibility, medication, credentials |
| File mover detection | Vendor-neutral delivery layer detection |
| Missing information detection | Basic missing gate detection |
| Risk scoring | Prototype scorecard logic |
| Ticket generation | Static governed hierarchy adapted to detected client/program |
| Jira export | CSV export |
| ADO export | CSV export through package generator |
| Rally export | CSV export through package generator |
| Asana export | CSV export through package generator |
| Evidence packet | Static evidence model adapted to detected request |

## Run Tests

The package generator has a basic automated test that verifies output files, scorecard state, ticket generation, and governance columns in the platform exports.

```bash
python -m pytest tests/test_governed_delivery_package.py
```

If pytest is not installed, the code can still be run manually through the package generator command above.

## Safety Rule

Do not use real PHI, PCI, credentials, secrets, or live client data in CLI inputs. Use synthetic, redacted, or generalized intake text.

## Best Next Enhancements

1. Replace keyword detection with structured intake parsing.
2. Add YAML-configurable scoring rules.
3. Add golden-output snapshots.
4. Add a web demo that wraps this CLI logic.
5. Add a human review packet generator.
6. Add support for source-to-target mapping intake.
7. Add configurable ticket templates by industry and workflow type.
8. Add direct Jira / ADO integration after CSV exports are stable.

## Example Trial Narrative

A user pastes this:

```text
We need to onboard a client for weekly healthcare outbound files. The SQL is mostly done, but Legal approval, final destination, recipient access, and test delivery are not confirmed.
```

The CLI returns:

```text
Governed Delivery Readiness: 62 / 100
Launch Position: Not launchable
Generated Tickets: 15
Launch Blockers: 6
Required Reviews: Legal, Privacy, Compliance, Data Governance, Security, QA, Platform Operations
Exports: Jira, ADO, Rally, Asana
```

That is the first no-brainer free trial moment.
