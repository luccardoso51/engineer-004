# Benchmark results

Evidence tier: Tier 3 (source record) per SCORING.md — timings are
reproducible with `python3 scripts/benchmark.py`; census counts are
derived from the checksummed fixture via the CLI census.

## Provenance

- Fixture: `fixtures/event_sample.jsonl`
- SHA-256: `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235`
  - Reproduce with: `shasum -a 256 fixtures/event_sample.jsonl`

## Performance ([Benchmarked])

- Iterations: 10000
- Events per call: 24
- Total wall time: 1.133173s
- Mean latency per call: 0.113216ms
- Median latency per call: 0.111458ms
- Throughput: 211794.72 events/sec

## Pass/fail counts ([Observed] from census summary)

- Total census keys: 24
- Clean: 11
- Flagged: 12
- Dead letter: 1

## Anomaly class counts ([Observed])

- bot_burst: 4
- clock_skew: 1
- compliance_critical: 1
- duplicate_event_id: 1
- future_timestamp: 1
- malformed_json_record: 1
- missing_required_field: 1
- schema_drift: 1
- timezone_offset: 1
- unexpected_pii: 1

## Action counts ([Observed])

- dead_letter: 1
- dedupe: 1
- flag_for_correction: 3
- normalize: 1
- quarantine: 6
- route_compliance: 1
