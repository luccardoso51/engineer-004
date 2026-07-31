# Domain glossary

Brief version: 2026-07. Fixture checksum (SHA-256): `1aeb24b415009e89fcf8acb5a178410faf216dc17b16920d9849ecc8bbb24235`.

## Core entities

Event — A single SDK-emitted behavioral record (page view, click, form submission, custom event, or compliance signal). Identified by `event_id`. Carries client timestamp (`ts`), server receipt time (`received_at`), `tenant_id`, and `anonymous_id` for stitching.

Tenant — A customer organization in the multi-tenant platform (~500+). All analytics data is scoped by `tenant_id`; unattributable events (null `tenant_id`) are quarantined, never defaulted to a tenant.

Anonymous identity — The `anonymous_id` assigned by the SDK; used for session-scoped behavior tracking and stitching before explicit user identification.

## Anomaly classes (fixture-grounded)

Duplicate event_id — Retry delivering the same `event_id` twice; absorbed idempotently by dedupe on `event_id`, not payload+timestamp. Example: evt-0002.

Clock skew — Client `ts` materially after `received_at` due to client clock error. Example: evt-0005.

Timezone offset — Systematic `ts` offset (e.g. wrong timezone) with matching sub-second fraction on both timestamps. Example: evt-0006; not a real future event.

Future timestamp — `ts` impossibly ahead of `received_at` (e.g. wrong year). Example: evt-0016.

Unattributable event — Missing required `tenant_id`; quarantined, not silently dropped or assigned. Example: evt-0011.

PII in properties — Unexpected personally identifiable information in free-form event properties; detected, redacted before hot-path storage, raw copy quarantined. Example: evt-0007.

Schema drift — Legacy SDK field names/shapes differing from canonical schema; normalized, not dropped (no forced SDK upgrade). Example: evt-0009.

Bot burst — High-velocity scanner/bot traffic from a single anonymous identity; flagged and excluded from hot-path rollups and personalization triggers; retained in cold storage for audit. Examples: evt-0012–evt-0015.

Malformed record — Unparseable JSON at ingest; dead-lettered; loader must not crash. Example: evt-0020.

## Compliance signals (not data-quality anomalies)

Privacy request — A compliance mandate (e.g. delete_all_data) routed to a dedicated compliance workflow, never counted in analytics volume. Example: evt-0017.

## Delivery concepts

Hot path — Sub-5-second read layer for dashboards and personalization triggers (live counters, rollup tiles).

Cold path — Durable, replayable storage for audit, warehouse export, and batch analytics.

Quarantine — Encrypted, restricted-access storage for events or payloads that must not enter analytics (PII raw copies, null tenant_id, compliance-adjacent rejects).

Dead-letter queue (DLQ) — Durable holding area for records that fail validation or parsing; enables replay without blocking the pipeline.
