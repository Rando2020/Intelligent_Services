# Intelligent Services

**Governed AI for work that can't afford to guess.**

Intelligent Services is a framework and executable prototype that turns messy operational intake into governed, audit-ready delivery work. It understands business documentation, project lifecycles, SOPs, governance and compliance constraints, execution readiness, engineering data safety, platform-specific controls, last-mile delivery risk, and human review escalation.

It is built for operational reasoning, not legal advice. Agents identify risks, missing evidence, contradictions, and required escalation points. Legal, privacy, security, and compliance owners remain responsible for final interpretation and approval.

---

## The pipeline

```text
Messy intake
  → Normalized intake
  → YAML rule matching
  → Risk scoring
  → Platform / tool detection
  → Missing-information detection
  → Timeline & launch-readiness review
  → Ticket hierarchy generation
  → Jira / ADO / Rally / Asana export
  → Evidence packet
  → Backend API response
  → Jira-native dry-run payloads
  → Human review routing
```

The differentiated value isn't generic ticket writing. It's preventing bad intake, weak platform controls, unclear approvals, and last-mile delivery gaps from becoming production or compliance incidents.

---

## Product spine

| Component | Purpose |
|---|---|
| **Governed Delivery CLI** | Converts messy intake into scorecards, tickets, evidence, and exports. |
| **YAML Rule Engine** | Matches configurable governance rules against normalized intake and injects findings, blockers, evidence, and tickets. |
| **Platform Profile Engine** | Detects named tools (Snowflake, dbt, SFTP/MFT, Tableau, Power BI, APIs) and maps them to required governance checks. |
| **File Mover Governance** | Treats delivery layers as governed control surfaces, not operational afterthoughts. |
| **Ticket Exporters** | Generates Jira, ADO, Rally, and Asana-friendly CSVs. |
| **Evidence Packet Generator** | Converts risks and controls into launch-readiness evidence requirements. |
| **Backend Demo API** | Wraps the Python generator behind `/api/analyze` for demo apps and integrations. |
| **Free Trial Demo App** | Static trial front door for showing messy intake to governed work output. |
| **Jira Forge Scaffold** | Jira project page and issue panel scaffold for Atlassian-native analysis and dry-run issue payloads. |

---

## Quick start

```bash
# Healthcare file-mover delivery demo — the last-mile delivery risk story
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

> A technically correct pipeline can still create a compliance event if the file is mislabeled, routed to the wrong recipient, sent to the wrong destination, or launched without evidence.

```bash
# Platform stack governance demo — engineers name their tools, the system maps controls
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/platform_stack_governance/messy_intake.md \
  --output-dir generated/free_trial/platform_stack_governance
```

Example stack the engine recognizes: `Snowflake → dbt → SFTP / MFT → Tableau / Power BI → API`

---

## Backend demo API

```bash
python apps/backend-demo-api/server.py
```

Default endpoint:

```text
http://localhost:8787/api/analyze
```

Example:

```bash
curl -X POST http://localhost:8787/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo Intake","intake":"We use Snowflake, dbt, SFTP, Tableau, and an API. Legal and Security are not confirmed."}'
```

---

## Free trial demo app

```bash
cd apps/free-trial-demo
python -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

The demo lets a user:

- Load the file mover demo
- Load the full platform stack demo
- Paste custom synthetic intake
- See detected platforms
- See launch blockers
- Preview generated tickets and evidence
- Download sample Jira / ADO / Rally / Asana CSV exports

---

## Jira-native scaffold

```text
apps/jira-forge-governed-delivery/
```

Current scaffold includes:

- Jira project page module
- Jira issue panel module
- Backend analysis resolver
- Jira issue context resolver
- Dry-run Jira issue payload preparation

Actual Jira issue creation is intentionally not enabled yet. The scaffold prepares payloads first so field mapping, permissions, issue type behavior, and safety controls can be reviewed before write actions are introduced.

---

## Generated package outputs

```text
normalized_intake.json          rule_match_report.json / rule_match_report.md
scorecard.json / scorecard.md   platform_profile_report.json / platform_profile_report.md
generated_ticket_hierarchy.json generated_ticket_hierarchy.md
jira_export.csv  ado_export.csv  rally_export.csv  asana_export.csv
evidence_packet.json / evidence_packet.md
launch_readiness_summary.md
```

---

## Repository structure

```text
.
├── README.md
├── INDEX.md
├── apps/        # Backend API, static free-trial demo app, Jira Forge scaffold
├── docs/        # Framework guides: governance, SOP scoring, legal/SME review,
│                #   data/dev engineering, file-mover governance, CLI quickstart
├── rules/       # Rule packs: legacy YAML plus executable JSON-compatible YAML
├── schemas/     # JSON schemas: governance rule, execution rule, intake, ticket,
│                #   scorecard, evidence packet, platform profile
├── tools/       # Executable: delivery CLI, package generator, rule engine,
│                #   exporters, platform detector & augmenters
├── examples/    # Free-trial demo intakes
└── tests/       # pytest coverage for YAML rules, package generation, backend API & Forge scaffold
```

---

## Rule packs

| Rule pack | Purpose |
|---|---|
| `rules/governed_delivery_rules.yaml` | Executable governed delivery findings, evidence, and recommended tickets. |
| `rules/launch_blocker_rules.yaml` | Executable launch-blocking conditions and required resolutions. |
| `rules/evidence_rules.yaml` | Executable evidence packet requirements. |
| `rules/ticket_builder_rules.yaml` | Executable rule-driven ticket generation. |
| `rules/data_governance_rules.yaml` | Baseline governance and regulatory overlay logic. |
| `rules/sop_quality_rules.yaml` | SOP quality scoring and mandatory gate caps. |
| `rules/legal_sme_review_rules.yaml` | Review routing and escalation conditions. |
| `rules/data_dev_engineering_rules.yaml` | Engineering-safe data use, transformation, enrichment, and delivery controls. |

Prototype note: the executable rule packs use `.yaml` for readability but currently contain JSON-compatible YAML so the rule engine can remain dependency-free.

## Regulatory overlays

The system separates baseline governance controls from regulatory overlays, which trigger only when the data and context actually invoke them.

| Overlay | Trigger examples |
|---|---|
| GDPR | EU/EEA personal data, EU/EEA users, behavioral monitoring, cross-border transfer. |
| CCPA/CPRA | California resident personal information, sale/share/opt-out workflows. |
| HIPAA | PHI, claims, eligibility, medication, payer/provider/business-associate workflows. |
| PCI-DSS | Cardholder data, payment workflows, cardholder-data-environment systems. |

---

## SOP maturity model (L0–L6)

| Level | Meaning |
|---|---|
| L0 | None / tribal knowledge |
| L1 | Documented but unverified |
| L2 | Reviewed |
| L3 | Approved & owned |
| L4 | Linked to work items & evidence |
| L5 | Automated / enforced in workflows, policies, CI/CD |
| L6 | Adaptive / org-specific rules, exceptions, monitoring |

---

## Run the tests

```bash
python -m pytest \
  tests/test_yaml_rule_packs.py \
  tests/test_governed_delivery_package.py \
  tests/test_platform_stack_profiles.py \
  tests/test_backend_demo_api.py \
  tests/test_jira_forge_scaffold.py
```

---

## Roadmap

| Priority | Build | Why |
|---:|---|---|
| 1 | Connect static free-trial UI to backend API | Make the demo use real package generation instead of local simulation. |
| 2 | Enable controlled Jira issue creation | Move Forge scaffold from dry-run payloads to actual issue creation after field mapping review. |
| 3 | True YAML parser / stricter schema validation | Improve authoring experience and catch malformed rules earlier. |
| 4 | Contradiction detector | Compare SOPs, tickets, timelines, data maps, and manifests for mismatch risk. |
| 5 | More platform profiles | Cloud storage, Databricks, GitHub, Airflow, Informatica, Salesforce. |
| 6 | Direct ADO integration | Move beyond CSV export once package logic is stable. |
| 7 | SOC 2 / audit control map | Stronger enterprise-readiness story. |

---

## Important disclaimer

This repository provides an operational governance framework. It does not provide legal advice and does not replace review by legal, privacy, security, compliance, product, architecture, data engineering, or operational owners. Inputs are processed to generate outputs you own; they are not stored long-term or used to train models.

## License

See [LICENSE](LICENSE).

---

*Built by Josiah Parve — a healthcare product operations leader with 10+ years turning complex, regulated environments into scalable products. [josiahparve@gmail.com](mailto:josiahparve@gmail.com) · [LinkedIn](https://www.linkedin.com/in/josiah-p-bbb896169)*
