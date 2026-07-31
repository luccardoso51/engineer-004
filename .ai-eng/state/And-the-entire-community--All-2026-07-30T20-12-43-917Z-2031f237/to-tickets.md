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