Title: Evidence log & number-provenance pass

Identifier: #4

Description:
What to build: the evidence log assigning a proof tier to every substantive claim in the packet, with the highest tiers reserved for claims that trace to the real benchmark run, plus the observed/estimated/benchmarked/assumed tag applied consistently to every number across the design doc, script output, and the log itself.

Blocked by: Anomaly-detection script, tests & benchmark; Design doc

- [ ] Every substantive claim in the packet assigned a proof tier per scoring_rubric.md's tiering scheme
- [ ] Tier 3/4 entries reserved for, and traced to, the actual local benchmark run output from ticket 2
- [ ] Every quantitative figure across the design doc, script output, and the evidence log itself tagged observed/estimated/benchmarked/assumed
- [ ] Design doc's latency/throughput/cost claims cross-checked against evidence log entries for consistency

Labels: none

Acceptance criteria (if any are present in the body or a checklist):
- Every substantive claim in the packet assigned a proof tier per scoring_rubric.md's tiering scheme
- Tier 3/4 entries reserved for, and traced to, the actual local benchmark run output from ticket 2
- Every quantitative figure across the design doc, script output, and the evidence log itself tagged observed/estimated/benchmarked/assumed
- Design doc's latency/throughput/cost claims cross-checked against evidence log entries for consistency

Relevant comments (only ones that change scope or add requirements — skip chit-chat):
none

Linked context (one entry per followed link; "none" if the ticket links to nothing):
--- scoring_rubric.md (https://github.com/luccardoso51/engineer-004/blob/main/scoring_rubric.md) ---
Public Review Guide: Engineer 004

This guide is challenge-specific but intentionally high level. Read SCORING.md first: the five evaluation dimensions, the evidence tiers, and the number source labels apply to every challenge. Private reviewer calibration, answer benchmarks, and follow-up exercises are not published.

What Strong Submissions Demonstrate

1. Alternatives considered, not just components named
Strong designs explain why each technology was chosen over the obvious alternatives, in terms of this brief's latency target, event volume, team size, and budget ceiling. A component diagram without rejected options reads as a tutorial, not a decision.

2. Arithmetic that survives inspection
Throughput, storage, and cost claims should come with visible back-of-envelope math, and every input labeled as observed, benchmarked, or assumed. Strong submissions size the system for the stated spike multiplier and show the cost estimate against the stated ceiling.

3. A migration plan that takes the constraint seriously
Existing integrations cannot break and the SDK cannot change. Strong answers show a phased cutover with validation (for example, parallel-run comparison), a rollback trigger, and a definition of "data accuracy verified" that is testable. This section separates operators from diagram authors.

4. Failure design for the unhappy paths
The current system loses events under load. Strong designs state their delivery guarantees precisely, show where backpressure and buffering live, what degrades first under overload, and how loss or duplication would be detected rather than assumed away.

5. Compliance treated as architecture
Deletion requests, multi-tenancy, and audit requirements shape data layout and retention. Strong submissions design for them up front; bolting them on later is a known trap for this kind of pipeline.

6. Scope discipline
Two dedicated engineers and a phased timeline are the real budget. Strong answers say what the MVP excludes and what they would do differently with more time or money, as the brief asks.

Challenge-Specific Failure Modes

- Buzzword architecture. Naming a fashionable stack with no data-flow reasoning, sizing math, or connection to the constraints. This is the default generic-AI answer for this brief.
- The skipped migration. A clean greenfield design that never explains how 500+ customers move without breakage. The migration is most of the actual risk.
- Unlabeled performance claims. Latency and throughput figures asserted without stating whether they are benchmarked, estimated, or assumed.
- Over-engineering. A design that a dozen-person company could not build or operate, ignoring the team and budget in the brief.

Evidence That Matters for This Brief

- Tier 2 is the floor: the architecture diagram plus a design doc a reviewer can interrogate; better, a small repo or runnable prototype of the riskiest component.
- Tier 3 strengthens it: benchmark runs, load-test output, traces, or cost calculations with sources shown.
- Tier 4 is the differentiator: measured before/after from a comparable system you actually built or fixed, method stated.
- In your evidence log, tie each headline claim (latency, loss rate, cost) to its tier. "It should handle it" is Tier 0.

Strong or close submissions may be asked to walk through the design live with a changed constraint, such as a tighter budget or a new compliance requirement.

Fixture Verification

The brief requires working the fixture dataset in fixtures/event_sample.jsonl. Reviewers hold the private key of seeded issues, so the fastest ways to lose are: analysis that never cites the data, conclusions that treat a planted issue as clean signal, and recommendations the fixture contradicts. Strong submissions cite specific ids, catch most of the seeded issues, state the fixture checksum, and say what they refused to conclude because the sample is small.

Format, page limits, and the full submission packet are defined in the challenge brief (brief.md) and the repository README. You can pre-screen your packet with python3 scripts/validate_submission.py.

--- SCORING.md (referenced by scoring_rubric.md as governing source for evidence tiers and number source labels; ../../SCORING.md from repo root) ---
Required Evidence Standards

Every submission should include an evidence log. Label your proof with the highest tier you can support:

Tier 0 — Claims only: You asserted it, but did not show proof.
Tier 1 — Screenshots: Static proof of a screen, doc, result, or workflow.
Tier 2 — Demo artifact: A sheet, repo, Loom, workflow, prototype, dashboard, or mock that can be reviewed.
Tier 3 — Logs or source records: Exports, raw data, source records, commits, prompt traces, CRM notes, analytics pulls, or similar.
Tier 4 — Before and after data: Measured change with a clear benchmark and method.
Tier 5 — Independent verification: A user, customer, system, reviewer, or production process confirms the result.

Lower tiers can be useful context. Higher tiers usually carry more weight.

Number Source Labels

Every number in the submission must be labeled by source type:

- Observed: measured directly from a real system, dataset, user, or experiment.
- Estimated: your own estimate based on stated reasoning.
- Benchmarked: pulled from a named external benchmark, public source, or comparable case.
- Assumed: a placeholder assumption used to make the plan concrete.

Examples:
- "[Observed] 48 leads entered the sheet last week."
- "[Estimated] This should take 6 hours to build because two APIs are already connected."
- "[Benchmarked] 2 percent to 5 percent reply rate based on prior cold outbound benchmarks."
- "[Assumed] $100/hour blended cost for internal time."

Unlabeled numbers hurt the review. Fake precision hurts more than honest assumptions.

Verification note: An [Observed] number or a Tier 2-5 evidence claim that gives a reviewer nothing to check — no link, file, screenshot, record, or reproduction step — is scored as Tier 0: claims only. The pre-screen (python3 scripts/validate_submission.py) flags high-tier claims with nothing checkable before you submit.

--- #2 Anomaly-detection script, tests & benchmark (https://github.com/luccardoso51/engineer-004/issues/2) ---
Status: CLOSED

What it delivers: detect_anomalies(events) -> list[Anomaly] seam plus thin CLI wrapper extending src/analytics_pipeline/main.py; Python 3.11 stdlib only; fixture loading that handles malformed/truncated evt-0020 without crashing (dead-letter/parse-failure result); unittest suite with one test per confirmed anomaly class from ticket 1, one clean/negative case, and one test per borderline case; full test suite passing against real fixture; real local benchmark run capturing throughput and latency of detect_anomalies against the full fixture with raw timing and pass/fail counts. This is the artifact whose benchmark output ticket 4 must trace Tier 3/4 entries to.

--- #3 Design doc (https://github.com/luccardoso51/engineer-004/issues/3) ---
Status: CLOSED

What it delivers: ≤4-page redesigned-pipeline doc covering architecture, scale/reliability/migration, and trade-offs/risks; current-state failure modes mapped to fixes; latency budget under 5s; cost breakdown within $50K/mo at 50M+ events/day; phased 3-month MVP / 6-month full plan for 2 senior engineers; multi-tenant isolation for 500+ tenants; SOC2/GDPR/CCPA controls; zero-data-loss mechanism; burst handling; named AWS services with rejected alternatives; fixture handled anomaly-class by anomaly-class with event_id citations and fixture checksum; migration/cutover with validation and rollback trigger; trade-offs/risks section; explicit assumptions. Ticket 4 must cross-check this doc's latency/throughput/cost claims against the evidence log.