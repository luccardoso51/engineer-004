Ticket:
Title: Design doc

Identifier: #3

Description:
What to build: the ≤4-page redesigned-pipeline doc — architecture, scale/reliability/migration, and trade-offs/risks per the brief's three required sections — covering current-state problems mapped to fixes, named AWS services with alternatives considered, latency and cost budgets, phased delivery plan, multi-tenant isolation, compliance controls, zero-loss mechanism, burst handling, and the fixture handled anomaly-class by anomaly-class with event_id citations.

Blocked by: Fixture forensics & anomaly taxonomy

- [ ] ≤4 pages (diagrams excluded from count)
- [ ] Current pipeline's specific failure modes (15-30min latency, ~3% loss, crashes) each mapped to a specific fix
- [ ] Latency budget breakdown (ingestion → processing → storage → query) summing under 5s
- [ ] Cost breakdown fitting within $50K/mo at 50M+ events/day
- [ ] Phased delivery plan mapped to 3-month MVP / 6-month full build, 2 senior engineers
- [ ] Multi-tenant isolation strategy for 500+ tenants stated explicitly
- [ ] SOC2/GDPR/CCPA controls (encryption, residency, right-to-deletion, audit logging, tenant segregation) named explicitly
- [ ] Zero-data-loss mechanism specified (at-least-once delivery, idempotent dedupe by event_id, DLQ, replay)
- [ ] Multi-tenant burst/spike handling addressed
- [ ] Named AWS services throughout, each with alternatives considered and rejected
- [ ] Fixture handled anomaly-class by anomaly-class, citing specific event_ids from ticket 1, plus the fixture checksum stated in the doc
- [ ] Migration/cutover plan with validation approach and rollback trigger
- [ ] Trade-offs/risks section: what's optimized for vs sacrificed, what would change with more time/budget
- [ ] Doc draws on Lucas's real queue-based backend experience where genuinely applicable, and references PostHog only as an SDK consumer
- [ ] Assumptions Lucas had to make called out explicitly in the doc

Labels: none

Acceptance criteria (if any are present in the body or a checklist):
- ≤4 pages (diagrams excluded from count)
- Current pipeline's specific failure modes (15-30min latency, ~3% loss, crashes) each mapped to a specific fix
- Latency budget breakdown (ingestion → processing → storage → query) summing under 5s
- Cost breakdown fitting within $50K/mo at 50M+ events/day
- Phased delivery plan mapped to 3-month MVP / 6-month full build, 2 senior engineers
- Multi-tenant isolation strategy for 500+ tenants stated explicitly
- SOC2/GDPR/CCPA controls (encryption, residency, right-to-deletion, audit logging, tenant segregation) named explicitly
- Zero-data-loss mechanism specified (at-least-once delivery, idempotent dedupe by event_id, DLQ, replay)
- Multi-tenant burst/spike handling addressed
- Named AWS services throughout, each with alternatives considered and rejected
- Fixture handled anomaly-class by anomaly-class, citing specific event_ids from ticket 1, plus the fixture checksum stated in the doc
- Migration/cutover plan with validation approach and rollback trigger
- Trade-offs/risks section: what's optimized for vs sacrificed, what would change with more time/budget
- Doc draws on Lucas's real queue-based backend experience where genuinely applicable, and references PostHog only as an SDK consumer
- Assumptions Lucas had to make called out explicitly in the doc

Relevant comments (only ones that change scope or add requirements — skip chit-chat):
none

Linked context (one entry per followed link; "none" if the ticket links to nothing):
--- brief.md (https://github.com/luccardoso51/engineer-004/blob/main/brief.md) ---
Challenge: Engineer 004 — System Design: Real-Time Analytics Pipeline

The Situation: Series B martech startup rebuilding analytics pipeline. ~50M events/day from JavaScript SDK (page views, clicks, form submissions, custom events). Current latency 15-30 minutes; customers want <5 second real-time. System crashes during traffic spikes. ~3% event loss during peak. Customers need real-time dashboards, behavior-triggered personalization, behavioral segmentation, warehouse export (Snowflake, BigQuery), GDPR/CCPA compliance.

Constraints: $50K/month infrastructure ceiling; MVP in 3 months, full system in 6 months; 2 senior engineers dedicated; cannot break existing integrations during migration.

Your Task: Design architecture for a real-time analytics pipeline solving latency, reliability, and scale.

Three required submission sections:

1. Architecture & Technology Choices
   - High-level system diagram: SDK to dashboard data flow
   - Technologies/services per component with rationale vs alternatives
   - Event data structure and user identity/stitching

2. Scale, Reliability & Migration
   - Handle 50M+ events/day and 10x traffic spikes with zero data loss
   - Migration from current system without breaking things; rollback plan
   - Data accuracy validation

3. Trade-offs & Risks
   - Optimizing for vs sacrificing
   - What could go wrong; what would change with more time/budget

Additional constraints: Must run on AWS; cannot require customers to update SDK; multi-tenant (500+ customers); SOC 2, GDPR, CCPA compliance.

Ground It in the Sample Data (Required):
- Fixture: fixtures/event_sample.jsonl — synthetic snapshot with seeded issues
- Design must state anomaly class by anomaly class how pipeline handles what is in the sample, citing specific event_ids
- Call out at least three things in the data not to act on at face value, and why
- State fixture checksum: shasum -a 256 fixtures/event_sample.jsonl
- Brief version: 2026-07 — state this version in written answer

Format: PDF or Markdown, maximum 4 pages (diagrams excluded from page count). Estimated time 1-2 hours.

--- Fixture forensics & anomaly taxonomy (#1) (https://github.com/luccardoso51/engineer-004/issues/1) ---
Status: CLOSED (merged via PR #8)

Delivers: docs/fixture-forensics.md — event_id-cited ground-truth catalog of fixtures/event_sample.jsonl, corrected nine-class anomaly taxonomy, sha256 checksum, and not-at-face-value write-up. Ticket 3 must cite event_ids and checksum from this artifact.

Key content from docs/fixture-forensics.md:

Provenance:
- File: fixtures/event_sample.jsonl
- SHA-256: 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235
- 25 physical lines; 24 JSON records parse; 1 line (file line 21, evt-0020) fails to parse
- 23 distinct event_ids (evt-0002 appears twice)

Corrected nine-class taxonomy (replaces spec's placeholder list):

| # | Class | Event(s) | Signal |
| 1 | Duplicate event_id / idempotency violation | evt-0002 | Same event_id on two records (lines 2 and 5), identical ts/payload, received_at differs ~7.4s |
| 2 | Out-of-order timestamp (client clock skew) | evt-0005 | received_at ~47s earlier than ts |
| 3 | Systematic timezone offset | evt-0006 | ts ~65 min ahead of received_at; matching .552 ms suffix |
| 4 | Future / impossible timestamp | evt-0016 | ts year 2027, received_at 2026 |
| 5 | Missing required field (unattributable) | evt-0011 | tenant_id is null |
| 6 | Unexpected PII in free-form payload | evt-0007 | contact_email and phone in custom event properties |
| 7 | Schema drift / non-conforming shape | evt-0009 | type pageview (not page_view); timestamp not ts; no received_at; page_path/ref instead of path/referrer |
| 8 | Bot / scanner volume-spike burst | evt-0012, evt-0013, evt-0014, evt-0015 | Four page_views from anon-8fc in ~50ms, scanner referrer, sequential paths |
| 9 | Malformed / corrupt JSON record | evt-0020 | File line 21 not valid JSON (missing closing brace) |

Classes dropped from placeholder (not in fixture): tenant_id mismatch/spoofing, cross-tenant leakage, per-tenant volume drop-to-zero, generic impossible field values.

Additional workflow concern (not a data-quality anomaly): evt-0017 privacy_request / delete_all_data — GDPR compliance signal requiring downstream workflow, not filtering.

Per-event verdicts: evt-0001 clean; evt-0002 duplicate; evt-0003 clean; evt-0004 clean; evt-0005 clock skew; evt-0006 timezone bug; evt-0007 PII; evt-0008 clean; evt-0009 schema drift; evt-0010 clean; evt-0011 null tenant_id; evt-0012–0015 bot burst; evt-0016 future timestamp; evt-0017 compliance-critical; evt-0018 clean; evt-0019 clean; evt-0020 malformed JSON; evt-0021–0024 clean.

Six items NOT to take at face value:
1. evt-0006 — systematic timezone bug, not real future event; use received_at for ordering
2. evt-0009 — legacy SDK shape; normalize, do not drop (brief forbids forcing SDK upgrade)
3. evt-0017 — GDPR delete_all_data mandate; route to compliance workflow, not analytics volume
4. evt-0002 duplicate — dedupe on event_id, not payload+ts; absorb retry idempotently
5. evt-0011 null tenant_id — quarantine; do not default to a tenant or silently drop
6. evt-0020 malformed — dead-letter and continue; must not crash loader

Handoff to ticket 3: design doc must handle each anomaly class above with event_id citations and state checksum 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235.

Linked but not fetched:
- SCORING.md (../../SCORING.md) — referenced in brief.md, not in ticket #3 body; not committed to repo scaffold
- scoring_rubric.md — not cited in ticket #3
- Anomaly-detection script, tests & benchmark (#2) — not listed as blocker for #3 (tickets 2 and 3 can run in parallel once #1 is done); out of scope for this ticket's blockers
- https://www.singlegrain.com/careers/ — marketing/careers page from brief.md; not fetched

---

Assistant:
Exploring the codebase to see what's already documented before asking blocking questions.
For the ingestion and stream-processing backbone (everything downstream — hot-path latency, dedupe placement, burst absorption, cost math — hangs off this), which pattern should the design doc commit to?

a) Kinesis Data Streams as the durable ingest buffer, with Lambda or Fargate consumers for validation, normalization, dedupe, and fan-out to hot and cold paths — reject MSK/Kafka (2-engineer ops burden) and direct-to-database ingest (no replay buffer, spikes crash writers)

b) SQS (per-tenant or pooled queues) with Lambda consumers — lean on your RabbitMQ mental model for backpressure and DLQ; reject Kinesis (less familiar operational model for you) and Kafka

c) API Gateway → Kinesis Data Firehose → S3 as primary path, with a separate low-latency side channel (e.g. DynamoDB/ElastiCache fed by a Firehose destination or a parallel Lambda) for the <5s dashboard query path

d) MSK (managed Kafka) as the central bus — strongest replay/partitioning story, but highest operational surface for a 2-engineer team on a 3-month MVP

My recommendation: a. It maps cleanly to the brief's failure modes (15–30 min latency → decouple ingest from processing; ~3% loss → durable stream + DLQ; spike crashes → buffer absorbs burst before workers), gives a natural place for evt-0002 idempotent dedupe and evt-0020 DLQ without killing the loader, and keeps shard/partition strategy as the explicit multi-tenant isolation knob. SQS (b) is viable but ordering and dedupe across retries are harder to explain convincingly at 50M/day; Firehose-primary (c) makes the hot path feel bolted on; MSK (d) is over-ops for this team size.

User:
a

---

Assistant:
For the hot path that must serve dashboards and personalization triggers in under 5 seconds end-to-end, what should the design doc name as the primary real-time query store (the layer readers hit for "what happened in the last few seconds/minutes")?

a) DynamoDB — tenant-scoped partition keys (tenant_id + metric/window), on-demand scaling for bursts, DynamoDB Streams for downstream fan-out; reject pure Redis (memory cost at 50M/day aggregation cardinality) and Timestream (segmentation query patterns are awkward)

b) ElastiCache (Redis) — sub-ms reads for counters, session-scoped segment membership, and personalization trigger state; cold/replayable truth stays on S3 via the Kinesis path; reject DynamoDB as primary (you'd be modeling Redis-shaped data in a less natural store)

c) Split hot tier — ElastiCache for personalization trigger state and live counters, DynamoDB for dashboard rollups and segment definitions; both fed by the same stream consumers (more moving parts, strongest fit for both <5s dashboards and "viewed pricing 3x" segmentation)

d) Amazon Timestream — time-series native, good for event-volume dashboards; reject as sole hot store because behavioral segmentation and identity stitching don't map cleanly to TSDB query patterns at this latency target

My recommendation: c. The brief asks for both real-time dashboards and behavior-triggered personalization/segmentation — Redis-shaped reads (counters, recent-event windows per anonymous_id) and DynamoDB-shaped reads (tenant rollup tiles, segment rule metadata) are different access patterns; splitting them lets the latency budget allocate ~1s to query without forcing one store to do both jobs. Pure DynamoDB (a) works but personalization trigger evaluation gets expensive; pure Redis (b) makes dashboard rollups and audit-friendly segment history harder to justify under compliance requirements.

User:
c

---

Assistant:
For multi-tenant isolation across 500+ tenants on the Kinesis backbone you approved, how should the design doc partition ingest and processing so one tenant's Black Friday spike doesn't starve or crash everyone else?

a) Tiered streams (e.g. standard / high-volume / enterprise) — tenants assigned to a tier by contracted throughput; each tier is its own Kinesis stream with independently sized shards; partition key still tenant_id within the stream; reject per-tenant streams (500+ streams unoperable) and a single shared stream with no tiering (noisy-neighbor risk at 10x spikes)

b) Single shared stream, partition key = tenant_id — hash tenants across N shards sized for aggregate 50M/day + 10x spike headroom; per-tenant ingest rate limits at API Gateway/WAF enforce fairness; reject tiered streams (extra onboarding/placement logic you may not need at MVP)

c) Single shared stream, partition key = hash(tenant_id + anonymous_id) — maximizes shard utilization and spreads bot bursts (evt-0012–0015) across shards; tenant isolation enforced only at the application layer (DynamoDB/Redis key prefixes, IAM), not at the stream partition level

d) Pool-of-queues model — multiple Kinesis streams as a pool, tenants dynamically mapped to a stream pool slot based on current volume; more flexible than fixed tiers but more routing metadata to operate

My recommendation: a. The brief's spike crashes and ~3% loss under peak are classic noisy-neighbor symptoms; tiered streams let you size shards for known high-volume tenants without over-provisioning 500 idle partitions, and they give a clean compliance story (enterprise tier can carry stricter residency/encryption controls). Per-tenant streams (rejected in a) is ops death; pure hash spreading (c) doesn't stop one hot tenant from filling every shard if they're huge; single stream without tiering (b) works for MVP math but is harder to defend when a reviewer asks "what happens when tenant #47 sends 10x on Black Friday?" Pool routing (d) is clever but adds moving parts two engineers shouldn't own in month one.

User:
a

---

Assistant:
For the Kinesis consumers that validate, normalize, dedupe, and fan-out to the hot tier (ElastiCache + DynamoDB) and the cold tier, what compute model should the design doc commit to?

a) Lambda only — one function per stage (ingest-normalize, dedupe, hot-writer, cold-writer); provisioned concurrency on high-volume tier consumers to cap cold-start latency; reject Fargate (extra cluster ops for two engineers)

b) Fargate/ECS only — long-running consumers with the Kinesis Client Library or enhanced fan-out; better for sustained replay and complex normalization (evt-0009 schema drift, evt-0006 timestamp correction); reject Lambda (15-minute timeout ceiling on large replays, cold-start jitter in the latency budget)

c) Hybrid — Lambda for the hot-path fan-out writers (normalize → dedupe checkpoint → Redis/DynamoDB, latency-sensitive); Fargate for cold-path writers (S3 parquet landing, warehouse staging, DLQ replay jobs); reject single compute everywhere (forces a trade-off neither path optimizes for)

d) Lambda for MVP, migrate hot consumers to Fargate at 6-month scale — doc describes both but phases the choice; reject committing to one model now (reviewer may read it as undecided architecture)

My recommendation: c. You already split the hot store; splitting compute matches that boundary — Lambda's millisecond-scale fan-out fits the <5s budget's processing leg, while Fargate's always-on consumers handle S3 batching, parquet conversion, and multi-hour DLQ replays (evt-0020 malformed lines) without fighting Lambda timeouts. Lambda-only (a) makes replay and warehouse export awkward; Fargate-only (b) adds unnecessary baseline cost and cold-start isn't a problem but hot-path latency variance is harder to cap; phased indecision (d) reads as hedging rather than a design choice.

User:
c

---

Assistant:
For the phased delivery plan (3-month MVP / 6-month full build, two senior engineers), what should the design doc treat as MVP-complete at month 3 versus explicitly deferred to months 4–6?

a) MVP (3mo): tiered Kinesis ingest, hybrid consumers, dedupe/DLQ/replay, hot dashboards via DynamoDB rollups, basic ElastiCache live counters, parallel-run migration with rollback triggers, fixture anomaly handling end-to-end; deferred to 4–6mo: Snowflake/BigQuery native connectors, advanced segment builder, bot-ML scoring beyond heuristic flagging (evt-0012–0015), multi-region residency

b) MVP (3mo): ingest + cold S3 landing + correctness (dedupe, DLQ, replay, migration validation) only; deferred: all customer-facing query surfaces (dashboards, personalization triggers, segmentation, warehouse export) — proves zero-loss first, latency second

c) MVP (3mo): full hot path including personalization triggers and basic segmentation in Redis/DynamoDB plus S3 cold store; deferred: warehouse export connectors and enterprise compliance extras (cross-region, advanced audit); migration is shadow-mode only until month 6

d) MVP (3mo): single-tier stream (no tiered streams yet), Lambda-only consumers, DynamoDB-only hot store — tiered streams, ElastiCache split, and Fargate cold path land in months 4–6 as scale hardening

My recommendation: a. It maps each brief failure mode to a month-3 fix (latency → hot path live; loss → dedupe/DLQ; crashes → Kinesis buffer + tiered streams), delivers something customers can actually see on a dashboard, and keeps warehouse export and heavier compliance as honest 6-month work — two engineers can't wire Snowflake/BigQuery connectors, a segment builder, and migration cutover in 90 days without cutting reliability depth. Option (b) ignores the brief's "<5s dashboard" requirement as the customer pain; (c) overloads MVP with personalization/segmentation plus full migration; (d) contradicts the architecture choices you already approved (tiered streams, hybrid compute, split hot tier) and would read as planning to throw away month-1 work.

User:
a

---

Assistant:
For the migration/cutover section, the brief names failure modes (15–30 min latency, ~3% loss, spike crashes) but not the current pipeline's actual shape — what should the design doc assume you're migrating away from, so each failure mode maps to a concrete "before → after" fix?

a) SDK → HTTP API → in-memory/Redis queue → synchronous Python workers → PostgreSQL (dashboards query Postgres directly or via a slow materialized-view refresh) — spike crashes = worker OOM/connection exhaustion; loss = unacked queue messages; latency = batch refresh cadence; ties naturally to your RabbitMQ/queue experience as the "before" picture

b) SDK → HTTP API → direct PostgreSQL INSERT (no durable queue) — loss and crashes under spike = DB write saturation and dropped API responses; latency = scheduled ETL/aggregation job every 15–30 min to a reporting layer

c) SDK → S3 batch uploads → nightly/hourly Glue/Spark job → PostgreSQL — latency is entirely batch-schedule-driven; spikes buffer in S3 but processing lag is structural; loss = failed batch runs

d) State only the observable symptoms without naming a current architecture — map each failure mode to the new design's fix and flag "current internals assumed, not specified in brief" in the assumptions section

My recommendation: a. It's the most plausible explanation for all three failure modes simultaneously (crashes + loss + minutes of latency), it's operable by a 12-person martech team on the stated stack, and it gives you an honest place to reference queue-based backend experience (backpressure, at-least-once retries, why evt-0002 dedupe matters) without claiming you operated Kinesis at scale. (b) doesn't explain crashes as cleanly; (c) makes 15–30 min latency the happy path, not a degradation; (d) is safe but weaker on the rubric's "migration takes the constraint seriously" criterion.

User:
a

---

Assistant:
For the bot/scanner burst class in the fixture (evt-0012–evt-0015: four page_views from the same anonymous_id in ~50ms, scanner referrer, sequential paths), what should the pipeline do after classification?

a) Flag and exclude from hot path — heuristic bot score at normalize stage (referrer domain, events-per-second per anonymous_id); enriched record lands in cold S3 with anomaly metadata for audit; skipped for ElastiCache counters and DynamoDB dashboard rollups; personalization triggers never fire on flagged events

b) Flag but keep in hot path — same detection heuristics, anomaly_class attached to every downstream copy, dashboard queries default to excluding bot_flagged=true but cold storage retains everything; personalization layer applies an explicit bot filter

c) Rate-limit at ingest (API Gateway/WAF per tenant_id + anonymous_id) — absorb the burst before it hits Kinesis; events still stored if they pass the throttle, no separate bot classifier in MVP

d) Hard drop at ingest — scanner referrer and velocity threshold cause immediate reject (4xx) with no durable record; minimizes hot-path noise and cost; rejected events logged to CloudWatch only

My recommendation: a. It handles the spike without crashing (your approved buffer + tiered streams absorb volume) while keeping customer-facing metrics clean — four bot page_views shouldn't increment pricing-page counts or fire personalization. Cold S3 retention preserves auditability and SOC2 traceability. (b) works but leaves bot traffic in Redis counters unless every reader remembers the filter. (c) stops the burst early but doesn't generalize to bots that arrive under the rate limit. (d) violates the zero-loss story for events the SDK already sent and removes forensic evidence you'd want for compliance review.

User:
a

---

Assistant:
For unexpected PII in free-form event properties (evt-0007: contact_email and phone embedded in a custom event's properties bag), what should the pipeline do at processing time?

a) Detect, redact, and quarantine — regex/heuristic PII scanner on properties after normalization; raw copy with PII lands in an encrypted quarantine prefix in S3 (restricted IAM, short retention); hot path and dashboard rollups store redacted properties only; compliance audit log records detection

b) Detect and hash — replace email/phone with salted HMAC tokens so identity stitching across events is still possible for opted-in users; no separate quarantine bucket; reject full redaction (breaks downstream workflows that need a stable pseudonymous key)

c) Detect and flag only — attach pii_detected=true and field paths to the enriched event; no automatic mutation of payload; downstream consumers and warehouse export apply tenant-configured policies; reject because it leaves PII in ElastiCache/DynamoDB hot stores

d) Hard reject at ingest — return 4xx to SDK for events containing detectable PII in properties; forces client correction; reject because brief forbids SDK changes and you can't rely on clients to retry correctly

My recommendation: a. PII in hot stores (Redis/DynamoDB) is a GDPR/CCPA liability and contradicts the compliance-as-architecture rubric; redaction before hot-path write is the safe default. Quarantine in encrypted S3 with tight retention gives auditors evidence of detection without polluting analytics. Hashing (b) is defensible for stitching but adds key-management complexity and still stores derived PII. Flag-only (c) leaves toxic data in the <5s path. Hard reject (d) conflicts with no-SDK-change constraint and risks evt-0007-style data silently disappearing from the customer's view.

User:
a

---

Assistant:
For the compliance workflow signal in the fixture (evt-0017: privacy_request / delete_all_data for tenant-002) — which is a downstream mandate, not a data-quality anomaly — how should the design doc describe routing and execution?

a) Dedicated compliance stream — privacy_request events bypass analytics hot-path writers after normalize; routed to a separate SQS queue + Step Functions workflow that orchestrates deletion across S3 prefixes, DynamoDB items, ElastiCache keys, and warehouse staging tables by tenant_id + subject identifiers; audit log records each deletion step with event_id citation; analytics counters never increment

b) Same Kinesis path with a consumer fork — evt-0017 tagged event_type=compliance at normalize; hot/cold analytics consumers drop it; a parallel Lambda subscribed to the enriched stream (or DynamoDB Streams on a compliance inbox table) triggers deletion jobs; simpler topology, one ingest contract

c) Out-of-band API only — privacy requests are not carried as analytics events; customers call a separate GDPR API; evt-0017 in the fixture is treated as a misrouted SDK event that gets quarantined like evt-0011; reject because forensics explicitly says route to compliance workflow, not filter

d) Tag and defer — evt-0017 stored in cold S3 with compliance_flag; nightly batch job processes deletion requests; reject for right-to-deletion SLA (GDPR expects timely erasure, not next-day batch)

My recommendation: a. Forensics says route to compliance workflow, not analytics volume — a dedicated queue + orchestrator makes tenant-scoped erasure explicit, testable, and auditable (SOC2), and keeps evt-0017 from ever touching Redis rollups. Same-path fork (b) is viable but muddies the "analytics vs compliance" boundary reviewers will probe. Out-of-band only (c) ignores the fixture's planted signal. Batch defer (d) is weak on GDPR timeliness.

User:
a

---

Assistant:
For zero-data-loss dedupe on duplicate event_id (evt-0002: same event_id twice, identical payload, received_at differs ~7.4s — absorb retry idempotently, not dedupe on payload+ts), where should the design doc place the idempotency check and what store backs it?

a) DynamoDB idempotency table — partition key event_id (global across tenants since event_ids are unique in fixture); conditional write / put-if-absent in the hot-path Lambda immediately after normalize; duplicate returns early before Redis/Dynamo rollup writes; TTL ~7 days (covers retry window); DLQ only for events that fail validation, not duplicates

b) Redis SET per tenant — ElastiCache SET tenant_id:event_id with TTL; faster check, co-located with hot counters; reject because Redis persistence/replay story is weaker for audit and compliance than DynamoDB for dedupe state

c) Kinesis exactly-once semantics + Flink state — rely on managed exactly-once processing; reject because you chose Lambda/Fargate hybrid, not Flink, and evt-0002 proves client retries not stream replay are the source

d) Dedupe on cold path only — both copies land in hot stores, Fargate compaction job collapses duplicates in S3; reject because it violates <5s accuracy and inflates dashboard counts until batch correction

My recommendation: a. evt-0002's signal is retry with same event_id — a DynamoDB conditional put is the standard at-least-once idempotency pattern, maps directly to your queue experience (consumer ack + idempotent handler), survives Lambda retries, and gives a queryable dedupe audit trail. Redis (b) is fast but the wrong durability tier for the dedupe ledger. Exactly-once (c) overpromises on your stack. Cold-only dedupe (d) means dashboards double-count for minutes.

User:
a

---

Assistant:
For migration/cutover from the assumed current pipeline (SDK → API → Redis queue → sync workers → PostgreSQL), what cutover model and rollback trigger should the design doc commit to?

a) Parallel-run with per-tenant promotion — tee ingest at API Gateway to old queue path and new Kinesis path from day one of migration; hourly validation job compares event counts, distinct event_id sets, and rollup checksums per tenant_id; promote tenant when parity ≥99.9% for 72 consecutive hours; rollback trigger for that tenant = any hour parity <99.9%, p99 end-to-end latency >5s for 15 minutes, or DLQ volume >0.1% of ingest — promotion reverts to old path via Gateway routing weight without SDK change

b) Percentage traffic shift (blue/green) — route 5%→25%→50%→100% of API traffic to new ingest via weighted target groups; rollback trigger = automatic weight revert to 0% on rollback alarm (latency, error rate, or validation divergence); no per-tenant granularity

c) Tier-ordered cutover — migrate enterprise tier tenants first (weeks 1–4), then standard (weeks 5–8); each tier is big-bang within the tier; rollback = revert entire tier to old path if validation fails post-cutover

d) Maintenance-window big-bang — all 500+ tenants cut over in a single scheduled window; rollback = restore PostgreSQL snapshot and revert DNS to old API; validation is pre-window rehearsal only

My recommendation: a. The brief's hardest constraint is "cannot break existing integrations" across 500+ tenants — per-tenant promotion with continuous parity checking is the most defensible operator story and gives a concrete, testable definition of "data accuracy verified." Percentage shift (b) is simpler but a bad tenant's 5% share still corrupts global dashboards. Tier big-bang (c) is reasonable but riskier within a tier. Maintenance-window big-bang (d) is what the rubric calls "the skipped migration."

User:
a

---

Assistant:
For SOC2/GDPR/CCPA residency and tenant segregation in the design doc, what geographic and encryption model should MVP (month 3) commit to versus what lands in months 4–6?

a) Single primary region (us-east-1) at MVP — all tiered Kinesis streams, hot stores, and cold S3 in one region; logical isolation via tenant_id partition keys, per-tenant KMS CMKs for S3 quarantine/compliance prefixes, and IAM boundaries; EU data residency for hot-path dashboards explicitly deferred to months 4–6 (dedicated eu-west-1 stack for EU-contracted tenants); doc states this as an explicit assumption

b) Dual-region from day one — US tenants in us-east-1, EU tenants in eu-west-1, separate full stacks per region including Kinesis tiers and hot stores; reject for two-engineer 3-month MVP (doubles operational surface)

c) Global API (CloudFront + Route 53 latency routing) with all durable data in us-east-1 — ingest is global, storage centralized; encryption at rest via single regional KMS; reject because GDPR contractual residency for EU martech customers is hard to defend

d) US hot path + EU cold replication only — ElastiCache/DynamoDB stay us-east-1 for all tenants; S3 cross-region replication to eu-west-1 for EU tenant cold prefixes; reject because hot dashboards and personalization triggers would still process EU data in the US

My recommendation: a. It fits your approved MVP scope (residency deferred to 4–6), stays within budget math for month 3, and still names the controls reviewers want (encryption, tenant segregation, audit logging, right-to-deletion workflow) with honest logical isolation rather than fake geographic isolation. Dual-region now (b) blows the timeline. US-only for everyone (c) and US-hot/EU-cold (d) are GDPR weak points you'd have to over-explain in trade-offs.

User:
a

---

Assistant:
For the ticket deliverable itself, where and in what format should the design doc live in the repo?

a) docs/design-pipeline.md — Markdown in the existing docs/ folder alongside fixture-forensics.md; diagrams as Mermaid or ASCII in the same file or linked files excluded from page count per brief; PDF export only when uploading to careers, not committed

b) docs/design-pipeline.md plus a committed PDF (docs/design-pipeline.pdf) generated from the Markdown — both artifacts in repo

c) submission/design-pipeline.md at repo root level — separates challenge submission artifacts from internal working docs

d) Single root-level DESIGN.md — maximum visibility, matches some challenge repos' convention

My recommendation: a. The repo already anchors analysis in docs/ (fixture-forensics.md, adr/); keeping the design doc there is consistent, Markdown diffs cleanly in PR review, and the brief's "PDF or Markdown" means one format in-repo is enough — PDF generation stays an upload-step, not a maintenance burden. Committed PDF (b) goes stale on every edit. submission/ prefix (c) adds a folder the scaffold doesn't use yet. Root DESIGN.md (d) is fine but less consistent with where ticket 1 landed its artifact.

User:
a

---

Assistant:
```ticket-grill-complete
summary: Ticket #3 delivers docs/design-pipeline.md — a ≤4-page Markdown design doc (brief version 2026-07; diagrams/Mermaid excluded from page count; PDF only at careers upload, not committed) with three sections (Architecture & Technology Choices; Scale, Reliability & Migration; Trade-offs & Risks). Backbone: SDK → API Gateway (tee for migration) → tiered Kinesis Data Streams (standard/high-volume/enterprise tiers; partition key tenant_id; rejects per-tenant streams and single-stream noisy-neighbor) → hybrid consumers: Lambda for hot-path normalize/dedupe/fan-out (provisioned concurrency on high-volume tiers); Fargate for cold-path S3 parquet landing, warehouse staging, DLQ replay. Hot path split: ElastiCache (Redis) for live counters and personalization trigger state; DynamoDB for dashboard rollups and segment definitions. Cold path: S3 (Fargate writers). Dedupe: DynamoDB idempotency table, partition key event_id, conditional put after normalize, ~7-day TTL; duplicates (evt-0002) exit before hot writes; DLQ only for validation/parse failures not dupes. Current broken system assumed (stated explicitly): SDK → HTTP API → Redis queue → synchronous Python workers → PostgreSQL with slow materialized-view refresh — maps failures: 15–30min latency → decoupled stream + hot stores; ~3% loss → durable Kinesis buffer + at-least-once + idempotent dedupe; spike crashes → tiered stream buffering + per-tenant API rate limits. Multi-tenant isolation: tiered streams + tenant_id partition keys + per-tenant KMS CMKs for quarantine/compliance S3 prefixes + IAM boundaries; MVP single region us-east-1 with EU hot-path residency deferred months 4–6 (explicit assumption). Zero-loss: at-least-once Kinesis, idempotent dedupe, DLQ (evt-0020 malformed JSON dead-lettered, loader continues), replay from S3/DLQ via Fargate jobs. Burst/bot handling (evt-0012–0015): heuristic bot score at normalize (referrer, velocity per anonymous_id); flagged events to cold S3 with anomaly metadata; excluded from ElastiCache/DynamoDB rollups and personalization triggers. PII (evt-0007): regex/heuristic scan on properties; redact before hot writes; encrypted quarantine S3 prefix with restricted IAM and short retention; audit log. Null tenant_id (evt-0011): quarantine, never default or silent drop. Schema drift (evt-0009): normalize legacy fields to canonical shape, do not drop. Timestamps: evt-0005 clock skew and evt-0006 timezone offset — flag anomaly class, prefer received_at for ordering where ts suspect; evt-0016 future ts flagged. evt-0017 privacy_request/delete_all_data: bypass analytics; dedicated SQS + Step Functions orchestrating erasure across S3, DynamoDB, ElastiCache, warehouse staging by tenant_id/subject; audit each step citing event_id. Fixture: cite all nine anomaly classes plus evt-0017 workflow concern with event_ids; six not-at-face-value items from fixture-forensics; checksum 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235. Migration: parallel-run tee at API Gateway from day one; hourly per-tenant validation (counts, distinct event_ids, rollup checksums); promote tenant when ≥99.9% parity for 72h; rollback trigger = parity <99.9% any hour, p99 latency >5s for 15min, or DLQ >0.1% of ingest — revert Gateway routing weight per tenant, no SDK change. MVP month 3: tiered ingest, hybrid consumers, dedupe/DLQ/replay, hot dashboards (DynamoDB), basic ElastiCache counters, parallel-run migration, full fixture anomaly handling. Deferred months 4–6: Snowflake/BigQuery native connectors, advanced segment builder, bot-ML beyond heuristics, multi-region EU stack. Phased plan for 2 senior engineers. Latency budget (ingestion→processing→storage→query) summing <5s with labeled sources. Cost breakdown ≤$50K/mo at 50M+ events/day with visible math and observed/estimated/benchmarked/assumed labels. Every named AWS service includes rejected alternatives with rationale. Trade-offs: optimized vs sacrificed; what changes with more time/budget. Ground queue-based backend experience (RabbitMQ-adjacent: backpressure, at-least-once, idempotent handlers) where analogous; PostHog referenced only as SDK consumer, not operator. Collaboration model from prep: propose-with-reasoning, Lucas approves/overrides; adjacent experience tier (not Tier-4 production pipeline scale). Assumptions section lists: current pipeline shape, us-east-1 MVP residency, EU deferral, tier count/sizing estimates, event_id global uniqueness for dedupe table.
```