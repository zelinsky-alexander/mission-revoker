"""Mission dependency graph and coverage analysis."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable

from .models import Node, NodeStatus


class MissionGraph:
    """In-memory directed graph keyed by stable node identifiers."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._children: dict[str, set[str]] = defaultdict(set)

    def add_node(self, node: Node) -> None:
        existing = self._nodes.get(node.node_id)
        if existing and existing.mission_id != node.mission_id:
            raise ValueError(f"node {node.node_id!r} is already bound to another mission")
        if node.parent_id == node.node_id:
            raise ValueError("a node cannot be its own parent")
        self._nodes[node.node_id] = node
        if node.parent_id:
            self._children[node.parent_id].add(node.node_id)
            self._assert_acyclic_from(node.node_id)

    def add_nodes(self, nodes: Iterable[Node]) -> None:
        for node in nodes:
            self.add_node(node)

    def get(self, node_id: str) -> Node:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"unknown node: {node_id}") from exc

    def nodes_for_mission(self, mission_id: str) -> list[Node]:
        return sorted(
            (node for node in self._nodes.values() if node.mission_id == mission_id),
            key=lambda node: node.node_id,
        )

    def descendants(self, root_id: str, *, include_root: bool = False) -> list[Node]:
        self.get(root_id)
        result: list[Node] = [self._nodes[root_id]] if include_root else []
        queue: deque[str] = deque(sorted(self._children.get(root_id, set())))
        visited: set[str] = set()
        while queue:
            current_id = queue.popleft()
            if current_id in visited:
                continue
            visited.add(current_id)
            result.append(self._nodes[current_id])
            queue.extend(sorted(self._children.get(current_id, set())))
        return result

    def mark_subtree(self, root_id: str, status: NodeStatus) -> list[Node]:
        affected = self.descendants(root_id, include_root=True)
        for node in affected:
            node.status = status
        return affected

    def orphan_nodes(self, mission_id: str) -> list[Node]:
        """Return nodes whose declared parent is absent from the current graph."""
        return [
            node
            for node in self.nodes_for_mission(mission_id)
            if node.parent_id and node.parent_id not in self._nodes
        ]

    def coverage(self, mission_id: str) -> dict[str, int]:
        nodes = self.nodes_for_mission(mission_id)
        return {
            "known_nodes": len(nodes),
            "orphan_nodes": len(self.orphan_nodes(mission_id)),
            "unknown_status_nodes": sum(node.status is NodeStatus.UNKNOWN for node in nodes),
        }

    def to_dict(self, mission_id: str) -> dict[str, object]:
        return {
            "mission_id": mission_id,
            "coverage": self.coverage(mission_id),
            "nodes": [node.to_dict() for node in self.nodes_for_mission(mission_id)],
        }

    def _assert_acyclic_from(self, node_id: str) -> None:
        seen: set[str] = set()
        current = self._nodes[node_id]
        while current.parent_id:
            if current.parent_id == node_id or current.parent_id in seen:
                raise ValueError(f"cycle detected while adding node {node_id!r}")
            seen.add(current.parent_id)
            parent = self._nodes.get(current.parent_id)
            if parent is None:
                return
            current = parent
