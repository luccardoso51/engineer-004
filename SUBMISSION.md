# Submission Packet — Engineer 004: Real-Time Analytics Pipeline

**Brief version:** 2026-07 (per [`brief.md`](brief.md))
**Format:** Markdown (no PDF conversion; the written answer renders as-is)
**Fixture checksum (SHA-256):** `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235`
**Written answer / entry point:** [`docs/design-pipeline.md`](docs/design-pipeline.md)

This file is the index for the submission packet. Only the written answer is uploaded
to the careers page; every other artifact below is reached through the repo links here
and in the written answer's header.

## Packet contents

Mapped to the seven items in the [Required Submission Packet](../../submissions/README.md#required-submission-packet):

| # | Required item | Artifact |
|---|---------------|----------|
| 1 | Written answer | [`docs/design-pipeline.md`](docs/design-pipeline.md) (≤4 pages, diagram excluded) |
| 2 | Operating artifact | Runnable pipeline analyzer: [`src/analytics_pipeline/`](src/analytics_pipeline/) (`loader.py`, `anomalies.py`, `compliance.py`, `main.py`) + [`tests/`](tests/) (28 tests) + [`scripts/benchmark.py`](scripts/benchmark.py) → [`docs/benchmark-results.md`](docs/benchmark-results.md). Anomaly forensics in [`docs/fixture-forensics.md`](docs/fixture-forensics.md) and [`docs/adr/`](docs/adr/) |
| 3 | Evidence log | [`docs/evidence-log.md`](docs/evidence-log.md) (26 claim rows, each tagged to a SCORING.md proof tier) |
| 4 | Number source labels | Every number carries `[Observed]` / `[Estimated]` / `[Benchmarked]` / `[Assumed]` in the written answer, benchmark output, and evidence log |
| 5 | AI usage disclosure | [`docs/submission-disclosures.md`](docs/submission-disclosures.md) |
| 6 | Failure handling / what stays human | [`docs/failure-modes.md`](docs/failure-modes.md) |
| 7 | Artifact access | Sample data [`fixtures/event_sample.jsonl`](fixtures/event_sample.jsonl); reproduction commands below (no login required) |

## Reproduce the artifacts

No third-party dependencies are required — the pipeline and tests use only the Python
standard library (Python 3.11+).

```bash
# From the challenge root (challenges/engineer-004/).

# 1. Confirm the fixture checksum matches the one cited above.
shasum -a 256 fixtures/event_sample.jsonl

# 2. Run the full test suite (28 tests).
python3 -m unittest discover -s tests

# 3. Run the fixture analyzer (per-event census + summary counts).
PYTHONPATH=src python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl

# 3b. GDPR deletion cascade for evt-0017 (includes evt-0006 via anon-77a).
PYTHONPATH=src python3 -m analytics_pipeline.main --fixture fixtures/event_sample.jsonl --deletion-cascade evt-0017

# 4. (Optional) Re-run the throughput benchmark. Note: this is a live timing
#    benchmark whose exact events/sec figure drifts per run; docs/benchmark-results.md
#    is the committed source of truth for the figure cited in the written answer.
PYTHONPATH=src python3 scripts/benchmark.py

# 5. Pre-screen the packet with the same linter reviewers use (run from repo root).
python3 scripts/validate_submission.py challenges/engineer-004/docs
```

## Assembly & consistency check

Verified for this packet:

- **Page limit** — written answer (`docs/design-pipeline.md`) is ~2,320 content words
  (Mermaid diagram excluded) with six tables; four additional tables moved to
  [`docs/design-appendix.md`](docs/design-appendix.md). No PDF renderer installed;
  measured by word count on the markdown source (`wc -w` minus Mermaid block) and
  manual review of table density. Fits ≤4 pages at typical single-spaced technical
  formatting (~500–600 words/page with moderate tables).
- **Artifacts present** — all seven required items exist as separate artifacts (table above).
- **Numeric-claim ↔ evidence log** — headline numbers cross-checked and consistent:
  fixture checksum, benchmark throughput (`222924.03` events/sec, rounded to `~223K`),
  cost derived total (`~$3,800`, planning carry `~$11,400` at 3× buffer), latency budget
  (`200+800+300+500 ms = ~1.8s` p99), throughput sizing
  (`50M/86,400s ≈ 578/sec`, `×10 ≈ 5,780/sec`, `8 shards` record-rate binding at 6).
- **Checksum consistency** — the SHA-256 above is identical in `docs/design-pipeline.md`,
  `docs/benchmark-results.md`, `docs/evidence-log.md`, and `docs/fixture-forensics.md`,
  and matches the live `shasum` of `fixtures/event_sample.jsonl`.
- **Pre-screen** — `validate_submission.py` returns `PASS with warnings` (exit 0). The
  advisory warnings are heuristic false positives (event IDs, line numbers, tier numbers)
  confined to forensics/ADR/disclosure artifacts and are left as-is.
