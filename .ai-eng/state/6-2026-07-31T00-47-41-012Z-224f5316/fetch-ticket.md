Title: Failure-modes & what-stays-human

Identifier: #6

Description:
What to build: the architecture stress-test covering hot-partition tenants, ingestion backpressure, cross-region failover, and poison-pill/malformed events, plus the section naming which decisions and judgment calls stay human rather than automated.

Blocked by: Anomaly-detection script, tests & benchmark; Design doc

- [ ] Failure-modes section covers hot-partition tenants, ingestion backpressure, cross-region failover, and poison-pill/malformed events, tied to how the ticket 2 script actually handles evt-0020
- [ ] What-stays-human section names specific decisions kept out of automation (tenant onboarding exceptions, anomaly-detection threshold tuning, compliance sign-off, incident triage judgment calls) with reasoning

Labels: none

Acceptance criteria (if any are present in the body or a checklist):
- Failure-modes section covers hot-partition tenants, ingestion backpressure, cross-region failover, and poison-pill/malformed events, tied to how the ticket 2 script actually handles evt-0020
- What-stays-human section names specific decisions kept out of automation (tenant onboarding exceptions, anomaly-detection threshold tuning, compliance sign-off, incident triage judgment calls) with reasoning

Relevant comments (only ones that change scope or add requirements — skip chit-chat):
none (no comments on the issue)

Linked context (one entry per followed link; "none" if the ticket links to nothing):
--- #2 Anomaly-detection script, tests & benchmark (https://github.com/luccardoso51/engineer-004/issues/2) — CLOSED ---
Delivers: the detect_anomalies(events) -> list[Anomaly] seam plus a thin CLI wrapper (extending src/analytics_pipeline/main.py), a unittest suite, and a real local benchmark run against the fixture. Key point for this ticket: fixture loading must handle the malformed/truncated line (evt-0020) without crashing, routing it to a dead-letter/parse-failure result instead of failing — this is the concrete behavior ticket #6's failure-modes section needs to cite when describing how evt-0020 (poison-pill/malformed event) is actually handled. Status: CLOSED (done), so this behavior should exist in the codebase to reference.

--- #3 Design doc (https://github.com/luccardoso51/engineer-004/issues/3) — CLOSED ---
Delivers: the ≤4-page redesigned-pipeline doc covering architecture, scale/reliability/migration, and trade-offs/risks, including named AWS services with alternatives, latency/cost budgets, phased delivery plan, multi-tenant isolation (500+ tenants), SOC2/GDPR/CCPA compliance controls, zero-data-loss mechanism (at-least-once delivery, idempotent dedupe by event_id, DLQ, replay), multi-tenant burst/spike handling, fixture anomaly-class-by-anomaly-class handling with event_id citations, migration/cutover plan, and trade-offs/risks. This is the governing architecture doc that ticket #6's failure-modes stress-test and what-stays-human section must build on top of (e.g., DLQ/replay mechanism for poison-pill events, multi-tenant isolation for hot-partition tenants, phased build for cross-region failover). Status: CLOSED (done), so this doc should already exist in the repo to reference directly.