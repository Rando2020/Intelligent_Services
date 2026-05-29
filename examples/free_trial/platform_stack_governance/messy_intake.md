# Messy Intake Scenario: Platform Stack Governance

## Raw Request

We need to launch a new governed healthcare reporting workflow for a payer client by August 15. The data is currently stored in Snowflake. Analytics Engineering is transforming it through dbt models. The weekly outbound file will be delivered through SFTP or another approved managed file transfer process. A dashboard will also be published in Tableau for internal operations, and a partner API may be used later to send status updates.

The SQL and dbt models are mostly built, but we still need to confirm the final approved field list, Snowflake role access, masking or row access policies, dbt test coverage, Tableau row-level security, SFTP destination folder, recipient allowlist, and API payload requirements. Legal has not yet approved the final field list. Security has not completed the access review. QA has not completed a production-equivalent test delivery.

The team wants to move quickly because leadership already shared the August 15 target date with the client.

## Known Context

| Field | Value |
|---|---|
| Client | Example Payer |
| Program | Healthcare Reporting |
| Target launch date | August 15 |
| Data platform | Snowflake |
| Transformation layer | dbt |
| File delivery | SFTP / managed file transfer |
| Reporting layer | Tableau |
| Future integration | Partner API |
| Data involved | Claims, eligibility, adherence, member-level reporting, operational status updates |
| External delivery | Yes |
| Legal approval | Not confirmed |
| Data Governance approval | Not confirmed |
| Security review | Not confirmed |
| Snowflake role access review | Not confirmed |
| Snowflake masking / row access policies | Not confirmed |
| dbt tests and lineage review | Not confirmed |
| Tableau row-level security validation | Not confirmed |
| SFTP destination and recipient allowlist | Not confirmed |
| API payload contract | Not confirmed |
| Production-equivalent test delivery | Not confirmed |
| Runbook and monitoring | Not confirmed |

## Expected Agent Behavior

The agent should detect the named platforms and map them to platform-specific governance controls.

Detected profiles should include:

1. Snowflake Control Profile
2. dbt Transformation Control Profile
3. SFTP / Managed File Transfer Control Profile
4. Tableau / Power BI Reporting Control Profile
5. API Integration Control Profile
6. Generic File Mover Control Profile, if external delivery language is detected

The agent should generate:

1. Governed delivery scorecard
2. Platform control profile report
3. Missing information questions
4. Launch blockers
5. Ticket hierarchy
6. Jira / ADO / Rally / Asana exports
7. Evidence packet
8. Launch readiness summary

## Why This Scenario Matters

This shows the larger product idea: dev and data engineers can describe their normal tool stack, and the agent translates those tools into the governance checks, tickets, evidence, and launch gates required for safe delivery.
