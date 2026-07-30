import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics_pipeline.main import load_jsonl  # noqa: E402


class TestLoadJsonl(unittest.TestCase):
    def test_loads_fixture_events(self) -> None:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "event_sample.jsonl"
        events = load_jsonl(fixture)
        self.assertGreater(len(events), 0)
        self.assertIn("event_id", events[0])


if __name__ == "__main__":
    unittest.main()
