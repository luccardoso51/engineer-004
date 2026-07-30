# ADR 0001: Timestamp anomaly classification by signal, not event_id

## Status

Accepted

## Context

The fixture plants three distinct timestamp-related issues (`evt-0005` clock skew,
`evt-0006` systematic timezone offset, `evt-0016` future/impossible timestamp).
Ticket 2 requires feature-based heuristics rather than hard-coding known
`event_id`s so the detector can generalize beyond this file.

## Decision

Classify timestamp anomalies using measurable signals:

1. **Future / impossible** — `ts` is more than 24 hours ahead of `received_at`, or
   `ts.year` exceeds `received_at.year`.
2. **Systematic timezone offset** — `ts` is more than 30 minutes ahead of
   `received_at` *and* the sub-second (microsecond) fraction matches on both
   timestamps (the `.552` fingerprint on `evt-0006`).
3. **Clock skew** — `received_at` is earlier than `ts` by at least 5 seconds,
   and the case does not match the timezone-offset rule above.

`received_at` is treated as authoritative for ordering when timezone offset is
detected (`action=flag_for_correction`).

## Consequences

- Thresholds are fixture-tuned heuristics, not statistically calibrated for
  production traffic.
- Borderline cases between skew and offset rely on the millisecond-fraction
  fingerprint; random drift without that signal stays in the clock-skew bucket.
- No `event_id` literals appear in timestamp classification code.
