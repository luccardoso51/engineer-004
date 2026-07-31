What I built: Expanded docs/evidence-log.md from 11 headline rows to 24 rubric-aligned claim clusters covering fixture grounding, benchmark validation, throughput/latency/cost sizing, migration/reliability, failure design, compliance, architecture trade-offs, and scope discipline. Reserved Tier 3 for local benchmark output and fixture-derived census counts (no Tier 4). Applied inline [Observed]/[Estimated]/[Benchmarked]/[Assumed] tags to every quantitative figure across docs/design-pipeline.md, docs/benchmark-results.md, docs/evidence-log.md, and docs/submission-disclosures.md. Fixed scripts/benchmark.py and docs/benchmark-results.md to label local measurements [Observed] instead of [Benchmarked]. Reworded the throughput claim to detect_anomalies() subroutine throughput (~223K events/sec rounded; exact 222924.03 events/sec) vs peak ingest (~5,780 events/sec [Estimated]). Added Artifact access section with reproduction commands. Cross-checked design doc cost (~$42,000) and latency (~1.8s p99) against evidence log row 24.

Assumptions: Benchmark timings vary per machine run; committed values are from the final local run on this workstation. Month-phase references (months 1–3, 4–6) and event IDs were left untagged per ticket guidance. Author prior-experience claim (row 23) labeled [Assumed] rather than [Observed].

Test results: pytest 26 passed, 0 failed; validate_submission.py on the four packet docs — all checks PASS (required sections, verifiability, number labels, evidence tiers, brief version).

Code review: Standards — fixed shard-count mislabeling ([Benchmarked]→[Estimated] for 30 shards), duplicate tag, and TLS label; Spec — all acceptance criteria met after fixes; minor residual duplication of reproduction commands accepted for readability.

How to test it yourself:
1. cd to the repo root and run: python3 /Users/lucasrodrigues/Projetos/beat-claude/scripts/validate_submission.py docs/design-pipeline.md docs/evidence-log.md docs/submission-disclosures.md docs/benchmark-results.md — expect Result: PASS with no warnings.
2. Run pytest -q — expect 26 passed.
3. Run python3 scripts/benchmark.py — regenerates docs/benchmark-results.md with [Observed]-tagged timings and census counts.
4. Open docs/evidence-log.md — confirm 24 substantive claim rows, Tier 3 rows 1–4 and 20 trace to benchmark/fixture commands, row 24 cross-checks design doc figures.
5. Open docs/design-pipeline.md — confirm inline source labels on cost table (~$42,000), latency budget (~1.8s p99), and throughput (~223K events/sec rounded).