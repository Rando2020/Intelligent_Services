import json
from pathlib import Path


import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "backend-demo-api"))

import server  # noqa: E402


def test_backend_demo_api_analyze_returns_generated_package():
    payload = {
        "title": "Backend API Test",
        "intake": "We use Snowflake, dbt, SFTP, Tableau, and an API for healthcare claims and eligibility reporting. Legal, Security, destination, recipient access, and QA test delivery are not confirmed.",
    }

    result = server.analyze(payload)

    assert result["request_id"]
    assert result["summary"]["overall_rating"] == "at_risk"
    assert result["summary"]["launch_position"] == "not_launchable"
    assert result["summary"]["matched_rule_count"] >= 1
    assert result["summary"]["detected_platform_count"] >= 5
    assert result["summary"]["ticket_count"] >= 1
    assert result["exports"]["jira_csv"].startswith("Issue Type")
    assert "Risk Rating" in result["exports"]["ado_csv"]
    assert result["platform_profile_report"]["detected_platform_count"] >= 5


def test_sparse_pharmacy_claims_eligibility_intake_is_not_false_ready():
    payload = {
        "title": "Sparse Healthcare Intake Test",
        "intake": "we need to launch a pharmacy product. We are taking in eligibility and claims data",
    }

    result = server.analyze(payload)
    matched_rule_ids = {rule["id"] for rule in result["rule_match_report"]["matched_rules"]}
    prioritized_ticket_titles = [ticket["title"] for ticket in result.get("prioritized_tickets", [])]

    assert result["summary"]["overall_rating"] == "at_risk"
    assert result["summary"]["launch_position"] == "not_launchable"
    assert result["summary"]["overall_score"] <= 64
    assert "GOV-DELIVERY-004" in matched_rule_ids
    assert "Complete discovery for sparse regulated healthcare product intake" in prioritized_ticket_titles
    assert result["summary"]["detected_platform_count"] == 0


def test_backend_demo_api_rejects_empty_intake():
    try:
        server.analyze({"intake": ""})
    except server.DemoApiError as exc:
        assert exc.status_code == 400
        assert "intake" in exc.message.lower()
    else:
        raise AssertionError("Expected DemoApiError for empty intake")
