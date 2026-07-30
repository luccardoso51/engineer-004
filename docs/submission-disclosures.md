# Submission Disclosures

Per `brief.md` submission packet items #5–7 and `SCORING.md` AI Usage / Failure Modes sections. Excluded from the 4-page written-answer limit.

## AI usage disclosure

| Item | Detail |
|------|--------|
| Tools used | Cursor (Composer agent), Nemo CLI orchestration |
| AI helped with | Structuring the design doc against the brief checklist; drafting Mermaid diagram; cross-referencing `docs/fixture-forensics.md` event_ids; cost/latency table formatting |
| Human decisions | Architecture choices (Kinesis tiering over MSK, parallel-run migration, DynamoDB dedupe key); anomaly handling policy (six "not at face value" refusals); throughput/cost arithmetic; phased MVP scope; compliance workflow requiring human approval |
| Human verification | Ran `shasum -a 256 fixtures/event_sample.jsonl`; ran full `pytest` suite; re-derived cost line items and shard math; read every fixture event in forensics doc against design table |
| Known weak spots | Latency and AWS cost figures are `[Estimated]` — no load test or AWS bill yet; EU residency deferred; bot detection is heuristic-only in MVP |

## What breaks it

| Failure mode | Why the design fails | Detection |
|--------------|---------------------|-----------|
| `event_id` not globally unique | Dedupe table collapses distinct events | Sudden rollup drops; parity check vs legacy |
| Sustained spike >`[Estimated]` 30K events/sec | Kinesis shard capacity exhausted despite buffering | `IteratorAge` alarm; ingest 503 rate |
| Dedupe TTL < replay lag | Double-counted events after DLQ replay | `DuplicateEventRate` after replay jobs |
| Bot heuristic false positive | Legitimate traffic excluded from hot rollups | Tenant support tickets; per-tenant override list |
| Parallel-run tee misconfigured | Legacy path starved or double-billed | Per-path ingest counters diverge |
| GDPR erasure partial failure | `evt-0017`-class requests leave data in cold S3 | Step Functions failure state; audit log gap |
| EU tenant routed to `us-east-1` post-month 4 | GDPR residency violation | Tenant config audit |

## What stays human

| Decision | Why not automated |
|----------|-------------------|
| GDPR/CCPA erasure approval (`evt-0017`) | Legal scope confirmation; prevent mistaken full-account wipe |
| Quarantine release for `evt-0011` (null `tenant_id`) | Attribution requires support investigation, not guesswork |
| Tenant tier promotion/demotion | Business relationship + ingest profile judgment |
| Migration promote per tenant (`[Assumed]` 72h parity gate) | Rollback cost is customer-visible; engineer signs off |
| Bot-flag override for enterprise tenants | False positive risk on high-value traffic |
| Shard-split runbook execution during Black Friday | Capacity change with spend impact; on-call judgment |
| PII quarantine review (`evt-0007`) | Compliance officer confirms redaction scope |
