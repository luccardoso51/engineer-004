import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics_pipeline.loader import load_jsonl  # noqa: E402
from analytics_pipeline.main import build_report  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "event_sample.jsonl"
ROOT = Path(__file__).resolve().parents[1]


class TestMainCli(unittest.TestCase):
    def test_build_report_has_24_census_keys(self) -> None:
        report = build_report(load_jsonl(FIXTURE))
        self.assertEqual(report["summary"]["total_keys"], 24)
        self.assertIn("evt-0020", report["events"])
        self.assertEqual(report["events"]["evt-0020"]["status"], "dead_letter")

    def test_evt_0020_dead_letter_not_crash(self) -> None:
        report = build_report(load_jsonl(FIXTURE))
        dead = report["events"]["evt-0020"]
        self.assertEqual(len(dead["anomalies"]), 1)
        self.assertEqual(dead["anomalies"][0]["action"], "dead_letter")

    def test_cli_prints_json(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "analytics_pipeline.main", "--fixture", str(FIXTURE)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(ROOT / "src")},
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["summary"]["total_keys"], 24)


if __name__ == "__main__":
    unittest.main()
