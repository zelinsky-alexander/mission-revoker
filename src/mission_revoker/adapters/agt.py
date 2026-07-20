"""Minimal normalization boundary for AGT-like audit entries.

This module intentionally avoids importing Microsoft Agent Governance Toolkit.
It accepts a plain mapping so upstream SDK changes remain isolated here.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..models import Event, EventType, parse_datetime


def normalize_agt_event(payload: Mapping[str, Any], *, mission_id: str) -> Event:
    event_type = _map_type(str(payload.get("event_type", "")))
    data = dict(payload.get("data", {}))
    return Event(
        event_id=str(payload.get("entry_id") or payload.get("event_id")),
        event_type=event_type,
        occurred_at=parse_datetime(str(payload["timestamp"])),
        source_system="microsoft-agt",
        mission_id=mission_id,
        node_id=_text(payload.get("agent_did")),
        parent_id=_text(payload.get("target_did")),
        action_id=_text(data.get("action_id") or payload.get("trace_id")),
        attributes={
            "action": payload.get("action"),
            "outcome": payload.get("outcome"),
            "policy_decision": payload.get("policy_decision"),
            "matched_rule": payload.get("matched_rule"),
            "upstream": data,
        },
    )


def _map_type(value: str) -> EventType:
    mapping = {
        "agent_invocation": EventType.DELEGATION_CREATED,
        "tool_invocation": EventType.ACTION_DISPATCHED,
        "tool_blocked": EventType.AUTHORIZATION_DECISION,
        "policy_evaluation": EventType.AUTHORIZATION_DECISION,
        "agent_terminated": EventType.TASK_CANCELLED,
    }
    return mapping.get(value, EventType.EVIDENCE_GAP)


def _text(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None
