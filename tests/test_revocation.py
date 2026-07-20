import unittest
from datetime import datetime, timezone

from mission_revoker.graph import MissionGraph
from mission_revoker.models import Node, NodeKind, NodeStatus
from mission_revoker.revocation import InMemoryRevocationAdapter, RevocationCoordinator


class RevocationTests(unittest.TestCase):
    def test_fanout_marks_supported_nodes_and_unknowns(self) -> None:
        graph = MissionGraph()
        graph.add_nodes(
            [
                Node("mission", "mission", NodeKind.MISSION, "core"),
                Node("agt-agent", "mission", NodeKind.AGENT, "agt", "mission"),
                Node("a2a-task", "mission", NodeKind.TASK, "a2a", "agt-agent"),
            ]
        )
        coordinator = RevocationCoordinator(
            graph,
            [
                InMemoryRevocationAdapter("core"),
                InMemoryRevocationAdapter("agt"),
            ],
        )

        run = coordinator.revoke_subtree(
            "mission",
            requested_at=datetime(2026, 7, 20, 10, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(run.accepted_count, 2)
        self.assertEqual(run.unsupported_count, 1)
        self.assertEqual(graph.get("mission").status, NodeStatus.REVOKED)
        self.assertEqual(graph.get("agt-agent").status, NodeStatus.REVOKED)
        self.assertEqual(graph.get("a2a-task").status, NodeStatus.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
