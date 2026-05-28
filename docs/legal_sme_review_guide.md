# Legal and SME Review Guide

## Purpose

This guide defines the human review layer for Intelligent Services.

The AI can identify likely governance, compliance, contract, privacy, security, and operational risks. It can also summarize evidence and route review packets. It must not make final legal conclusions or approve risk on behalf of Legal, Privacy, Security, Compliance, or business owners.

The purpose of this workflow is to help reviewers focus on the exact parts of a project that need judgment.

## Why This Exists

AI is useful for pattern detection, consistency checks, document comparison, and missing evidence detection.

AI is not reliable enough to independently decide:

- Whether a regulation legally applies
- Whether a contractual clause permits a workflow
- Whether a claim is safe to publish externally
- Whether a workaround is acceptable risk
- Whether de-identification or anonymization is legally sufficient
- Whether a vendor arrangement satisfies all contractual, privacy, security, and compliance requirements

When the AI reaches one of those boundaries, it should create a Legal / SME Review Packet.

## Reviewer Types

| Reviewer | Reviews |
|---|---|
| Legal Counsel | Contract interpretation, regulatory applicability, liability, external claims, cross-border transfer, legal holds, customer commitments. |
| Privacy Officer / Data Protection SME | Personal data, consent, lawful basis, privacy notice, data rights, opt-out, de-identification, retention, data minimization. |
| Security SME | Access, encryption, secure transfer, logging, credentials, secrets, incident triggers, vendor security controls. |
| Compliance Owner | HIPAA, PCI-DSS, SOC 2, audit evidence, control operation, policy adherence, training requirements. |
| Operational SME | Whether the SOP or workflow accurately reflects real execution, dependencies, timing, owners, and handoffs. |
| Product / Business Owner | Business purpose, feature intent, customer-facing commitments, scope, prioritization, and risk ownership routing. |

## Review Triggers

| Trigger ID | Trigger | Default Reviewers |
|---|---|---|
| `LEGAL-TRIGGER-001` | Regulatory applicability unclear | Legal, Privacy, Compliance |
| `LEGAL-TRIGGER-002` | External-facing claim or customer commitment | Legal, Product Owner, Operational SME |
| `LEGAL-TRIGGER-003` | Contract, SOW, DPA, BAA, or vendor terms ambiguity | Legal, Privacy, Security, Compliance |
| `LEGAL-TRIGGER-004` | Sensitive data handling ambiguity | Privacy, Security, Compliance |
| `LEGAL-TRIGGER-005` | AI limitation or low-confidence classification | Operational SME, Privacy, Compliance |
| `LEGAL-TRIGGER-006` | Cross-border, offshore, or third-party access | Legal, Privacy, Security, Compliance |
| `LEGAL-TRIGGER-007` | Risk acceptance required | Legal, Security, Compliance, Product Owner |

## Project Sections the AI Should Extract

The AI should avoid sending a reviewer the entire project unless necessary. It should extract the relevant section, summarize it, redact sensitive data, and ask a specific decision question.

| Project Section | Review Focus |
|---|---|
| Strategy and scope documents | Business purpose, customer commitments, assumptions, exclusions, success metrics. |
| Data inventory and flow map | Data elements, source systems, destinations, recipients, retention, access roles. |
| SOPs and runbooks | Trigger conditions, inputs, outputs, execution steps, exception paths, approvals, evidence. |
| Gantt charts and project plans | Milestones, dependencies, review gates, external delivery dates, owners, critical path. |
| Contracts, SOWs, DPAs, BAAs, vendor agreements | Relevant clauses, data processing terms, service commitments, audit rights, confidentiality, security terms. |
| Jira, ADO, and implementation tickets | User stories, acceptance criteria, linked SOPs, data fields, deployment/delivery steps, comments showing uncertainty. |

## Legal / SME Review Packet Template

```markdown
## Legal / SME Review Packet

### Review Summary
- Packet ID:
- Project:
- Lifecycle phase:
- Trigger IDs:
- Recommended reviewers:
- Due date or blocking milestone:
- Sensitive data redaction status:

### Why Human Review Is Needed
- AI observation:
- AI confidence:
- Unresolved assumption:
- Risk if wrong:

### Specific Sections to Review
| Artifact | Section / Location | Why It Matters | Extracted Summary or Redacted Excerpt |
|---|---|---|---|

### Decision Needed
- Question for reviewer:
- Decision options:
  1.
  2.
  3.
- Recommended owner:

### Impacted Work
| Item | Impact |
|---|---|
| SOPs | |
| Gantt / Project Plan | |
| Jira / ADO Tickets | |
| Data Map | |
| Vendor / Contract | |
| SOP Score / Gate | |

### Final Decision Log
| Reviewer | Decision | Conditions | Date | Follow-up Action |
|---|---|---|---|---|
```

## Example Review Packet

```markdown
## Legal / SME Review Packet

### Review Summary
- Packet ID: LSR-2026-0001
- Project: New Client Data Ingestion Workflow
- Lifecycle phase: Planning
- Trigger IDs: LEGAL-TRIGGER-001, LEGAL-TRIGGER-003, LEGAL-TRIGGER-004
- Recommended reviewers: Legal Counsel, Privacy Officer, Compliance Owner, Security SME
- Due date or blocking milestone: Before production data transfer
- Sensitive data redaction status: Redacted. No live PHI included.

### Why Human Review Is Needed
- AI observation: The SOP references eligibility and claims files, but the project documents do not clearly state whether the data includes PHI, whether a BAA is executed, or whether the vendor can access production files.
- AI confidence: Medium
- Unresolved assumption: AI cannot determine whether the existing vendor agreement covers this specific data exchange and support workflow.
- Risk if wrong: Production PHI could be shared without appropriate contractual, privacy, security, or compliance approval.

### Specific Sections to Review
| Artifact | Section / Location | Why It Matters | Extracted Summary or Redacted Excerpt |
|---|---|---|---|
| Data Map | Source/Destination table | Shows claims and eligibility movement to external SFTP location. | Eligibility and claims files sent weekly to vendor-managed transfer location. |
| SOW | Data Exchange section | May define permitted file exchange and recipient obligations. | Clause summary needed. AI cannot determine scope from current notes. |
| SOP | Step 4: Upload production files | Execution step may occur before contract/security approval. | Upload production files after QA approval. No BAA/security checkpoint listed. |
| Gantt | Week 3 milestone | Timeline shows file delivery before Legal/Security review milestone. | External file delivery scheduled before review gate. |

### Decision Needed
- Question for reviewer: Does the existing contract/BAA/security review authorize this production PHI data exchange and vendor access model?
- Decision options:
  1. Approved as written.
  2. Approved with conditions, such as adding BAA reference, security checkpoint, and access restrictions.
  3. Not approved. Workflow must be revised before production transfer.
- Recommended owner: Compliance Owner with Legal and Security input.

### Impacted Work
| Item | Impact |
|---|---|
| SOPs | Add contract/BAA/security checkpoint before production file upload. |
| Gantt / Project Plan | Move production delivery after review approval. |
| Jira / ADO Tickets | Add acceptance criteria requiring BAA/security evidence. |
| Data Map | Add vendor role, access scope, and retention handling. |
| Vendor / Contract | Confirm applicable BAA/SOW/DPA coverage. |
| SOP Score / Gate | `GATE-REGULATED-NO-CONTROLS` remains active until resolved. |

### Final Decision Log
| Reviewer | Decision | Conditions | Date | Follow-up Action |
|---|---|---|---|---|
| Pending | Pending | Pending | Pending | Pending |
```

## Best Practice vs Pragmatic Workaround

| Scenario | Best Practice | Pragmatic Workaround |
|---|---|---|
| AI cannot determine regulatory applicability | Route to Legal/Privacy/Compliance before execution. | Mark overlay unresolved and block only the high-risk workflow step until reviewed. |
| Contract language is ambiguous | Ask Legal to review the specific clause and workflow dependency. | Summarize the clause and request a narrow decision instead of full contract review. |
| SOP may expose sensitive data | Redact immediately and route to Privacy/Security/Compliance. | Replace live data with synthetic examples before continuing the review. |
| Project timeline skips legal/security review | Add a formal review gate before production delivery. | Add a temporary manual approval checkpoint with named owner and expiration date. |
| AI has low confidence in an operational workflow | Route to Operational SME for validation. | Allow draft status only. Do not mark SOP active until SME confirms. |

## Agent Rules

The AI must:

- Identify the specific project section needing review.
- Explain why it cannot safely decide.
- Route to the minimum necessary reviewers.
- Provide exact questions and decision options.
- Redact sensitive data where possible.
- Track the final human decision back to impacted SOPs, project plans, tickets, data maps, vendor records, and scores.

The AI must not:

- Provide legal advice.
- Mark unclear regulatory applicability as resolved.
- Hide assumptions in polished language.
- Send entire contracts or sensitive records for broad review when a narrow excerpt is enough.
- Include unnecessary PHI, PCI, credentials, secrets, or sensitive records in review packets.

## Related Files

- `rules/legal_sme_review_rules.yaml`
- `rules/data_governance_rules.yaml`
- `rules/sop_quality_rules.yaml`
- `docs/data_governance_compliance_framework.md`
- `docs/sop_quality_scoring_guide.md`
