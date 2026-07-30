"""Entry point stub for the analytics pipeline challenge artifact.

This module is a scaffolding placeholder. The actual fixture-anomaly
detection logic (duplicate event_id, clock skew between ts/received_at,
PII in event properties, etc.) belongs here once the analysis is built.
"""

from __future__ import annotations

import argparse
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    """Read a newline-delimited JSON file into a list of dicts."""
    import json

    with path.open("r", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Analytics pipeline fixture analyzer")
    parser.add_argument(
        "--fixture",
        type=Path,
        default=Path("fixtures/event_sample.jsonl"),
        help="Path to the JSONL event fixture",
    )
    args = parser.parse_args()

    events = load_jsonl(args.fixture)
    print(f"Loaded {len(events)} events from {args.fixture}")


if __name__ == "__main__":
    main()
