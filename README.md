# Intelligent Services

Intelligent Services is a framework for building AI-assisted operational systems that can understand business documentation, project lifecycles, SOPs, governance requirements, compliance constraints, execution readiness, and human review escalation.

## Current Focus

The first rule packs establish a data governance, compliance, SOP quality, and Legal/SME review foundation for agents that need to reason across:

- Strategy documents
- SOPs and runbooks
- Gantt charts and project plans
- Jira or ADO work items
- Data maps and system dependencies
- Contracts, SOWs, DPAs, BAAs, and vendor terms
- Access, vendor, privacy, security, and compliance evidence
- Operational readiness and audit-readiness scoring
- Human review routing when AI cannot safely determine an answer

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

The repository now includes a weighted 100-point SOP scoring model.

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

## Repository Structure

```text
.
├── README.md
├── docs/
│   ├── data_governance_compliance_framework.md
│   ├── legal_sme_review_guide.md
│   └── sop_quality_scoring_guide.md
├── rules/
│   ├── data_governance_rules.yaml
│   ├── legal_sme_review_rules.yaml
│   └── sop_quality_rules.yaml
└── schemas/
    └── governance_rule.schema.json
```

## How Agents Should Use These Rules

Agents should not simply summarize documents. They should evaluate whether a workflow is governed, traceable, executable, audit-ready, and properly routed for human review where needed.

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

## Important Disclaimer

This repository provides an operational governance framework. It does not provide legal advice and does not replace review by legal, privacy, security, compliance, product, or operational owners.

## Next Recommended Builds

- Add a SOC 2 and audit control mapping rule pack.
- Add a project document ingestion workflow.
- Add a contradiction detector for SOPs, Gantt charts, and Jira/ADO work items.
- Add example scorecards and review packets for healthcare, finance, retail, SaaS, and public sector workflows.
- Add a lightweight CLI or script that reads an SOP and produces a structured scorecard plus Legal/SME review packet when needed.
