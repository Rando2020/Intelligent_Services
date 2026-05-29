# Analyzed Scorecard: Healthcare File Mover Delivery

## Overall Result

| Category | Score | Rating | Launch Position |
|---|---:|---|---|
| Governed Delivery Readiness | 62 / 100 | At Risk | Not launchable until blockers are resolved |
| Intake Quality | L2 | Draft intake | Needs refinement before delivery work |
| Timeline Risk | L2 | At risk | Launch date may be driving controls rather than controls driving launch |
| Data Risk | L4 | Governed required | Healthcare data and external delivery require review gates |
| File Mover Risk | L1 | Assumed | Delivery process is referenced but not validated |
| Ticket Quality | L2 | Draft | Tickets can be generated, but several must be discovery/gate tickets |

## Primary Finding

The project appears technically close because the SQL is mostly done, but the external delivery layer is not governed enough for launch.

A correct pipeline does not prove safe delivery. The final file mover route, destination, recipient access, file naming, approval evidence, and production-equivalent test delivery are unresolved.

## Detected Risk Drivers

| Risk Driver | Status | Impact |
|---|---|---|
| Healthcare data involved | Present | Requires Legal, Privacy, Data Governance, and Security review |
| External recipient | Present | Requires delivery controls and recipient allowlist |
| Final destination unknown | Missing | Launch blocker |
| Recipient access unknown | Missing | Launch blocker |
| Legal approval unknown | Missing | Launch blocker |
| Final field list approval unknown | Missing | Launch blocker |
| Test delivery evidence missing | Missing | Launch blocker |
| Runbook missing | Missing | Operational risk |
| Monitoring missing | Missing | Operational risk |
| Target date already known | Present | Timeline pressure risk |

## Required Missing Information

1. What exact file mover, portal, API, cloud storage, report export, or delivery mechanism will be used?
2. What is the approved destination folder, bucket, endpoint, portal, mailbox, or report location?
3. Who is allowed to receive or access the file?
4. Has Legal approved the final field list and use case?
5. Has Data Governance approved minimum necessary fields?
6. Has Security reviewed external access and service account permissions?
7. Is a BAA, contract, or permitted-use reference confirmed?
8. What file naming convention will prevent wrong-client or wrong-program labeling?
9. What manifest, checksum, or delivery log will prove correct delivery?
10. Has production-equivalent test delivery been completed?
11. What is the rollback or pause plan if the file is wrong?
12. Who owns weekly monitoring and exception handling?

## Launch Blockers

| Blocker | Required Resolution |
|---|---|
| Legal approval not confirmed | Attach Legal approval or review decision |
| Final field list not approved | Attach approved field list and minimization review |
| Destination not confirmed | Attach approved destination evidence |
| Recipient access not confirmed | Attach access review and allowlist |
| File mover route not validated | Complete route configuration review |
| Test delivery not completed | Attach production-equivalent delivery log |
| No manifest/checksum evidence | Define and attach control totals |
| Runbook not confirmed | Create operational runbook |
| Monitoring not confirmed | Define alerting and exception owner |

## Recommended Final Rating After Remediation

If all blockers are resolved and evidence is attached, this request could move from L2/L1 delivery risk to L4 Controlled or L5 Automated and Auditable depending on whether the delivery path uses automated allowlists, manifests, route validation, and monitoring.
