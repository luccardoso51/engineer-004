"""JSONL fixture loading with dead-letter support for malformed records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

_EVENT_ID_PATTERN = re.compile(r'"event_id"\s*:\s*"([^"]+)"')


@dataclass(frozen=True)
class DeadLetter:
    """A line that failed JSON parsing."""

    line_number: int
    raw_text: str
    event_id: str
    error: str


@dataclass(frozen=True)
class LoadResult:
    """Outcome of loading a JSONL fixture file."""

    events: list[dict]
    dead_letters: list[DeadLetter]


def _extract_event_id(raw_text: str, line_number: int) -> str:
    match = _EVENT_ID_PATTERN.search(raw_text)
    if match:
        return match.group(1)
    return f"line:{line_number}"


def load_jsonl(path: Path) -> LoadResult:
    """Read a newline-delimited JSON file, dead-lettering malformed lines."""
    events: list[dict] = []
    dead_letters: list[DeadLetter] = []

    with path.open("r", encoding="utf-8") as fh:
        for line_number, line in enumerate(fh, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                events.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                dead_letters.append(
                    DeadLetter(
                        line_number=line_number,
                        raw_text=stripped,
                        event_id=_extract_event_id(stripped, line_number),
                        error=str(exc),
                    )
                )

    return LoadResult(events=events, dead_letters=dead_letters)
