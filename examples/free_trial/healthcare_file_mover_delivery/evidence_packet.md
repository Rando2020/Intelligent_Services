# Evidence Packet: Healthcare File Mover Delivery

## Purpose

This evidence packet defines what must be collected before a regulated external file delivery can be considered launch-ready.

## Required Evidence

| Evidence Area | Required Artifact | Owner Role | Launch Blocker |
|---|---|---|---|
| Business approval | Approved business purpose or implementation request | Product / Implementation | Yes |
| Legal approval | Contract, BAA, SOW, permitted-use approval, or Legal decision | Legal / Compliance | Yes |
| Data Governance | Approved field list and minimum necessary review | Data Governance / Product | Yes |
| Source-to-target mapping | Mapping document with source fields, transformations, filters, and target fields | Data Engineering | Yes |
| Data QA | Row counts, reconciliation totals, schema validation, exception review | QA / Data Engineering | Yes |
| Delivery mechanism | Approved file mover, API, portal, cloud folder, report export, or other delivery layer | Implementation / Platform Ops | Yes |
| Destination validation | Folder path, endpoint, bucket, portal location, report location, or recipient mailbox evidence | Platform Ops / Security | Yes |
| Recipient allowlist | Approved users, groups, service accounts, or partner endpoints | Security | Yes |
| Access review | Permission review and least-privilege confirmation | Security | Yes |
| File naming control | Naming convention and payload ownership reconciliation | Data Engineering / QA | Yes |
| Manifest/checksum | Row count, file count, checksum, batch ID, schema version, or control file | Data Engineering | Yes |
| Test delivery | Production-equivalent delivery log, receipt, confirmation, or screenshot with sensitive data redacted | QA / Platform Ops | Yes |
| Monitoring | Job status, alert routing, failure notification, exception owner | Platform Ops | Conditional |
| Runbook | Weekly operation steps, owner, escalation path, pause/rollback plan | Implementation / Operations | Yes |
| Launch approval | Final go/no-go decision with named approvers | Product / PM / Compliance | Yes |

## Evidence Quality Rules

1. Evidence should prove the control, not merely describe the control.
2. Screenshots must be redacted if they include PHI, PII, PCI, credentials, tokens, secrets, or client confidential values.
3. File names alone are not proof of payload ownership.
4. Folder labels alone are not proof of destination ownership.
5. Prior client setup is not proof that this client setup is safe.
6. Production delivery should not begin until all launch blockers are resolved or formally accepted by authorized owners.

## Trial Demo Summary

For the free trial, the agent should present this evidence packet as a checklist and clearly mark missing evidence as launch blockers. This is the feature that differentiates the tool from generic AI ticket writing.
