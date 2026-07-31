# Real-Time Analytics Pipeline — Design Document (Written answer)

**Brief version:** 2026-07  
**Fixture checksum (SHA-256):** `[Observed]` `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235` — reproduce: `shasum -a 256 fixtures/event_sample.jsonl`  
**Author context:** Queue-based backend experience (RabbitMQ-adjacent patterns: backpressure, at-least-once delivery, idempotent handlers). PostHog referenced only as an SDK consumer, not as infrastructure we operate.  
**Operating artifacts (excluded from page count):** [`docs/design-appendix.md`](design-appendix.md), `docs/fixture-forensics.md`, `src/analytics_pipeline/` + `tests/`, `docs/benchmark-results.md`, `docs/evidence-log.md`, `docs/submission-disclosures.md`, `docs/failure-modes.md`.

Assumptions and supporting-service tables live in [`docs/design-appendix.md`](design-appendix.md).

---

## 1. Architecture & Technology Choices

### High-level data flow

```mermaid
flowchart LR
  SDK[JS SDK] --> GW[API Gateway]
  GW -->|tee 100%| OLD[Legacy Redis queue]
  GW -->|new path| RT[Request Validator]
  RT --> KIN[Kinesis tiered streams]
  KIN --> LAM[Lambda hot-path]
  LAM --> DDB[(DynamoDB rollups)]
  LAM --> EC[(ElastiCache counters)]
  KIN --> FGT[Fargate cold-path]
  FGT --> S3[(S3 Parquet)]
  S3 --> WH[Snowflake / BigQuery]
  DDB --> DASH[Dashboard API]
  EC --> PERS[Personalization triggers]
  LAM --> DLQ[SQS DLQ]
  DLQ --> RPL[Fargate replay jobs]
  GW -->|privacy_request| COMP[Step Functions erasure]
```

**Ingestion:** API Gateway (HTTP API) with Lambda authorizer validating API keys → `tenant_id` mapping. Gateway tees `[Assumed]` 100% of traffic to the legacy Redis queue during migration (no SDK change). New path validates JSON shape, stamps `received_at`, routes to one of three Kinesis Data Streams by tenant tier (partition key: `tenant_id`). This mirrors a RabbitMQ topology: Gateway is the exchange, Kinesis shards are durable queues with backpressure, and consumers ack only after idempotent side-effects — the pattern that eliminated message loss in prior queue-based systems.

- **Chosen:** API Gateway + Kinesis Data Streams (tiered). Partitioning by `tenant_id` preserves per-tenant ordering and isolates noisy neighbors across tiers.
- **Rejected:** MSK/Kafka — higher ops overhead for `[Assumed]` 2 engineers. Per-tenant Kinesis streams — `[Assumed]` 500+ stream management cost. Single shared stream — enterprise tenant spikes starve others. ALB + direct Lambda — no durable buffer, reintroduces loss on spike.

**Hot-path processing:** Lambda (Python, provisioned concurrency on high-volume tiers) normalizes schema, dedupes, fans out to hot stores.

- **Chosen:** Lambda for normalize/dedupe/fan-out — scales to zero off-peak, sub-second cold-start mitigated by provisioned concurrency on burst-prone tiers.
- **Rejected:** ECS-only hot path — slower scale-out under spike; always-on cost. Kinesis Data Analytics — overkill for MVP normalization logic.

**Hot storage:** ElastiCache (Redis) for live counters and personalization trigger state (TTL keys per `anonymous_id`/`user_id`). DynamoDB for dashboard rollups (tenant-scoped partition keys) and segment definitions.

- **Chosen:** ElastiCache + DynamoDB — ElastiCache for sub-10ms `[Estimated]` counter increments; DynamoDB for queryable aggregates, segment definitions, and behavioral rules (e.g., "viewed pricing 3×").
- **Rejected:** PostgreSQL hot path — current system's bottleneck. OpenSearch for rollups — higher cost and ops for simple key-value aggregates.

**Cold-path processing:** Fargate tasks consume Kinesis via Enhanced Fan-Out, write Parquet to S3, stage warehouse loads.

- **Chosen:** Fargate — long-running batch-friendly writers without Lambda `[Benchmarked]` 15-min ceiling.
- **Rejected:** Glue streaming — slower iteration for 2-engineer team; Fargate gives direct control.

**Query layer:** API Gateway → Lambda reading DynamoDB/ElastiCache.

- **Chosen:** API Gateway + Lambda — matches existing HTTP API patterns; team familiarity.
- **Rejected:** AppSync — GraphQL adds client contract change risk. CloudFront-cached S3 — stale for real-time dashboards.

Warehouse export (months 4–6): S3 → Snowflake/BigQuery native connectors. **Rejected:** Kinesis Data Firehose direct-to-warehouse — less control over Parquet schema evolution.

### Event data structure & identity stitching

Canonical fields: `event_id`, `tenant_id`, `type`, `ts`, `received_at`, `anonymous_id`, `user_id`, `properties`, `anomaly_flags[]`. `identify` events (`evt-0003`, `evt-0008`, `evt-0022`) write `(tenant_id, anonymous_id) → user_id` to DynamoDB; subsequent events stitch on `user_id` when present, else `anonymous_id`. All lookups tenant-scoped.

**Retroactive backfill (fixture-forced).** Three anonymous sessions arrive *before* their `identify` event links them to a `user_id`: `evt-0001`/`evt-0002` precede `evt-0003` (`anon-9f2 → u-5511`); `evt-0004` precedes `evt-0008` (`anon-c81 → u-2209`); `evt-0007` precedes `evt-0022` (`anon-3d0 → u-7304`). **Chosen:** stitch at query time — rollups keyed by `anonymous_id` until identify, then segment membership queries union both keys. **Rejected:** hot-path rollup rewrite on identify — write amplification on every identify (especially enterprise tenants with long anonymous sessions) for marginal dashboard freshness gain. Trade-off: query cost and segment-definition complexity vs. avoiding burst writes on identify storms.

Behavioral rules example: segment "viewed pricing `[Observed]` 3×" — `evt-0019` carries `properties.count_today: 3` on a `viewed_pricing` custom event (the brief's own segmentation example).

### Fixture anomaly handling (nine classes + compliance workflow)

Ground truth: `docs/fixture-forensics.md`. Validated by `detect_anomalies()` (`python3 -m unittest discover -s tests`; local benchmark `[Observed]` ~223K events/sec subroutine throughput in `docs/benchmark-results.md` — measures in-process detection only, not end-to-end pipeline latency).

**Not at face value (six refusals):** (1) `evt-0006` — `[Observed]` 65-min `ts` offset with matching `.552` ms suffix is a timezone bug, not a future event; order by `received_at`. (2) `evt-0009` — legacy SDK shape; normalize, never drop (brief forbids SDK upgrade). (3) `evt-0017` — GDPR `delete_all_data` mandate, not analytics volume; route to compliance workflow. (4) `evt-0002` — retry signature (`received_at` `[Observed]` +7.4s); dedupe on `event_id` only. (5) `evt-0011` — null `tenant_id` is unattributable; quarantine, never default. (6) `evt-0020` — corrupt JSON; DLQ and continue, never crash loader.

| Class | Event(s) | Pipeline behavior |
|-------|----------|-------------------|
| 1. Duplicate `event_id` | `evt-0002` | DynamoDB conditional put on `event_id` (~7-day TTL `[Assumed]`). Second delivery exits before hot writes. |
| 2. Clock skew | `evt-0005` | Flag `clock_skew`; prefer `received_at` when `ts` suspect (~47s skew `[Observed]`). |
| 3. Timezone offset | `evt-0006` | Flag `timezone_offset`; order by `received_at` (see refusals above). |
| 4. Future timestamp | `evt-0016` | Flag `future_ts`; exclude from time-windowed rollups; retain in cold S3. |
| 5. Missing `tenant_id` | `evt-0011` | Quarantine to encrypted S3 prefix (see refusals above). |
| 6. Unexpected PII | `evt-0007` | Redact `contact_email`/`phone` before hot writes; original to quarantine S3; audit log. |
| 7. Schema drift | `evt-0009` | Normalize legacy fields to canonical shape; stamp `received_at` (see refusals above). |
| 8. Bot burst | `evt-0012`–`evt-0015` | Bot score → cold S3; excluded from hot rollups (~50ms burst `[Observed]`). |
| 9. Malformed JSON | `evt-0020` | SQS DLQ with raw line; loader continues (see refusals above). |
| Compliance workflow | `evt-0017` | SQS → Step Functions erasure across all stores; audit each step; not analytics volume. Erasure must cascade to events keyed to the subject's `user_id`/`anonymous_id` even when not named on the request — fixture: `evt-0006` shares `anon-77a` with `evt-0017` (`find_deletion_cascade()` in the artifact demonstrates this on the sample file). |

---

## 2. Scale, Reliability & Migration

### Throughput sizing `[Estimated]`

Volume base (used consistently below): `[Observed from brief]` 50M events/day → `[Estimated]` 1.5B events/month; `[Estimated]` ~578 events/sec average (`50_000_000 ÷ 86_400`); `[Estimated]` ~5,780 events/sec at the stated 10× spike.

Mean serialized event size: `[Observed]` ~229 bytes from the fixture (`24` parseable records; sample is `25` lines).

Kinesis shard limits (`[Benchmarked]` AWS public pricing, us-east-1): `[Benchmarked]` 1,000 records/sec and `[Benchmarked]` 1 MB/sec per shard. At peak: record rate needs `[Estimated]` ceil(5,780 ÷ 1,000) = `6` shards; data rate needs `[Estimated]` ceil(5,780 × 229 B ÷ 1 MB) = `2` shards. **Record rate binds.** Base `[Estimated]` `8` shards across three tiers (`4+2+2`) for tier separation and headroom — well under the prior `[Estimated]` `30`-shard estimate, which sized only against record rate and ignored the data-rate limit.

### Latency budget (target: <5s end-to-end) `[Estimated]`

| Stage | Component | p99 budget | Notes |
|-------|-----------|------------|-------|
| Ingestion | SDK batch → API Gateway → Kinesis PutRecord | `[Estimated]` 200ms | SDK batches `[Assumed]` ≤20 events; Gateway regional |
| Processing | Kinesis → Lambda normalize/dedupe | `[Estimated]` 800ms | Provisioned concurrency on hot tiers; includes DynamoDB conditional put |
| Storage write | DynamoDB + ElastiCache parallel writes | `[Estimated]` 300ms | Provisioned DDB with autoscaling |
| Query | API Gateway → Lambda → DynamoDB/ElastiCache read | `[Estimated]` 500ms | Cached segment definitions |
| **Total** | | **`[Estimated]` ~1.8s p99** | Headroom for `[Estimated]` 10× spike queueing; hard SLA alert at `[Assumed]` 5s |

### Cost breakdown at 50M+ events/day `[Estimated]` / `[Assumed]`

All lines use the `[Estimated]` 1.5B events/month volume base. Pricing `[Benchmarked]` from AWS public pages (us-east-1, on-demand where applicable). `[Assumed]` SDK batches ~20 events per HTTP request (brief forbids SDK change — inherited behaviour, named as risk).

| Service | Monthly cost | Basis |
|---------|-------------|-------|
| Kinesis shard hours (`[Estimated]` 8 shards) | `[Estimated]` $88 | `[Estimated]` 8 × `[Benchmarked]` $0.015/shard-hr × `[Estimated]` 730h = $87.60 |
| Kinesis PUT payload units | `[Estimated]` $1,050 | `[Assumed]` ~20 events/PutRecord → `[Estimated]` 75M units/mo × `[Benchmarked]` $0.014/M = $1,050 |
| Kinesis enhanced fan-out (cold path) | `[Estimated]` $92 | `[Estimated]` 8 consumer-shard-hrs × `[Benchmarked]` $0.015 × 730h = $87.60; + `[Estimated]` ~$4 data retrieval |
| Lambda (hot-path) | `[Estimated]` $180 | `[Estimated]` 75M invocations/mo (`[Assumed]` batched); `[Estimated]` 256MB × `[Estimated]` 200ms → ~$64 compute + ~$15 requests + modest provisioned concurrency |
| DynamoDB provisioned (dedupe + rollups) | `[Estimated]` $1,000 | `[Estimated]` ~3B writes/mo with autoscaling; `[Benchmarked]` on-demand at same volume ≈ `[Estimated]` $3,750 — ~4× higher; provisioned chosen for cost at sustained volume |
| ElastiCache (r6g.large × 2) | `[Estimated]` $301 | `[Benchmarked]` ~$0.205/hr × 2 × `[Estimated]` 730h |
| Fargate (cold-path writers) | `[Estimated]` $288 | `[Estimated]` 4 tasks × (2 vCPU + 4GB) × `[Benchmarked]` rates × `[Estimated]` 730h |
| S3 (Parquet + quarantine) | `[Estimated]` $46 | `[Estimated]` ~2TB × `[Benchmarked]` $0.023/GB |
| API Gateway (HTTP API) | `[Estimated]` $75 | `[Assumed]` batched: `[Estimated]` 75M req/mo × `[Benchmarked]` $1.00/M. **Sensitivity:** unbatched 1.5B req/mo → `[Estimated]` ~$1,500 |
| CloudWatch Logs (sampled) | `[Estimated]` $2 | `[Assumed]` 1% sampling of ~345GB/mo ingest × `[Benchmarked]` $0.50/GB; unsampled ≈ `[Estimated]` $172 |
| NAT Gateway + data transfer | `[Estimated]` $60 | `[Benchmarked]` ~$32.85/gateway + modest egress |
| KMS + misc (SQS, Step Functions, Secrets) | `[Estimated]` $350 | `[Assumed]` ~200 CMKs × `[Benchmarked]` $1/mo + API; DLQ/compliance workflow |
| Parallel-run overlap (months 1–3) | `[Estimated]` $300 | `[Assumed]` 100% tee to legacy + new path doubles ingest-side API/Kinesis during migration |
| **Derived total** | **`[Estimated]` ~$3,800** | Sum of lines above |
| **Planning carry (3× buffer)** | **`[Estimated]` ~$11,400** | `[Estimated]` explicit buffer for unmodelled line items (multi-AZ, extended retention, load-test spend) — judgment, not hidden padding |

**DynamoDB trade-off (surfaced by corrected math).** On-demand at `[Estimated]` 1.5B dedupe writes/month alone is `[Estimated]` ~$1,875; doubling for rollup writes ≈ `[Estimated]` $3,750. Provisioned capacity with autoscaling at the same volume lands `[Estimated]` ~4× lower (~$1,000 line above). **Chosen:** provisioned — a 2-engineer team can manage capacity alarms; the savings fund multi-AZ redundancy and load testing. **Rejected:** on-demand for simplicity — viable for MVP spike uncertainty, but expensive at `[Estimated]` 1.5B sustained writes.

**Headroom under `[Assumed]` $50K ceiling.** The `[Estimated]` ~$3,800 derived total (carried at `[Estimated]` ~$11,400 in planning) leaves budget for: multi-AZ ElastiCache/DynamoDB, Kinesis extended retention beyond 24h, EU region stack earlier than months 4–6, dedicated load-testing environment, and reserved-capacity buffers for Black-Friday-scale spikes.

### Multi-tenant isolation (500+ tenants)

- **Stream tiering:** Tenants assigned to standard/high-volume/enterprise Kinesis streams by ingest profile — not per-tenant streams (ops) nor single stream (noisy-neighbor).
- **Partition key:** `tenant_id` on every Kinesis record and DynamoDB key.
- **Encryption:** Per-tenant KMS CMKs for quarantine and compliance S3 prefixes; default AWS-managed keys elsewhere.
- **IAM:** Tenant-scoped IAM boundaries on dashboard API; no cross-tenant DynamoDB queries.
- **Rate limiting:** API Gateway usage plans per tenant tier; burst tokens for legitimate spikes.

### Zero-data-loss mechanism

1. **At-least-once:** Kinesis retains `[Assumed]` 24h+; consumers checkpoint after durable side-effects.
2. **Idempotent dedupe:** DynamoDB table, PK=`event_id`, conditional put after normalize, `[Assumed]` ~7-day TTL. Duplicates (`evt-0002`) exit before hot writes.
3. **DLQ:** SQS dead-letter for validation/parse failures (`evt-0020`) — not for duplicates.
4. **Replay:** Fargate jobs replay DLQ and S3 quarantine after fix; idempotency prevents double-apply.
5. **Degradation order:** personalization freshness → dashboard staleness (up to `[Assumed]` 30s) → per-tenant rate limits → DLQ (never silent discard).
6. **Detection:** hourly parity vs legacy; CloudWatch `IteratorAge`, `DLQDepth`, `DuplicateEventRate`; sample-stream census via `detect_anomalies()`.

### Burst / spike handling

- CloudWatch alarms on `GetRecords.IteratorAgeMilliseconds` trigger runbook shard splits (Kinesis has no native lag-driven autoscaling) `[Assumed]`; target `[Assumed]` <60s behind.
- Per-tenant API rate limits with burst allowance.
- Bot heuristic (`evt-0012`–`evt-0015` pattern) diverts flagged traffic to cold S3, protecting ElastiCache/DynamoDB hot path.
- Lambda provisioned concurrency pre-warmed on high-volume tiers before known events (Black Friday runbook).

Compliance controls table: [`docs/design-appendix.md`](design-appendix.md).

### Migration & cutover

**Strategy:** Parallel-run from day one. API Gateway tees `[Assumed]` 100% to legacy Redis queue AND new Kinesis path. No SDK change.

**Validation (testable definition):** Hourly per-tenant: (1) ingest count delta `[Assumed]` ≤0.1% tolerance, (2) symmetric difference of `event_id` sets = ∅, (3) rollup checksum match (DynamoDB vs PostgreSQL materialized views).

**Promote:** Move tenant Gateway routing weight to new path when `[Assumed]` ≥99.9% parity for `[Assumed]` 72 consecutive hours.

**Rollback trigger (any one):**
- Parity `[Assumed]` <99.9% for any hour
- p99 end-to-end latency `[Assumed]` >5s for `[Assumed]` 15 minutes
- DLQ rate `[Assumed]` >0.1% of ingest volume

**Rollback action:** Revert Gateway routing weight per tenant to legacy path. Kinesis buffer retains events for replay after fix.

### Phased delivery (2 senior engineers)

| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| MVP | Months 1–3 | Tiered ingest, hybrid consumers, dedupe/DLQ/replay, hot dashboards (DynamoDB), basic ElastiCache counters, parallel-run migration, full fixture anomaly handling |
| Full build | Months 4–6 | Snowflake/BigQuery native connectors, advanced segment builder UI, bot-ML beyond heuristics, multi-region EU stack, provisioned concurrency automation |

---

## 3. Trade-offs & Risks

### Optimizing for vs. sacrificing

| Optimized | Sacrificed |
|-----------|------------|
| `[Assumed]` Sub-5s dashboard latency for `[Estimated]` 95% of events | Sub-second latency for warehouse analytics (cold path: minutes) |
| Zero data loss via at-least-once + idempotent dedupe | Exactly-once semantics (dedupe window = TTL, `[Assumed]` ~7 days) |
| 2-engineer operability (managed AWS services) | Full control / cost optimization of self-managed Kafka |
| Migration safety (parallel-run, per-tenant rollback) | Faster cutover (72h parity gate adds weeks to full migration) |
| Multi-tenant isolation without per-tenant infra | Noisy-neighbor risk within same tier (mitigated by tier promotion) |

### What could go wrong

See `docs/failure-modes.md` for the full architecture stress-test. Headline risks: dedupe TTL expiry; bot false positives; shard exhaustion beyond `[Estimated]` 8-shard budget at spikes above `[Estimated]` 10×; single-region blast radius; EU residency delay.

### With more time/budget

More budget: self-managed MSK, per-tenant enterprise shards, ML bot/PII detection. More time: Flink sessionization, multi-region active-active with EU residency from day one.
