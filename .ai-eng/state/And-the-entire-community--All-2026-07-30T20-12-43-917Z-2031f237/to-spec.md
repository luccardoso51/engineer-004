## Problem Statement

Lucas is applying to SingleGrain's system-design challenge "Real-Time Analytics Pipeline" (engineer-004). The challenge asks him to redesign a martech analytics pipeline that currently has 15–30 minute latency, ~3% event loss, and is crash-prone, into a system that delivers <5s real-time analytics on AWS at 50M+ events/day across 500+ tenants, within a $50K/mo budget, a 3-month MVP / 6-month full-build timeline, a 2-senior-engineer team, SOC2/GDPR/CCPA compliance, and zero data loss.

A design doc alone would read as theoretical. Lucas's direct experience is adjacent, not identical, to this problem — he has built queue-based backend systems and has used PostHog only as an SDK consumer, not as an operator of ingestion infrastructure at this scale. Submitting a polished architecture without demonstrating hands-on rigor, without being explicit about which numbers are real versus estimated, and without disclosing how AI was used to produce the work risks reading as unsubstantiated or dishonest about its own confidence level — a particular risk for a challenge that is likely evaluating engineering judgment as much as it is evaluating the architecture itself.

## Solution

Produce one complete, submission-ready packet, built under an approve/override collaboration model (Claude proposes each architectural and technical decision with explicit reasoning; Lucas approves or overrides it before it's treated as final). The packet consists of:

1. A ≤4-page design doc for the redesigned pipeline, covering the current-state problems, target architecture, latency/loss/cost budget, phased delivery plan, and compliance posture.
2. A working, runnable anomaly-detection script (Python 3.11, standard library only) with a `unittest` suite, exercised against the challenge's fixture data.
3. An evidence log that assigns each claim a proof tier and states what substantiates it.
4. Every quantitative claim in the packet labeled by provenance: observed, estimated, benchmarked, or assumed.
5. An AI-usage disclosure describing what Claude produced, what Lucas directed/approved/overrode, and where Lucas's real experience was used to ground or correct the output.
6. A failure-modes section for the proposed architecture.
7. A "what stays human" section identifying the decisions and judgment calls in this design that should not be delegated to AI or automation, now or in production.

The packet is meant to be internally consistent: the design doc's latency/throughput/cost claims should trace back to the evidence log, and the evidence log's Tier 3/4 (highest-rigor) entries should trace back to the actual local benchmark run of the anomaly-detection script against the fixture — not to assertion.

## User Stories

1. As a challenge reviewer, I want a design doc that is ≤4 pages, so that I can evaluate the architecture without wading through unnecessary volume.
2. As a challenge reviewer, I want the design doc to name the current pipeline's specific failure modes (15–30min latency, ~3% loss, crashes) and map each to a specific fix in the new design, so that I can verify the redesign actually addresses the stated problem rather than being generic.
3. As a challenge reviewer, I want an explicit latency budget breakdown (ingestion → processing → storage → query) that sums to under 5 seconds, so that I can sanity-check the <5s real-time claim.
4. As a challenge reviewer, I want an explicit cost breakdown that fits within $50K/mo at 50M+ events/day, so that I can verify the design is economically realistic, not just technically plausible.
5. As a challenge reviewer, I want a phased delivery plan mapped to 3 months (MVP) and 6 months (full system) with 2 senior engineers, so that I can judge whether the scope is deliverable by the stated team.
6. As a challenge reviewer, I want the multi-tenant isolation strategy for 500+ tenants made explicit, so that I can assess data-isolation and noisy-neighbor risk.
7. As a challenge reviewer, I want the SOC2/GDPR/CCPA compliance controls (encryption, data residency, right-to-deletion, audit logging, tenant data segregation) named explicitly, so that I can verify compliance wasn't an afterthought.
8. As a challenge reviewer, I want the zero-data-loss guarantee backed by a specific delivery/idempotency mechanism (e.g., at-least-once delivery, dedupe, DLQ, replay), so that the "zero loss" claim is falsifiable, not just asserted.
9. As Lucas, I want each architectural decision proposed with reasoning and trade-offs before I approve it, so that I retain ownership of the design and can catch mismatches with my real experience.
10. As Lucas, I want to be able to override any proposed decision, so that the final design reflects my actual engineering judgment, not just the AI's default recommendation.
11. As Lucas, I want the design to draw on my real experience with queue-based backend systems where genuinely applicable, so that the doc reflects authentic depth rather than borrowed knowledge.
12. As Lucas, I want PostHog referenced only in the way I've actually used it (as an SDK consumer), so that I don't misrepresent my level of operational experience with it.
13. As a challenge reviewer, I want a working anomaly-detection script rather than pseudocode, so that I can verify Lucas can execute, not just design.
14. As a challenge reviewer, I want the script restricted to Python 3.11 standard library, so that I can run it without dependency friction.
15. As a challenge reviewer, I want a `unittest` suite accompanying the script, so that I can verify correctness claims myself rather than trust them blindly.
16. As a challenge reviewer, I want the script to process the actual fixture provided with the challenge, so that its output is grounded in the same data I'll be evaluating against.
17. As a challenge reviewer, I want each detected anomaly reported against its `event_id`, so that I can trace every flag back to a specific record.
18. As a challenge reviewer, I want the script to address each of the fixture's nine identified anomaly classes, so that I can confirm full coverage rather than partial handling.
19. As Lucas, I want the fixture's own labels/comments treated as claims to verify rather than ground truth, so that I don't propagate a planted error in the fixture into my submission.
20. As a challenge reviewer, I want a section explicitly flagging fixture items that should not be taken at face value (e.g., mislabeled anomalies, ambiguous edge cases, contradictory metadata), so that I can see Lucas questioned the input rather than trusting it blindly.
21. As Lucas, I want an evidence log that assigns a proof tier to every substantive claim in the packet, so that a reviewer can see which claims are rigorously substantiated versus reasoned estimates.
22. As a challenge reviewer, I want the evidence log's highest tiers (3/4) reserved for claims backed by an actual local run of the script against the fixture, so that "rigorous" isn't just a label.
23. As Lucas, I want to actually run the benchmark locally (throughput, latency, correctness against fixture) rather than estimate it, so that the Tier 3/4 claims in the evidence log are true.
24. As a challenge reviewer, I want every numeric claim in the packet tagged as observed, estimated, benchmarked, or assumed, so that I can weight each number appropriately instead of treating them as uniformly authoritative.
25. As a challenge reviewer, I want an AI-usage disclosure stating what Claude authored, what Lucas approved or overrode, and where, so that the collaboration is transparent rather than hidden.
26. As a challenge reviewer, I want a failure-modes section for the proposed architecture (e.g., hot-partition tenants, ingestion backpressure, cross-region failover, poison-pill events), so that I can see the design was stress-tested on paper.
27. As a challenge reviewer, I want a "what stays human" section naming the decisions that should not be automated away (e.g., tenant onboarding exceptions, anomaly-detection threshold tuning, compliance sign-off, incident triage judgment calls), so that I can assess Lucas's judgment about the limits of automation.
28. As Lucas, I want the packet to stay within the 4-page limit for the design doc while keeping the script/tests/evidence log as separate artifacts, so that page-limit compliance doesn't force me to cut substance from the supporting evidence.
29. As a challenge reviewer, I want the design doc's architecture choices to be named AWS services (not generic placeholders), so that I can evaluate concrete technical decisions.
30. As Lucas, I want assumptions I had to make (e.g., about the exact fixture format or the precise nine anomaly classes) called out explicitly rather than silently baked into the design, so that I can correct them before submission if they're wrong.
31. As a challenge reviewer, I want to see how the design handles multi-tenant burst traffic (a subset of tenants spiking well above baseline), since this is a common real-world martech failure mode not always covered by average-throughput numbers.
32. As Lucas, I want the collaboration model itself (approve/override, per-decision) documented in the AI-usage disclosure, so that the process is legible to a reviewer evaluating how I work with AI tools.

## Implementation Decisions

- **Single seam for the testable artifact**: the anomaly-detection script exposes one primary entry point — a `detect_anomalies(events) -> list[Anomaly]`-style function (plus a thin CLI wrapper that reads the fixture file and prints/serializes results by `event_id`). All `unittest` coverage and the local benchmark run go through this one seam. No separate seams are introduced per anomaly class; each class is a case fed through the same function, keeping the packet's testing surface to the minimum needed for Tier 3/4 rigor.
- **Anomaly taxonomy**: the challenge fixture is understood to define nine anomaly classes. Since the fixture's exact contents haven't been inspected in this conversation, the working taxonomy assumed for design purposes (to be confirmed/corrected against the real fixture before finalizing) covers: duplicate `event_id` (idempotency violation), out-of-order/clock-skew timestamps, missing required schema fields, tenant_id mismatch or spoofing, per-tenant volume spike (bot/burst), per-tenant volume drop-to-zero (silent ingestion failure), impossible field values (negative counts, future timestamps), cross-tenant data leakage, and unexpected PII in a non-PII field. This is flagged as an assumption pending real fixture review, not a confirmed fact.
- **Fixture skepticism as a first-class step**: before the script is finalized, the fixture's own annotations/labels are treated as claims to verify, not ground truth — the packet includes a short written pass identifying fixture items (e.g., ambiguous labels, internally inconsistent metadata, or a possible planted mislabel) that should not be taken at face value, separate from the script's own detection output.
- **Architecture direction for the design doc**: stream ingestion via a managed, horizontally-scalable service (e.g., Kinesis Data Streams, one stream/shard-group per tenant tier rather than per tenant, to bound shard count at 500+ tenants); stateless stream processors (Lambda or Fargate) performing validation, dedup, and anomaly flagging inline; a hot path to a low-latency store for the <5s query requirement and a cold path to S3 for durable, replayable storage and batch analytics. Exact service choices, shard/partition strategy, and processor concurrency are proposed-with-reasoning items for Lucas to approve or override individually, not pre-decided here.
- **Zero-data-loss mechanism**: at-least-once delivery from ingestion through processing, idempotent writes keyed by `event_id` for dedup, and a dead-letter path for events that fail validation/processing, with replay capability from the durable store — proposed as the mechanism that makes the "zero loss" claim falsifiable and testable rather than asserted.
- **Multi-tenant isolation and compliance**: tenant-scoped partitioning/keying to prevent cross-tenant leakage, encryption in transit and at rest, tenant-level data deletion path for CCPA/GDPR right-to-deletion, and audit logging for SOC2 — each named explicitly in the design doc rather than referenced generically.
- **Cost and delivery phasing**: the $50K/mo budget and 3-month MVP / 6-month full-build timeline with 2 senior engineers are treated as hard constraints the architecture must fit, driving preference toward managed AWS services over self-operated infrastructure to keep the 2-engineer team viable.
- **Proof-tier structure for the evidence log**: a tiering scheme (e.g., Tier 1 = assumption/industry-standard reasoning, Tier 2 = estimated from stated constraints, Tier 3 = derived from a documented calculation, Tier 4 = directly observed from the actual local benchmark run of the script against the fixture) is applied per claim, with Tier 3/4 reserved for claims that trace to the real benchmark, not to the design doc's architectural reasoning.
- **Number labeling convention**: every quantitative figure in the packet carries an inline provenance tag — observed, estimated, benchmarked, or assumed — applied consistently across the design doc, evidence log, and script output.

## Testing Decisions

- A good test here exercises the `detect_anomalies` seam's external behavior — given a fixture event (or a constructed minimal event matching one of the nine classes), assert the correct anomaly class and `event_id` are flagged (or correctly not flagged for clean events) — not internal helper functions or intermediate data structures.
- The `unittest` suite covers, at minimum, one representative case per anomaly class in the fixture's taxonomy (nine positive cases), at least one clean/negative case that should produce no flags, and any borderline/ambiguous cases identified during the fixture-skepticism pass (to lock in Lucas's stated judgment about them rather than leave the ambiguity implicit).
- The local benchmark (throughput and latency of `detect_anomalies` against the full fixture, run for real rather than estimated) is what elevates the corresponding evidence-log entries to Tier 3/4; the benchmark run's raw output (timing, pass/fail counts) is what the evidence log entry points to as substantiation.
- No prior art exists in this repo/context for this pattern (this is a net-new, standalone artifact for a job-application challenge, not an addition to an existing test suite) — the suite follows standard Python `unittest` conventions (one test class, one method per case, descriptive method names naming the anomaly class under test).

## Out of Scope

- Actual AWS deployment or infrastructure-as-code (Terraform/CDK) — the design doc specifies the architecture; nothing is provisioned.
- Production-grade pipeline code beyond the fixture anomaly-detection script — the script is a scoped, fixture-proven artifact, not the full ingestion/processing system described in the design doc.
- Use of real tenant/production data — only the challenge's fixture data is used.
- An actual SOC2 audit or formal compliance certification — the packet describes compliance controls, it does not obtain certification.
- Front-end/dashboard work, alerting integrations, or on-call runbooks beyond what's needed for the failure-modes section.
- Full capacity planning/provisioning for all 500+ tenants — the design doc addresses the isolation and scaling strategy, not a tenant-by-tenant rollout plan.
- Interview preparation or other application materials beyond this packet.

## Further Notes

- **Non-interactive process note**: this spec was produced without an interactive seam/scope check with Lucas (per the operating constraints of this run). The single-seam choice for the anomaly-detection script and the assumed nine-class taxonomy should be treated as proposals for Lucas to confirm or override, consistent with the approve/override model requested for the rest of the work.
- **Fixture access gap**: the actual challenge fixture (its schema, its nine anomaly classes, and any embedded labels/annotations) has not been inspected as part of producing this spec. The anomaly taxonomy and fixture-skepticism approach above are best-effort placeholders based on common martech-analytics failure patterns and should be corrected against the real fixture before the script and evidence log are finalized.
- **Grounding in real experience**: per the request, the design doc should lean on Lucas's queue-based backend experience where it's genuinely analogous (e.g., delivery guarantees, backpressure, dedup/idempotency reasoning) and should reference PostHog only as an SDK consumer — it should not imply operational experience running a PostHog-like ingestion platform, since that would misrepresent Lucas's background.
- **No fixed deadline**: work can proceed iteratively through the approve/override cycle without time pressure; this spec does not impose a delivery date.
- **Page-limit interaction**: the ≤4-page constraint applies to the design doc specifically; the script, tests, evidence log, AI-usage disclosure, failure-modes, and what-stays-human sections are treated as accompanying artifacts rather than counted against that limit, unless Lucas overrides this interpretation.