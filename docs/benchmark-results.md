# Benchmark results

Evidence tier: Tier 3 (source record) per SCORING.md — timings are
reproducible with `python3 scripts/benchmark.py`; census counts are
derived from the checksummed fixture via the CLI census.

## Provenance

- Fixture: `fixtures/event_sample.jsonl`
- SHA-256: `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235` `[Observed]`
  - Reproduce with: `shasum -a 256 fixtures/event_sample.jsonl`

## Performance ([Observed])

Regenerate: `python3 scripts/benchmark.py`

- Iterations: 10000 `[Observed]`
- Events per call: 24 `[Observed]`
- Total wall time: 1.076600s `[Observed]`
- Mean latency per call: 0.107545ms `[Observed]`
- Median latency per call: 0.105916ms `[Observed]`
- Throughput: 222924.03 events/sec `[Observed]`

## Pass/fail counts ([Observed] from census summary)

From: `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl`

- Total census keys: 24 `[Observed]`
- Clean: 11 `[Observed]`
- Flagged: 12 `[Observed]`
- Dead letter: 1 `[Observed]`

## Anomaly class counts ([Observed])

From: `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl`

- bot_burst: 4 `[Observed]`
- clock_skew: 1 `[Observed]`
- compliance_critical: 1 `[Observed]`
- duplicate_event_id: 1 `[Observed]`
- future_timestamp: 1 `[Observed]`
- malformed_json_record: 1 `[Observed]`
- missing_required_field: 1 `[Observed]`
- schema_drift: 1 `[Observed]`
- timezone_offset: 1 `[Observed]`
- unexpected_pii: 1 `[Observed]`

## Action counts ([Observed])

From: `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl`

- dead_letter: 1 `[Observed]`
- dedupe: 1 `[Observed]`
- flag_for_correction: 3 `[Observed]`
- normalize: 1 `[Observed]`
- quarantine: 6 `[Observed]`
- route_compliance: 1 `[Observed]`
