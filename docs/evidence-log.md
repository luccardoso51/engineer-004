# Evidence Log

Per `SCORING.md` and `brief.md` submission packet item #3. Maps headline claims to evidence tiers and reproduction steps. Number source labels per `SCORING.md`: `[Observed]`, `[Estimated]`, `[Benchmarked]`, `[Assumed]`.

## Headline claims

| Claim | Tier | Source label | How to verify |
|-------|------|--------------|---------------|
| Fixture contains 9 anomaly classes + `evt-0017` compliance signal | 3 | `[Observed]` | `docs/fixture-forensics.md`; `shasum -a 256 fixtures/event_sample.jsonl` → `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235` |
| Anomaly detection handles all fixture classes without loader crash | 3 | `[Observed]` | `pytest tests/test_anomalies.py -q`; `python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl` |
| Hot-path normalize/dedupe throughput >> ingest rate | 3 | `[Benchmarked]` | `python3 scripts/benchmark.py` → `docs/benchmark-results.md` (~212K events/sec mean) |
| End-to-end p99 latency ~1.8s (target <5s) | 2 | `[Estimated]` | Component budget table in `docs/design-pipeline.md` §2; no production trace yet |
| Monthly infra ~$42K (ceiling $50K) | 2 | `[Estimated]` | Cost table with per-line arithmetic in `docs/design-pipeline.md` §2 |
| 50M events/day → ~578 events/sec avg; ~5,780/sec at 10x spike | 2 | `[Estimated]` | `50_000_000 ÷ 86_400 ≈ 578`; `578 × 10 = 5,780` in design doc §2 |
| 30 Kinesis shards absorb 10x spike with ~5.2x headroom | 2 | `[Estimated]` | `30 shards × 1,000 rec/s/shard = 30,000 rec/s` vs 5,780 peak in design doc §2 |
| Current system ~3% loss at peak, 15–30 min latency | 0 | `[Assumed]` | Brief-stated current-state; no access to production |
| Queue-based idempotent-consumer pattern reduces loss | 2 | `[Observed]` | Author prior queue-based backend experience; method in design doc §1 ingestion paragraph |
| Migration parity gate ≥99.9% for 72h before tenant promote | 2 | `[Assumed]` | Testable definition in design doc §2; not yet executed |
| GDPR erasure for `evt-0017` requires human approval | 2 | `[Assumed]` | Workflow design in design doc §1; no live erasure run |

## Operating artifacts (Tier 2+)

| Artifact | Tier | Path |
|----------|------|------|
| Fixture forensics catalog | 3 | `docs/fixture-forensics.md` |
| Anomaly detection + tests | 2 | `src/analytics_pipeline/`, `tests/` |
| Benchmark output | 3 | `docs/benchmark-results.md` (regenerate: `python3 scripts/benchmark.py`) |
| Design document | 2 | `docs/design-pipeline.md` |

## Number source summary

All quantitative claims in `docs/design-pipeline.md` use inline `[Observed]`, `[Estimated]`, `[Benchmarked]`, or `[Assumed]` tags. Fixture-derived quantities (`evt-0005` ~47s skew, `evt-0012`–`evt-0015` ~50ms burst) are `[Observed]` per `docs/fixture-forensics.md`. AWS pricing inputs are `[Estimated]` from public on-demand list prices at design time.
