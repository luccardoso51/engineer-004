#!/usr/bin/env python3
"""Benchmark detect_anomalies throughput and latency against the real fixture."""

from __future__ import annotations

import hashlib
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
FIXTURE_SHA256 = "1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235"


def _fixture_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _format_report(
    *,
    fixture_sha256: str,
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
        "Evidence tier: Tier 3 (source record) per SCORING.md — timings are",
        "reproducible with `python3 scripts/benchmark.py`; census counts are",
        "derived from the checksummed fixture via the CLI census.",
        "",
        "## Provenance",
        "",
        f"- Fixture: `{FIXTURE.relative_to(ROOT)}`",
        f"- SHA-256: `{fixture_sha256}`",
        "  - Reproduce with: `shasum -a 256 fixtures/event_sample.jsonl`",
        "",
        "## Performance ([Benchmarked])",
        "",
        f"- Iterations: {iterations}",
        f"- Events per call: {event_count}",
        f"- Total wall time: {total_seconds:.6f}s",
        f"- Mean latency per call: {mean_ms:.6f}ms",
        f"- Median latency per call: {median_ms:.6f}ms",
        f"- Throughput: {throughput:.2f} events/sec",
        "",
        "## Pass/fail counts ([Observed] from census summary)",
        "",
        f"- Total census keys: {summary['total_keys']}",
        f"- Clean: {summary['clean']}",
        f"- Flagged: {summary['flagged']}",
        f"- Dead letter: {summary['dead_letter']}",
        "",
        "## Anomaly class counts ([Observed])",
        "",
    ]
    for anomaly_class, count in summary["anomaly_class_counts"].items():
        lines.append(f"- {anomaly_class}: {count}")
    lines.extend(["", "## Action counts ([Observed])", ""])
    for action, count in summary["action_counts"].items():
        lines.append(f"- {action}: {count}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    fixture_sha256 = _fixture_sha256(FIXTURE)
    if fixture_sha256 != FIXTURE_SHA256:
        raise SystemExit(
            f"fixture checksum mismatch: expected {FIXTURE_SHA256}, got {fixture_sha256}"
        )

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
        fixture_sha256=fixture_sha256,
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
