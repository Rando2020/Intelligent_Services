# File Mover and Last-Mile Delivery Governance Guide

## Purpose

This guide defines vendor-neutral controls for any system that moves, delivers, uploads, exports, publishes, or exposes files or datasets outside the originating system.

The key principle is simple: a technically correct pipeline can still create a compliance incident when the final delivery layer is misconfigured.

This guide is intentionally not specific to MOVEit. MOVEit is one example of a managed file transfer platform, but the same governance model applies to any file mover or outbound delivery layer.

## File Mover Definition

A file mover is any tool, job, platform, script, or workflow that transfers, publishes, routes, exports, uploads, or grants access to files or datasets.

## Covered Delivery Layers

| Delivery Layer | Examples | Governance Risk |
|---|---|---|
| Managed file transfer | MOVEit, GoAnywhere MFT, Kiteworks, Cleo, IBM Sterling, Axway | Wrong recipient, wrong folder, wrong route, missing approval |
| SFTP / FTPS | Client SFTP, vendor SFTP, internal secure FTP | Credential misuse, path error, weak destination validation |
| Cloud object storage | AWS S3, Azure Blob, Google Cloud Storage | Bucket/container permissions, public exposure, stale files |
| Collaboration storage | SharePoint, OneDrive, Google Drive, Box, Dropbox Business | Overbroad permissions, link sharing, uncontrolled retention |
| API delivery | REST API, GraphQL API, webhook, partner endpoint | Wrong endpoint, auth issue, payload mismatch |
| Reporting exports | Tableau, Power BI, Looker, CSV download, scheduled report | Row-level security gaps, overexposed dashboards, incorrect filters |
| Portal upload | Client portal, vendor portal, payer portal, pharmacy portal | Manual upload error, wrong client selection, no receipt proof |
| Email delivery | Secure email, encrypted attachment, manual attachment | Human error, wrong recipient, attachment leakage |
| Batch orchestration | Airflow, Informatica, ActiveBatch, cron, SQL Agent, dbt Cloud | Wrong schedule, stale output, wrong environment, no alerting |
| Manual transfer | Local desktop upload, ad hoc shared folder, one-off script | Uncontrolled storage, weak evidence, high human error |

## Core Rule

The delivery layer is part of the governed control boundary.

Do not treat file movement as an operational afterthought. A file mover controls who receives data, where data lands, when it is sent, how it is named, what evidence exists, and whether the organization can prove the right data went to the right destination.

## Last-Mile Delivery Risk Patterns

| Risk Pattern | Example | Required Control |
|---|---|---|
| Wrong recipient | File sent to the wrong client folder or partner endpoint | Recipient allowlist and canonical client ID validation |
| Wrong file label | File name says one client but payload belongs to another | Manifest validation and source-to-destination reconciliation |
| Wrong route | Job points to copied or outdated folder path | Route configuration review and peer approval |
| Manual destination selection | User chooses folder, portal, or recipient manually | Two-person review or automation with allowlist |
| Free-text client names | Routing depends on typed client name or spreadsheet tab | Canonical ID, client master, or controlled lookup table |
| Missing delivery evidence | Team cannot prove what was sent, where, and when | Delivery log, checksum, receipt, manifest, and approval record |
| Missing access review | External users retain access after program end | Periodic access recertification and offboarding trigger |
| Test path differs from production | Test file succeeds, production route is different | Production-equivalent test path or explicit delta review |
| Stale scheduled job | Old automation continues sending files | Job inventory, owner, active/inactive status, monitoring |
| Overexposed reporting export | Dashboard export includes unauthorized population | Row-level security validation and export review |

## Required Controls Before External Delivery

| Control | Required Evidence |
|---|---|
| Canonical recipient identification | Client ID, partner ID, recipient allowlist, approved destination |
| Destination validation | Folder path, bucket, endpoint, portal, report, or mailbox confirmation |
| File naming control | Naming convention, client/program/date logic, environment marker |
| Manifest or control file | Row count, file count, checksum, schema version, batch ID |
| Access control review | User/group permissions, service account permissions, expiration rules |
| Route configuration review | Source, destination, schedule, environment, owner, approval |
| Test delivery | Test log, receipt confirmation, negative test where appropriate |
| Production approval | Release ticket, approver, launch date, rollback/pause plan |
| Monitoring and alerting | Job status, failure alert, delivery confirmation, exception owner |
| Retention and cleanup | Retention duration, archive path, deletion process, evidence location |

## File Mover Rating Scale

| Rating | Name | Meaning | Launch Position |
|---|---|---|---|
| L0 | Unknown | Delivery layer is not identified | Not launchable |
| L1 | Assumed | Delivery path is assumed from prior work or tribal knowledge | Not launchable |
| L2 | Defined | Delivery path is documented but not independently validated | At risk |
| L3 | Validated | File, destination, recipient, naming, access, and logs are tested | Launchable with standard approval |
| L4 | Controlled | Validated plus monitoring, manifest, checksum, and approval evidence | Strong launch readiness |
| L5 | Automated and auditable | Config-driven routing, allowlists, reconciliations, alerts, and audit package | Best practice |

## Automatic Launch Blockers

The launch should be blocked or escalated if any of the following are true:

1. External delivery is required but the destination is not approved.
2. Recipient access is not reviewed.
3. Routing depends on free-text names, copied folders, or manual selection.
4. File name and payload ownership are not reconciled.
5. Test delivery did not use a production-equivalent route.
6. No delivery log, manifest, checksum, receipt, or approval record exists.
7. The file contains PHI, PII, PCI, credentials, or client confidential data without approved handling.
8. The delivery job has no accountable owner.
9. No pause, rollback, or incident escalation path exists.
10. The delivery layer is changed after QA without re-validation.

## Best Practice

Use config-driven routing with canonical IDs, recipient allowlists, environment separation, manifests, checksums, delivery logs, monitoring, and approval evidence.

## Pragmatic Workaround

If automation is not available yet, require a documented checklist, two-person review, approved destination evidence, delivery receipt, and ticket-attached proof before production delivery.

## Agent Instructions

When an agent detects external delivery, file movement, reporting export, API publication, portal upload, or shared-folder delivery, it should:

1. Classify the delivery layer.
2. Identify whether regulated or sensitive data is involved.
3. Ask for destination, recipient, route, naming, access, and evidence details.
4. Apply the file mover rating scale.
5. Generate delivery validation tickets.
6. Add launch blockers when required evidence is missing.
7. Generate an evidence checklist.
8. Avoid vendor-specific assumptions unless the platform is explicitly named.

## Non-Legal Advice Notice

This guide provides operational governance support. It does not provide legal, security, privacy, or compliance approval and does not replace review by authorized owners.
