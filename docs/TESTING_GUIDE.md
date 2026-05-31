# Testing Guide

## Purpose

This guide is the local testing runbook for the current Governed Delivery Agent checkpoint.

Use it when you are ready to test the repo from your computer.

## What You Are Testing

The current checkpoint includes:

| Area | What should work |
|---|---|
| CLI package generator | Converts messy intake into scorecard, rules, platform profiles, tickets, exports, evidence, and launch summary. |
| YAML rule engine | Loads executable rule packs, matches rules, and injects findings, blockers, evidence, and tickets. |
| Platform profile engine | Detects tools such as Snowflake, dbt, SFTP/MFT, Tableau/Power BI, APIs, and generic file movers. |
| Backend demo API | Exposes `/health` and `/api/analyze` for real package generation. |
| Free trial web demo | Calls the backend API first and falls back to local preview if the backend is unavailable. |
| Jira Forge scaffold | Provides project-page/issue-panel scaffold and dry-run Jira issue payload preparation. |

## Safety Rule

Do not use real PHI, PCI, credentials, secrets, or live client data.

Use synthetic, redacted, or generalized intake text only.

## Prerequisites

You need:

| Requirement | Notes |
|---|---|
| Python 3.10+ | Python standard library is enough for most demo flows. |
| pytest | Needed for test suite. Install with `pip install pytest` if missing. |
| Git | Needed to clone/pull the repo. |
| Browser | Needed for the static free trial demo. |
| Node/npm | Only needed if you want to inspect or run the Jira Forge scaffold. |
| Atlassian Forge CLI | Only needed later for actual Forge deploy/install testing. |

## 1. Pull Latest Repo

From your local repo folder:

```bash
git checkout main
git pull origin main
```

If you do not have the repo locally yet:

```bash
git clone https://github.com/Rando2020/Intelligent_Services.git
cd Intelligent_Services
```

## 2. Run the Full Test Suite

From the repo root:

```bash
python -m pytest \
  tests/test_yaml_rule_packs.py \
  tests/test_governed_delivery_package.py \
  tests/test_platform_stack_profiles.py \
  tests/test_backend_demo_api.py \
  tests/test_jira_forge_scaffold.py \
  tests/test_free_trial_demo_backend_wiring.py
```

### Expected Result

All tests should pass.

If `pytest` is missing:

```bash
pip install pytest
```

## 3. Test the CLI Package Generator

### Healthcare File Mover Demo

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/healthcare_file_mover_delivery/messy_intake.md \
  --output-dir generated/free_trial/healthcare_file_mover_delivery
```

### Platform Stack Demo

```bash
python tools/generate_governed_delivery_package.py \
  --input examples/free_trial/platform_stack_governance/messy_intake.md \
  --output-dir generated/free_trial/platform_stack_governance
```

### Expected Generated Files

Each output folder should include:

```text
normalized_intake.json
rule_match_report.json
rule_match_report.md
scorecard.json
scorecard.md
platform_profile_report.json
platform_profile_report.md
generated_ticket_hierarchy.json
generated_ticket_hierarchy.md
jira_export.csv
ado_export.csv
rally_export.csv
asana_export.csv
evidence_packet.json
evidence_packet.md
launch_readiness_summary.md
```

## 4. Inspect Key CLI Outputs

Open these files after running the platform stack demo:

```text
generated/free_trial/platform_stack_governance/scorecard.md
generated/free_trial/platform_stack_governance/rule_match_report.md
generated/free_trial/platform_stack_governance/platform_profile_report.md
generated/free_trial/platform_stack_governance/generated_ticket_hierarchy.md
generated/free_trial/platform_stack_governance/evidence_packet.md
```

### Expected Platform Detections

The platform stack demo should detect:

| Expected Profile |
|---|
| Snowflake |
| dbt |
| SFTP / Managed File Transfer |
| Tableau / Power BI |
| API Integration |
| Generic File Mover |

### Expected Rule Behavior

The rule match report should show matched rules from these packs:

| Pack |
|---|
| Governed Delivery Rules |
| Launch Blocker Rules |
| Evidence Rules |
| Ticket Builder Rules |

## 5. Start the Backend Demo API

From the repo root:

```bash
python apps/backend-demo-api/server.py
```

Expected console output:

```text
Governed Delivery Backend Demo API running at http://127.0.0.1:8787
```

### Health Check

In a browser or terminal:

```bash
curl http://localhost:8787/health
```

Expected response:

```json
{
  "ok": true,
  "service": "governed-delivery-backend-demo-api"
}
```

### Analyze Endpoint Test

```bash
curl -X POST http://localhost:8787/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo Intake","intake":"We use Snowflake, dbt, SFTP, Tableau, and an API. Legal and Security are not confirmed."}'
```

Expected response includes:

| Field | Expected |
|---|---|
| `summary.overall_rating` | `at_risk` |
| `summary.launch_position` | `not_launchable` |
| `summary.matched_rule_count` | Greater than 0 |
| `summary.detected_platform_count` | Greater than 0 |
| `exports.jira_csv` | CSV text |
| `tickets` | Generated ticket array |

## 6. Start the Free Trial Web Demo

Open a second terminal.

From the repo root:

```bash
cd apps/free-trial-demo
python -m http.server 4173
```

Open:

```text
http://localhost:4173
```

### Test Flow

1. Confirm the app loads.
2. Click **Load platform stack demo**.
3. Click **Analyze intake**.
4. Confirm the score renders.
5. Confirm detected platforms render.
6. Confirm launch blockers render.
7. Confirm generated tickets render.
8. Confirm evidence requirements render.
9. Download Jira CSV.
10. Download ADO CSV.
11. Download Rally CSV.
12. Download Asana CSV.

### Expected Backend Behavior

If the backend is running, the score summary should say it is using backend results and should show matched rules/detected platforms.

### Expected Fallback Behavior

If the backend is not running, the app should still work but display a message similar to:

```text
Backend unavailable, using local fallback.
```

## 7. Test Jira Forge Scaffold File Presence

The Forge scaffold is not expected to be production-ready yet. Current testing validates the scaffold exists and is intentionally dry-run only.

```bash
python -m pytest tests/test_jira_forge_scaffold.py
```

### Expected Behavior

The scaffold should include:

| File / Behavior | Expected |
|---|---|
| `manifest.yml` | Contains project page and issue panel modules. |
| `src/resolvers.js` | Contains backend analysis resolver. |
| `src/resolvers.js` | Contains dry-run issue payload preparation. |
| Actual Jira issue creation | Not enabled yet. |

## 8. Common Issues

### Backend is not running

Symptom:

```text
Backend unavailable, using local fallback.
```

Fix:

```bash
python apps/backend-demo-api/server.py
```

### Port already in use

If port `8787` is already used:

```bash
PORT=8790 python apps/backend-demo-api/server.py
```

Then update the demo backend URL before loading the app:

```html
<script>
  window.GOVERNED_DELIVERY_API_URL = "http://localhost:8790/api/analyze";
</script>
```

### Pytest missing

Fix:

```bash
pip install pytest
```

### Browser blocks backend call

The backend sends permissive CORS headers for local demo testing. Confirm the backend URL is correct and the backend is running.

## 9. Definition of Passing Local Test

The checkpoint is considered working if:

| Requirement | Pass Criteria |
|---|---|
| Tests pass | All listed pytest files pass. |
| CLI package works | Both demo commands generate the expected package files. |
| Backend works | `/health` and `/api/analyze` return valid JSON. |
| Free trial UI works | UI calls backend and renders score, platforms, blockers, tickets, and evidence. |
| Exports work | Jira, ADO, Rally, and Asana CSV downloads work. |
| Fallback works | UI still renders local preview when backend is off. |

## 10. What Not To Test Yet

Do not expect these to be complete yet:

| Area | Status |
|---|---|
| Production authentication | Not implemented. |
| Persistent storage | Not implemented. |
| Real Jira issue creation | Not enabled. Dry-run only. |
| Marketplace app setup | Not started. |
| Enterprise tenant isolation | Not implemented. |
| Real PHI/PCI/secrets handling | Not supported. |

## 11. Next After Testing

After the checkpoint is validated locally, the safest next builds are:

1. Enable controlled Jira issue creation behind explicit confirmation.
2. Add Databricks, cloud storage, GitHub, Airflow/Informatica/ActiveBatch, and Salesforce platform profiles.
3. Add SOC 2 / audit control mapping.
4. Add deployment plan for backend API and static trial app.
