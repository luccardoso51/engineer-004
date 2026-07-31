import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics_pipeline.compliance import find_deletion_cascade  # noqa: E402
from analytics_pipeline.loader import load_jsonl  # noqa: E402
from analytics_pipeline.main import report_deletion_cascade  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "event_sample.jsonl"


class TestDeletionCascade(unittest.TestCase):
    def test_evt_0017_cascade_includes_evt_0006(self) -> None:
        load_result = load_jsonl(FIXTURE)
        privacy_event = next(e for e in load_result.events if e["event_id"] == "evt-0017")
        cascade = find_deletion_cascade(load_result.events, privacy_event)
        self.assertIn("evt-0017", cascade)
        self.assertIn("evt-0006", cascade)
        self.assertNotIn("evt-0001", cascade)

    def test_cli_deletion_cascade_report(self) -> None:
        load_result = load_jsonl(FIXTURE)
        report = report_deletion_cascade(load_result, "evt-0017")
        self.assertEqual(report["privacy_event_id"], "evt-0017")
        self.assertGreaterEqual(report["cascade_count"], 2)
        self.assertIn("evt-0006", report["cascade_event_ids"])


if __name__ == "__main__":
    unittest.main()
