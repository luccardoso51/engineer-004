import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics_pipeline.loader import load_jsonl  # noqa: E402
from analytics_pipeline.main import build_report  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "event_sample.jsonl"


class TestLoadJsonl(unittest.TestCase):
    def test_loads_fixture_events(self) -> None:
        result = load_jsonl(FIXTURE)
        self.assertEqual(len(result.events), 24)
        self.assertIn("event_id", result.events[0])

    def test_dead_letters_malformed_evt_0020(self) -> None:
        result = load_jsonl(FIXTURE)
        self.assertEqual(len(result.dead_letters), 1)
        dead = result.dead_letters[0]
        self.assertEqual(dead.event_id, "evt-0020")
        self.assertEqual(dead.line_number, 21)

    def test_malformed_json_record_class_evt_0020(self) -> None:
        report = build_report(load_jsonl(FIXTURE))
        anomaly = report["events"]["evt-0020"]["anomalies"][0]
        self.assertEqual(anomaly["anomaly_class"], "malformed_json_record")
        self.assertEqual(anomaly["action"], "dead_letter")

    def test_dead_letter_fallback_event_id(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as fh:
            fh.write("{not valid json at all\n")
            path = Path(fh.name)
        try:
            result = load_jsonl(path)
            self.assertEqual(len(result.dead_letters), 1)
            self.assertEqual(result.dead_letters[0].event_id, "line:1")
            self.assertEqual(len(result.events), 0)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
