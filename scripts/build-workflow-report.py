#!/usr/bin/env python3

import csv
import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DETAIL_DIR = ROOT_DIR / "flows" / "raw" / "workflow-details"
REPORT_DIR = ROOT_DIR / "flows" / "reports"
SUMMARY_CSV = REPORT_DIR / "workflow-summary.csv"
FINDINGS_MD = REPORT_DIR / "workflow-findings.md"


def iter_action_strings(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and key.lower() in {
                "actiontype",
                "actiontypeid",
                "type",
                "typename",
                "functionname",
            }:
                yield value
            yield from iter_action_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_action_strings(item)


def classify_actions(actions):
    tokens = [token.lower() for token in iter_action_strings(actions)]
    text = " ".join(tokens)

    categories = []
    checks = [
        ("send_email", ("email", "marketing email")),
        ("set_property", ("property", "set_property", "setproperty")),
        ("branch", ("branch", "if_then", "if/then")),
        ("delay", ("delay", "wait_until", "wait")),
        ("create_record", ("create", "record")),
        ("create_task", ("task",)),
        ("list_membership", ("list",)),
    ]

    for label, patterns in checks:
        if all(pattern in text for pattern in patterns):
            categories.append(label)

    return ",".join(categories)


def classify_trigger(enrollment):
    if not enrollment:
        return "none"

    text = json.dumps(enrollment).lower()

    if "list" in text:
        return "list-based"
    if "event" in text:
        return "event-based"
    if "filter" in text:
        return "filter-based"
    if "property" in text:
        return "property-based"
    if "form" in text:
        return "form-based"
    return "custom"


def load_workflows():
    workflows = []
    if not DETAIL_DIR.exists():
        return workflows

    for path in sorted(DETAIL_DIR.glob("*.json")):
        with path.open() as handle:
            workflows.append(json.load(handle))
    return workflows


def build_rows(workflows):
    rows = []
    for workflow in workflows:
        actions = workflow.get("actions") or []
        enrollment = workflow.get("enrollmentCriteria") or workflow.get("enrollment") or {}
        row = {
            "id": workflow.get("id", ""),
            "name": workflow.get("name", ""),
            "isEnabled": workflow.get("isEnabled", ""),
            "type": workflow.get("type", workflow.get("flowType", "")),
            "objectTypeId": workflow.get("objectTypeId", ""),
            "revisionId": workflow.get("revisionId", ""),
            "createdAt": workflow.get("createdAt", ""),
            "updatedAt": workflow.get("updatedAt", ""),
            "actionCount": len(actions) if isinstance(actions, list) else 0,
            "actionCategories": classify_actions(actions),
            "hasEnrollmentCriteria": bool(enrollment),
            "triggerType": classify_trigger(enrollment),
        }
        rows.append(row)
    return rows


def write_summary(rows):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "name",
        "isEnabled",
        "type",
        "objectTypeId",
        "revisionId",
        "createdAt",
        "updatedAt",
        "actionCount",
        "actionCategories",
        "hasEnrollmentCriteria",
        "triggerType",
    ]
    with SUMMARY_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_findings(rows):
    send_email = [row["name"] or row["id"] for row in rows if "send_email" in row["actionCategories"]]
    set_property = [row["name"] or row["id"] for row in rows if "set_property" in row["actionCategories"]]
    branches = [row["name"] or row["id"] for row in rows if "branch" in row["actionCategories"]]
    delays = [row["name"] or row["id"] for row in rows if "delay" in row["actionCategories"]]

    lines = [
        "# Workflow Findings",
        "",
        f"- Total workflows analyzed: {len(rows)}",
        f"- Workflows with email actions: {len(send_email)}",
        f"- Workflows with property updates: {len(set_property)}",
        f"- Workflows with branching: {len(branches)}",
        f"- Workflows with delays: {len(delays)}",
        "",
        "## Sample Matches",
        "",
        f"- Email actions: {', '.join(send_email[:10]) if send_email else 'None detected'}",
        f"- Property updates: {', '.join(set_property[:10]) if set_property else 'None detected'}",
        f"- Branching: {', '.join(branches[:10]) if branches else 'None detected'}",
        f"- Delays: {', '.join(delays[:10]) if delays else 'None detected'}",
        "",
        "The CSV report is the authoritative flattened summary. Refer back to the raw workflow JSON files for exact workflow definitions.",
    ]

    FINDINGS_MD.write_text("\n".join(lines) + "\n")


def main():
    workflows = load_workflows()
    rows = build_rows(workflows)
    write_summary(rows)
    write_findings(rows)
    print(f"Wrote {SUMMARY_CSV}")
    print(f"Wrote {FINDINGS_MD}")


if __name__ == "__main__":
    main()
