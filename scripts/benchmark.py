#!/usr/bin/env python3
"""Benchmark detect_anomalies throughput and latency against the real fixture."""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from analytics_pipeline.anomalies import detect_anomalies  # noqa: E402
from analytics_pipeline.loader import load_jsonl  # noqa: E402
from analytics_pipeline.main import build_report  # noqa: E402

FIXTURE = ROOT / "fixtures" / "event_sample.jsonl"
OUTPUT = ROOT / "docs" / "benchmark-results.md"
ITERATIONS = 10_000


def _format_report(
    *,
    iterations: int,
    event_count: int,
    total_seconds: float,
    latencies_ms: list[float],
    summary: dict,
) -> str:
    mean_ms = statistics.mean(latencies_ms)
    median_ms = statistics.median(latencies_ms)
    throughput = (iterations * event_count) / total_seconds

    lines = [
        "# Benchmark results",
        "",
        f"- Fixture: `{FIXTURE.relative_to(ROOT)}`",
        f"- Iterations: {iterations}",
        f"- Events per call: {event_count}",
        f"- Total wall time: {total_seconds:.6f}s",
        f"- Mean latency per call: {mean_ms:.6f}ms",
        f"- Median latency per call: {median_ms:.6f}ms",
        f"- Throughput: {throughput:.2f} events/sec",
        "",
        "## Pass/fail counts (from census summary)",
        "",
        f"- Total census keys: {summary['total_keys']}",
        f"- Clean: {summary['clean']}",
        f"- Flagged: {summary['flagged']}",
        f"- Dead letter: {summary['dead_letter']}",
        "",
        "## Anomaly class counts",
        "",
    ]
    for anomaly_class, count in summary["anomaly_class_counts"].items():
        lines.append(f"- {anomaly_class}: {count}")
    lines.extend(["", "## Action counts", ""])
    for action, count in summary["action_counts"].items():
        lines.append(f"- {action}: {count}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    load_result = load_jsonl(FIXTURE)
    events = load_result.events
    event_count = len(events)
    summary = build_report(load_result)["summary"]

    latencies_ms: list[float] = []
    start = time.perf_counter()
    for _ in range(ITERATIONS):
        call_start = time.perf_counter()
        detect_anomalies(events)
        latencies_ms.append((time.perf_counter() - call_start) * 1000)
    total_seconds = time.perf_counter() - start

    report = _format_report(
        iterations=ITERATIONS,
        event_count=event_count,
        total_seconds=total_seconds,
        latencies_ms=latencies_ms,
        summary=summary,
    )

    OUTPUT.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
