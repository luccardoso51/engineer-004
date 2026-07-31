Ticket:
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

---

Assistant:
Good — I have all the ground-truth facts I need (fixture contents, corrected taxonomy, current test failure confirming the malformed line does crash `load_jsonl` today). Now for the decisions the ticket leaves open.

What fields should the `Anomaly` type itself carry?

a) Minimal — event_id, anomaly_class (str/enum), detail (free-text reason) only.
b) Minimal + action — adds a recommended-action field (e.g. "quarantine", "dedupe", "normalize", "flag_for_correction", "route_compliance") so the taxonomy's remediation guidance from ticket 1 is machine-readable, not just prose.
c) Minimal + raw event — (a) or (b) plus the offending event dict attached, so downstream consumers don't need a second lookup.

My recommendation: (b) — a small `@dataclass(frozen=True)` with `event_id: str`, `anomaly_class: str`, `detail: str`, `action: str`. Ticket 1's taxonomy is explicitly remediation-bearing (dedupe-by-event_id, quarantine-don't-drop, normalize-don't-drop, treat-received_at-as-authoritative, route-to-compliance), and encoding that as a field makes the CLI output and tests actually assert the *behavior* the forensics doc cares about, not just a label. I'd skip attaching the raw event (c) — keeps the seam thin and JSON-serializable without extra work.

User:
before we continue, I'm horried about this. Other references in the doc (SCORING.md, scoring_rubric.md, docs/adr/to-spec.md) are scoring/grading meta-documents cited for provenance/traceabili

---

Assistant:
That message looks like it got cut off partway through — it reads as a fragment of the ticket context rather than an answer to the Anomaly-shape question. Could you clarify what you meant (what's the concern), or if it was a stray paste, just answer a/b/c on the Anomaly fields question above (my recommendation is b)?

User:
these docs are very important, it should be in the repo

---

Assistant:
Checked both: `SCORING.md` does exist, just one level up at the outer repo root (`/Users/lucasrodrigues/Projetos/beat-claude/SCORING.md`), matching the `../../SCORING.md` path the brief already points to — nothing missing there. `docs/adr/to-spec.md` doesn't exist anywhere as a real file; it's referenced in the forensics doc as an internal scoping note ("recorded during scoping... not itself committed to this scaffold") — reads like an answer-key-style document this hiring-challenge repo deliberately keeps out of the candidate-facing scaffold, not something ticket 1 or 2 forgot to add. Ticket 2's checklist doesn't mention adding any of these.

Given that, should I treat this as a non-issue and proceed with ticket 2's actual scope (recommended — nothing is actually missing, and adding an answer-key doc would be scope creep + probably wrong), or is there a specific doc among these three you want added/fixed as part of this work?

User:
yes, lets continue them, lets make sure to not lose anything. Also, the scoring file is important so we can evaluete the outcome of the task ok? Maybe we can write a test to judge, like a unit test

---

Assistant:
Good — I'll treat the missing-docs question as resolved (nothing to fix, proceed with ticket 2's actual scope).

On "write a test to judge" against SCORING.md: I want to pin down what that means concretely, because there are two very different things this could be:

a) Detection-accuracy tests — per-anomaly-class unittest cases that assert `detect_anomalies` flags exactly the expected `event_id`s from ticket 1's forensics catalog (e.g. assert evt-0007 is flagged as PII, evt-0002 as duplicate, etc.). This is mechanically testable and is already what ticket 2's checklist asks for ("one test per confirmed anomaly class... assert against the exact event_ids").
b) A broader meta-test that checks the whole submission packet against SCORING.md's dimensions (evidence log present, AI-usage disclosure present, number-source labels used, etc.) — similar to the `scripts/validate_submission.py` pre-screener mentioned in scoring_rubric.md, which lives one level up in the outer repo, not in this challenge scaffold.

SCORING.md's S1/S3/S5 dimensions (judgment, evidence quality, communication) are graded by a human/reviewer reading prose — they aren't the kind of thing a unit test can mechanically pass/fail.

My recommendation: (a) — it's already in ticket 2's scope, is genuinely testable, and is the closest thing to "a test that judges the outcome" that makes sense for this code seam. Is that what you meant, or did you want something closer to (b)?

User:
a

---

Assistant:
Good — that's already covered by the ticket's own checklist (per-class tests asserting against ticket 1's exact `event_id`s), so no new scope needed there. Back to the `Anomaly` shape question from before: a) minimal (event_id, anomaly_class, detail), b) minimal + a machine-readable `action` field (dedupe/quarantine/normalize/flag/route_compliance), or c) (a) or (b) plus the raw event attached. I recommend (b) for the reasons given earlier — does that work for you?

User:
b

---

Assistant:
Locked in: `Anomaly` = dataclass with `event_id`, `anomaly_class`, `detail`, `action`.

Next: how should `evt-0017` (the GDPR `privacy_request`) be represented by `detect_anomalies`, given the forensics doc says it must be "kept distinct from the anomaly taxonomy" and routed to a compliance workflow rather than counted as a data-quality anomaly?

a) Excluded entirely — `detect_anomalies` only implements the 9 data-quality/malformed classes; compliance routing is out of scope for this seam (single return type, no second channel), and it's simply absent from the output.
b) Included, but tagged distinctly — emitted as an `Anomaly` with `anomaly_class="compliance_critical"` and `action="route_compliance"`, so it shows up in the CLI's keyed-by-event_id output for visibility, but consumers can filter it out of "anomaly counts" by class/action since it's clearly not a data-quality defect.

I recommend (b): the ticket's own borderline-case checklist requires a test for evt-0017's "don't count as a normal event, route to compliance" behavior — that's easiest to assert if `detect_anomalies` actually surfaces it (with a distinguishing tag), rather than silently dropping it, which would make the compliance signal invisible to the one seam the ticket defines. Which do you want?

User:
b

---

Assistant:
Next: `evt-0020` fails `json.loads` entirely (truncated JSON), so there's no parsed `event_id` field to key it by — yet the CLI output is "keyed by event_id" and the fixture doc clearly expects this record to be identifiable as `evt-0020`. How should the dead-letter entry get its key?

a) Best-effort regex extraction — scan the raw failed line for `"event_id":"..."` and use that as the key (`evt-0020` here); if no such pattern is found in some future malformed line, fall back to a synthetic key like `line:<n>`.
b) Always key by physical line number (`line:21`), never attempt to read anything out of text that failed to parse, to avoid trusting unparsed data.
c) Synthetic sequential key (`dead-letter-1`) independent of content or position.

I recommend (a): the raw text trivially contains `"event_id":"evt-0020"` even though the JSON as a whole is truncated, and keying it under `evt-0020` (with a fallback for the genuinely unidentifiable case) makes the CLI output legible and matches what the forensics doc and a human reviewer would expect to see. Which do you want?

User:
a

---

Assistant:
Next: the CLI's "results keyed by `event_id`" output — what should the actual JSON shape be, and which events appear in it?

a) Anomalies only — output is `{event_id: [ {anomaly_class, detail, action}, ... ]}`, containing only event_ids that have at least one anomaly (including the compliance-critical and dead-letter cases), sized to whatever's interesting. Clean events are omitted entirely.
b) Full census — output includes every distinct event_id (all 23 parsed + the 1 dead-lettered = 24 keys), each mapped to `{"anomalies": [...], "status": "clean"|"flagged"|"dead_letter"}`, so a reader can see the whole fixture's disposition including clean records, not just the flagged ones.
c) Full census plus summary — (b), plus a top-level `"summary"` key with counts per anomaly_class/action and total clean/flagged/dead-lettered, so the pass/fail counts needed for the benchmark step are already computed by the same code path.

I recommend (c): the ticket's benchmark AC explicitly needs "pass/fail counts captured," and computing that once in the CLI's serialization (rather than re-deriving it ad hoc in a separate benchmark script) keeps the seam single-sourced. Which do you want?

User:
c

---

Assistant:
Locked in: full-census CLI output with a summary block.

Next: the fixture only has 24 parseable records, so a single pass through `detect_anomalies` will complete in well under a millisecond — not enough to produce a meaningful throughput/latency number on its own. How should the benchmark get real, stable timing?

a) Repeat-loop — run `detect_anomalies` N times (e.g. 1,000 or 10,000 iterations) over the same loaded fixture, using `time.perf_counter()`, and report total wall time, mean/median per-call latency, and events/sec throughput computed from N × 24 events processed.
b) Single pass only — run it once, report the raw (sub-millisecond) number as-is, honestly labeled as noisy/low-precision given the fixture size, no artificial repetition.
c) Repeat-loop like (a), but also synthetically inflate the working set (e.g. concatenate the fixture's parsed events N times into one big list) to benchmark a single large `detect_anomalies` call rather than many small calls, closer to a "large batch" throughput scenario.

I recommend (a): it's the simplest honest way to get a stable per-call latency and throughput number from a tiny fixture without fabricating data, and it directly benchmarks the seam as it's actually called (once per batch of real events) rather than an artificially inflated batch shape. Where should the benchmark live — a standalone `scripts/benchmark.py`/`bench.py`, or a `--benchmark` flag on the existing CLI in `main.py`? I'd lean standalone script, since the CLI's job (per the ticket) is "read fixture, print/serialize results," and mixing in perf-loop concerns would make that thinner wrapper less thin. And where should the raw output artifact be saved — printed to stdout only, or also written to a committed file (e.g. `docs/benchmark-results.md` or `benchmark_output.txt`) so it's an inspectable artifact per the ticket's "artifact that proves execution" framing?

User:
why a is more recommended tha c?

---

Assistant:
Two reasons:

1. Fidelity to what's being measured. The ticket asks for "throughput and latency of `detect_anomalies` against the full fixture" — i.e. benchmark the seam as it's actually called in production: once per batch of real events. (a) does exactly that, many times, and derives throughput/latency from real per-call measurements. (c) changes the shape of the input itself (one giant synthetic list), which benchmarks a different question — "how does this scale with a 10,000-event batch" — that nobody asked for and that the 24-record fixture can't actually validate.

2. Correctness risk. Several anomaly classes are cross-event (duplicate `event_id`, the anon-8fc bot-burst window). If I naively concatenate the fixture N times to inflate (c), every event_id would now repeat N times, evt-0002's dup would balloon, and the bot-burst's ~50ms window logic would collide across copies unless I also offset timestamps per copy — extra fiddly logic just to build the benchmark input, and it would blow up the "pass/fail counts" so they no longer represent the real 24-record fixture (which is what the benchmark artifact is supposed to be proof against). (a) avoids all of that: the fixture is loaded and parsed once, and only the `detect_anomalies(events)` call itself is repeated, so pass/fail counts stay tied to the real fixture on every iteration.

Given that, do you want to go with (a), or still prefer (c) despite the added complexity and the risk of the counts no longer reflecting the real fixture?

User:
ok so lets go with a

---

Assistant:
Good — repeat-loop benchmark (a) it is. Two follow-ups I bundled in that message are still open: where should the benchmark live — a standalone `scripts/benchmark.py`, or a `--benchmark` flag on the existing CLI in `main.py`? I recommend standalone (keeps the CLI thin, per the ticket's own wording). And should the raw output also be written to a committed file (e.g. `docs/benchmark-results.md`), or is stdout-only sufficient as the "artifact that proves execution"? I recommend writing it to a committed file too, since a stdout-only run leaves no trace for a reviewer to inspect later. Agree with both recommendations?

User:
yes

---

Assistant:
One more implementation-shape decision: the existing `load_jsonl(path) -> list[dict]` in `main.py` will crash on `evt-0020` today (confirmed — I ran the current test suite and it throws `JSONDecodeError`). Since the loader needs to dead-letter that line rather than crash, its return shape has to change to expose both the parsed events and the dead-letter(s). How should that work?

a) Change `load_jsonl` itself to return a small result object, e.g. `LoadResult(events: list[dict], dead_letters: list[DeadLetter])`, replacing its current `list[dict]` return. The existing `tests/test_main.py` assertion (`len(events) > 0`, `"event_id" in events[0]`) gets updated to match, since the ticket has us rewriting the test suite anyway.
b) Leave `load_jsonl` untouched in behavior/signature (still returns `list[dict]`, silently drops unparseable lines internally, no visibility into what was dropped) and add a second function, e.g. `load_jsonl_with_dead_letters`, for the CLI/dead-letter-aware path.

I recommend (a): a loader that silently drops bad records without surfacing them (b) is exactly the "silently skip" failure mode ticket 1's forensics doc explicitly warns against for evt-0020, and maintaining two parallel loaders is redundant for a "thin" scaffold. Agree with (a)?

User:
is this permited? in the challenges rules?

---

Assistant:
Yes — nothing in the rules restricts it. The outer repo's `README.md` ("The Rules" section) says candidates can "use whatever tools you want" and should "build the required operating artifact," and this ticket's own description literally says "extending the existing `src/analytics_pipeline/main.py` scaffolding" — the scaffold is a starting point, not frozen reference code. `tests/test_main.py` is candidate-owned test code (not a grading harness — the private benchmark/rubric material is explicitly kept out of this repo per SCORING.md), so updating it to match the new loader behavior is expected, not against any rule.

Given that, still good with option (a) — change `load_jsonl` to return a `LoadResult(events, dead_letters)` and update the existing test accordingly?

User:
ok go with a

---

Assistant:
One more structural decision: where should the new code physically live?

a) All in `main.py` — `Anomaly`, `detect_anomalies`, the updated `load_jsonl`/`LoadResult`, and the CLI all stay in the single `src/analytics_pipeline/main.py` file, since the ticket phrases this as "extending the existing `src/analytics_pipeline/main.py` scaffolding."
b) Split into modules — `main.py` keeps just the CLI wrapper (thin, per the ticket's own description) and argument parsing; the loader and `detect_anomalies`/`Anomaly` move into new sibling modules under `src/analytics_pipeline/` (e.g. `loader.py`, `anomalies.py`), imported by `main.py`.

I recommend (b): the ticket calls the CLI wrapper "thin" and separately calls out `detect_anomalies` as "the single seam" — treating it as its own module (not entangled with argparse/print calls) makes it independently unit-testable and keeps `main.py` genuinely thin, while still satisfying "extending the existing scaffolding" since `main.py` remains the entry point and gets built on rather than replaced. Agree with (b), or do you want everything kept in the one file?

User:
b

---

Assistant:
One important algorithmic question, since three of the nine classes are all timestamp-based and need to be told apart programmatically rather than just matched by ID: `evt-0005` (clock skew), `evt-0006` (timezone offset), and `evt-0016` (future/impossible timestamp) all show `ts` disagreeing with `received_at`, but by different signatures. How should `detect_anomalies` actually tell these apart?

a) Feature-based heuristics — real rules derived from the signal ticket 1 documented: (1) future/impossible: `ts` is later than `received_at` by more than some large bound (e.g. `ts` falls on a different year, or the gap exceeds ~1 day) → flag future timestamp; (2) systematic timezone offset: `ts` and `received_at` disagree by tens of minutes or more, AND their sub-second/millisecond fraction matches exactly (the fingerprint ticket 1 called out) → flag timezone offset, treat `received_at` as authoritative; (3) plain clock skew: `received_at` precedes `ts` by some smaller bound (e.g. under an hour) without the matching-fraction fingerprint → flag out-of-order/skew. Documented as fixture-informed heuristics, not a statistically general drift detector.
b) ID-literal matching — special-case the known event_ids directly in the detection logic (`if event_id == "evt-0006": ...`).

I recommend (a) — (b) would mean `detect_anomalies` isn't really detecting anything, just recognizing specific IDs, which undercuts the entire point of "a script that detects the anomalies" the brief asks for. Agree with (a), and are you comfortable with those specific threshold choices (day-scale for future, matching-fraction + tens-of-minutes for timezone, sub-hour precedence for skew), or do you want different bounds?

User:
I dont get it, explain me in plain terms

---

Assistant:
Sorry, let me put it plainly.

There are three separate "the timestamp looks wrong" problems in the sample data, and the code needs to be able to tell which is which just by looking at the numbers — not by already knowing the answer.

1. `evt-0005` — "clock skew": the server logged that it got the event slightly before the event even happened (impossible by a small amount, ~47 seconds). Like a receipt stamped a few seconds before you paid.
2. `evt-0006` — "timezone bug": the event's own timestamp is about 65 minutes off from when the server got it — but the milliseconds portion at the very end matches exactly on both. That exact match is a giveaway that someone's clock is off by a fixed round amount (like a timezone misconfigured), not just random lag.
3. `evt-0016` — "impossible timestamp": the event claims to have happened over a year in the future. Not a small glitch — clearly bogus.

The question: should the code decide which bucket an event falls into by actually measuring things (how big the gap is, whether the milliseconds match) — real logic that would also work correctly on a different but similar event it's never seen? Or should it just special-case by name, e.g. "if event_id is literally evt-0006, say timezone bug" — which only works because I already know the answer key and isn't really "detecting" anything?

I recommend the first approach (measure the gap size + check for the matching-millisecond trick) — hardcoding IDs would mean the script isn't actually analyzing the data, just memorizing this one fixture, which defeats the point of building a detector. Does that make sense — okay to go with real measurement-based logic?

User:
yes i think so, I think this is something that the interviewer may ask later, this tradeoff, so lets save this decision somewhere that i can check later and understand

---

Assistant:
Saved as an ADR: `docs/adr/0001-timestamp-anomaly-classification-by-signal-not-id.md`. It records the trade-off in plain terms — feature-based detection vs. ID-literal matching, why we picked the former, and the honest caveat that the thresholds are hand-tuned to this fixture's magnitudes rather than statistically general. That's exactly the kind of thing worth having on hand if an interviewer asks "why build it this way."

I think that closes out the open decisions. Let me do a final sanity pass to make sure nothing's left dangling before I hand this off.

[Nemo: nudged — not a question]

---

Assistant:
```ticket-grill-complete
summary: Ticket #2 implements the detect_anomalies(events) -> list[Anomaly] seam, a thin CLI wrapper, a unittest suite, and a real local benchmark against fixtures/event_sample.jsonl (SHA-256 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235), building on the ground-truth catalog in docs/fixture-forensics.md (currently only on branch chore/fixture-forensics-anomaly-taxonomy, not yet on main — pull it in). The fixture has 25 physical lines, 24 parseable records, 23 distinct event_ids (evt-0002 duplicated), and one malformed line (file line 21, evt-0020) that fails json.loads entirely. The corrected 9-class taxonomy to detect: (1) duplicate event_id/idempotency (evt-0002, dedupe keyed on event_id, not payload+ts), (2) out-of-order timestamp/clock skew (evt-0005), (3) systematic timezone offset (evt-0006, ts ~65min ahead of received_at with matching millisecond fraction — treat received_at as authoritative), (4) future/impossible timestamp (evt-0016, ts a year ahead), (5) missing required field/unattributable (evt-0011, null tenant_id — quarantine, never default to a tenant), (6) unexpected PII in free-form payload (evt-0007), (7) schema drift/non-conforming shape (evt-0009, pageview/timestamp/page_path/ref shape — normalize, don't drop, since SDK upgrades can't be forced), (8) bot/scanner volume-spike burst (evt-0012..0015, same anonymous_id anon-8fc, ~50ms span, scanner referrer), (9) malformed/corrupt JSON record (evt-0020, dead-letter, don't crash, don't silently skip). evt-0017 (privacy_request/GDPR delete_all_data) is a compliance-critical signal kept distinct from data-quality anomalies but still surfaced through the same seam.

Decisions resolved during prep: Anomaly is a dataclass with event_id, anomaly_class, detail, and a machine-readable action field (e.g. dedupe/quarantine/normalize/flag_for_correction/route_compliance/dead_letter) capturing ticket 1's remediation guidance, so tests can assert behavior not just labels. evt-0017 is emitted as an Anomaly with anomaly_class="compliance_critical" and action="route_compliance" (included in output, filterable by class/action, not counted as a data-quality defect). The malformed evt-0020 line is dead-lettered by best-effort regex-extracting "event_id":"..." from the raw unparsed text (falls back to a line:<n> synthetic key if no id pattern is found) — load_jsonl is changed to return a LoadResult(events, dead_letters) dataclass instead of a bare list, and the existing tests/test_main.py assertion is updated accordingly (confirmed permitted — the scaffold is meant to be extended, per repo README and the ticket's own wording). The CLI output is a full census keyed by event_id: all 23 parsed ids plus the dead-lettered entry (24 keys total), each mapped to {"anomalies": [...], "status": "clean"|"flagged"|"dead_letter"}, plus a top-level "summary" block with counts per anomaly_class/action and totals for clean/flagged/dead-lettered — this summary doubles as the benchmark's required pass/fail counts. Code is split into modules under src/analytics_pipeline/: loader.py (LoadResult-returning loader with dead-lettering), anomalies.py (Anomaly dataclass + detect_anomalies, independently unit-testable), and main.py kept thin (CLI/argparse + serialization only). The benchmark is a standalone scripts/benchmark.py (not a CLI flag) that repeat-loops detect_anomalies many times over the same loaded fixture (not a synthetically inflated single batch, to avoid corrupting cross-event anomaly signals like duplicates/bot-bursts) using time.perf_counter(), reporting total wall time, mean/median per-call latency, and events/sec throughput, with output written both to stdout and to a committed artifact file (e.g. docs/benchmark-results.md) as proof of a real execution. Timestamp-anomaly classification (clock skew vs timezone offset vs future/impossible) uses real feature-based heuristics — gap magnitude, ordering direction, and matching sub-second/millisecond fraction as the timezone-bug fingerprint — rather than special-casing known event_ids, since ID-literal matching wouldn't generalize and would defeat the purpose of a detector; this trade-off and the accepted caveat that thresholds are fixture-tuned (not statistically general) is recorded in docs/adr/0001-timestamp-anomaly-classification-by-signal-not-id.md. The unittest suite should mirror the module split (tests per anomaly class asserting exact event_ids per ticket 1's catalog, one clean/negative case, one test per borderline "not at face value" case: evt-0006 ordering-by-received_at, evt-0009 normalize-not-drop, evt-0017 compliance routing, evt-0002 dedupe-by-event_id, evt-0011 quarantine-not-default, evt-0020 dead-letter-not-crash) and must pass against the real fixture. Investigated-and-cleared as non-issues: SCORING.md already exists one level up in the outer repo (../../SCORING.md, matches the brief's existing reference); docs/adr/to-spec.md is an intentionally uncommitted internal scoping/answer-key document per ticket 1's own forensics doc, not a gap to fill; a "test to judge the outcome against SCORING.md" was clarified to mean the already-in-scope per-class detection-accuracy tests (SCORING.md's judgment/communication dimensions are human-graded prose, not unit-testable).
```