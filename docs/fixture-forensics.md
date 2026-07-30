# Fixture Forensics & Anomaly Taxonomy

Forensic catalog of `fixtures/event_sample.jsonl`. This is the ground-truth
record of what is actually planted in the fixture, cited by `event_id`. Later
tickets (design write-up, evidence log, AI-usage disclosure, the
`detect_anomalies()` script and its tests) reference this document by path.

This ticket is analysis and documentation only. No detection code lives here.

## How this ticket maps to the scoring doc

Everything below is cross-referenced back to the scoring doc so no outcome or
recommendation is left un-anchored. Two documents govern:

- `SCORING.md` — the cross-challenge scoring guide the brief links to as
  `../../SCORING.md` (it lives above this challenge folder and is not committed
  to this scaffold, so treat these citations as pointers, not in-repo files).
  It defines the five evaluation dimensions (S1 Strategic judgment,
  S2 Execution detail, S3 Evidence quality, S4 AI fluency, S5 Communication),
  the evidence tiers, the number source labels, and the Verification /
  Integrity / "Failure Modes That Lose" sections.
- `scoring_rubric.md` (this challenge) — in particular its **Fixture
  Verification** paragraph, which is the bar this ticket is graded against.

Scoring tags used inline below: `[S1]`..`[S5]` are the SCORING.md dimensions;
`[Evidence]`, `[Numbers]`, `[Verify]`, `[Integrity]`, `[FailMode]` are the
SCORING.md sub-sections of the same name; `[FV]` is the scoring_rubric.md
Fixture Verification bar.

This ticket's five acceptance outcomes, each tied to what in the scoring doc it
earns:

| Ticket outcome | Where in this doc | Scoring reference |
|----------------|-------------------|-------------------|
| SHA-256 checksum recorded | Provenance | `[FV]` "state the fixture checksum" · `[Verify]` gives reviewers a checkable value · `[Numbers]` labeled `[Observed]` |
| Every event reviewed, signals cited by `event_id` | Per-event review + taxonomy | `[FV]` "cite specific ids" / "catch most of the seeded issues" · `[S3][Evidence]` Tier 3 source record |
| Corrected taxonomy, divergence from placeholder explained | Correction to the placeholder taxonomy | `[FV]` "conclusions that treat a planted issue as clean signal" is the losing move this correction prevents · `[S1]` judgment over rubric-matching · `[Integrity]` fixtures rotate, so the catalog is re-derived from this file, not a recycled list |
| ≥3 items not to take at face value, with reasoning | Items that should NOT be taken at face value | `[FV]` "say what they refused to conclude" · `[S1]` strategic judgment · brief item #7 "what stays human" |
| Standalone artifact later tickets reference | Whole doc + Handoff notes | `[S2]` execution detail for ticket 2 · Operating Artifact Requirement (an inspectable record) |

## Provenance

- File: `fixtures/event_sample.jsonl`
- SHA-256: `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235`
  - Reproduce with: `shasum -a 256 fixtures/event_sample.jsonl`
- Lines: 25 physical lines (file ends with a trailing newline).
- Records: 24 JSON records parse successfully; 1 line (file line 21,
  `evt-0020`) fails to parse. See the malformed-record class below.
- Distinct `event_id`s: 23 unique ids across the 24 parseable records
  (`evt-0001` .. `evt-0024`, with `evt-0002` appearing twice).

Brief version worked against: `2026-07` (per `brief.md`).

### Number source labels

Per `SCORING.md` and brief requirement #4, numbers are labeled by source.
Unless a value is tagged otherwise, **every quantity in this document is
`[Observed]`** — read directly from `fixtures/event_sample.jsonl` at the
checksum above, or exact arithmetic on those raw values (timestamp diffs,
counts). Reproduce any of them from the fixture. No `[Estimated]`,
`[Benchmarked]`, or `[Assumed]` numbers appear here; the interpretations
(e.g. "retry", "timezone bug") are labeled inferences, not numbers.

Evidence tier for this artifact: Tier 3 (source record) — findings are
reproducible from the checksummed raw file with `json.loads`.

### Method

Every line was parsed with a real `json.loads` pass. Successful records were
indexed by `event_id`; timestamp fields (`ts`/`timestamp` vs `received_at`)
were diffed; and the `anonymous_id -> tenant_id` and `user_id -> tenant_id`
maps were built to test for cross-tenant reuse. Findings below reflect what
that pass actually observed, not what the spec assumed.

## Correction to the spec's placeholder taxonomy

The spec (recorded during scoping as `docs/adr/to-spec.md` line 59, which is
not itself committed to this scaffold) proposed a nine-class taxonomy and
flagged it as an unverified assumption:

1. duplicate `event_id`
2. out-of-order / clock-skew timestamps
3. missing required fields
4. tenant_id mismatch / spoofing
5. per-tenant volume spike
6. per-tenant volume drop-to-zero
7. impossible field values
8. cross-tenant data leakage
9. unexpected PII

Checked against the actual fixture, that list is partly wrong. Three of its
classes are **not present** and are not testable against this file, and three
classes that **are** genuinely planted were missing from it. The corrected
taxonomy below still totals nine classes, but with a different composition.

Scoring reference: correcting the placeholder rather than shipping it is the
`[FV]` requirement not to "treat a planted issue as clean signal" and not to
make "recommendations the fixture contradicts"; it is `[S1]` judgment over
rubric-matching and `[Integrity]` (this catalog is re-derived from the current
checksummed fixture, not a recycled nine-class assumption).

### Classes dropped from the placeholder (not observed here)

- **tenant_id mismatch / spoofing** and **cross-tenant data leakage** — NOT
  present. Every `anonymous_id` maps to exactly one `tenant_id`, and every
  `user_id` maps to exactly one `tenant_id`. There is no anonymous/user id
  reused across tenants, so no leakage or spoofing signal exists to detect in
  this snapshot. (This was verified by building the id->tenant maps: both
  contained zero multi-tenant keys.)
- **per-tenant volume drop-to-zero** — NOT observable. The fixture is a single
  static snapshot spanning `[Observed]` ~17.5 minutes of `ts` (first event
  `evt-0001` at 14:02:11.104Z, last event `evt-0024` at 14:19:41.088Z), not a
  time series, so a per-tenant rate dropping to zero cannot be seen or tested
  against this file. A volume-collapse detector belongs to streaming/windowed
  data, not to this fixture.
- **impossible field values (generic negative/out-of-range)** — no negative
  counts or out-of-range primitives are planted. `evt-0019` carries
  `count_today: 3`, which is fine. The only genuinely impossible *value* in the
  file is a future-dated timestamp (`evt-0016`), which is better classed under
  timestamp anomalies (below). The generic "negative/impossible primitive"
  class as written has no instance here.

### Classes added (genuinely present, absent from the placeholder)

- **Schema drift / non-conforming event shape** — `evt-0009`.
- **Malformed / corrupt JSON record** — `evt-0020`.
- **Compliance-critical event type requiring workflow action** —
  `evt-0017` (`privacy_request`).

### Corrected nine-class taxonomy

| # | Class | Event(s) | Signal actually observed |
|---|-------|----------|--------------------------|
| 1 | Duplicate `event_id` / idempotency violation | `evt-0002` | Same `event_id` on two records (file lines 2 and 5), identical `ts` and payload, `received_at` differs by ~7.4s. |
| 2 | Out-of-order timestamp (client clock skew) | `evt-0005` | `received_at` (14:04:12.930Z) is ~47s *earlier* than `ts` (14:05:00.120Z). |
| 3 | Systematic timezone offset (not random skew) | `evt-0006` | `ts` (15:11:03.552Z) is exactly ~65 min *ahead* of `received_at` (14:06:03.552Z); millisecond suffix `.552` matches on both. |
| 4 | Future / impossible timestamp | `evt-0016` | `ts` year is 2027 while `received_at` is 2026 (~1 year in the future). |
| 5 | Missing required field (unattributable) | `evt-0011` | `tenant_id` is `null` — event cannot be attributed to a tenant. |
| 6 | Unexpected PII in free-form payload | `evt-0007` | `contact_email` and `phone` embedded in a `custom` event's `properties`, not a dedicated PII-protected field. |
| 7 | Schema drift / non-conforming shape | `evt-0009` | `type` is `pageview` (not `page_view`); uses `timestamp` not `ts`; has no `received_at`; uses `page_path`/`ref` instead of `path`/`referrer`. |
| 8 | Bot / scanner volume-spike burst | `evt-0012`, `evt-0013`, `evt-0014`, `evt-0015` | Four `page_view`s from the same `anonymous_id` (`anon-8fc`), `ts` values 14:10:00.001 → .051Z (~50ms span), each `referrer` `https://scanner.example-bot.net`, hitting `/pricing`,`/features`,`/docs`,`/about` in sequence. |
| 9 | Malformed / corrupt JSON record | `evt-0020` | File line 21 is not valid JSON (missing closing brace); `json.loads` raises, while the file continues validly afterward. |

Compliance-critical event type (`evt-0017`, `privacy_request` /
`delete_all_data` under GDPR) is retained as a distinct concern in the
"not-at-face-value" section: it is not a data-quality *anomaly* to filter, it
is a legal signal that must trigger downstream work. It is called out
explicitly so it is never silently counted as a generic `custom` event.

Net change vs the placeholder:
- Dropped: tenant mismatch/spoofing, cross-tenant leakage, drop-to-zero,
  generic negative/impossible-value class.
- Added: schema drift, malformed JSON record, and (as a workflow concern)
  compliance-critical event type.

## Per-event review

| Line | event_id | tenant | type | Verdict |
|------|----------|--------|------|---------|
| 1 | evt-0001 | t-042 | page_view | Clean baseline. |
| 2 | evt-0002 | t-042 | click | **Duplicate** (see line 5). First delivery. |
| 3 | evt-0003 | t-042 | identify | Clean; associates `anon-9f2` -> `u-5511`. |
| 4 | evt-0004 | t-017 | page_view | Clean; `referrer` null (legitimately optional). |
| 5 | evt-0002 | t-042 | click | **Duplicate of line 2**: identical `ts`/payload; `received_at` +7.4s. Retry, not a second click. |
| 6 | evt-0005 | t-017 | form_submit | **Clock skew**: `received_at` ~47s before `ts`. |
| 7 | evt-0006 | t-088 | page_view | **Timezone bug**: `ts` ~65 min ahead of `received_at`, matching `.552` ms. |
| 8 | evt-0007 | t-042 | custom | **PII** (`contact_email`, `phone`) in `properties`. |
| 9 | evt-0008 | t-017 | identify | Clean; `anon-c81` -> `u-2209`. |
| 10 | evt-0009 | t-042 | pageview | **Schema drift**: wrong type spelling, `timestamp`/`page_path`/`ref`, no `received_at`. |
| 11 | evt-0010 | t-088 | click | Clean. |
| 12 | evt-0011 | (null) | page_view | **Missing `tenant_id`**: unattributable/orphaned. |
| 13 | evt-0012 | t-042 | page_view | **Bot burst** (anon-8fc, scanner referrer). |
| 14 | evt-0013 | t-042 | page_view | **Bot burst**. |
| 15 | evt-0014 | t-042 | page_view | **Bot burst**. |
| 16 | evt-0015 | t-042 | page_view | **Bot burst**. |
| 17 | evt-0016 | t-017 | custom | **Future timestamp**: `ts` in 2027. |
| 18 | evt-0017 | t-088 | privacy_request | **Compliance-critical**: GDPR `delete_all_data` for `u-1077`/`anon-77a`. |
| 19 | evt-0018 | t-017 | page_view | Clean; `anon-c81` -> `u-2209` (consistent with evt-0008). |
| 20 | evt-0019 | t-042 | custom | Clean; `count_today: 3` (valid, not impossible). |
| 21 | evt-0020 | t-088 | click | **Malformed JSON**: missing closing brace; `json.loads` fails. |
| 22 | evt-0021 | t-017 | page_view | Clean. |
| 23 | evt-0022 | t-042 | identify | Clean; `anon-3d0` -> `u-7304`. |
| 24 | evt-0023 | t-088 | form_submit | Clean. |
| 25 | evt-0024 | t-017 | page_view | Clean; `anon-52d` -> `u-8842` (consistent with evt-0016). |

(“Line” is the physical file line. Note the `evt-0002` duplicate on line 5
shifts every subsequent event one line down, so `evt-0020` sits on file line
21, not line 20.)

## Items that should NOT be taken at face value

The brief requires at least three. Six strong candidates were found; all six
are listed so downstream tickets can pick the strongest for the written answer.

Scoring reference for the whole section: this is the `[FV]` bar "say what they
refused to conclude", `[S1]` strategic judgment, and brief item #7 "what stays
human". Each item's own scoring tag is on its last line.

1. **`evt-0006` — do not treat as a real future-dated event.** The `ts` is
   ~65 minutes ahead of `received_at` with an exactly matching `.552`
   millisecond suffix. Random clock drift does not preserve the sub-second
   fraction across a 65-minute gap; this is the fingerprint of a systematic
   timezone/offset bug on the client (e.g. a fixed hour added). The pipeline
   should treat `received_at` as authoritative for ordering rather than
   trusting `ts`, and flag the source for correction — not silently accept a
   65-minute-future event.
   Scoring: `[FV]` refuse to treat a planted signal as clean · `[S1]` judgment.

2. **`evt-0009` — do not simply discard as "broken".** The differences
   (`pageview`, `timestamp`, `page_path`, `ref`, no `received_at`) are
   internally consistent — this looks like a legitimate older-SDK / legacy
   event shape, not random corruption. It should be *normalized* to the current
   schema and stamped with a server-side receive time, not dropped. Dropping it
   would silently lose real traffic from customers on an older SDK — and the
   brief forbids forcing an SDK upgrade.
   Scoring: `[S1]` judgment (normalize vs drop) · brief constraint "cannot
   require customers to update SDK" · `[FailMode]` avoids losing real traffic.

3. **`evt-0017` — do not count as a normal analytics event.** It is a GDPR
   `delete_all_data` mandate for `u-1077`/`anon-77a`, not a page view to
   tally. Taken at face value it would inflate `custom`/event volume and, worse,
   fail a legal obligation. It must route to a compliance workflow that purges
   that subject's *other* events downstream and confirms deletion — a
   human/approved action, not an automated metric increment.
   Scoring: brief item #7 "what stays human" · `[S1]` compliance-as-architecture
   (also scoring_rubric.md failure mode "compliance bolted on later").

4. **`evt-0002` duplicate — do not dedupe on payload+`ts`, and do not treat as
   two clicks.** The two copies share `ts` and payload but differ in
   `received_at` (~7.4s), which is the signature of a client retry after a slow
   or failed ack. Deduplication must key on `event_id` (idempotency key), and
   the pipeline must be idempotent so the retry is absorbed rather than counted
   twice.
   Scoring: `[S2]` execution detail (idempotency key = `event_id`) · `[FailMode]`
   avoids double-counting under retry.

5. **`evt-0011` null `tenant_id` — do not silently drop, and do not default it
   to a tenant.** An unattributable event could indicate SDK misconfiguration
   or an attempted injection. Defaulting it to some tenant would corrupt that
   tenant's data; silently dropping it hides the misconfiguration. It should be
   quarantined/routed for investigation.
   Scoring: `[S1]` judgment (quarantine vs default/drop) · brief "multi-tenant"
   constraint (defaulting corrupts a tenant's data).

6. **`evt-0020` malformed record — do not let it crash the loader, and do not
   silently skip it.** The parse failure is an isolated corrupt record (the file
   is valid before and after it), so the loader must dead-letter this line and
   continue. This is precisely the record ticket 2's fixture loader must
   dead-letter rather than crash on.
   Scoring: `[FailMode]` "one-off demo that only works on the happy path" ·
   `[S2]` execution detail for ticket 2's loader.

## Handoff notes for later tickets

Each handoff outcome carries the scoring reference it is meant to earn once
ticket 2 acts on it, so the thread from this catalog to the graded submission
stays explicit.

- Detection code, CLI, and the unittest suite are ticket 2's scope (blocked by
  this ticket). Ticket 2 should assert against the exact `event_id`s above.
  Scoring: `[S3][Evidence]` a runnable script raises the fixture work to a
  Tier 2/3 operating artifact · `[FV]` "cite specific ids".
- Ticket 2's loader must survive `evt-0020` (file line 21) via dead-lettering,
  and must still yield the 24 parseable records.
  Scoring: `[FailMode]` happy-path-only demo · `[S2]` execution detail.
- Dedup logic must key on `event_id` (`evt-0002` case).
  Scoring: `[S2]` execution detail · `[FailMode]` avoids double-counting.
- The `privacy_request` (`evt-0017`) path is a workflow/compliance concern, not
  a filter — keep it distinct from data-quality anomalies.
  Scoring: `[S1]` compliance-as-architecture · brief item #7 "what stays human".
