# Benchmark results

- Fixture: `fixtures/event_sample.jsonl`
- Iterations: 10000
- Events per call: 24
- Total wall time: 1.037826s
- Mean latency per call: 0.103686ms
- Median latency per call: 0.102458ms
- Throughput: 231252.69 events/sec

## Pass/fail counts (from census summary)

- Total census keys: 24
- Clean: 11
- Flagged: 12
- Dead letter: 1

## Anomaly class counts

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

## Action counts

- dead_letter: 1
- dedupe: 1
- flag_for_correction: 3
- normalize: 1
- quarantine: 6
- route_compliance: 1
