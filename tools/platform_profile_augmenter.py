#!/usr/bin/env python3
"""
Platform Profile Augmenter

Takes platform_profile_report.json and injects detected platform controls into:
- generated_ticket_hierarchy.json
- generated_ticket_hierarchy.md
- evidence_packet.json
- evidence_packet.md
- jira_export.csv

ADO, Rally, and Asana exports should be regenerated after augmentation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import governed_delivery_cli


PLATFORM_EPIC_ID = "EPIC-PLATFORM-001"
PLATFORM_EPIC_TITLE = "Platform Control Profile Governance"


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def first_initiative_id(tickets: list[dict[str, Any]]) -> str:
    for ticket in tickets:
        if ticket.get("work_item_type") == "initiative":
            return str(ticket.get("external_id", "INIT-001"))
    return "INIT-001"


def base_ticket_defaults(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    first = tickets[0] if tickets else {}
    return {
        "platform": "generic",
        "request_type": first.get("request_type", "platform_governance"),
        "program": first.get("program", "Unknown"),
        "client": first.get("client", "Unknown"),
        "systems_impacted": first.get("systems_impacted", []),
        "data_involved": first.get("data_involved", []),
        "phi_flag": bool(first.get("phi_flag", False)),
        "pii_flag": bool(first.get("pii_flag", False)),
        "pci_flag": bool(first.get("pci_flag", False)),
        "external_recipient": bool(first.get("external_recipient", False)),
        "file_movement_required": bool(first.get("file_movement_required", False)),
        "delivery_method": first.get("delivery_method", "unknown"),
        "legal_review_required": bool(first.get("legal_review_required", True)),
        "security_review_required": True,
        "data_governance_required": True,
        "qa_required": True,
        "soc2_impact": ["Access Control", "Change Management", "Processing Integrity", "Confidentiality"],
        "risk_rating": "L4",
        "timeline_risk_rating": first.get("timeline_risk_rating", "L2"),
        "ticket_quality_rating": first.get("ticket_quality_rating", "L2"),
        "priority": "high",
        "assignee": "TBD",
        "due_date": first.get("due_date", ""),
        "sprint_or_iteration": "",
        "dependencies": [],
        "blockers": [],
        "evidence_links": [],
        "status": "New",
        "export_ready": True,
    }


def build_platform_epic(parent_id: str, defaults: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_id": PLATFORM_EPIC_ID,
        "parent_external_id": parent_id,
        "work_item_type": "epic",
        "title": PLATFORM_EPIC_TITLE,
        "description": "Apply platform-specific governance controls based on detected tools, systems, and delivery layers in the intake.",
        "business_context": "Named systems and platforms require platform-aware governance checks in addition to baseline delivery controls.",
        "user_story": "As an accountable delivery team, I need platform-specific governance checks so that engineering work is safe, controlled, and auditable.",
        "acceptance_criteria": [
            "Detected platform profiles are reviewed.",
            "Required platform checks are converted into work items or evidence requirements.",
            "Platform-specific launch blockers are resolved or formally accepted.",
            "Evidence packet includes platform-specific artifacts.",
        ],
        "definition_of_done": [
            "Platform profile report is generated.",
            "Recommended platform tickets are created.",
            "Required evidence is attached or explicitly marked not applicable.",
            "Open platform blockers are resolved or accepted by authorized owners.",
        ],
        "owner_role": "Product / Platform Governance / Security",
        "evidence_required": ["platform_profile_report", "platform_control_evidence"],
        "launch_blocker": True,
        **defaults,
    }


def build_platform_story(profile: dict[str, Any], ticket_def: dict[str, Any], index: int, defaults: dict[str, Any]) -> dict[str, Any]:
    evidence_required = ticket_def.get("evidence_required") or profile.get("required_evidence", [])[:5]
    required_checks = profile.get("required_checks", [])
    acceptance_criteria = [
        f"Detected profile {profile.get('id')} is reviewed for applicability.",
        "Required platform checks are assigned an owner or marked not applicable with rationale.",
        "Required evidence is attached before launch approval.",
        "Any platform-specific blocker is resolved or formally accepted.",
    ]
    if required_checks:
        acceptance_criteria.append("Priority checks include: " + ", ".join(required_checks[:5]) + ".")

    return {
        "external_id": f"PLATFORM-STORY-{index:03d}",
        "parent_external_id": PLATFORM_EPIC_ID,
        "work_item_type": "story",
        "title": ticket_def.get("title", f"Review {profile.get('name')} controls"),
        "description": ticket_def.get("purpose", f"Review platform-specific controls for {profile.get('name')}.") + f"\n\nDetected profile: {profile.get('id')} ({profile.get('platform_type')}).",
        "business_context": "The intake names systems or platforms that introduce specific governance, access, data, delivery, or reporting controls.",
        "user_story": f"As a platform owner, I need to review {profile.get('name')} controls so that platform-specific governance risks are addressed before launch.",
        "acceptance_criteria": acceptance_criteria,
        "definition_of_done": [
            "Required checks are completed or marked not applicable with rationale.",
            "Required evidence is attached.",
            "Launch blockers are resolved or accepted by authorized owners.",
            "Ticket is linked to the platform control profile epic.",
        ],
        "owner_role": ticket_def.get("owner_role", "Platform Owner / Security / Data Governance"),
        "evidence_required": evidence_required,
        "launch_blocker": bool(ticket_def.get("launch_blocker", True)),
        **defaults,
    }


def evidence_item_exists(packet: dict[str, Any], area: str, artifact: str) -> bool:
    for item in packet.get("evidence_items", []):
        if item.get("evidence_area") == area and item.get("required_artifact") == artifact:
            return True
    return False


def add_platform_evidence(packet: dict[str, Any], report: dict[str, Any]) -> None:
    evidence_items = packet.setdefault("evidence_items", [])
    open_blockers = packet.setdefault("open_blockers", [])

    for profile in report.get("detected_profiles", []):
        area = f"Platform profile: {profile.get('name')}"
        for artifact in profile.get("required_evidence", []):
            if not evidence_item_exists(packet, area, artifact):
                evidence_items.append({
                    "evidence_area": area,
                    "required_artifact": artifact,
                    "owner_role": "Platform Owner / Security / Data Governance",
                    "status": "missing",
                    "launch_blocker": True,
                    "evidence_link": "",
                    "decision_notes": "",
                    "approved_by": "",
                    "approved_at": "",
                    "expires_or_review_by": "",
                })

        for blocker in profile.get("launch_blockers", []):
            blocker_text = f"{profile.get('name')}: {blocker}"
            if blocker_text not in open_blockers:
                open_blockers.append(blocker_text)

    if report.get("detected_profiles"):
        packet["launch_decision"] = "blocked"


def augment_package(output_dir: Path) -> list[Path]:
    ticket_path = output_dir / "generated_ticket_hierarchy.json"
    evidence_path = output_dir / "evidence_packet.json"
    report_path = output_dir / "platform_profile_report.json"

    tickets: list[dict[str, Any]] = load_json(ticket_path)
    evidence_packet: dict[str, Any] = load_json(evidence_path)
    report: dict[str, Any] = load_json(report_path)

    detected_profiles = report.get("detected_profiles", [])
    if not detected_profiles:
        return []

    defaults = base_ticket_defaults(tickets)
    parent_id = first_initiative_id(tickets)

    if not any(ticket.get("external_id") == PLATFORM_EPIC_ID for ticket in tickets):
        tickets.append(build_platform_epic(parent_id, defaults))

    existing_titles = {ticket.get("title") for ticket in tickets}
    next_index = 1
    for profile in detected_profiles:
        for ticket_def in profile.get("recommended_tickets", []):
            title = ticket_def.get("title")
            if title in existing_titles:
                continue
            tickets.append(build_platform_story(profile, ticket_def, next_index, defaults))
            existing_titles.add(title)
            next_index += 1

    add_platform_evidence(evidence_packet, report)

    write_json(ticket_path, tickets)
    write_json(evidence_path, evidence_packet)
    (output_dir / "generated_ticket_hierarchy.md").write_text(governed_delivery_cli.render_tickets_md([dict_to_ticket(ticket) for ticket in tickets]), encoding="utf-8")
    (output_dir / "evidence_packet.md").write_text(governed_delivery_cli.render_evidence_md(evidence_packet), encoding="utf-8")
    governed_delivery_cli.write_jira_csv(output_dir / "jira_export.csv", [dict_to_ticket(ticket) for ticket in tickets])

    return [
        ticket_path,
        output_dir / "generated_ticket_hierarchy.md",
        evidence_path,
        output_dir / "evidence_packet.md",
        output_dir / "jira_export.csv",
    ]


def dict_to_ticket(data: dict[str, Any]) -> governed_delivery_cli.Ticket:
    fields = governed_delivery_cli.Ticket.__dataclass_fields__.keys()
    filtered = {field: data.get(field) for field in fields}

    # Defaults for optional list/string fields when data came from older generated packages.
    list_fields = [
        "acceptance_criteria",
        "definition_of_done",
        "systems_impacted",
        "data_involved",
        "soc2_impact",
        "dependencies",
        "blockers",
        "evidence_required",
        "evidence_links",
    ]
    for field in list_fields:
        if filtered.get(field) is None:
            filtered[field] = []

    bool_fields = [
        "phi_flag",
        "pii_flag",
        "pci_flag",
        "external_recipient",
        "file_movement_required",
        "legal_review_required",
        "security_review_required",
        "data_governance_required",
        "qa_required",
        "launch_blocker",
        "export_ready",
    ]
    for field in bool_fields:
        filtered[field] = bool(filtered.get(field))

    string_defaults = {
        "external_id": "",
        "parent_external_id": "",
        "platform": "generic",
        "work_item_type": "task",
        "title": "",
        "description": "",
        "business_context": "",
        "user_story": "",
        "request_type": "platform_governance",
        "program": "Unknown",
        "client": "Unknown",
        "delivery_method": "unknown",
        "risk_rating": "L4",
        "timeline_risk_rating": "L2",
        "ticket_quality_rating": "L2",
        "priority": "high",
        "owner_role": "Platform Owner",
        "assignee": "TBD",
        "due_date": "",
        "sprint_or_iteration": "",
        "status": "New",
    }
    for field, default in string_defaults.items():
        if filtered.get(field) is None:
            filtered[field] = default

    return governed_delivery_cli.Ticket(**filtered)
