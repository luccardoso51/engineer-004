Ticket:
Title: Fixture forensics & anomaly taxonomy

Identifier: #1

What to build: the real, event_id-cited catalog of what's actually planted in fixtures/event_sample.jsonl, correcting the spec's placeholder nine-class taxonomy (which the spec itself flagged as an unverified assumption) against what's actually in the file, plus the fixture's sha256 checksum and the brief-required write-up of items that should not be taken at face value.

Blocked by: None — can start immediately

- [ ] sha256 checksum of fixtures/event_sample.jsonl computed and recorded
- [ ] Every event in the fixture reviewed; anomaly signals actually present cataloged and cited by event_id
- [ ] Corrected anomaly taxonomy documented, noting where it diverges from the original placeholder list and why
- [ ] At least three fixture items identified that should not be taken at face value, with reasoning per item
- [ ] Findings written as a standalone artifact that later tickets can reference

---

Assistant:
Before I write this up, one open decision the ticket leaves to us: where this standalone artifact should live, since later tickets (design doc, evidence log, AI-disclosure, detection-script tests) will need to reference it by path.

a) docs/fixture-forensics.md — new top-level docs/ folder; conventional location for a findings doc, easy to link from other tickets
b) FIXTURE_FORENSICS.md at repo root — most visible, no new folder, but clutters root alongside brief.md/claude_baseline.md
c) fixtures/FORENSICS.md — lives right next to the fixture it describes, but odd to put prose docs inside a fixtures/ data folder

I'd recommend (a): docs/fixture-forensics.md. The repo has no docs/ yet, but it's the natural place to start accumulating the design doc, evidence log, and other write-ups this packet needs, and "docs/" reads cleanly as a cross-reference target from other tickets.

[Nemo: nudged — not a question]

---

Assistant:
Where should this standalone artifact live so later tickets (design doc, evidence log, disclosure, detection-script tests) can reference it by a stable path?

a) docs/fixture-forensics.md — new top-level docs/ folder, conventional home for findings docs
b) FIXTURE_FORENSICS.md at repo root — most visible, no new folder, but clutters root
c) fixtures/FORENSICS.md — sits next to the data it describes, but mixes prose into a data folder

I'd recommend (a), since docs/ will likely need to hold the design doc and evidence log too. Which do you want?

User:
a

---

Assistant:
```ticket-grill-complete
summary: Ticket #1 (Fixture forensics & anomaly taxonomy) scope: produce a standalone, event_id-cited forensic catalog of fixtures/event_sample.jsonl, correcting the spec's unverified placeholder nine-class taxonomy (docs/adr/to-spec.md line 59: duplicate event_id, out-of-order/clock-skew timestamps, missing required fields, tenant_id mismatch/spoofing, per-tenant volume spike, per-tenant volume drop-to-zero, impossible field values, cross-tenant data leakage, unexpected PII) against what is actually planted. Decision resolved this session: the artifact lives at docs/fixture-forensics.md (new top-level docs/ folder), since later tickets (design doc, evidence log, AI-usage disclosure, anomaly-detection script/tests) will reference it by path. Verified facts to ground the write-up: sha256 of fixtures/event_sample.jsonl is 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235; file has 25 lines / 24 unique event_ids (evt-0001..evt-0024) because evt-0002 is duplicated (file lines 2 and 5, identical payload/ts, received_at differs by ~7.4s — retry/idempotency case, not two distinct clicks). Confirmed anomalies present, by event_id: evt-0002 (dup) — duplicate event_id / idempotency violation; evt-0005 — received_at earlier than ts (client clock skew / out-of-order); evt-0006 — ts ~65 minutes ahead of received_at with matching millisecond suffix (.552), suggesting a systematic timezone bug rather than random skew; evt-0007 — PII (contact_email, phone) embedded in a "custom" event's properties, not a dedicated PII-protected field; evt-0009 — schema drift: type "pageview" not "page_view", uses "timestamp" instead of "ts", has no received_at field, and uses page_path/ref instead of path/referrer; evt-0011 — tenant_id is null (missing required field, orphaned/unattributable event); evt-0012–evt-0015 — four page_views firing within ~33ms, same anon-8fc, all referred from https://scanner.example-bot.net, hitting /pricing,/features,/docs,/about in sequence — bot/scanner burst pattern; evt-0016 — ts year 2027 vs received_at 2026 (future/impossible timestamp); evt-0017 — type privacy_request (GDPR delete_all_data) for user u-1077/anon-77a — a compliance-critical event requiring special handling, not a generic custom event; evt-0020 (file line 21, since the evt-0002 duplicate shifts line numbers) — truncated/malformed JSON (missing closing brace), confirmed via a real parse pass: json.loads fails on this line while the file continues validly afterward, i.e. an isolated corrupt record, not file truncation — this is the exact line ticket 2's fixture loader must dead-letter instead of crashing on. Checked and NOT present in this fixture despite being in the placeholder list: cross-tenant anonymous_id/user_id reuse (every anon_id and user_id maps to exactly one tenant_id, no leakage or spoofing found), and per-tenant volume drop-to-zero (fixture is a single static snapshot, not a time series, so this class isn't observable/testable here) — both should be called out as divergences from the placeholder taxonomy, along with negative-count "impossible values" (none found; the only impossible-value case observed is the future timestamp in evt-0016). New classes not in the placeholder list but genuinely present: schema drift/non-conforming event shape (evt-0009), malformed/corrupt JSON record (evt-0020), and compliance-critical event type requiring workflow action (evt-0017, privacy_request). Net: corrected taxonomy still totals nine classes but with different composition than the placeholder (dropped: tenant mismatch/spoofing, cross-tenant leakage, drop-to-zero, generic negative-value case; added: schema drift, malformed JSON record, compliance-critical event type). "Not at face value" candidates (need at least 3, have ~6 strong ones to choose from): evt-0006's suspiciously-exact ms-match timestamp skew (likely a client timezone bug, not a real future-dated event); evt-0009 (may be a legitimate older-SDK/legacy event shape needing normalization, not simply "broken"); evt-0017 (must not be logged/counted as a normal analytics event — it's a legal deletion mandate that should trigger purging u-1077/anon-77a's other events downstream); evt-0002's duplicate (dedup must key off event_id, not payload+ts, given the differing received_at suggests a client retry after a slow/failed ack); evt-0011's null tenant_id (should not be silently dropped or defaulted to a tenant — could indicate SDK misconfiguration or an attempted attack, needs investigation routing); evt-0020 (parse failures must route to dead-letter, not be silently skipped or crash the loader). Scope note: this ticket is analysis/documentation only — the actual detect_anomalies() implementation, CLI, and unittest suite are explicitly ticket 2's job (blocked by this ticket), so no code is expected here beyond the markdown artifact recording the checksum, full per-event review, corrected taxonomy with divergence rationale, and the face-value writeup.
```