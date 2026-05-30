#!/usr/bin/env python3
"""
Governed Delivery Backend Demo API

Dependency-light HTTP API that wraps tools/generate_governed_delivery_package.py.

Endpoints:
- GET /health
- POST /api/analyze

Safety:
Do not send real PHI, PCI, credentials, secrets, or live client data.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SCRIPT = REPO_ROOT / "tools" / "generate_governed_delivery_package.py"
MAX_INTAKE_CHARS = 25_000
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787


class DemoApiError(Exception):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


class Handler(BaseHTTPRequestHandler):
    server_version = "GovernedDeliveryDemoAPI/0.1"

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._send_json(200, {"ok": True, "service": "governed-delivery-backend-demo-api"})
            return
        self._send_json(404, {"error": "not_found", "message": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/analyze":
            self._send_json(404, {"error": "not_found", "message": "Endpoint not found"})
            return

        try:
            payload = self._read_json_body()
            result = analyze(payload)
            self._send_json(200, result)
        except DemoApiError as exc:
            self._send_json(exc.status_code, {"error": "request_error", "message": exc.message})
        except Exception as exc:  # pragma: no cover, defensive server boundary
            self._send_json(500, {"error": "internal_error", "message": str(exc)})

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            raise DemoApiError(400, "Request body is required")
        if content_length > MAX_INTAKE_CHARS * 4:
            raise DemoApiError(413, "Request body is too large")
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DemoApiError(400, f"Invalid JSON: {exc}") from exc

    def _send_json(self, status_code: int, payload):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format, *args):  # noqa: A003, keep BaseHTTPRequestHandler signature
        sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))


def analyze(payload: dict) -> dict:
    intake = str(payload.get("intake", "")).strip()
    title = str(payload.get("title", "Governed Delivery Demo Intake")).strip() or "Governed Delivery Demo Intake"

    if not intake:
        raise DemoApiError(400, "Field 'intake' is required")
    if len(intake) > MAX_INTAKE_CHARS:
        raise DemoApiError(413, f"Intake exceeds {MAX_INTAKE_CHARS} characters")

    request_id = str(uuid.uuid4())
    tmp_root = Path(tempfile.mkdtemp(prefix="governed_delivery_api_"))

    try:
        input_path = tmp_root / "messy_intake.md"
        output_dir = tmp_root / "package"
        input_path.write_text(intake, encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PACKAGE_SCRIPT),
                "--input",
                str(input_path),
                "--output-dir",
                str(output_dir),
                "--title",
                title,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )

        if completed.returncode != 0:
            raise DemoApiError(500, f"Package generation failed: {completed.stderr or completed.stdout}")

        return build_response(request_id, output_dir, completed.stdout)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def csv_preview(path: Path, max_rows: int = 20) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = []
        for idx, row in enumerate(reader):
            if idx >= max_rows:
                break
            rows.append(dict(row))
        return rows


def build_response(request_id: str, output_dir: Path, log: str) -> dict:
    scorecard = read_json(output_dir / "scorecard.json") or {}
    tickets = read_json(output_dir / "generated_ticket_hierarchy.json") or []
    evidence_packet = read_json(output_dir / "evidence_packet.json") or {}
    rule_match_report = read_json(output_dir / "rule_match_report.json") or {}
    platform_profile_report = read_json(output_dir / "platform_profile_report.json") or {}

    return {
        "request_id": request_id,
        "summary": {
            "overall_score": scorecard.get("overall_score"),
            "overall_rating": scorecard.get("overall_rating"),
            "launch_position": scorecard.get("launch_position"),
            "matched_rule_count": rule_match_report.get("matched_rule_count", 0),
            "detected_platform_count": platform_profile_report.get("detected_platform_count", 0),
            "ticket_count": len(tickets),
            "launch_blocker_count": len(scorecard.get("launch_blockers", [])),
            "evidence_item_count": len(evidence_packet.get("evidence_items", [])),
        },
        "scorecard": scorecard,
        "rule_match_report": rule_match_report,
        "platform_profile_report": platform_profile_report,
        "tickets": tickets,
        "evidence_packet": evidence_packet,
        "exports": {
            "jira_csv": read_text(output_dir / "jira_export.csv"),
            "ado_csv": read_text(output_dir / "ado_export.csv"),
            "rally_csv": read_text(output_dir / "rally_export.csv"),
            "asana_csv": read_text(output_dir / "asana_export.csv"),
            "jira_preview": csv_preview(output_dir / "jira_export.csv"),
            "ado_preview": csv_preview(output_dir / "ado_export.csv"),
            "rally_preview": csv_preview(output_dir / "rally_export.csv"),
            "asana_preview": csv_preview(output_dir / "asana_export.csv"),
        },
        "markdown": {
            "scorecard": read_text(output_dir / "scorecard.md"),
            "ticket_hierarchy": read_text(output_dir / "generated_ticket_hierarchy.md"),
            "evidence_packet": read_text(output_dir / "evidence_packet.md"),
            "launch_readiness_summary": read_text(output_dir / "launch_readiness_summary.md"),
            "platform_profile_report": read_text(output_dir / "platform_profile_report.md"),
            "rule_match_report": read_text(output_dir / "rule_match_report.md"),
        },
        "generator_log": log,
    }


def run_server():
    host = os.environ.get("HOST", DEFAULT_HOST)
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Governed Delivery Backend Demo API running at http://{host}:{port}")
    print("Safety: do not send real PHI, PCI, credentials, secrets, or live client data.")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
