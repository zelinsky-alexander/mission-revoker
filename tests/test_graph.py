import unittest

from mission_revoker.graph import MissionGraph
from mission_revoker.models import Node, NodeKind


class MissionGraphTests(unittest.TestCase):
    def test_descendants_and_orphans(self) -> None:
        graph = MissionGraph()
        graph.add_nodes(
            [
                Node("mission-1", "mission-1", NodeKind.MISSION, "test"),
                Node("agent-a", "mission-1", NodeKind.AGENT, "agt", "mission-1"),
                Node("task-a", "mission-1", NodeKind.TASK, "a2a", "agent-a"),
                Node("orphan", "mission-1", NodeKind.ACTION, "unknown", "missing-parent"),
            ]
        )

        descendants = [node.node_id for node in graph.descendants("mission-1")]
        self.assertEqual(descendants, ["agent-a", "task-a"])
        self.assertEqual([node.node_id for node in graph.orphan_nodes("mission-1")], ["orphan"])

    def test_cycle_is_rejected(self) -> None:
        graph = MissionGraph()
        graph.add_node(Node("a", "m", NodeKind.AGENT, "test", "b"))
        with self.assertRaises(ValueError):
            graph.add_node(Node("b", "m", NodeKind.AGENT, "test", "a"))


if __name__ == "__main__":
    unittest.main()
