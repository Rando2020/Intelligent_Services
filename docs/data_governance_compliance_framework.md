# Data Governance and Compliance Rule Framework

## Purpose

This framework gives Intelligent Services agents a repeatable way to evaluate operational workflows, SOPs, project plans, Gantt charts, data flows, integrations, and implementation artifacts against baseline data governance and regulatory expectations.

It is designed for operational reasoning, not legal advice. Agents should identify risks, missing evidence, contradictions, and required escalation points. Legal, privacy, security, and compliance owners remain responsible for final interpretation and approval.

## Core Operating Model

The system must evaluate every project through four layers:

1. **Baseline governance controls**
   - Data classification
   - Data lifecycle management
   - Access control
   - Encryption and secure transmission
   - Retention and disposal
   - Documentation ownership
   - Evidence collection

2. **Regulatory overlays**
   - GDPR
   - CCPA/CPRA
   - HIPAA
   - PCI-DSS
   - Additional overlays can be added later for GLBA, SOC 2, SOX, FERPA, ISO 27001, state privacy laws, and industry-specific rules.

3. **Project lifecycle alignment**
   - Initiation
   - Planning
   - Execution
   - Monitoring and control
   - Closure

4. **Document governance**
   - Source of truth
   - Version control
   - SOP linkage
   - Contradiction detection
   - Change impact propagation

## Agent Decision Flow

When an agent reviews a project, it should follow this sequence.

### Step 1: Classify the data

Ask:

- What data is being collected, generated, transformed, stored, accessed, sent, or deleted?
- Does it include personal data, PHI, payment card data, confidential business data, credentials, secrets, or regulated records?
- Who owns the data?
- Who can access it?
- Where does it move?
- How long is it retained?
- What evidence proves these answers?

Relevant controls:

- `CTRL-DATA-MAP`
- `CTRL-ACCESS`
- `CTRL-RETENTION`

### Step 2: Determine regulatory overlays

Do not assume every regulation applies. Trigger overlays based on data type, geography, industry, contractual obligations, system use, and vendor involvement.

| Overlay | Trigger Examples | Agent Caution |
|---|---|---|
| GDPR | EU/EEA personal data, EU/EEA users, monitoring behavior, cross-border transfer | Do not assume consent is always the correct lawful basis. |
| CCPA/CPRA | California resident personal information, sale/share/consumer rights workflows | Do not assume every business is subject without checking applicability. |
| HIPAA | PHI, healthcare payer/provider/clearinghouse/business associate workflows | Do not place PHI in tickets, logs, prompts, screenshots, or repos. |
| PCI-DSS | Payment card data, payment workflows, cardholder data environment | Do not store or expose PAN, CVV, full card data, or card data screenshots. |

### Step 3: Map documents to project lifecycle

| Lifecycle Phase | Primary Documents | Governance Review |
|---|---|---|
| Initiation | Strategy docs, scope docs, data classification, stakeholder map | Define business purpose, data categories, owners, and regulatory exposure. |
| Planning | Gantt charts, dependency maps, SOP linkage matrix, control plan | Link milestones to SOPs and evidence requirements. |
| Execution | SOPs, runbooks, QA records, access approvals, change logs | Confirm teams use active procedures and capture exceptions. |
| Monitoring and Control | Audit logs, risk logs, compliance checklist, evidence index | Detect contradictions, missing evidence, and control failures. |
| Closure | Final acceptance, archive manifest, retention/disposal record, lessons learned | Archive stale docs and assign ongoing maintenance ownership. |

Relevant rules:

- `DOC-001`
- `DOC-002`
- `DOC-003`
- `DOC-004`
- `DOC-005`

### Step 4: Link dependencies

Every project task should link to the artifact that governs it.

Examples:

| Project Task | Required Link |
|---|---|
| Deploy code | Deployment SOP |
| Configure file exchange | SFTP or secure transfer runbook |
| Load client data | Data ingestion SOP |
| Grant user access | Access request and approval policy |
| Perform QA | QA test plan and validation evidence |
| Send external file | Data delivery SOP and approved recipient list |

If a task has no governing artifact, the system should flag it as an execution risk.

### Step 5: Audit for consistency

The system should cross-reference:

- Strategy documents
- Gantt charts
- SOPs
- Jira or ADO work items
- HR or capacity documents
- Vendor contracts
- Security reviews
- Data maps
- Training records
- Change logs

Contradictions should be logged with:

- Contradiction summary
- Affected documents
- Risk level
- Decision owner
- Required resolution
- Date resolved
- Updated source of truth

### Step 6: Establish the single source of truth

The system should require:

- Canonical document link
- Document owner
- Version
- Effective date
- Approval status
- Review cadence
- Archive location for superseded documents

No active process should rely on an outdated, ownerless, or unapproved SOP.

## Essential Compliance Program Elements

| Element | Rule Expectation | Evidence |
|---|---|---|
| Data lifecycle management | Track how data is generated, accessed, stored, transmitted, retained, and destroyed. | Data inventory, flow diagram, retention schedule, disposal log |
| User consent and lawful basis | Confirm clear permission, lawful basis, notice, and opt-out rights where applicable. | Consent record, privacy notice, lawful basis assessment |
| Security controls | Use access controls, encryption, secure transmission, monitoring, and logging. | Access matrix, encryption standard, audit logs, security review |
| Policies and training | Maintain written procedures and verify relevant staff training. | SOPs, training records, acknowledgements, escalation contacts |
| Third-party risk management | Review vendors, processors, subprocessors, APIs, and cloud services. | Vendor inventory, contract, DPA/BAA, security review, offboarding plan |
| Compliance ownership | Assign accountable personnel for oversight and decisions. | RACI/PASCI, DPO/privacy owner/security owner/compliance owner records |

## Agent Output Template

Agents evaluating a workflow should return:

```markdown
## Governance Review Summary

### Scope Reviewed
- Project:
- Documents reviewed:
- Systems involved:
- Data categories:
- Lifecycle phase:

### Applicable Baseline Controls
| Control ID | Status | Evidence | Gap |
|---|---|---|---|

### Potential Regulatory Overlays
| Overlay | Trigger | Applies? | Evidence Needed | Escalation |
|---|---|---|---|---|

### Document Governance Findings
| Rule ID | Finding | Risk | Owner | Action |
|---|---|---|---|---|

### Contradictions or Missing Evidence
| Item | Impact | Required Decision |
|---|---|---|

### Recommended Next Actions
1.
2.
3.
```

## Best Practice vs Pragmatic Workaround

| Scenario | Best Practice | Pragmatic Workaround |
|---|---|---|
| No data inventory exists | Build a full data inventory and flow map before implementation. | Start with a critical-path inventory for high-risk data and expand iteratively. |
| SOPs are outdated | Pause execution until SOPs are updated and approved. | Add a temporary approved deviation log with owner, date, and review deadline. |
| Gantt tasks are not linked to SOPs | Require every execution task to link to a governing artifact. | Link the highest-risk tasks first, especially data movement, access, delivery, and deployment. |
| Vendor review is incomplete | Block production data sharing until review is complete. | Use synthetic or de-identified test data only, with documented approval. |
| Regulatory applicability is unclear | Escalate to legal/privacy/compliance owner before processing. | Mark overlay as unresolved and block high-risk actions until reviewed. |

## Current Rule Files

- `rules/data_governance_rules.yaml`
- `schemas/governance_rule.schema.json`

## Future Expansion

Recommended next rule packs:

- `rules/soc2_controls.yaml`
- `rules/healthcare_interoperability_rules.yaml`
- `rules/vendor_risk_rules.yaml`
- `rules/sop_quality_rules.yaml`
- `rules/project_lifecycle_rules.yaml`
- `rules/ai_agent_data_handling_rules.yaml`
