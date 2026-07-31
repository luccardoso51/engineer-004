Title: Anomaly-detection script, tests & benchmark

Identifier: #2

Description:
What to build: the detect_anomalies(events) -> list[Anomaly] seam plus a thin CLI wrapper, extending the existing src/analytics_pipeline/main.py scaffolding, with a unittest suite and a real local benchmark run against the fixture — the artifact that proves execution, not just design.

Blocked by: Fixture forensics & anomaly taxonomy

- [ ] detect_anomalies(events) -> list[Anomaly] implemented as the single seam, Python 3.11 stdlib only
- [ ] Thin CLI wrapper reads the fixture file and prints/serializes results keyed by event_id
- [ ] Fixture loading handles the malformed/truncated line (evt-0020) without crashing, routing it to a dead-letter/parse-failure result instead
- [ ] unittest suite with one test per confirmed anomaly class from ticket 1, one clean/negative case, and one test per borderline case identified in ticket 1's face-value list
- [ ] Full test suite passes against the real fixture
- [ ] Local benchmark executed for real: throughput and latency of detect_anomalies against the full fixture, with raw timing and pass/fail counts captured

Labels: none

Acceptance criteria (if any are present in the body or a checklist):
- detect_anomalies(events) -> list[Anomaly] implemented as the single seam, Python 3.11 stdlib only
- Thin CLI wrapper reads the fixture file and prints/serializes results keyed by event_id
- Fixture loading handles the malformed/truncated line (evt-0020) without crashing, routing it to a dead-letter/parse-failure result instead
- unittest suite with one test per confirmed anomaly class from ticket 1, one clean/negative case, and one test per borderline case identified in ticket 1's face-value list
- Full test suite passes against the real fixture
- Local benchmark executed for real: throughput and latency of detect_anomalies against the full fixture, with raw timing and pass/fail counts captured

Relevant comments (only ones that change scope or add requirements — skip chit-chat):
none (no comments on the issue)

Linked context (one entry per followed link; "none" if the ticket links to nothing):
--- Issue #1: Fixture forensics & anomaly taxonomy (https://github.com/luccardoso51/engineer-004/issues/1) — blocking issue, CLOSED ---
Delivers: the ground-truth forensic catalog of fixtures/event_sample.jsonl (merged via PR #8, which added docs/fixture-forensics.md). Status: done/merged, so ticket #2 can rely on it directly.

Full content of the referenced artifact, docs/fixture-forensics.md (the actual deliverable of ticket #1, which ticket #2 must build its tests against):

FIXTURE: fixtures/event_sample.jsonl, SHA-256 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235. 25 physical lines; 24 records parse successfully; file line 21 (evt-0020) fails to parse (malformed JSON, missing closing brace) — this is the record ticket 2's loader must dead-letter rather than crash on. 23 distinct event_ids across 24 parseable records (evt-0002 appears twice).

CORRECTED 9-CLASS ANOMALY TAXONOMY (replaces the spec's placeholder nine-class list — three placeholder classes dropped as not present in this fixture: tenant_id mismatch/spoofing, cross-tenant leakage, per-tenant volume drop-to-zero, plus the generic negative/impossible-value class; three real classes added: schema drift, malformed JSON record, compliance-critical event type):

1. Duplicate event_id / idempotency violation — evt-0002 (same event_id on file lines 2 and 5, identical ts/payload, received_at differs by ~7.4s — a client retry, not two clicks; dedup must key on event_id).
2. Out-of-order timestamp (client clock skew) — evt-0005 (received_at ~47s earlier than ts).
3. Systematic timezone offset (not random skew) — evt-0006 (ts ~65 min ahead of received_at; matching .552ms suffix on both — fingerprint of a timezone bug, not random drift; treat received_at as authoritative for ordering).
4. Future/impossible timestamp — evt-0016 (ts year 2027 vs received_at 2026).
5. Missing required field (unattributable) — evt-0011 (tenant_id is null; should be quarantined/routed for investigation, not dropped or defaulted to a tenant).
6. Unexpected PII in free-form payload — evt-0007 (contact_email and phone embedded in a custom event's properties).
7. Schema drift / non-conforming shape — evt-0009 (type "pageview" not "page_view"; uses timestamp not ts; no received_at; page_path/ref instead of path/referrer — looks like a legit older-SDK shape; should be normalized, not dropped, since the brief forbids forcing an SDK upgrade).
8. Bot/scanner volume-spike burst — evt-0012, evt-0013, evt-0014, evt-0015 (same anonymous_id anon-8fc, ts span ~50ms, scanner referrer, hitting /pricing,/features,/docs,/about in sequence).
9. Malformed/corrupt JSON record — evt-0020 (file line 21 fails json.loads; file is valid before and after it).

Additionally, evt-0017 (privacy_request / GDPR delete_all_data) is called out as a compliance-critical event type — NOT a data-quality anomaly to filter/count, but a legal signal that must route to a workflow (kept distinct from the anomaly taxonomy above).

Per-event verdicts table confirms all 25 fixture lines' classification (all events not listed above are "Clean").

SIX "do not take at face value" items (ticket 2 should test at least the borderline/reasoning-bearing ones as borderline cases per its own checklist):
1. evt-0006 — don't treat as a genuine future event; treat received_at as authoritative for ordering, flag source for correction.
2. evt-0009 — don't discard as broken; normalize to current schema rather than drop (avoids losing real traffic from older SDKs).
3. evt-0017 — don't count as a normal analytics/custom event; route to compliance workflow (human/approved action), not an automated metric increment.
4. evt-0002 duplicate — don't dedupe on payload+ts; key on event_id (idempotency key) so retries are absorbed, not double-counted.
5. evt-0011 null tenant_id — don't silently drop or default to a tenant (defaulting would corrupt that tenant's data); quarantine for investigation.
6. evt-0020 malformed record — don't crash the loader and don't silently skip; dead-letter it and continue processing.

Handoff notes explicitly directed at ticket #2: assert against the exact event_ids above; loader must survive evt-0020 via dead-lettering and still yield the 24 parseable records; dedup logic must key on event_id; the privacy_request (evt-0017) path must be kept distinct from data-quality anomalies (workflow concern, not a filter).

Other references in the doc (SCORING.md, scoring_rubric.md, docs/adr/to-spec.md) are scoring/grading meta-documents cited for provenance/traceability, not implementation requirements — not fetched, as they're outside this challenge's committed scaffold or are grading rubrics rather than ticket content.