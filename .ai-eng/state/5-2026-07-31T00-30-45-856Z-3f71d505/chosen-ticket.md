Title: AI-usage disclosure

Identifier: #5

Description:
What to build: the disclosure describing what Claude produced, what Lucas directed/approved/overrode and where, the per-decision approve/override collaboration model itself, and where Lucas's real experience was used to ground or correct the output.

Blocked by: Anomaly-detection script, tests & benchmark; Design doc

- [ ] States what Claude produced/drafted
- [ ] States what Lucas directed, approved, or overrode, with concrete examples
- [ ] Documents the per-decision approve/override collaboration model itself
- [ ] States where Lucas's real experience (queue-based systems, PostHog as SDK consumer only) was used to ground or correct the output

Labels: none

Acceptance criteria (if any are present in the body or a checklist):
- States what Claude produced/drafted
- States what Lucas directed, approved, or overrode, with concrete examples
- Documents the per-decision approve/override collaboration model itself
- States where Lucas's real experience (queue-based systems, PostHog as SDK consumer only) was used to ground or correct the output

Relevant comments (only ones that change scope or add requirements — skip chit-chat):
none (no comments on the issue)

Linked context (one entry per followed link; "none" if the ticket links to nothing):
--- Anomaly-detection script, tests & benchmark (#2) (https://github.com/luccardoso51/engineer-004/issues/2) ---
Status: CLOSED. Delivers: the detect_anomalies(events) -> list[Anomaly] function (single seam, Python 3.11 stdlib only) plus a thin CLI wrapper extending src/analytics_pipeline/main.py, a unittest suite (one test per confirmed anomaly class from ticket 1, one clean/negative case, one per borderline case), fixture loading that routes the malformed/truncated line (evt-0020) to a dead-letter/parse-failure result instead of crashing, the full suite passing against the real fixture, and a real local benchmark (throughput/latency, raw timing, pass/fail counts) against the full fixture. This is the "artifact that proves execution" the disclosure will need to describe concretely (what Claude produced, what Lucas directed/approved/overrode).

--- Design doc (#3) (https://github.com/luccardoso51/engineer-004/issues/3) ---
Status: CLOSED. Delivers: a ≤4-page redesigned-pipeline architecture doc covering: current-state failure modes (15-30min latency, ~3% loss, crashes) each mapped to a fix; latency budget breakdown summing under 5s; cost breakdown under $50K/mo at 50M+ events/day; phased delivery plan (3-month MVP / 6-month full build, 2 senior engineers); multi-tenant isolation for 500+ tenants; SOC2/GDPR/CCPA controls; zero-data-loss mechanism; burst/spike handling; named AWS services with alternatives considered and rejected; fixture handled anomaly-class by anomaly-class with event_id citations and fixture checksum; migration/cutover plan with rollback trigger; trade-offs/risks section; explicit call-outs of assumptions Lucas had to make. Notably, this doc's own acceptance criteria already require it to draw on Lucas's real queue-based backend experience where applicable and reference PostHog only as an SDK consumer — directly overlapping with what ticket #5's disclosure must also state.