# Submission Disclosures

Per `brief.md` submission packet items #5–7 and `SCORING.md` AI Usage / Failure Modes sections. Excluded from the 4-page written-answer limit.

## AI usage disclosure

| Item | Detail |
|------|--------|
| Tools used | Claude (primary drafting model) + Cursor (Composer agent, token-exhaustion fallback that did real implement-cycle work), both orchestrated by Nemo — a CLI pipeline Lucas built himself |
| AI helped with | Structuring the design doc against the brief checklist; drafting Mermaid diagram; cross-referencing `docs/fixture-forensics.md` event_ids; cost/latency table formatting |
| Human decisions | Architecture choices (Kinesis tiering over MSK, parallel-run migration, DynamoDB dedupe key); anomaly handling policy (six "not at face value" refusals); throughput/cost arithmetic; phased MVP scope; compliance workflow requiring human approval |
| Human verification | Ran `shasum -a 256 fixtures/event_sample.jsonl`; ran full `pytest` suite; re-derived cost line items and shard math; read every fixture event in forensics doc against design table |
| Known weak spots | Latency and AWS cost figures are `[Estimated]` — no load test or AWS bill yet; EU residency deferred; bot detection is heuristic-only in MVP |

The summary table above is the at-a-glance version. The subsections below expand it: the collaboration model that produced this submission, a concrete drafted-vs-directed breakdown, and where real engineering experience corrected the AI's output.

### Collaboration model

Every artifact in this repo was produced under one explicit rule, locked in at the start of the project: **Claude proposes the architecture and every major decision with its reasoning; Lucas explicitly reviews and either approves or overrides each one before it is treated as final.** This was chosen deliberately over the two alternatives — Lucas hand-driving every decision (too slow, wastes the model), or Claude silently deciding routine matters (no real review, and the reasoning disappears). The middle path keeps a human accountable for every decision that matters while letting the model do the drafting.

The mechanism that runs this model is **Nemo, a CLI orchestration tool Lucas built himself** — not a third-party product. Nemo drives a staged pipeline: `grill → spec → tickets → per-ticket implement-prep grilling → implement → verify`. Each stage forces a decision point back to Lucas before the next begins. Claude is the primary model; Cursor is configured as an automatic fallback for when Claude's token budget is exhausted. The pipeline itself is the operating artifact that proves the collaboration model is real rather than performative: the approve/override checkpoints are structural, not a story told after the fact. This disclosure, and the transcripts behind it, are the audit trail.

### What Claude drafted vs. what Lucas directed, approved, or overrode

**What Claude produced (drafted):** the full architecture doc `docs/design-pipeline.md` (tiered Kinesis backbone, hybrid Lambda/Fargate consumers, split ElastiCache/DynamoDB hot tier, DynamoDB dedupe, parallel-run migration, all nine fixture anomaly classes plus `evt-0017` compliance routing with `event_id` citations); the detection code `src/analytics_pipeline/anomalies.py`, `loader.py`, and the updated `main.py`; the `unittest` suite; `scripts/benchmark.py`; the ADR `docs/adr/0001-timestamp-anomaly-classification-by-signal-not-id.md`; `docs/evidence-log.md`; `docs/fixture-forensics.md`; and this disclosure file itself.

**What Lucas directed, approved, or overrode (with concrete examples):**

- **Reviewed approvals, not rubber-stamps.** Lucas approved essentially every lettered recommendation Claude proposed — Kinesis backbone, split hot tier, tiered streams, hybrid compute, the MVP scope for the design doc — but only *after* asking pushback questions first, e.g. "why is (a) more recommended than (c)?" and "is this permitted in the challenge rules?". The approvals followed genuine per-decision interrogation, which is the difference between review and blind sign-off.
- **Directed (not merely approved) #1 — preserving governance docs.** Mid-way through the anomaly-detection ticket, Lucas stopped the flow — "before we continue, I'm horrified about this... these docs are very important, it should be in the repo" — directing that the challenge's scoring and governance material be preserved rather than dropped as the pipeline reshuffled files. `scoring_rubric.md` sits in the repo as the direct result; the top-level `SCORING.md` it and `brief.md` reference (via `../../SCORING.md`) is the shared challenge-framework doc that defines the evidence tiers this submission is graded against.
- **Directed (not merely approved) #2 — the timestamp ADR.** Lucas explicitly directed that the timestamp-anomaly-classification trade-off be captured as a standalone ADR "somewhere that i can check later," because "the interviewer may ask later." That instruction produced `docs/adr/0001-timestamp-anomaly-classification-by-signal-not-id.md`; it would not exist otherwise.
- **Tooling reality.** Claude was the primary drafting model throughout. Cursor was configured as an automatic fallback and *actually fired* during implement-cycle gap-closing and code-review passes when Claude's token budget ran out — it did real work (checksum/label fixes, scaffolding of `docs/evidence-log.md` and this disclosure file, CCPA controls), not just sitting configured-but-unused. Both were orchestrated by Nemo.

### Where Lucas's real experience grounded or corrected the output

Lucas's genuine background is **queue-based backend work** (RabbitMQ-style messaging: backpressure, at-least-once delivery, idempotent handlers) and **hands-on PostHog experience strictly as an SDK-integrating consumer** — never as a builder of ingestion or streaming internals. This boundary is stated up front in the design doc's `Author context` line and is enforced through evidence-tier discipline: no Tier-4 "I've built this before" claims are made about pipeline internals, and every pipeline-specific throughput/latency/cost number is labeled `[Estimated]` or `[Assumed]` unless it was locally benchmarked against the fixture (as the anomaly-detection script's timing was).

The concrete place this real experience corrected and grounded the AI-drafted architecture is the ingestion section of `docs/design-pipeline.md`, which reframes the Kinesis backbone through a RabbitMQ analogy drawn from Lucas's own systems:

> "This mirrors a RabbitMQ topology: Gateway is the exchange, Kinesis shards are durable queues with backpressure, and consumers ack only after idempotent side-effects — the pattern that eliminated message loss in prior queue-based systems."

That passage is not a generic restatement of streaming theory — it is Lucas mapping a proven, hands-on pattern onto Claude's proposed AWS topology, which is why the zero-data-loss mechanism is framed the way it is. PostHog, by contrast, appears in the docs only as an SDK-consumer reference point, never as evidence that Lucas has operated ingestion infrastructure.

## Failure modes & what stays human

Moved to its own operating artifact: see **`docs/failure-modes.md`** for the
architecture stress-test (hot-partition tenants, ingestion backpressure,
cross-region failover, poison-pill/malformed events) and the single merged
"What stays human" table. It is kept there so the packet carries one
authoritative version of this analysis rather than two divergent copies.
