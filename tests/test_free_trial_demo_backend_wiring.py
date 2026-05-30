from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FREE_TRIAL_APP = REPO_ROOT / "apps" / "free-trial-demo"


def test_free_trial_demo_calls_backend_api_with_fallback():
    app_js = (FREE_TRIAL_APP / "app.js").read_text(encoding="utf-8")

    assert "BACKEND_API_URL" in app_js
    assert "http://localhost:8787/api/analyze" in app_js
    assert "fetch(BACKEND_API_URL" in app_js
    assert "renderBackendResult" in app_js
    assert "renderLocalResult" in app_js
    assert "Backend unavailable" in app_js


def test_free_trial_demo_downloads_backend_exports_when_available():
    app_js = (FREE_TRIAL_APP / "app.js").read_text(encoding="utf-8")

    assert "lastExportCsv" in app_js
    assert "result.exports?.jira_csv" in app_js
    assert "result.exports?.ado_csv" in app_js
    assert "result.exports?.rally_csv" in app_js
    assert "result.exports?.asana_csv" in app_js
