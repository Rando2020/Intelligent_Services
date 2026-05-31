#!/usr/bin/env python3
"""
Governed Workflow Diagram Generator

Creates Visio-like workflow diagram specs from a generated governed delivery package.

Outputs:
- workflow_diagram.json
- workflow_diagram.md
- workflow_diagram.mmd
- workflow_diagram.drawio.xml

This is intentionally dependency-free and produces a portable intermediate
representation that UI tools can render as swimlanes, node graphs, or exportable
diagrams.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


LANES = [
    {"id": "intake", "label": "Intake / Product", "owner_role": "Product / Implementation"},
    {"id": "governance", "label": "Governance Review", "owner_role": "Legal / Compliance / Data Governance"},
    {"id": "engineering", "label": "Engineering / Platform", "owner_role": "Data Engineering / Platform"},
    {"id": "qa", "label": "QA / Evidence", "owner_role": "QA / Operations"},
    {"id": "delivery", "label": "Launch / Delivery", "owner_role": "Product / Operations"},
]


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def safe_id(value: str) -> str:
    cleaned = "".join(char if char.isalnum() else "_" for char in value)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:80] or "node"


def truncate(value: str, limit: int = 80) -> str:
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def build_workflow_diagram(output_dir: Path, title: str | None = None) -> dict[str, Any]:
    normalized = load_json(output_dir / "normalized_intake.json") or {}
    scorecard = load_json(output_dir / "scorecard.json") or {}
    rule_report = load_json(output_dir / "rule_match_report.json") or {"matched_rules": []}
    profile_report = load_json(output_dir / "platform_profile_report.json") or {"detected_profiles": []}
    tickets = load_json(output_dir / "generated_ticket_hierarchy.json") or []
    evidence_packet = load_json(output_dir / "evidence_packet.json") or {"evidence_items": []}

    diagram_title = title or normalized.get("title") or "Governed Delivery Workflow"
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []

    def add_node(node_id: str, label: str, node_type: str, lane: str, **extra: Any) -> None:
        if any(node["id"] == node_id for node in nodes):
            return
        nodes.append({
            "id": node_id,
            "label": label,
            "type": node_type,
            "lane": lane,
            **extra,
        })

    def add_edge(source: str, target: str, label: str = "") -> None:
        if source and target and any(edge["from"] == source and edge["to"] == target for edge in edges):
            return
        edges.append({"from": source, "to": target, "label": label})

    add_node("start", "Messy Intake Submitted", "start", "intake", description="User submits messy operational intake.")
    add_node("normalize", "Normalize Intake", "process", "intake", description="Extract client, program, data types, systems, unknowns, and target launch context.")
    add_node("rules", "Apply YAML Rules", "control", "governance", description="Match configured governance, evidence, launch blocker, and ticket-builder rules.")
    add_node("platforms", "Detect Platform Profiles", "system", "engineering", description="Detect tools such as Snowflake, dbt, SFTP/MFT, Tableau/Power BI, APIs, and file movers.")
    add_node("score", f"Readiness Score: {scorecard.get('overall_score', 'N/A')}", "decision", "governance", description=f"Launch position: {scorecard.get('launch_position', 'unknown')}")

    add_edge("start", "normalize")
    add_edge("normalize", "rules")
    add_edge("rules", "platforms")
    add_edge("platforms", "score")

    previous_rule_node = "rules"
    for rule in rule_report.get("matched_rules", [])[:8]:
        node_id = f"rule_{safe_id(rule.get('id', 'rule'))}"
        add_node(
            node_id,
            truncate(f"{rule.get('id')}: {rule.get('name')}", 72),
            "blocked" if rule.get("launch_blocker") else "control",
            "governance",
            description=rule.get("finding", ""),
            source_rule_id=rule.get("id"),
            risk_level=rule.get("severity"),
            launch_blocker=bool(rule.get("launch_blocker")),
            evidence_required=rule.get("required_evidence", []),
        )
        add_edge(previous_rule_node, node_id, "matched")
        previous_rule_node = node_id
    add_edge(previous_rule_node, "score", "feeds score")

    previous_profile_node = "platforms"
    for profile in profile_report.get("detected_profiles", [])[:8]:
        node_id = f"profile_{safe_id(profile.get('id', 'profile'))}"
        add_node(
            node_id,
            truncate(profile.get("name", "Platform Profile"), 72),
            "system",
            "engineering",
            description=f"Detected keywords: {', '.join(profile.get('matched_keywords', []))}",
            source_profile_id=profile.get("id"),
            risk_level=profile.get("suggested_current_level"),
            launch_blocker=bool(profile.get("launch_blockers")),
            evidence_required=profile.get("required_evidence", []),
        )
        add_edge(previous_profile_node, node_id, "detected")
        previous_profile_node = node_id
    add_edge(previous_profile_node, "score", "platform risk")

    add_node("tickets", "Generate Work Items", "process", "delivery", description="Create governed Jira/ADO/Rally/Asana-ready work items.")
    add_node("evidence", "Assemble Evidence Packet", "evidence", "qa", description="Collect required artifacts, approvals, and validation evidence.")
    add_node("exports", "Export Jira / ADO / Rally / Asana", "export", "delivery", description="Produce CSV exports for work management systems.")
    add_node("decision", "Launch Decision", "decision", "delivery", description="Go/no-go decision based on blockers and evidence.")

    add_edge("score", "tickets", "create work")
    add_edge("score", "evidence", "collect proof")
    add_edge("tickets", "exports")
    add_edge("evidence", "decision")
    add_edge("exports", "decision")

    blocking_items = scorecard.get("launch_blockers", [])[:8]
    previous_blocker_node = "score"
    for index, blocker in enumerate(blocking_items, start=1):
        node_id = f"blocker_{index}"
        add_node(
            node_id,
            truncate(blocker.get("blocker", "Launch Blocker"), 72),
            "blocked",
            "governance",
            description=blocker.get("required_resolution", "Resolution required before launch."),
            launch_blocker=True,
            evidence_required=blocker.get("evidence_required", []),
        )
        add_edge(previous_blocker_node, node_id, "blocks")
        add_edge(node_id, "decision", "must resolve")
        previous_blocker_node = node_id

    evidence_items = evidence_packet.get("evidence_items", [])[:8]
    for index, item in enumerate(evidence_items, start=1):
        node_id = f"evidence_{index}"
        add_node(
            node_id,
            truncate(item.get("required_artifact", "Evidence"), 72),
            "evidence",
            "qa",
            description=item.get("evidence_area", "Evidence area"),
            launch_blocker=bool(item.get("launch_blocker")),
        )
        add_edge("evidence", node_id, "requires")
        add_edge(node_id, "decision", "supports")

    final_type = "blocked" if scorecard.get("launch_position") == "not_launchable" else "end"
    final_label = "Not Launchable" if scorecard.get("launch_position") == "not_launchable" else "Launchable With Controls"
    add_node("end", final_label, final_type, "delivery", description="Final readiness state for current intake.")
    add_edge("decision", "end")

    diagram = {
        "id": safe_id(diagram_title).lower(),
        "title": diagram_title,
        "orientation": "LR",
        "lanes": LANES,
        "nodes": nodes,
        "edges": edges,
    }
    diagram["exports"] = {
        "mermaid": render_mermaid(diagram),
        "markdown": render_markdown(diagram),
        "drawio_xml": render_drawio_xml(diagram),
    }
    return diagram


def render_mermaid(diagram: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    lane_nodes: dict[str, list[dict[str, Any]]] = {lane["id"]: [] for lane in diagram.get("lanes", [])}
    for node in diagram.get("nodes", []):
        lane_nodes.setdefault(node.get("lane", "other"), []).append(node)

    for lane in diagram.get("lanes", []):
        lane_id = lane["id"]
        lines.append(f"  subgraph {safe_id(lane_id)}[{quote_mermaid(lane['label'])}]")
        for node in lane_nodes.get(lane_id, []):
            lines.append(f"    {safe_id(node['id'])}{mermaid_shape(node)}")
        lines.append("  end")

    for edge in diagram.get("edges", []):
        label = edge.get("label", "")
        connector = f" -- {quote_mermaid(label)} --> " if label else " --> "
        lines.append(f"  {safe_id(edge['from'])}{connector}{safe_id(edge['to'])}")

    lines.extend([
        "  classDef blocked fill:#fee2e2,stroke:#dc2626,color:#7f1d1d;",
        "  classDef control fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e;",
        "  classDef evidence fill:#fef3c7,stroke:#d97706,color:#78350f;",
        "  classDef system fill:#ede9fe,stroke:#7c3aed,color:#3b0764;",
        "  classDef export fill:#dcfce7,stroke:#16a34a,color:#14532d;",
    ])
    for node in diagram.get("nodes", []):
        if node.get("type") in {"blocked", "control", "evidence", "system", "export"}:
            lines.append(f"  class {safe_id(node['id'])} {node['type']};")
    return "\n".join(lines) + "\n"


def mermaid_shape(node: dict[str, Any]) -> str:
    label = quote_mermaid(node.get("label", node.get("id", "node")))
    node_type = node.get("type")
    if node_type == "decision":
        return f"{{{label}}}"
    if node_type == "start" or node_type == "end":
        return f"([{label}])"
    if node_type == "blocked":
        return f"[[{label}]]"
    if node_type == "evidence":
        return f"[/{label}/]"
    return f"[{label}]"


def quote_mermaid(value: str) -> str:
    return '"' + str(value).replace('"', "'") + '"'


def render_markdown(diagram: dict[str, Any]) -> str:
    lines = [f"# {diagram.get('title', 'Workflow Diagram')}", "", "## Mermaid", "", "```mermaid", diagram["exports"]["mermaid"] if "exports" in diagram else render_mermaid(diagram), "```", "", "## Nodes", "", "| ID | Label | Type | Lane | Launch Blocker |", "|---|---|---|---|---|"]
    for node in diagram.get("nodes", []):
        lines.append(f"| {node['id']} | {node['label']} | {node['type']} | {node['lane']} | {'Yes' if node.get('launch_blocker') else 'No'} |")
    lines.extend(["", "## Edges", "", "| From | To | Label |", "|---|---|---|"])
    for edge in diagram.get("edges", []):
        lines.append(f"| {edge['from']} | {edge['to']} | {edge.get('label', '')} |")
    return "\n".join(lines) + "\n"


def render_drawio_xml(diagram: dict[str, Any]) -> str:
    """Create a basic draw.io compatible XML document.

    This is intentionally simple. It gives the UI/export layer a starting point
    that can be imported into diagrams.net/draw.io, then improved later.
    """
    cells = [
        '<mxCell id="0" />',
        '<mxCell id="1" parent="0" />',
    ]
    x_by_lane = {lane["id"]: 40 + index * 260 for index, lane in enumerate(diagram.get("lanes", []))}
    y_by_lane = {lane["id"]: 40 for lane in diagram.get("lanes", [])}
    for node in diagram.get("nodes", []):
        lane = node.get("lane", "intake")
        x = x_by_lane.get(lane, 40)
        y = y_by_lane.get(lane, 40)
        y_by_lane[lane] = y + 100
        style = drawio_style(node.get("type"))
        cells.append(
            f'<mxCell id="{html.escape(node["id"])}" value="{html.escape(node.get("label", ""))}" style="{style}" vertex="1" parent="1">'
            f'<mxGeometry x="{x}" y="{y}" width="220" height="70" as="geometry" />'
            '</mxCell>'
        )
    for index, edge in enumerate(diagram.get("edges", []), start=1):
        cells.append(
            f'<mxCell id="edge_{index}" value="{html.escape(edge.get("label", ""))}" edge="1" parent="1" source="{html.escape(edge["from"])}" target="{html.escape(edge["to"])}" style="endArrow=block;html=1;rounded=0;">'
            '<mxGeometry relative="1" as="geometry" />'
            '</mxCell>'
        )
    xml = "".join(cells)
    return f'<mxfile><diagram name="{html.escape(diagram.get("title", "Workflow"))}"><mxGraphModel><root>{xml}</root></mxGraphModel></diagram></mxfile>\n'


def drawio_style(node_type: str | None) -> str:
    base = "rounded=1;whiteSpace=wrap;html=1;"
    if node_type == "decision":
        return "rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;"
    if node_type == "blocked":
        return base + "fillColor=#f8cecc;strokeColor=#b85450;"
    if node_type == "evidence":
        return base + "fillColor=#fff2cc;strokeColor=#d6b656;"
    if node_type == "system":
        return base + "fillColor=#e1d5e7;strokeColor=#9673a6;"
    if node_type == "export":
        return base + "fillColor=#d5e8d4;strokeColor=#82b366;"
    return base + "fillColor=#dae8fc;strokeColor=#6c8ebf;"


def write_workflow_outputs(output_dir: Path, title: str | None = None) -> list[Path]:
    diagram = build_workflow_diagram(output_dir, title=title)
    json_path = output_dir / "workflow_diagram.json"
    md_path = output_dir / "workflow_diagram.md"
    mermaid_path = output_dir / "workflow_diagram.mmd"
    drawio_path = output_dir / "workflow_diagram.drawio.xml"
    json_path.write_text(json.dumps(diagram, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    mermaid_path.write_text(diagram["exports"]["mermaid"], encoding="utf-8")
    drawio_path.write_text(diagram["exports"]["drawio_xml"], encoding="utf-8")
    md_path.write_text(render_markdown(diagram), encoding="utf-8")
    return [json_path, md_path, mermaid_path, drawio_path]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a governed workflow diagram from an existing package output directory.")
    parser.add_argument("--output-dir", required=True, help="Existing generated package output directory.")
    parser.add_argument("--title", default=None, help="Optional diagram title.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = write_workflow_outputs(Path(args.output_dir), title=args.title)
    print("Workflow diagram outputs generated:")
    for path in outputs:
        print(f"- {path}")


if __name__ == "__main__":
    main()
