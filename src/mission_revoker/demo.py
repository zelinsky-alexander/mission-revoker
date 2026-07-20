"""Deterministic local scenario used by the CLI and tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .models import Event, EventType


def demo_events() -> list[Event]:
    base = datetime(2026, 7, 20, 9, 59, 55, tzinfo=timezone.utc)

    def event(
        offset_ms: int,
        event_id: str,
        event_type: EventType,
        *,
        action_id: str | None = None,
        attributes: dict[str, object] | None = None,
        source: str = "demo",
    ) -> Event:
        return Event(
            event_id=event_id,
            event_type=event_type,
            occurred_at=base + timedelta(milliseconds=offset_ms),
            source_system=source,
            mission_id="mission-demo",
            action_id=action_id,
            attributes=attributes or {},
        )

    return [
        event(0, "evt-001", EventType.MISSION_CREATED),
        event(
            1000,
            "evt-002",
            EventType.AUTHORIZATION_DECISION,
            action_id="action-safe",
            attributes={"decision": "allow", "tool": "report.write"},
        ),
        event(1500, "evt-003", EventType.ACTION_DISPATCHED, action_id="action-safe"),
        event(
            1800,
            "evt-004",
            EventType.EXECUTION_ACKNOWLEDGED,
            action_id="action-safe",
            attributes={"status": "success"},
        ),
        event(5000, "evt-005", EventType.REVOCATION_REQUESTED),
        event(
            5400,
            "evt-006",
            EventType.AUTHORIZATION_DECISION,
            action_id="action-late",
            attributes={"decision": "allow", "cached": True},
            source="child-agent",
        ),
        event(
            5600,
            "evt-007",
            EventType.ACTION_DISPATCHED,
            action_id="action-late",
            source="queue-worker",
        ),
        event(
            5700,
            "evt-008",
            EventType.EXECUTION_ACKNOWLEDGED,
            action_id="action-late",
            attributes={"status": "cancelled"},
            source="mock-mcp-tool",
        ),
        event(
            6200,
            "evt-009",
            EventType.EFFECT_OBSERVED,
            action_id="action-late",
            attributes={"effect": "github.comment.created", "external_id": "comment-17"},
            source="target-ledger",
        ),
        event(
            6500,
            "evt-010",
            EventType.ACTION_DISPATCHED,
            action_id="action-unknown",
            source="unmapped-worker",
        ),
    ]
