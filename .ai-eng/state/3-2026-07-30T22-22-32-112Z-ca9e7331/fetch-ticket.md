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