"""Report formatting helpers."""

from __future__ import annotations

import json

from .reconciliation import ReconciliationReport


def render_text(report: ReconciliationReport) -> str:
    lines = [
        f"Mission: {report.mission_id}",
        f"Revoked at: {report.revoked_at.isoformat() if report.revoked_at else 'not observed'}",
        f"Actions: {report.action_count}",
        f"Post-revocation attempts: {report.post_revocation_attempts}",
        f"Post-revocation observed effects: {report.post_revocation_effects}",
        f"Evidence gaps: {report.evidence_gaps}",
        f"Overall: {report.overall}",
    ]
    if report.findings:
        lines.append("")
        lines.append("Findings:")
        for finding in report.findings:
            action = f" action={finding.action_id}" if finding.action_id else ""
            lines.append(f"- [{finding.severity.upper()}] {finding.code}:{action} {finding.message}")
    return "\n".join(lines)


def render_json(report: ReconciliationReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)
