"""CLI entry point for the analytics pipeline fixture analyzer."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from analytics_pipeline.anomalies import Anomaly, detect_anomalies
from analytics_pipeline.loader import DeadLetter, LoadResult, load_jsonl


def _anomaly_to_dict(anomaly: Anomaly) -> dict:
    return asdict(anomaly)


def _dead_letter_anomaly(dead_letter: DeadLetter) -> Anomaly:
    return Anomaly(
        event_id=dead_letter.event_id,
        anomaly_class="malformed_json_record",
        detail=f"json.loads failed on line {dead_letter.line_number}: {dead_letter.error}",
        action="dead_letter",
    )


def build_report(load_result: LoadResult) -> dict:
    """Build a census keyed by event_id with per-event status and summary counts."""
    anomalies = detect_anomalies(load_result.events)
    by_event_id: dict[str, list[Anomaly]] = {}
    for anomaly in anomalies:
        by_event_id.setdefault(anomaly.event_id, []).append(anomaly)

    census: dict[str, dict] = {}
    for event in load_result.events:
        event_id = str(event["event_id"])
        event_anomalies = by_event_id.get(event_id, [])
        if event_id not in census:
            census[event_id] = {
                "anomalies": [_anomaly_to_dict(a) for a in event_anomalies],
                "status": "flagged" if event_anomalies else "clean",
            }

    for dead_letter in load_result.dead_letters:
        anomaly = _dead_letter_anomaly(dead_letter)
        census[dead_letter.event_id] = {
            "anomalies": [_anomaly_to_dict(anomaly)],
            "status": "dead_letter",
        }

    class_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    for entry in census.values():
        for anomaly in entry["anomalies"]:
            class_counts[anomaly["anomaly_class"]] += 1
            action_counts[anomaly["action"]] += 1

    clean_count = sum(1 for entry in census.values() if entry["status"] == "clean")
    flagged_count = sum(1 for entry in census.values() if entry["status"] == "flagged")
    dead_letter_count = sum(1 for entry in census.values() if entry["status"] == "dead_letter")

    return {
        "events": census,
        "summary": {
            "total_keys": len(census),
            "clean": clean_count,
            "flagged": flagged_count,
            "dead_letter": dead_letter_count,
            "anomaly_class_counts": dict(sorted(class_counts.items())),
            "action_counts": dict(sorted(action_counts.items())),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analytics pipeline fixture analyzer")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("fixtures/event_sample.jsonl"),
        help="Path to the JSONL event fixture",
    )
    args = parser.parse_args()

    load_result = load_jsonl(args.fixture)
    report = build_report(load_result)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
