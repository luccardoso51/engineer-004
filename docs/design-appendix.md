# Design Appendix — Supporting Tables

Operating artifact excluded from the 4-page written-answer limit. Linked from
[`docs/design-pipeline.md`](design-pipeline.md).

## Assumptions

| Assumption | Rationale |
|------------|-----------|
| Current pipeline is SDK → HTTP API → Redis queue → synchronous Python workers → PostgreSQL with slow materialized-view refresh | Brief describes broken system; no production access to confirm |
| MVP runs single-region `us-east-1`; EU data residency deferred to months 4–6 | 2-engineer team; compliance controls designed now, EU stack later |
| Three Kinesis tiers (standard / high-volume / enterprise) sized from tenant ingest profiles | Rejects per-tenant streams (ops burden at 500+ tenants) and single-stream (noisy-neighbor) |
| `event_id` is globally unique per logical event | Required for DynamoDB dedupe table; SDK contract |
| Tier counts and shard sizing are estimates pending load test | Labeled `[Estimated]` in cost/latency tables |
| SDK batches `[Assumed]` ~20 events per HTTP request | Brief forbids SDK change; batching behaviour is inherited, not set |

## Current-state failure modes → fixes

| Failure mode | Root cause (assumed) | Fix |
|--------------|---------------------|-----|
| `[Assumed]` 15–30 min dashboard latency | Synchronous workers + PostgreSQL materialized-view refresh blocks hot path | Decouple ingest (Kinesis buffer) from compute; write rollups to DynamoDB/ElastiCache for sub-second reads |
| `[Assumed]` ~3% event loss at peak | Redis queue overflow + worker crashes drop unacked messages | Durable Kinesis retention (`[Assumed]` 24h+), at-least-once consumers, idempotent dedupe by `event_id`, DLQ for poison records |
| Crashes during traffic spikes | Single Redis queue + fixed worker pool; no per-tenant isolation | Tiered streams absorb burst; API Gateway per-tenant rate limits; Lambda provisioned concurrency on high-volume tiers; bot traffic diverted to cold path |

## Supporting services

| Service | Chosen for | Rejected alternative |
|---------|-----------|---------------------|
| SQS (DLQ) | Poison-message queue for parse failures (`evt-0020`) | SNS — no built-in retry/DLQ redrive; EventBridge — better for routing, weaker poison-queue semantics |
| Step Functions (`evt-0017`) | Multi-store GDPR erasure orchestration with audit trail | Lambda-only chain — harder to observe/replay long workflows; SWF — deprecated |
| S3 | Durable Parquet landing, quarantine, warehouse staging | EFS — higher cost at `[Estimated]` ~2TB/mo volume; Glacier — too slow for replay |
| KMS | Per-tenant CMKs for quarantine/compliance prefixes | CloudHSM — over budget for MVP; no encryption — SOC 2 blocker |
| CloudWatch | Metrics, alarms (shard lag, DLQ depth, p99 latency) | Datadog — adds `[Estimated]` ~$3K/mo; self-hosted Prometheus — ops burden |
| Secrets Manager | API key rotation | SSM Parameter Store — no automatic rotation |

## Compliance controls (SOC 2 / GDPR / CCPA)

| Control | Implementation |
|---------|----------------|
| Encryption at rest | KMS on S3, DynamoDB, Kinesis (server-side); per-tenant CMKs for quarantine |
| Encryption in transit | TLS `[Assumed]` 1.2+ on API Gateway; Kinesis in-VPC endpoints |
| Data residency | MVP: `us-east-1`; EU stack months 4–6 with tenant-level routing |
| Right to deletion (GDPR) | `evt-0017` workflow: Step Functions erasure across all stores; human approval gate; confirmation audit log; cascade resolver finds events keyed to subject `user_id`/`anonymous_id` (fixture: `evt-0006` shares `anon-77a` with `evt-0017`) |
| CCPA access / opt-out | Dashboard export API for access/portability; `do_not_sell` tenant flag suppresses third-party warehouse sync |
| Audit logging | CloudTrail (API), S3 access logs (quarantine), DynamoDB streams (dedupe audit) |
| Tenant segregation | Partition keys, IAM boundaries, separate KMS keys for sensitive prefixes |
