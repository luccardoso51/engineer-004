Title: Fixture forensics & anomaly taxonomy

Identifier: #1

What to build: the real, event_id-cited catalog of what's actually planted in fixtures/event_sample.jsonl, correcting the spec's placeholder nine-class taxonomy (which the spec itself flagged as an unverified assumption) against what's actually in the file, plus the fixture's sha256 checksum and the brief-required write-up of items that should not be taken at face value.

Blocked by: None — can start immediately

- [ ] sha256 checksum of fixtures/event_sample.jsonl computed and recorded
- [ ] Every event in the fixture reviewed; anomaly signals actually present cataloged and cited by event_id
- [ ] Corrected anomaly taxonomy documented, noting where it diverges from the original placeholder list and why
- [ ] At least three fixture items identified that should not be taken at face value, with reasoning per item
- [ ] Findings written as a standalone artifact that later tickets can reference