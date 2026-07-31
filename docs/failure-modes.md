# Failure Modes & What Stays Human

Architecture stress-test for the pipeline designed in `docs/design-pipeline.md`,
plus the decisions this design deliberately keeps out of automation. This is a
packet operating artifact (excluded from the 4-page written-answer limit),
alongside `docs/evidence-log.md` and `docs/submission-disclosures.md`. It is the
single home for the failure-mode and what-stays-human analysis; the short
tables that used to live in `docs/submission-disclosures.md` now point here.

Evidence-tier discipline (per `SCORING.md` number labels) is preserved
throughout: the one place this document can cite *observed, benchmarked*
behavior is the poison-pill scenario, which reflects code that actually runs in
`src/analytics_pipeline/loader.py` against `fixtures/event_sample.jsonl`. Every
other mitigation below is a **designed** production mechanism from
`design-pipeline.md` that is not yet built — labeled as such so the two are
never conflated.

## 1. Architecture stress-test

The four scenarios the pipeline is most likely to fail under, scanned first,
then each worked through in narrative. Only the poison-pill row is grounded in
running code; the other three are stress-tests of the *design*.

### Scan table

| Failure mode | Trigger | What breaks first | Detection | Mitigation |
|--------------|---------|-------------------|-----------|------------|
| Hot-partition tenant | One tenant's burst exceeds its Kinesis shard's `[Benchmarked]` 1,000 rec/s within its tier | Per-tenant ordering stalls; that shard's `IteratorAge` climbs while tier-mates lag behind it | `GetRecords.IteratorAgeMilliseconds` alarm on the affected shard; per-tenant ingest counters | Tier promotion (move tenant to higher tier); runbook shard-split; API Gateway per-tenant burst caps. **Designed**, not yet built. |
| Ingestion backpressure | Aggregate load exceeds the `[Estimated]` ~30-shard budget, or Lambda concurrency / DynamoDB dedupe throughput saturates | Whichever downstream capacity is tightest — dedupe conditional-put throttles, then Lambda concurrency, then shard capacity | `IteratorAge`, Lambda `Throttles`, DynamoDB `ThrottledRequests`, ingest 503 rate | Documented degradation order (personalization → dashboard staleness → per-tenant rate limits → DLQ, never silent discard); Kinesis retention as buffer for replay. **Designed**, not yet built. |
| Cross-region failover | `us-east-1` regional impairment (MVP is single-region) | Everything — there is no automated multi-region failover in the MVP; ingest and dashboards go down together | AWS Health events; synthetic canary on ingest + dashboard endpoints; multi-region absence is a known, accepted gap | Human-triggered response only: hold at the Gateway, drain to Kinesis retention, resume on recovery. EU multi-region stack is phased for months 4–6. **Gap accepted for MVP.** |
| Poison-pill / malformed event | A corrupt or truncated record on the wire (fixture case: `evt-0020`, file line 21, missing closing brace) | Nothing downstream — the record is isolated at parse time and the stream continues | Dead-letter count / DLQ depth; the malformed line is captured with its `line_number`, `raw_text`, extracted `event_id`, and parser error | **Local script: Observed & benchmarked** — `load_jsonl` dead-letters the line and continues (see below). **Production SQS DLQ + replay: Designed**, not yet built. |

### 1.1 Hot-partition tenants

The design partitions Kinesis by `tenant_id` and groups tenants into three
streams (standard / high-volume / enterprise) sized from ingest profiles — see
`design-pipeline.md` §"Multi-tenant isolation (500+ tenants)" and its
`Assumptions` table. That choice buys per-tenant ordering and cross-tier
noisy-neighbor isolation, but it deliberately does **not** give each tenant its
own shard (rejected as `[Assumed]` 500+ stream ops burden). The residual risk
lives *inside* a tier: a single tenant whose real-time burst exceeds one
shard's `[Benchmarked]` 1,000 rec/s throughput becomes a hot partition. Because
records for that tenant share a partition key, they queue on the same shard —
that shard's `IteratorAge` climbs while the tenant's own events fall behind,
and, in the worst case, tier-mates hashed to the same shard inherit the lag.

This is the streaming-time counterpart of the fixture's bot-burst class
(`evt-0012`–`evt-0015`, four hits from `anon-8fc` in a `[Observed]` ~50ms span):
the same shape of concentrated burst, but from a legitimate high-value tenant
rather than a scanner, so it cannot simply be diverted to the cold path.

Mitigation (all **designed**, not yet built) follows `design-pipeline.md`
§"Burst / spike handling": the `IteratorAge` alarm fires the shard-split
runbook; API Gateway per-tenant usage plans cap the burst with a token
allowance for legitimate spikes; and sustained pressure is answered by
promoting the tenant to a higher tier. The promotion decision itself is a human
call (see §2) — it is a business-relationship and ingest-profile judgment, not
a threshold.

### 1.2 Ingestion backpressure

Backpressure is the aggregate-load version of the same problem: total ingest
outruns downstream capacity. Sizing (`design-pipeline.md` §"Throughput sizing")
budgets `[Estimated]` ~8 shards for `[Estimated]` ~5,780 events/sec at a
`[Estimated]` 10× spike (record-rate limit binds at `[Estimated]` 6 shards;
`[Estimated]` 8 chosen for tier separation and headroom) — but a spike beyond
that budget, or a slowdown in any single downstream stage, exhausts capacity.
The first thing to break is not necessarily the shards: the DynamoDB dedupe
conditional-put (one write per event, PK=`event_id`) or Lambda hot-path
concurrency can saturate first, throttling upstream and driving `IteratorAge`
up even while raw shard capacity remains.

The design's answer is an explicit, ordered degradation rather than collapse
(`design-pipeline.md` §"Zero-data-loss mechanism", step 5): personalization
freshness is sacrificed first, then dashboard staleness (up to `[Assumed]` 30s),
then per-tenant rate limits tighten, and only then does traffic route to the
DLQ — **never** a silent discard. Kinesis retention (`[Assumed]` 24h+) acts as
the buffer that makes this survivable: events sit durably in the stream and are
replayed once capacity recovers. Detection is `IteratorAge`, Lambda
`Throttles`, DynamoDB `ThrottledRequests`, and the ingest 503 rate. All of this
is **designed**, not yet built and not yet load-tested — the throughput numbers
are `[Estimated]`, with no AWS bill or load test behind them.

### 1.3 Cross-region failover

This is the scenario where honesty matters more than a mitigation. The MVP runs
**single-region `us-east-1`** by explicit assumption (`design-pipeline.md`
`Assumptions` table and §"Compliance controls → Data residency"), chosen for a
`[Assumed]` 2-engineer team. There is **no automated multi-region failover**.
The blast radius of a `us-east-1` regional impairment is therefore the whole
system: ingestion (API Gateway, Kinesis), hot stores (DynamoDB, ElastiCache),
and the dashboard API all go down together.

Stated plainly in RTO/RPO terms:

- **RPO** is bounded by Kinesis durable retention: events already accepted into
  the stream survive the outage and replay on recovery, so accepted-event data
  loss trends to zero *provided the region's storage is not lost*. In-flight
  requests not yet accepted by the Gateway are dropped and depend on SDK client
  retry.
- **RTO** is **not** an automated number — it is however long AWS takes to
  restore the region plus human-triggered drain/replay. There is no warm standby
  region in the MVP to cut over to.

The MVP response is deliberately human-triggered (see §2, incident triage): hold
or shed at the Gateway, let Kinesis retention absorb what it can, and resume on
recovery rather than firing an unbuilt, untested automated failover. The EU
multi-region stack is phased for **months 4–6** (`design-pipeline.md`
§"Phased delivery"), which is when active-active / regional failover becomes
real. Until then this is a **known, accepted gap**, not an oversight — carrying
an untested failover path would be its own failure mode.

### 1.4 Poison-pill / malformed events

This is the one scenario tied to code that actually runs today, so it gets the
strongest evidence tier in this document — and the sharpest distinction between
what is **observed** and what is **designed**.

**Observed (Tier 3/4 — local script, benchmarked).** `src/analytics_pipeline/loader.py`
`load_jsonl()` reads the fixture line by line. Each line is parsed inside a
`try` that catches `json.JSONDecodeError`; on failure it constructs a
`DeadLetter(line_number, raw_text, event_id, error)` — where `event_id` is
regex-extracted from the raw text via `_extract_event_id`, falling back to
`"line:N"` when even that can't be recovered — appends it to `dead_letters`, and
**continues the loop without raising**. Valid lines accumulate in `events`. The
function returns a `LoadResult(events, dead_letters)`, so a single corrupt
record can never crash the load or silently vanish: it is captured with enough
context (line number, raw bytes, best-effort id, parser error) to triage or
replay later.

Verified concretely against the planted poison-pill, `evt-0020`: per
`docs/fixture-forensics.md` it sits on **file line 21** (the duplicate
`evt-0002` on line 5 shifts every later event down one line) and is missing its
closing brace. Loading `fixtures/event_sample.jsonl` yields **24 parseable
records and exactly 1 dead-letter** for that line, and the file parses cleanly
before and after it — matching the forensics catalog's per-event verdict and
the "do not let it crash the loader, and do not silently skip it" refusal. The
anomaly-detection test suite and benchmark run over this same loader, which is
why this row — and only this row — is `[Observed]`/`[Benchmarked]` rather than
`[Estimated]`.

**Designed (not yet built).** The production analogue is the **SQS DLQ + replay**
mechanism in `design-pipeline.md` (§"Supporting services", §"Zero-data-loss
mechanism" steps 3–4, and the fixture anomaly table's class 9): parse/validation
failures route to an SQS dead-letter queue with the raw record, Fargate replay
jobs re-drive them after a fix, and idempotent dedupe by `event_id` prevents
double-apply on replay. `DLQDepth` is the CloudWatch alarm. None of that AWS
plumbing exists yet — it is the same *policy* (dead-letter, never crash, never
silently discard, replay after fix) proven locally in the loader, projected onto
production infrastructure that is still designed-not-built. The local
`DeadLetter` dataclass is the concrete, runnable stand-in that demonstrates the
policy is real rather than aspirational.

## 2. What stays human

The decisions below are deliberately kept out of automation. This table is the
**single, complete, de-duplicated** list: it merges the four judgment calls
this stress-test surfaces with the seven previously recorded in
`docs/submission-disclosures.md`'s "What stays human" table, folding overlaps
(notably GDPR/CCPA erasure approval, which appeared in both) into one entry
each. Each row gives the reasoning — why a human, not a rule, owns it.

| Decision | Why it stays human |
|----------|--------------------|
| Compliance sign-off — GDPR/CCPA erasure approval (`evt-0017`), SOC 2 audit review | Legal scope confirmation before an irreversible action: a `delete_all_data` mandate must be scoped so it purges the right subject's data without a mistaken full-account or cross-tenant wipe, and SOC 2-relevant changes need an accountable reviewer. Automating the approval removes the legal accountability the control exists to provide. (Merges the former "GDPR/CCPA erasure approval (`evt-0017`)" entry with the new compliance sign-off decision.) |
| Anomaly-detection threshold tuning | The detection thresholds (e.g. the ADR's 30-min timezone-offset and 5-second clock-skew cutoffs) are **fixture-tuned heuristics, not statistically calibrated for production traffic** — per `docs/adr/0001-timestamp-anomaly-classification-by-signal-not-id.md`, Consequences. Retuning them against real tenant traffic is a judgment call about false-positive vs false-negative cost that must be made by a human who can see the downstream impact, not auto-fitted to a moving distribution. |
| Tenant onboarding exceptions | When a new tenant's traffic profile doesn't fit a standard tier assignment, placing them needs a human read of their expected volume, burst shape, and business tier — an automated default risks assigning a bursty tenant to a shared shard and creating the §1.1 hot-partition failure on day one. |
| Incident triage judgment calls | During a stress-test scenario (e.g. §1.3), choosing **failover vs throttle vs rollback** trades customer impact against cost against data-loss risk in real time. There is no rule that gets this right across contexts; on-call judgment weighing blast radius and business impact owns it — especially given the MVP has no automated cross-region failover to defer to. |
| Quarantine release for `evt-0011` (null `tenant_id`) | Attributing an orphaned, unattributable event requires support investigation; guessing a tenant would corrupt that tenant's data, and defaulting hides a possible SDK misconfiguration or injection. |
| Tenant tier promotion / demotion | A business-relationship and ingest-profile judgment (also the standing mitigation for §1.1). Moving a tenant between Kinesis tiers has cost and isolation consequences a threshold can't weigh. |
| Migration promote-per-tenant | The `[Assumed]` 72h parity gate is checkable, but the promote decision has customer-visible rollback cost, so an engineer signs off per tenant rather than auto-promoting on a green metric. |
| Bot-flag override for enterprise tenants | The bot heuristic (`evt-0012`–`evt-0015` pattern) can false-positive on high-value traffic; excluding a real enterprise tenant's traffic from hot rollups is costly enough that a human confirms the override. |
| Shard-split runbook execution | A capacity change with direct spend impact (the §1.1 hot-partition and §1.2 backpressure mitigation). On-call judgment decides when the `IteratorAge` alarm warrants the split rather than an automated scale action. |
| PII quarantine review (`evt-0007`) | A compliance officer confirms the redaction scope for unexpected PII (`contact_email`/`phone` in a `custom` payload) before it is released — the tool flags, the human decides what is safe to surface. |

Taken together these draw one line: **automation detects, routes, buffers, and
flags; humans own every decision that is irreversible, legally accountable,
cost-bearing, or a real-time trade-off between competing harms.** That line is
also why the cross-region gap in §1.3 is answered by a human runbook rather than
an unbuilt automated failover — the honest MVP keeps the judgment where the
accountability is.
