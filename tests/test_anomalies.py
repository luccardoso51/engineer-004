import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from analytics_pipeline.anomalies import Anomaly, detect_anomalies  # noqa: E402
from analytics_pipeline.loader import load_jsonl  # noqa: E402
from analytics_pipeline.main import build_report  # noqa: E402

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "event_sample.jsonl"


def _ids_for_class(anomalies: list[Anomaly], anomaly_class: str) -> set[str]:
    return {a.event_id for a in anomalies if a.anomaly_class == anomaly_class}


def _actions_for_id(anomalies: list[Anomaly], event_id: str) -> set[str]:
    return {a.action for a in anomalies if a.event_id == event_id}


class TestDetectAnomaliesOnFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = load_jsonl(FIXTURE).events
        cls.anomalies = detect_anomalies(cls.events)

    def test_duplicate_event_id_evt_0002(self) -> None:
        self.assertIn("evt-0002", _ids_for_class(self.anomalies, "duplicate_event_id"))
        dupes = [a for a in self.anomalies if a.anomaly_class == "duplicate_event_id"]
        self.assertEqual(len(dupes), 1)
        self.assertEqual(dupes[0].action, "dedupe")

    def test_clock_skew_evt_0005(self) -> None:
        self.assertIn("evt-0005", _ids_for_class(self.anomalies, "clock_skew"))

    def test_timezone_offset_evt_0006(self) -> None:
        self.assertIn("evt-0006", _ids_for_class(self.anomalies, "timezone_offset"))

    def test_future_timestamp_evt_0016(self) -> None:
        self.assertIn("evt-0016", _ids_for_class(self.anomalies, "future_timestamp"))

    def test_missing_tenant_evt_0011(self) -> None:
        self.assertIn("evt-0011", _ids_for_class(self.anomalies, "missing_required_field"))
        self.assertIn("quarantine", _actions_for_id(self.anomalies, "evt-0011"))

    def test_unexpected_pii_evt_0007(self) -> None:
        self.assertIn("evt-0007", _ids_for_class(self.anomalies, "unexpected_pii"))

    def test_schema_drift_evt_0009(self) -> None:
        self.assertIn("evt-0009", _ids_for_class(self.anomalies, "schema_drift"))
        self.assertIn("normalize", _actions_for_id(self.anomalies, "evt-0009"))

    def test_bot_burst_evt_0012_through_0015(self) -> None:
        flagged = _ids_for_class(self.anomalies, "bot_burst")
        self.assertEqual(flagged, {"evt-0012", "evt-0013", "evt-0014", "evt-0015"})

    def test_compliance_critical_evt_0017(self) -> None:
        self.assertIn("evt-0017", _ids_for_class(self.anomalies, "compliance_critical"))
        self.assertIn("route_compliance", _actions_for_id(self.anomalies, "evt-0017"))

    def test_clean_negative_evt_0001(self) -> None:
        flagged = {a.event_id for a in self.anomalies}
        self.assertNotIn("evt-0001", flagged)

    def test_all_nine_taxonomy_classes_present_in_pipeline(self) -> None:
        report = build_report(load_jsonl(FIXTURE))
        classes = set(report["summary"]["anomaly_class_counts"])
        expected = {
            "duplicate_event_id",
            "clock_skew",
            "timezone_offset",
            "future_timestamp",
            "missing_required_field",
            "unexpected_pii",
            "schema_drift",
            "bot_burst",
            "malformed_json_record",
        }
        self.assertTrue(expected.issubset(classes))


class TestBorderlineCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.events = load_jsonl(FIXTURE).events
        cls.by_id = {event["event_id"]: event for event in cls.events}

    def test_evt_0006_not_classified_as_future(self) -> None:
        anomalies = detect_anomalies(self.events)
        classes = {a.anomaly_class for a in anomalies if a.event_id == "evt-0006"}
        self.assertIn("timezone_offset", classes)
        self.assertNotIn("future_timestamp", classes)
        self.assertIn("flag_for_correction", _actions_for_id(anomalies, "evt-0006"))

    def test_evt_0009_normalize_not_drop(self) -> None:
        anomalies = detect_anomalies(self.events)
        drift = [a for a in anomalies if a.event_id == "evt-0009"]
        self.assertEqual(len(drift), 1)
        self.assertEqual(drift[0].action, "normalize")

    def test_evt_0017_routes_compliance_not_quality_defect(self) -> None:
        anomalies = detect_anomalies(self.events)
        compliance = [a for a in anomalies if a.event_id == "evt-0017"]
        self.assertEqual(len(compliance), 1)
        self.assertEqual(compliance[0].anomaly_class, "compliance_critical")

    def test_evt_0002_dedupe_by_event_id_not_payload(self) -> None:
        duplicates = [e for e in self.events if e["event_id"] == "evt-0002"]
        self.assertEqual(len(duplicates), 2)
        anomalies = detect_anomalies(self.events)
        dup_anomalies = [a for a in anomalies if a.event_id == "evt-0002"]
        self.assertEqual(len(dup_anomalies), 1)
        self.assertEqual(dup_anomalies[0].action, "dedupe")

    def test_evt_0011_quarantine_not_default(self) -> None:
        anomalies = detect_anomalies(self.events)
        missing = [a for a in anomalies if a.event_id == "evt-0011"]
        self.assertEqual(missing[0].action, "quarantine")

    def test_evt_0020_dead_letter_not_crash(self) -> None:
        load_result = load_jsonl(FIXTURE)
        self.assertEqual(len(load_result.dead_letters), 1)
        report = build_report(load_result)
        dead = report["events"]["evt-0020"]
        self.assertEqual(dead["status"], "dead_letter")
        self.assertEqual(dead["anomalies"][0]["anomaly_class"], "malformed_json_record")


if __name__ == "__main__":
    unittest.main()
