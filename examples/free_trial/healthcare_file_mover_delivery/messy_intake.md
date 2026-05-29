# Messy Intake Scenario: Healthcare File Mover Delivery

## Raw Request

We need to onboard Centene for weekly LAMP outbound files by July 1. The file will include eligibility, claims, adherence opportunities, and pharmacy outreach records. The client needs the file every week and wants it delivered through their approved file delivery process.

We have a draft file layout and the data team says the SQL is mostly done. We still need to confirm the final delivery folder or endpoint, who should receive access, and whether Legal has approved the final field list. The team believes this is similar to prior client deliveries, so they want to move quickly.

## Known Context

| Field | Value |
|---|---|
| Client | Centene |
| Program | LAMP |
| Delivery cadence | Weekly |
| Target launch date | July 1 |
| Data involved | Eligibility, claims, adherence opportunities, pharmacy outreach records |
| External delivery | Yes |
| Delivery method | File mover / client-approved external delivery process |
| File layout | Draft exists |
| SQL / pipeline status | Mostly done |
| Legal approval | Not confirmed |
| Final field list approval | Not confirmed |
| Destination folder / endpoint | Not confirmed |
| Recipient access | Not confirmed |
| Runbook | Not confirmed |
| Monitoring | Not confirmed |
| Production-equivalent test delivery | Not confirmed |

## Why This Scenario Matters

This is a strong trial scenario because the technical work may appear close to complete, but launch readiness is still risky. The agent should detect that the delivery layer, recipient validation, legal approval, access review, and evidence package are unresolved.

## Expected Agent Behavior

The agent should not simply generate development tickets. It should:

1. Classify this as regulated external data delivery.
2. Assign elevated risk because healthcare data is involved.
3. Flag missing Legal, Data Governance, Security, QA, and Delivery evidence.
4. Generate a correct ticket hierarchy.
5. Create file mover validation work items.
6. Mark launch as blocked until required controls are complete.
7. Produce export-ready Jira / ADO / Rally / Asana ticket rows.
