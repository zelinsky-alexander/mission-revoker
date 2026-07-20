"""Revocation fan-out coordination and adapter contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Protocol

from .graph import MissionGraph
from .models import Node, NodeStatus, utc_now


@dataclass(frozen=True, slots=True)
class RevocationResult:
    target_id: str
    source_system: str
    accepted: bool
    enforced_at: datetime | None = None
    detail: str = ""

    def to_dict(self) -> dict[str, object]:
        result = asdict(self)
        result["enforced_at"] = self.enforced_at.isoformat() if self.enforced_at else None
        return result


class RevocationAdapter(Protocol):
    source_system: str

    def supports(self, node: Node) -> bool:
        """Return whether this adapter can revoke or cancel the node."""

    def revoke(self, node: Node, *, requested_at: datetime) -> RevocationResult:
        """Attempt revocation and return independently recordable evidence."""


@dataclass(slots=True)
class RevocationRun:
    root_id: str
    requested_at: datetime
    targeted_nodes: list[str]
    results: list[RevocationResult]

    @property
    def accepted_count(self) -> int:
        return sum(result.accepted for result in self.results)

    @property
    def unsupported_count(self) -> int:
        return len(self.targeted_nodes) - len(self.results)


class RevocationCoordinator:
    def __init__(self, graph: MissionGraph, adapters: list[RevocationAdapter] | None = None) -> None:
        self.graph = graph
        self.adapters = list(adapters or [])

    def revoke_subtree(
        self,
        root_id: str,
        *,
        requested_at: datetime | None = None,
    ) -> RevocationRun:
        timestamp = requested_at or utc_now()
        targets = self.graph.descendants(root_id, include_root=True)
        results: list[RevocationResult] = []

        for node in targets:
            adapter = next((item for item in self.adapters if item.supports(node)), None)
            if adapter is None:
                node.status = NodeStatus.UNKNOWN
                continue
            result = adapter.revoke(node, requested_at=timestamp)
            results.append(result)
            if result.accepted:
                node.status = NodeStatus.REVOKED
            else:
                node.status = NodeStatus.UNKNOWN

        return RevocationRun(
            root_id=root_id,
            requested_at=timestamp,
            targeted_nodes=[node.node_id for node in targets],
            results=results,
        )


class InMemoryRevocationAdapter:
    """Deterministic adapter for local tests and demos."""

    def __init__(self, source_system: str, *, reject_targets: set[str] | None = None) -> None:
        self.source_system = source_system
        self.reject_targets = set(reject_targets or set())
        self.calls: list[str] = []

    def supports(self, node: Node) -> bool:
        return node.source_system == self.source_system

    def revoke(self, node: Node, *, requested_at: datetime) -> RevocationResult:
        self.calls.append(node.node_id)
        accepted = node.node_id not in self.reject_targets
        return RevocationResult(
            target_id=node.node_id,
            source_system=self.source_system,
            accepted=accepted,
            enforced_at=requested_at if accepted else None,
            detail="revoked" if accepted else "simulated adapter rejection",
        )
