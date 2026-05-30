# Governed Delivery Backend Demo API

## Purpose

This is a dependency-light backend API that wraps the Python package generator.

It allows the free trial web demo or future apps to send messy intake text and receive a governed delivery package.

## Run Locally

From the repository root:

```bash
python apps/backend-demo-api/server.py
```

Default URL:

```text
http://localhost:8787
```

## Endpoints

### Health

```bash
curl http://localhost:8787/health
```

### Analyze Intake

```bash
curl -X POST http://localhost:8787/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"title":"Demo Intake","intake":"We use Snowflake, dbt, SFTP, Tableau, and an API. Legal and Security are not confirmed."}'
```

## Response Shape

The API returns selected package outputs:

```json
{
  "request_id": "...",
  "summary": {...},
  "scorecard": {...},
  "rule_match_report": {...},
  "platform_profile_report": {...},
  "tickets": [...],
  "evidence_packet": {...},
  "exports": {
    "jira_csv": "...",
    "ado_csv": "...",
    "rally_csv": "...",
    "asana_csv": "..."
  }
}
```

## Safety Rule

Do not send real PHI, PCI, credentials, secrets, or live client data. Use synthetic, redacted, or generalized intake text.

## Production Notes

This is intentionally a demo API. Before production use, add:

- Authentication
- Rate limiting
- Request size limits by account tier
- Tenant isolation
- Secrets management
- Structured logging without sensitive values
- Async job execution for large packages
- Data retention policy
- Export storage controls
- Security review
