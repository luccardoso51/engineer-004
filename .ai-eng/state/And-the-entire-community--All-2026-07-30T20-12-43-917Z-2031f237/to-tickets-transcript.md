Spec:
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

---

Assistant:
I explored the repo (fixtures/event_sample.jsonl, brief.md, scoring_rubric.md, existing src/analytics_pipeline/main.py + tests/test_main.py scaffolding, and the .ai-eng config pointing at a GitHub tracker).

One thing worth flagging before the breakdown: I read the actual fixture (24 events). It does NOT cleanly match the 9-class placeholder taxonomy from the spec. What's actually planted looks like: duplicate event_id (evt-0002 twice), received_at earlier than ts (evt-0005), a ~1hr ts/received_at skew (evt-0006), a ts a full year in the future (evt-0016), PII (email+phone) sitting in a custom event's properties (evt-0007), a schema-drifted event using different field names and missing ts (evt-0009), a null tenant_id (evt-0011), a same-anonymous_id/same-referrer burst of 4 page views in ~50ms (evt-0012-15, bot-shaped), a truncated/malformed JSON line that would crash a naive parser (evt-0020), and a privacy_request/GDPR-delete event (evt-0017) that isn't an anomaly per se but has to be handled correctly. No tenant-spoofing or cross-tenant-leakage or volume-drop-to-zero cases visible in this static sample. So ticket 1 below is now "go confirm/correct the taxonomy against the real data," not "assume nine classes."

Proposed breakdown, 7 tickets:

1. Fixture forensics & anomaly taxonomy
   Blocked by: None — can start immediately
   Delivers: the real, event_id-cited catalog of what's actually planted in fixtures/event_sample.jsonl (superseding the placeholder 9-class list), the fixture's sha256 checksum, and the "at least three things not to take at face value" write-up the brief explicitly requires. This is the ground truth every other ticket cites.

2. Anomaly-detection script, tests & benchmark
   Blocked by: 1
   Delivers: the detect_anomalies(events) -> list[Anomaly] seam plus CLI wrapper, extending the existing main.py/load_jsonl scaffolding (which currently doesn't survive the malformed line at evt-0020 — that's the prefactor this ticket needs to fix first), a unittest suite with one case per confirmed anomaly class plus a clean case plus the borderline cases from ticket 1, run against the real fixture, and an actual local benchmark (throughput/latency/pass-fail counts) — the run that ticket 4's Tier 3/4 claims will point to.

3. Design doc
   Blocked by: 1
   Delivers: the ≤4-page doc — current-state problems mapped to fixes, named AWS architecture (ingestion, hot/low-latency path, cold/replayable path), latency budget summing under 5s, cost budget under $50K/mo, 3mo/6mo phased plan for a 2-engineer team, 500+-tenant isolation strategy, SOC2/GDPR/CCPA controls, zero-loss delivery/dedupe/DLQ mechanism, multi-tenant burst handling, migration/rollback plan, trade-offs — including the anomaly-class-by-class fixture handling with event_id citations the brief requires, grounded in Lucas's real queue-system experience and an accurate (SDK-consumer-only) framing of PostHog.

4. Evidence log & number-provenance pass
   Blocked by: 2, 3
   Delivers: the evidence log assigning a proof tier to every substantive claim, with Tier 3/4 reserved for entries that trace to ticket 2's real benchmark output — plus the observed/estimated/benchmarked/assumed tag applied to every number across the design doc, script output, and the log itself.

5. AI-usage disclosure
   Blocked by: 2, 3
   Delivers: the disclosure describing what was proposed vs. what Lucas approved/overrode across the script and design doc, the per-decision approve/override collaboration model itself, and where Lucas's real experience corrected or grounded the output.

6. Failure-modes & what-stays-human
   Blocked by: 2, 3
   Delivers: the architecture stress-test (hot-partition tenants, ingestion backpressure, cross-region failover, poison-pill/malformed events — tying back to how ticket 2's script actually handles evt-0020) and the section naming judgment calls that stay human (threshold tuning, tenant onboarding exceptions, compliance sign-off, incident triage).

7. Final packet assembly & consistency check
   Blocked by: 4, 5, 6
   Delivers: the packet as one internally-consistent whole — page-limit check on the design doc only, checksum stated, every design-doc number traceable to an evidence-log entry, artifacts (script/tests/log/disclosure/failure-modes) kept separate from the page count, and a pre-screen pass if scripts/validate_submission.py is available.

Questions for you:
- Does the granularity feel right, or should any of 4/5/6 (the three closing sections) be merged into fewer tickets since they're individually small?
- Any objection to ticket 1 overriding the spec's placeholder taxonomy with what I actually found in the fixture?
- Blocking edges look right to you — 2 and 3 as the frontier after 1, then 4/5/6 fan in from both, then 7 closes it out?

User:
explain me why ticket 1 overiders the spec?

---

Assistant:
Because the spec's taxonomy was explicitly marked as a guess, not a finding.

Look at how the spec itself frames it, in two places:

1. Implementation Decisions: "Since the fixture's exact contents haven't been inspected in this conversation, the working taxonomy assumed for design purposes... This is flagged as an assumption pending real fixture review, not a confirmed fact."
2. Further Notes: "The actual challenge fixture... has not been inspected as part of producing this spec. The anomaly taxonomy... should be corrected against the real fixture before the script and evidence log are finalized."

So the spec didn't assert nine specific classes as fact — it asserted them as a placeholder to be checked. When I did step 2 of the process (explore the codebase) I opened fixtures/event_sample.jsonl, which was sitting right there in the repo, and read all 24 events. That's the "real fixture review" the spec was waiting on.

What I found doesn't match the placeholder list point for point:

- Matches: duplicate event_id, PII in a non-PII field, missing required schema field.
- Doesn't match: the placeholder assumed "tenant_id mismatch or spoofing" — the fixture has a null tenant_id (evt-0011), not spoofing. It assumed "volume drop-to-zero" — impossible to observe in a static 24-event snapshot, there's no time series to go silent. It assumed "cross-tenant data leakage" — I don't see that pattern in the sample. It assumed generic "impossible field values (negative counts, future timestamps)" — what's actually there is more specific: one event a full year in the future (evt-0016) and a separate case where received_at is earlier than ts (evt-0005), which are two different failure shapes, not one bucket.
- Not in the placeholder at all: a truncated/malformed JSON line (evt-0020) that would throw on json.loads and crash the existing load_jsonl scaffolding rather than just flag an anomaly — that's a parse-failure/DLQ case, structurally different from the others. And a privacy_request/GDPR-delete event (evt-0017), which isn't an anomaly to flag but is a required-behavior case the design has to handle correctly.

Why this matters enough to be its own ticket rather than a footnote: the brief (brief.md, "Ground It in the Sample Data") is explicit that "it contains seeded issues... We know exactly what is planted in it, so your reading of the data tells us immediately whether the analysis is real," and the scoring rubric lists "conclusions that treat a planted issue as clean signal" as one of the fastest ways to lose. If ticket 2 builds detect_anomalies against the placeholder nine classes instead of what's actually in the file, the script would silently mis-handle or miss evt-0020 and evt-0005/0006/0016's distinct skew shapes — exactly the failure mode the brief is testing for. So ticket 1 exists to lock in the corrected, event_id-cited taxonomy before any code or doc content is written against it, per this being an explicit assumption in the spec flagged for correction, and per user story 30 ("assumptions I had to make... called out explicitly... so I can correct them before submission").

Does that reasoning hold up for you, or do you want to keep the original nine-class list as the target and treat my fixture read as a side note instead?

User:
I understand, makes sense. Looks like this was placed by the interviewer  to trick us

---

Assistant:
Exactly — and brief.md says as much outright: "it contains seeded issues - not everything in it should be taken at face value... We know exactly what is planted in it, so your reading of the data tells us immediately whether the analysis is real." Reviewers hold the private key to what's seeded (per scoring_rubric.md's "Fixture Verification" section), so treating the placeholder taxonomy as gospel instead of actually reading the file would have been exactly the trap — a candidate optimizing for a generic answer instead of engaging with the specific data in front of them.

That's the whole reason ticket 1 exists as its own gate before the script or doc get written.

Still open from before, since we only resolved the ticket-1 question:

- Merge any of tickets 4/5/6 (evidence log, AI disclosure, failure-modes/what-stays-human) since they're individually small? Or keep them separate?
- Are the blocking edges right — 1 alone at the front, 2 and 3 as the parallel frontier after it, 4/5/6 fanning in from both 2 and 3, then 7 closing it out?

Or are you happy with the breakdown as posted and want me to move to publishing it?

User:
yes looks good

---

Assistant:
```tickets-approved
# Tickets: SingleGrain engineer-004 submission packet

Builds the complete, submission-ready packet for SingleGrain's "Real-Time Analytics Pipeline" challenge: a ≤4-page design doc, a working fixture anomaly-detection script with tests and a real local benchmark, an evidence log, an AI-usage disclosure, and failure-modes / what-stays-human sections — all built under an approve/override collaboration model and grounded in the actual challenge fixture (fixtures/event_sample.jsonl), not the placeholder assumptions in the original spec.

Work the frontier: any ticket whose blockers are all done. Tickets 2 and 3 can run in parallel once ticket 1 is done; tickets 4, 5, 6 can run in parallel once both 2 and 3 are done.

## Fixture forensics & anomaly taxonomy

What to build: the real, event_id-cited catalog of what's actually planted in fixtures/event_sample.jsonl, correcting the spec's placeholder nine-class taxonomy (which the spec itself flagged as an unverified assumption) against what's actually in the file, plus the fixture's sha256 checksum and the brief-required write-up of items that should not be taken at face value.

Blocked by: None — can start immediately

- [ ] sha256 checksum of fixtures/event_sample.jsonl computed and recorded
- [ ] Every event in the fixture reviewed; anomaly signals actually present cataloged and cited by event_id
- [ ] Corrected anomaly taxonomy documented, noting where it diverges from the original placeholder list and why
- [ ] At least three fixture items identified that should not be taken at face value, with reasoning per item
- [ ] Findings written as a standalone artifact that later tickets can reference

## Anomaly-detection script, tests & benchmark

What to build: the detect_anomalies(events) -> list[Anomaly] seam plus a thin CLI wrapper, extending the existing src/analytics_pipeline/main.py scaffolding, with a unittest suite and a real local benchmark run against the fixture — the artifact that proves execution, not just design.

Blocked by: Fixture forensics & anomaly taxonomy

- [ ] detect_anomalies(events) -> list[Anomaly] implemented as the single seam, Python 3.11 stdlib only
- [ ] Thin CLI wrapper reads the fixture file and prints/serializes results keyed by event_id
- [ ] Fixture loading handles the malformed/truncated line (evt-0020) without crashing, routing it to a dead-letter/parse-failure result instead
- [ ] unittest suite with one test per confirmed anomaly class from ticket 1, one clean/negative case, and one test per borderline case identified in ticket 1's face-value list
- [ ] Full test suite passes against the real fixture
- [ ] Local benchmark executed for real: throughput and latency of detect_anomalies against the full fixture, with raw timing and pass/fail counts captured

## Design doc

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

## Evidence log & number-provenance pass

What to build: the evidence log assigning a proof tier to every substantive claim in the packet, with the highest tiers reserved for claims that trace to the real benchmark run, plus the observed/estimated/benchmarked/assumed tag applied consistently to every number across the design doc, script output, and the log itself.

Blocked by: Anomaly-detection script, tests & benchmark; Design doc

- [ ] Every substantive claim in the packet assigned a proof tier per scoring_rubric.md's tiering scheme
- [ ] Tier 3/4 entries reserved for, and traced to, the actual local benchmark run output from ticket 2
- [ ] Every quantitative figure across the design doc, script output, and the evidence log itself tagged observed/estimated/benchmarked/assumed
- [ ] Design doc's latency/throughput/cost claims cross-checked against evidence log entries for consistency

## AI-usage disclosure

What to build: the disclosure describing what Claude produced, what Lucas directed/approved/overrode and where, the per-decision approve/override collaboration model itself, and where Lucas's real experience was used to ground or correct the output.

Blocked by: Anomaly-detection script, tests & benchmark; Design doc

- [ ] States what Claude produced/drafted
- [ ] States what Lucas directed, approved, or overrode, with concrete examples
- [ ] Documents the per-decision approve/override collaboration model itself
- [ ] States where Lucas's real experience (queue-based systems, PostHog as SDK consumer only) was used to ground or correct the output

## Failure-modes & what-stays-human

What to build: the architecture stress-test covering hot-partition tenants, ingestion backpressure, cross-region failover, and poison-pill/malformed events, plus the section naming which decisions and judgment calls stay human rather than automated.

Blocked by: Anomaly-detection script, tests & benchmark; Design doc

- [ ] Failure-modes section covers hot-partition tenants, ingestion backpressure, cross-region failover, and poison-pill/malformed events, tied to how the ticket 2 script actually handles evt-0020
- [ ] What-stays-human section names specific decisions kept out of automation (tenant onboarding exceptions, anomaly-detection threshold tuning, compliance sign-off, incident triage judgment calls) with reasoning

## Final packet assembly & consistency check

What to build: the packet assembled as one internally-consistent whole, ready for submission per the brief's format requirements.

Blocked by: Evidence log & number-provenance pass; AI-usage disclosure; Failure-modes & what-stays-human

- [ ] Design doc confirmed ≤4 pages, diagrams excluded from count
- [ ] Script, tests, benchmark output, evidence log, AI disclosure, and failure-modes/what-stays-human all present as separate artifacts alongside the doc
- [ ] Every numeric claim in the design doc has a corresponding evidence-log entry with matching provenance tag
- [ ] Fixture checksum consistent across design doc and evidence log
- [ ] scripts/validate_submission.py pre-screen run if available, issues resolved
- [ ] Packet packaged ready for submission per brief.md format (PDF or Markdown)
```