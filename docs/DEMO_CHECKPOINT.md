# Demo Checkpoint

## Checkpoint Name

Governed Delivery Agent: Backend-Connected Free Trial Demo

## Checkpoint Date

Created after backend API, free trial UI backend wiring, YAML rule validation, platform profiles, and Jira Forge scaffold were added.

## Purpose

This document defines the current known-good demo checkpoint before adding more features.

Use this as the baseline when testing locally or deciding whether new changes are safe to continue.

## Product State at This Checkpoint

The repo currently demonstrates this flow:

```text
Messy intake
→ normalized intake
→ YAML rule matching
→ scorecard
→ platform profile detection
→ launch blockers
→ ticket hierarchy
→ evidence packet
→ Jira / ADO / Rally / Asana CSV exports
→ backend API response
→ free trial UI rendering
→ Jira-native dry-run payload preparation
```

## What Is Included

| Area | Included |
|---|---|
| CLI package generator | Yes |
| YAML rule engine | Yes |
| YAML rule validation tests | Yes |
| Platform profile detection | Yes |
| Platform profile package augmentation | Yes |
| Backend demo API | Yes |
| Free trial static UI | Yes |
| Free trial backend-first analysis | Yes |
| Local UI fallback when backend is unavailable | Yes |
| Jira / ADO / Rally / Asana CSV exports | Yes |
| Jira Forge scaffold | Yes |
| Jira dry-run issue payload preparation | Yes |
| Real Jira issue creation | No |
| Production auth / tenant isolation | No |
| Real PHI/PCI/secrets handling | No |

## Core Files Added or Updated

### Apps

```text
apps/backend-demo-api/server.py
apps/backend-demo-api/README.md
apps/free-trial-demo/index.html
apps/free-trial-demo/styles.css
apps/free-trial-demo/app.js
apps/free-trial-demo/README.md
apps/jira-forge-governed-delivery/manifest.yml
apps/jira-forge-governed-delivery/package.json
apps/jira-forge-governed-delivery/README.md
apps/jira-forge-governed-delivery/src/index.js
apps/jira-forge-governed-delivery/src/resolvers.js
apps/jira-forge-governed-delivery/src/static/index.html
apps/jira-forge-governed-delivery/src/static/app.js
apps/jira-forge-governed-delivery/src/static/styles.css
```

### Tools

```text
tools/governed_delivery_cli.py
tools/generate_governed_delivery_package.py
tools/rule_loader.py
tools/rule_match_augmenter.py
tools/platform_profile_detector.py
tools/platform_profile_augmenter.py
tools/platform_exporters.py
```

### Rules

```text
rules/governed_delivery_rules.yaml
rules/launch_blocker_rules.yaml
rules/evidence_rules.yaml
rules/ticket_builder_rules.yaml
```

### Platform Profiles

```text
platform_profiles/snowflake.profile.json
platform_profiles/dbt.profile.json
platform_profiles/generic_file_mover.profile.json
platform_profiles/sftp_mft.profile.json
platform_profiles/tableau_powerbi.profile.json
platform_profiles/api.profile.json
```

### Tests

```text
tests/test_yaml_rule_packs.py
tests/test_governed_delivery_package.py
tests/test_platform_stack_profiles.py
tests/test_backend_demo_api.py
tests/test_jira_forge_scaffold.py
tests/test_free_trial_demo_backend_wiring.py
```

### Docs

```text
README.md
INDEX.md
docs/TESTING_GUIDE.md
docs/DEMO_CHECKPOINT.md
docs/governed_delivery_cli_quickstart.md
docs/file_mover_delivery_governance_guide.md
```

## Demo 1: Healthcare File Mover Delivery

### Purpose

Shows the last-mile delivery governance story.

### Value Statement

A technically correct pipeline can still create a compliance incident if the file is mislabeled, routed to the wrong recipient, sent to the wrong destination, or launched without evidence.

### Command

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

### Expected Result

The generated package should show:

| Area | Expected |
|---|---|
| Overall rating | `at_risk` |
| Launch position | `not_launchable` |
| Rule matches | Greater than 0 |
| Platform profiles | Generic File Mover and/or SFTP/MFT related controls |
| Launch blockers | Legal, destination, recipient access, test delivery, runbook/evidence gaps |
| Exports | Jira, ADO, Rally, Asana CSVs |

## Demo 2: Platform Stack Governance

### Purpose

Shows the platform-aware governance story.

### Value Statement

Engineers describe their tools. The system translates those tools into governance checks, tickets, evidence, and launch blockers.

### Stack

```text
Snowflake → dbt → SFTP / MFT → Tableau / Power BI → API
```

### Command

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/platform_stack_governance/messy_intake.md \
  --output-dir generated/free_trial/platform_stack_governance
```

### Expected Platform Profiles

| Profile | Expected Checks |
|---|---|
| Snowflake | Classification, object tags, masking, row access, role access, lineage, unload/export controls. |
| dbt | Model ownership, tests, lineage, docs, derived field sensitivity. |
| SFTP / MFT | Host/path, credentials, service account, route config, folder access. |
| Tableau / Power BI | Row-level security, export permissions, access, subscriptions, refresh validation. |
| API Integration | Auth, payload schema, logging, secrets, endpoint approval. |
| Generic File Mover | Destination, recipient, route, manifest, checksum, test delivery. |

## Backend Demo API Checkpoint

### Run

```bash
python apps/backend-demo-api/server.py
```

### Expected Health Endpoint

```bash
curl http://localhost:8787/health
```

Expected:

```json
{
  "ok": true,
  "service": "governed-delivery-backend-demo-api"
}
```

### Expected Analyze Endpoint

```bash
curl -X POST http://localhost:8787/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo Intake","intake":"We use Snowflake, dbt, SFTP, Tableau, and an API. Legal and Security are not confirmed."}'
```

Expected response includes:

```text
summary
scorecard
rule_match_report
platform_profile_report
tickets
evidence_packet
exports
markdown
```

## Free Trial UI Checkpoint

### Run

Terminal 1:

```bash
python apps/backend-demo-api/server.py
```

Terminal 2:

```bash
cd apps/free-trial-demo
python -m http.server 4173
```

Open:

```text
http://localhost:4173
```

### Expected UI Behavior

| Action | Expected |
|---|---|
| Load platform stack demo | Textarea loads Snowflake/dbt/SFTP/Tableau/API intake. |
| Analyze intake with backend running | UI renders backend-generated score, platforms, blockers, tickets, evidence. |
| Download exports | CSV files download from backend-generated export strings. |
| Stop backend and analyze | UI falls back to local preview and warns backend is unavailable. |

## Jira Forge Scaffold Checkpoint

### Purpose

The Jira scaffold proves the Atlassian-native direction without enabling risky write behavior yet.

### Current Behavior

| Feature | Status |
|---|---|
| Jira project page | Scaffolded |
| Jira issue panel | Scaffolded |
| Backend analysis resolver | Scaffolded |
| Jira issue context resolver | Scaffolded |
| Dry-run Jira payload generation | Scaffolded |
| Actual Jira issue creation | Intentionally disabled |

### Reason Actual Issue Creation Is Disabled

Before enabling Jira writes, we need:

1. Jira project field mapping.
2. Issue type mapping by project type.
3. Parent-child hierarchy strategy.
4. Permission review.
5. Explicit user confirmation.
6. Rollback/delete strategy for accidental creation.
7. Rate limit and max issue count controls.

## Known-Good Test Command

```bash
python -m pytest \
  tests/test_yaml_rule_packs.py \
  tests/test_governed_delivery_package.py \
  tests/test_platform_stack_profiles.py \
  tests/test_backend_demo_api.py \
  tests/test_jira_forge_scaffold.py \
  tests/test_free_trial_demo_backend_wiring.py
```

## Known Limitations

| Limitation | Reason |
|---|---|
| Executable YAML is JSON-compatible YAML | Keeps the rule engine dependency-free for now. |
| Free trial UI is static | Faster to test locally and easier to deploy early. |
| Backend uses local temp folders | Demo-safe and avoids persistence. |
| Backend has no auth | Not production-ready yet. |
| Backend has permissive CORS | Local demo convenience only. |
| Jira integration is dry-run only | Prevents accidental issue creation before field mapping. |
| No persistent audit trail | Needs secure storage and tenant model first. |
| No real sensitive data support | PHI/PCI/secrets handling requires security architecture. |

## Definition of Done for This Checkpoint

This checkpoint is considered valid when:

| Requirement | Pass Criteria |
|---|---|
| Tests pass | All six test files pass. |
| CLI works | Both demo package generator commands produce expected files. |
| Backend works | `/health` and `/api/analyze` return expected JSON. |
| UI works | Backend-connected free trial demo renders real analysis results. |
| Exports work | Jira, ADO, Rally, and Asana CSV downloads work. |
| Fallback works | UI still renders local preview if backend is stopped. |
| Jira scaffold is safe | Dry-run payloads only. No live issue creation. |

## Do Not Build Past This Until Tested

Before adding more capabilities, validate this checkpoint locally.

Do not enable Jira issue creation or add production deployment work until:

1. The backend API works locally.
2. The UI calls the backend successfully.
3. CSV exports download correctly.
4. The generated tickets/evidence make sense.
5. The fallback path works.
6. The test suite passes.

## Recommended Next Steps After Local Validation

| Priority | Next Step | Why |
|---:|---|---|
| 1 | Enable controlled Jira issue creation behind explicit confirmation | Moves from dry-run to useful Jira-native workflow. |
| 2 | Add more platform profiles | Increases governance translation power. |
| 3 | Add SOC 2 / audit control mapping | Strengthens enterprise credibility. |
| 4 | Add backend deployment guide | Makes the free trial demo shareable. |
| 5 | Add true YAML parser / schema validation | Improves rule authoring and safety. |
