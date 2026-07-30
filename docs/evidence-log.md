# Evidence Log

Per `SCORING.md` and `brief.md` submission packet item #3. Maps substantive claim clusters to evidence tiers and reproduction steps. Number source labels per `SCORING.md`: `[Observed]`, `[Estimated]`, `[Benchmarked]`, `[Assumed]`.

```sh
pytest -q && python3 scripts/benchmark.py
```

## Substantive claims

| # | Claim cluster | Tier | Source label | How to verify |
|---|---------------|------|--------------|---------------|
| 1 | Fixture checksum `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235`; `[Observed]` 24 parseable records, `[Observed]` 9 anomaly classes + `evt-0017` compliance signal cataloged | 3 | `[Observed]` | `shasum -a 256 fixtures/event_sample.jsonl`; `docs/fixture-forensics.md` |
| 2 | `detect_anomalies()` detects all `[Observed]` 9 fixture anomaly classes; loader survives `evt-0020` without crash | 3 | `[Observed]` | `pytest tests/test_anomalies.py -q`; `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl` |
| 3 | Census on checksummed fixture: `[Observed]` 24 total keys, `[Observed]` 11 clean, `[Observed]` 12 flagged, `[Observed]` 1 dead letter — matches forensics catalog | 3 | `[Observed]` | `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl` (summary block); `docs/fixture-forensics.md` |
| 4 | `detect_anomalies()` local benchmark: `[Observed]` 222924.03 events/sec throughput, `[Observed]` 0.107545ms mean / `[Observed]` 0.105916ms median per call over `[Observed]` 10000 iterations × `[Observed]` 24 events/call | 3 | `[Observed]` | `python3 scripts/benchmark.py` → `docs/benchmark-results.md` |
| 5 | `detect_anomalies()` subroutine throughput (`[Observed]` ~223K events/sec rounded) exceeds peak ingest (`[Estimated]` ~5,780 events/sec at 10× spike) by `[Estimated]` ~39× — subroutine only, not end-to-end hot path | 2 | `[Observed]` / `[Estimated]` | Benchmark in row 4 vs sizing in row 8; design doc §2 throughput |
| 6 | Six fixture refusals (timezone bug `evt-0006`, legacy shape `evt-0009`, compliance `evt-0017`, retry `evt-0002`, null tenant `evt-0011`, corrupt JSON `evt-0020`) — strategic judgment over naive classification | 2 | `[Observed]` | `docs/fixture-forensics.md` § "Items that should NOT be taken at face value"; design doc §1 refusals table |
| 7 | Kinesis tiering over MSK/Kafka and per-tenant streams — ops/reliability trade-off for `[Assumed]` 2-engineer team at `[Assumed]` 500+ tenants | 2 | `[Assumed]` / `[Estimated]` | Design doc §1 rejected-alternatives paragraphs; `docs/design-pipeline.md` |
| 8 | Throughput sizing: `[Estimated]` 50M events/day → `[Estimated]` ~578 events/sec avg; `[Estimated]` ×10 spike → `[Estimated]` ~5,780 events/sec peak | 2 | `[Estimated]` | `50_000_000 ÷ 86_400 ≈ 578`; `578 × 10 = 5,780` in design doc §2 |
| 9 | `[Estimated]` 30 Kinesis shards × `[Benchmarked]` 1,000 rec/s/shard = `[Estimated]` 30,000 rec/s capacity vs `[Estimated]` 5,780 peak → `[Estimated]` ~5.2× headroom | 2 | `[Benchmarked]` / `[Estimated]` | Design doc §2 throughput sizing; AWS Kinesis shard limit docs |
| 10 | End-to-end p99 latency budget `[Estimated]` ~1.8s (target `<` `[Assumed]` 5s brief SLA) — component sum, no production trace | 2 | `[Estimated]` | Design doc §2 latency budget table |
| 11 | Monthly infra `[Estimated]` ~$42,000 (ceiling `[Assumed]` $50K/mo) with per-line arithmetic | 2 | `[Estimated]` | Design doc §2 cost table; line items sum to `[Estimated]` ~$42,000 |
| 12 | Current system `[Assumed]` ~3% event loss at peak, `[Assumed]` 15–30 min dashboard latency — brief-stated, no production access | 0 | `[Assumed]` | `brief.md` current-system section; no Tier 4 before/after measurement |
| 13 | Zero-data-loss design: at-least-once Kinesis (`[Assumed]` 24h+ retention), idempotent dedupe by `event_id`, SQS DLQ for poison records, ordered degradation | 2 | `[Assumed]` / `[Estimated]` | Design doc §2 "Zero-data-loss mechanism"; `evt-0020` DLQ path in §1 |
| 14 | Parallel-run migration with testable parity: ingest delta `≤` `[Assumed]` 0.1%, symmetric `event_id` diff = ∅, rollup checksum match | 2 | `[Assumed]` | Design doc §2 "Migration & cutover" validation bullets |
| 15 | Promote tenant when `≥` `[Assumed]` 99.9% parity for `[Assumed]` 72 consecutive hours; rollback if parity `<` `[Assumed]` 99.9% or p99 `>` `[Assumed]` 5s for `[Assumed]` 15 min or DLQ `>` `[Assumed]` 0.1% | 2 | `[Assumed]` | Design doc §2 promote/rollback triggers |
| 16 | Failure degradation order: personalization freshness → dashboard staleness (up to `[Assumed]` 30s) → per-tenant rate limits → DLQ (never silent discard) | 2 | `[Assumed]` | Design doc §2 zero-data-loss §5–6; `docs/submission-disclosures.md` "What breaks it" |
| 17 | Compliance-as-architecture: GDPR erasure via Step Functions for `evt-0017`-class requests; per-tenant KMS CMKs; human approval gate | 2 | `[Assumed]` | Design doc §1 Step Functions row; §2 compliance table; disclosures "What stays human" |
| 18 | Multi-tenant isolation: stream tiering by ingest profile, `tenant_id` partition keys, IAM boundaries — not per-tenant infra | 2 | `[Estimated]` | Design doc §2 "Multi-tenant isolation" |
| 19 | Bot burst handling (`evt-0012`–`evt-0015`, `[Observed]` ~50ms window) diverts to cold S3, protecting hot rollups | 3 | `[Observed]` | `docs/fixture-forensics.md`; design doc §1 class 8 row |
| 20 | Clock skew (`evt-0005`, `[Observed]` ~47s) and PII redaction (`evt-0007`) handled per forensics, not dropped | 3 | `[Observed]` | `pytest tests/test_anomalies.py`; `docs/fixture-forensics.md` per-event review |
| 21 | Scope discipline: `[Assumed]` 2 senior engineers; MVP months 1–3, full build months 4–6; explicit exclusions (EU residency, ML bot detection) | 2 | `[Assumed]` | Design doc §2 phased delivery table; §3 "With more time/budget" |
| 22 | Sustained spike `>` `[Estimated]` 30K events/sec exhausts `[Estimated]` 30-shard Kinesis budget despite buffering | 2 | `[Estimated]` | `docs/submission-disclosures.md` "What breaks it"; design doc §2 throughput |
| 23 | Queue-based idempotent-consumer pattern (prior RabbitMQ-adjacent experience) informs Kinesis consumer design | 2 | `[Assumed]` | Author background in design doc §1 ingestion paragraph; not re-benchmarked here |
| 24 | Latency/cost consistency: design doc rounds throughput to `[Observed]` ~223K events/sec for readability; exact benchmark is `[Observed]` 222924.03 events/sec (row 4). Cost total `[Estimated]` ~$42,000 and p99 `[Estimated]` ~1.8s match design doc §2 exactly | 2 | `[Observed]` / `[Estimated]` | Cross-check `docs/design-pipeline.md` §2 vs rows 4, 10, 11 |

## Operating artifacts (Tier 2+)

| Artifact | Tier | Path |
|----------|------|------|
| Fixture forensics catalog | 3 | `docs/fixture-forensics.md` |
| Anomaly detection + tests | 2 | `src/analytics_pipeline/`, `tests/` |
| Benchmark output | 3 | `docs/benchmark-results.md` (regenerate: `python3 scripts/benchmark.py`) |
| Design document (written answer) | 2 | `docs/design-pipeline.md` |
| Submission disclosures | 2 | `docs/submission-disclosures.md` |

## Artifact access

Reproduce the operating artifacts locally from the repo root:

| Artifact | Command / path |
|----------|----------------|
| Fixture checksum | `shasum -a 256 fixtures/event_sample.jsonl` |
| Full test suite | `pytest -q` |
| Anomaly tests only | `pytest tests/test_anomalies.py -q` |
| CLI census + anomaly report | `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl` |
| Benchmark (regenerates `docs/benchmark-results.md`) | `python3 scripts/benchmark.py` |
| Design doc (written answer) | `docs/design-pipeline.md` |
| Number source labels | Inline `[Observed]` / `[Estimated]` / `[Benchmarked]` / `[Assumed]` tags in `docs/design-pipeline.md`, `docs/benchmark-results.md`, this file, and `docs/submission-disclosures.md` |
| AI usage disclosure | `docs/submission-disclosures.md` § "AI usage disclosure" |
| What breaks it / failure handling | `docs/submission-disclosures.md` § "What breaks it" |
| What stays human | `docs/submission-disclosures.md` § "What stays human" |

## Number source summary

All quantitative claims in `docs/design-pipeline.md`, `docs/benchmark-results.md`, this evidence log, and substantive figures in `docs/submission-disclosures.md` carry inline `[Observed]`, `[Estimated]`, `[Benchmarked]`, or `[Assumed]` tags. `[Observed]` applies to locally measured benchmark timings and fixture-derived census counts (see `python3 scripts/benchmark.py`). `[Benchmarked]` applies only to named external sources (e.g., AWS Kinesis `[Benchmarked]` 1,000 rec/s/shard limit, public on-demand pricing). `[Estimated]` covers sizing arithmetic and AWS cost lines. `[Assumed]` covers brief-stated current-state figures and untested operational thresholds.
