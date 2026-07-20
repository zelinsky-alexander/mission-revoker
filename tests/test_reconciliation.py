import unittest

from mission_revoker.demo import demo_events
from mission_revoker.reconciliation import Reconciler


class ReconciliationTests(unittest.TestCase):
    def test_demo_finds_post_revocation_effect_and_gap(self) -> None:
        report = Reconciler().reconcile(demo_events(), "mission-demo")

        self.assertEqual(report.overall, "UNTRUSTED")
        self.assertEqual(report.post_revocation_attempts, 2)
        self.assertEqual(report.post_revocation_effects, 1)
        self.assertGreaterEqual(report.evidence_gaps, 2)
        codes = {finding.code for finding in report.findings}
        self.assertIn("EFFECT_AFTER_REVOCATION", codes)
        self.assertIn("CANCELLED_BUT_EFFECT_OBSERVED", codes)
        self.assertIn("MISSING_EXECUTION_EVIDENCE", codes)


if __name__ == "__main__":
    unittest.main()
