# Governed Delivery CLI Quickstart

## Purpose

The Governed Delivery CLI is a lightweight prototype that converts messy intake into a governed delivery package.

It generates:

- Normalized intake JSON
- Governed delivery scorecard
- Generated ticket hierarchy
- Jira CSV export
- Evidence packet
- Launch readiness summary

This is the first executable step toward the governed delivery agent.

## Run the Demo

From the repository root:

```bash
python tools/governed_delivery_cli.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

## Optional Title Override

```bash
python tools/governed_delivery_cli.py \
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
| Evidence packet | Static evidence model adapted to detected request |

## Safety Rule

Do not use real PHI, PCI, credentials, secrets, or live client data in CLI inputs. Use synthetic, redacted, or generalized intake text.

## Best Next Enhancements

1. Replace keyword detection with structured intake parsing.
2. Add YAML-configurable scoring rules.
3. Add ADO, Rally, and Asana CSV exporters.
4. Add unit tests and golden-output snapshots.
5. Add a web demo that wraps this CLI logic.
6. Add a human review packet generator.
7. Add support for source-to-target mapping intake.
8. Add configurable ticket templates by industry and workflow type.

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
```

That is the first no-brainer free trial moment.
