"""Compliance helpers for privacy and erasure workflows."""

from __future__ import annotations


def find_deletion_cascade(events: list[dict], privacy_event: dict) -> list[str]:
    """Return event_ids in the same tenant that share the deletion subject's ids.

  A GDPR delete_all_data request names user_id and anonymous_id on the request
  event itself, but erasure must reach every stored event keyed to either id —
  including events that arrived before identify linked them.
    """
    tenant_id = privacy_event.get("tenant_id")
    user_id = privacy_event.get("user_id")
    anonymous_id = privacy_event.get("anonymous_id")
    matched: set[str] = set()

    for event in events:
        if event.get("tenant_id") != tenant_id:
            continue
        event_id = event.get("event_id")
        if event_id is None:
            continue
        if user_id and event.get("user_id") == user_id:
            matched.add(str(event_id))
        elif anonymous_id and event.get("anonymous_id") == anonymous_id:
            matched.add(str(event_id))

    return sorted(matched)
