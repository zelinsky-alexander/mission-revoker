"""Reconcile authorization evidence with downstream execution and effects."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Iterable

from .models import Event, EventType


@dataclass(slots=True)
class ActionEvidence:
    action_id: str
    authorization: Event | None = None
    queued: Event | None = None
    dispatched: Event | None = None
    acknowledged: Event | None = None
    observed_effects: list[Event] = field(default_factory=list)

    def latest_time(self) -> datetime | None:
        candidates = [
            event.occurred_at
            for event in (
                self.authorization,
                self.queued,
                self.dispatched,
                self.acknowledged,
            )
            if event is not None
        ]
        candidates.extend(event.occurred_at for event in self.observed_effects)
        return max(candidates) if candidates else None


@dataclass(frozen=True, slots=True)
class Finding:
    severity: str
    code: str
    action_id: str | None
    message: str
    evidence_event_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["evidence_event_ids"] = list(self.evidence_event_ids)
        return result


@dataclass(slots=True)
class ReconciliationReport:
    mission_id: str
    revoked_at: datetime | None
    action_count: int
    post_revocation_attempts: int
    post_revocation_effects: int
    evidence_gaps: int
    findings: list[Finding]

    @property
    def overall(self) -> str:
        if any(item.severity == "critical" for item in self.findings):
            return "UNTRUSTED"
        if self.evidence_gaps:
            return "UNKNOWN"
        return "TRUSTED"

    def to_dict(self) -> dict[str, object]:
        return {
            "mission_id": self.mission_id,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "action_count": self.action_count,
            "post_revocation_attempts": self.post_revocation_attempts,
            "post_revocation_effects": self.post_revocation_effects,
            "evidence_gaps": self.evidence_gaps,
            "overall": self.overall,
            "findings": [item.to_dict() for item in self.findings],
        }


class Reconciler:
    def reconcile(self, events: Iterable[Event], mission_id: str) -> ReconciliationReport:
        ordered = sorted(
            (event for event in events if event.mission_id == mission_id),
            key=lambda event: (event.occurred_at, event.event_id),
        )
        revoked_at = self._revocation_time(ordered)
        actions = self._group_actions(ordered)
        findings: list[Finding] = []
        post_attempts = 0
        post_effects = 0
        evidence_gaps = 0

        for action in actions.values():
            if action.authorization and action.authorization.attributes.get("decision") == "deny":
                if action.dispatched or action.acknowledged or action.observed_effects:
                    findings.append(
                        Finding(
                            severity="critical",
                            code="DENIED_ACTION_EXECUTED",
                            action_id=action.action_id,
                            message="Evidence indicates execution after an explicit deny decision.",
                            evidence_event_ids=self._ids(action),
                        )
                    )

            if revoked_at and action.dispatched and action.dispatched.occurred_at > revoked_at:
                post_attempts += 1
                findings.append(
                    Finding(
                        severity="high",
                        code="DISPATCH_AFTER_REVOCATION",
                        action_id=action.action_id,
                        message="The action was dispatched after mission revocation.",
                        evidence_event_ids=(action.dispatched.event_id,),
                    )
                )

            observed_after = [
                effect for effect in action.observed_effects if revoked_at and effect.occurred_at > revoked_at
            ]
            if observed_after:
                post_effects += len(observed_after)
                findings.append(
                    Finding(
                        severity="critical",
                        code="EFFECT_AFTER_REVOCATION",
                        action_id=action.action_id,
                        message="An independent downstream effect was observed after revocation.",
                        evidence_event_ids=tuple(effect.event_id for effect in observed_after),
                    )
                )

            if action.dispatched and not action.acknowledged and not action.observed_effects:
                evidence_gaps += 1
                findings.append(
                    Finding(
                        severity="medium",
                        code="MISSING_EXECUTION_EVIDENCE",
                        action_id=action.action_id,
                        message="The action was dispatched, but no acknowledgement or downstream effect evidence exists.",
                        evidence_event_ids=(action.dispatched.event_id,),
                    )
                )

            if action.acknowledged and action.acknowledged.attributes.get("status") == "cancelled":
                if action.observed_effects:
                    evidence_gaps += 1
                    findings.append(
                        Finding(
                            severity="critical",
                            code="CANCELLED_BUT_EFFECT_OBSERVED",
                            action_id=action.action_id,
                            message="The executor reported cancellation, but a downstream effect was observed.",
                            evidence_event_ids=self._ids(action),
                        )
                    )

        return ReconciliationReport(
            mission_id=mission_id,
            revoked_at=revoked_at,
            action_count=len(actions),
            post_revocation_attempts=post_attempts,
            post_revocation_effects=post_effects,
            evidence_gaps=evidence_gaps,
            findings=findings,
        )

    @staticmethod
    def _revocation_time(events: list[Event]) -> datetime | None:
        times = [
            event.occurred_at
            for event in events
            if event.event_type is EventType.REVOCATION_REQUESTED
        ]
        return min(times) if times else None

    @staticmethod
    def _group_actions(events: list[Event]) -> dict[str, ActionEvidence]:
        actions: dict[str, ActionEvidence] = {}
        for event in events:
            if not event.action_id:
                continue
            item = actions.setdefault(event.action_id, ActionEvidence(event.action_id))
            if event.event_type is EventType.AUTHORIZATION_DECISION:
                item.authorization = event
            elif event.event_type is EventType.ACTION_QUEUED:
                item.queued = event
            elif event.event_type is EventType.ACTION_DISPATCHED:
                item.dispatched = event
            elif event.event_type is EventType.EXECUTION_ACKNOWLEDGED:
                item.acknowledged = event
            elif event.event_type is EventType.EFFECT_OBSERVED:
                item.observed_effects.append(event)
        return actions

    @staticmethod
    def _ids(action: ActionEvidence) -> tuple[str, ...]:
        events = [
            action.authorization,
            action.queued,
            action.dispatched,
            action.acknowledged,
            *action.observed_effects,
        ]
        return tuple(event.event_id for event in events if event is not None)
