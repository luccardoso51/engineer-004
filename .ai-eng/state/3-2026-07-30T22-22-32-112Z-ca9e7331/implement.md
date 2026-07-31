Comparing the design doc with SCORING.md and aligning it with the rubric. Reading both documents and the repo context.
Aligning the design doc with SCORING.md: adding visible sizing math, failure-design detail, and the required submission-packet artifacts (evidence log, disclosures).
Addressing code review findings: fixing labels, deduplicating content, and adding CCPA controls.
What I built: Enhanced docs/design-pipeline.md for SCORING.md alignment — visible throughput sizing math (578 avg / 5,780 peak events/sec, 30-shard headroom), failure degradation folded into zero-data-loss section, CCPA access/opt-out controls, migration parallel-run cost note, labeled operational thresholds, and operating-artifact cross-references. Added docs/evidence-log.md (claim-to-tier mapping with reproduction steps) and docs/submission-disclosures.md (AI usage, what breaks it, what stays human).

Assumptions: Parallel-run legacy cost is sunk during months 1–3; CCPA opt-out implemented via tenant do_not_sell flag suppressing warehouse sync; Kinesis 1,000 rec/s/shard from AWS public service limits.

Test results: 26 passed, 0 failed (pytest). No mypy configured.

Code review: Standards — fixed duplicate throughput math, unlabeled thresholds, and Benchmarked tag clarity; Spec — all ticket acceptance criteria met, full SCORING submission packet now present via companion docs.

How to test it yourself:
1. Open docs/design-pipeline.md and confirm three brief sections plus throughput sizing, compliance (including CCPA row), and migration validation.
2. Open docs/evidence-log.md and docs/submission-disclosures.md for the full submission packet items 3, 5–7.
3. Run shasum -a 256 fixtures/event_sample.jsonl and verify checksum 1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235 appears in the design doc header.
4. Run pytest -q (expect 26 passed) and python3 scripts/benchmark.py to regenerate docs/benchmark-results.md.
5. Scan the fixture anomaly table for all nine classes plus evt-0017 with cited event_ids.