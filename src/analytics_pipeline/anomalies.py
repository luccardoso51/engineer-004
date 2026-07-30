"""Anomaly detection for analytics pipeline events."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

# Heuristic thresholds tuned for the fixture; see docs/adr/0001-*.md
_CLOCK_SKEW_MIN_SECONDS = 5.0
_TIMEZONE_OFFSET_MIN_SECONDS = 30 * 60
_FUTURE_MIN_SECONDS = 24 * 60 * 60
_BOT_BURST_WINDOW_MS = 200
_BOT_BURST_MIN_EVENTS = 3

_PII_EMAIL_KEYS = frozenset({"contact_email", "email"})
_PII_PHONE_KEYS = frozenset({"phone", "phone_number"})
_EMAIL_VALUE_PATTERN = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_PHONE_VALUE_PATTERN = re.compile(r"\+?\d[\d\-\(\)\s]{6,}\d")
_SCANNER_REFERRER_MARKERS = ("scanner", "bot", "crawler", "spider")

_CURRENT_SCHEMA_TYPES = frozenset(
    {"page_view", "click", "identify", "form_submit", "custom", "privacy_request"}
)


@dataclass(frozen=True)
class Anomaly:
    """A detected issue or compliance signal on an event."""

    event_id: str
    anomaly_class: str
    detail: str
    action: str


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _event_timestamp(event: dict) -> datetime | None:
    raw = event.get("ts") or event.get("timestamp")
    if raw is None:
        return None
    return _parse_timestamp(str(raw))


def _received_timestamp(event: dict) -> datetime | None:
    raw = event.get("received_at")
    if raw is None:
        return None
    return _parse_timestamp(str(raw))


def _subsecond_fraction(dt: datetime) -> str:
    return f"{dt.microsecond:06d}"


def _classify_timestamp_anomaly(event: dict) -> Anomaly | None:
    event_id = str(event["event_id"])
    ts = _event_timestamp(event)
    received_at = _received_timestamp(event)
    if ts is None or received_at is None:
        return None

    delta_seconds = (ts - received_at).total_seconds()
    abs_delta = abs(delta_seconds)

    if delta_seconds > _FUTURE_MIN_SECONDS or ts.year > received_at.year:
        return Anomaly(
            event_id=event_id,
            anomaly_class="future_timestamp",
            detail=f"ts is {abs_delta:.0f}s ahead of received_at (impossible future date)",
            action="flag_for_correction",
        )

    if (
        delta_seconds > _TIMEZONE_OFFSET_MIN_SECONDS
        and _subsecond_fraction(ts) == _subsecond_fraction(received_at)
    ):
        return Anomaly(
            event_id=event_id,
            anomaly_class="timezone_offset",
            detail=(
                f"ts is {delta_seconds / 60:.0f}min ahead of received_at with matching "
                "sub-second fraction (systematic timezone bug)"
            ),
            action="flag_for_correction",
        )

    if received_at < ts and abs_delta >= _CLOCK_SKEW_MIN_SECONDS:
        return Anomaly(
            event_id=event_id,
            anomaly_class="clock_skew",
            detail=f"received_at is {abs_delta:.0f}s earlier than ts (client clock skew)",
            action="flag_for_correction",
        )

    return None


def _detect_duplicate(event_id: str, seen: set[str]) -> Anomaly | None:
    if event_id in seen:
        return Anomaly(
            event_id=event_id,
            anomaly_class="duplicate_event_id",
            detail="duplicate event_id detected (idempotency violation; key dedupe on event_id)",
            action="dedupe",
        )
    seen.add(event_id)
    return None


def _detect_missing_tenant(event: dict) -> Anomaly | None:
    if event.get("tenant_id") is not None:
        return None
    return Anomaly(
        event_id=str(event["event_id"]),
        anomaly_class="missing_required_field",
        detail="tenant_id is null; event is unattributable",
        action="quarantine",
    )


def _iter_property_values(value: object):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key, nested
            yield from _iter_property_values(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_property_values(item)


def _detect_pii(event: dict) -> Anomaly | None:
    properties = event.get("properties")
    if not isinstance(properties, dict):
        return None

    found: list[str] = []
    for key, value in _iter_property_values(properties):
        key_lower = str(key).lower()
        if key_lower in _PII_EMAIL_KEYS or (
            isinstance(value, str) and _EMAIL_VALUE_PATTERN.search(value)
        ):
            found.append(f"email in {key!r}")
        if key_lower in _PII_PHONE_KEYS or (
            isinstance(value, str) and _PHONE_VALUE_PATTERN.search(value)
        ):
            found.append(f"phone in {key!r}")

    if not found:
        return None

    unique = sorted(set(found))
    return Anomaly(
        event_id=str(event["event_id"]),
        anomaly_class="unexpected_pii",
        detail=f"unexpected PII in properties: {', '.join(unique)}",
        action="quarantine",
    )


def _detect_schema_drift(event: dict) -> Anomaly | None:
    event_type = event.get("type")
    issues: list[str] = []

    if event_type is not None and event_type not in _CURRENT_SCHEMA_TYPES:
        issues.append(f"type {event_type!r} is non-conforming")

    if "timestamp" in event and "ts" not in event:
        issues.append("uses legacy timestamp field instead of ts")

    if "received_at" not in event:
        issues.append("missing received_at")

    legacy_fields = [field for field in ("page_path", "ref") if field in event.get("properties", {})]
    if legacy_fields:
        issues.append(f"legacy property fields: {', '.join(legacy_fields)}")

    if not issues:
        return None

    return Anomaly(
        event_id=str(event["event_id"]),
        anomaly_class="schema_drift",
        detail="; ".join(issues),
        action="normalize",
    )


def _detect_compliance(event: dict) -> Anomaly | None:
    if event.get("type") != "privacy_request":
        return None
    return Anomaly(
        event_id=str(event["event_id"]),
        anomaly_class="compliance_critical",
        detail="privacy_request requires compliance workflow routing",
        action="route_compliance",
    )


def _is_scanner_referrer(referrer: object) -> bool:
    if not isinstance(referrer, str):
        return False
    lowered = referrer.lower()
    return any(marker in lowered for marker in _SCANNER_REFERRER_MARKERS)


def _detect_bot_bursts(events: list[dict]) -> list[Anomaly]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        anonymous_id = event.get("anonymous_id")
        if anonymous_id is None:
            continue
        groups[str(anonymous_id)].append(event)

    anomalies: list[Anomaly] = []
    for anonymous_id, group in groups.items():
        page_views = []
        for event in group:
            if event.get("type") != "page_view":
                continue
            properties = event.get("properties")
            referrer = properties.get("referrer") if isinstance(properties, dict) else None
            if _is_scanner_referrer(referrer):
                page_views.append(event)
        if len(page_views) < _BOT_BURST_MIN_EVENTS:
            continue

        timestamps = [_event_timestamp(event) for event in page_views]
        if any(ts is None for ts in timestamps):
            continue

        span_ms = (max(timestamps) - min(timestamps)).total_seconds() * 1000
        if span_ms > _BOT_BURST_WINDOW_MS:
            continue

        for event in page_views:
            anomalies.append(
                Anomaly(
                    event_id=str(event["event_id"]),
                    anomaly_class="bot_burst",
                    detail=(
                        f"scanner volume burst from {anonymous_id} "
                        f"({len(page_views)} page_views in {span_ms:.0f}ms)"
                    ),
                    action="quarantine",
                )
            )

    return anomalies


def detect_anomalies(events: list[dict]) -> list[Anomaly]:
    """Detect data-quality anomalies and compliance signals across events."""
    anomalies: list[Anomaly] = []
    seen_event_ids: set[str] = set()

    for event in events:
        event_id = str(event["event_id"])

        duplicate = _detect_duplicate(event_id, seen_event_ids)
        if duplicate is not None:
            anomalies.append(duplicate)

        for detector in (
            _detect_compliance,
            _detect_missing_tenant,
            _detect_schema_drift,
            _detect_pii,
            _classify_timestamp_anomaly,
        ):
            finding = detector(event)
            if finding is not None:
                anomalies.append(finding)

    anomalies.extend(_detect_bot_bursts(events))
    return anomalies
