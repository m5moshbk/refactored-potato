# M5mOsH Internal Integration Contract

**Owner:** M5mOsH  
**Status:** Draft for branch review  
**Version:** 0.1.0  
**Branch:** `integration/m5mosh-unification-20261107`  
**Rights:** © M5mOsH All Rights Reserved

## 1. Purpose

This document defines a conservative, metadata-only integration boundary for m5moshbk/refactored-potato. It is a contract proposal, not a claim that runtime integration is already implemented.

## 2. Component responsibility

**Role:** Nexus project index/dashboard and inventory aggregation boundary. Inventory payloads may contain transient paths for validation, but the integration contract must not persist or forward file paths, filenames, or raw contents. Aggregate counters and approved SHA-256 fingerprints are the intended metadata boundary.

The service must keep its existing standalone behavior until an explicit implementation change is reviewed. This contract does not authorize new network calls, database writes, hosting changes, or secret configuration.

## 3. Shared event envelope

The canonical JSON Schema is `contracts/event-envelope.schema.json`. Producers must send only:
- event identity and type;
- UTC timestamp;
- source project and component identifiers;
- evidence classification (`discovered`, `observed`, `verified`, `historical`, or `planned`);
- bounded operational metadata (status, integer counters, SHA-256 fingerprints, duration, result code);
- references to evidence records, without embedding source documents.

The envelope deliberately excludes free-text payloads, file paths, filenames, raw content, credentials, personal data, and arbitrary nested properties. Unknown fields must be rejected, not silently forwarded.

## 4. Security and data boundaries

1. Service-to-service transport must use HTTPS/TLS.
2. Authentication material belongs only in the hosting provider's secret store and approved authorization headers. Never place it in URLs, payloads, commits, test fixtures, or logs.
3. No service may connect directly to another service's database.
4. Do not persist event content or evidence in a new database as part of this draft.
5. Apply least privilege, request-size limits, rate limits, idempotency, and bounded timeouts at the receiving boundary.
6. Treat provider search output as `discovered` until independently checked; do not upgrade evidence classification automatically.
7. Human approval is required before consequential actions such as publishing, payments, account changes, destructive operations, or production writes.

## 5. Initial interaction map

| Producer | Consumer | Initial contract |
|---|---|---|
| Intelligence | Nexus | Analysis summary metadata and evidence references |
| SADA | Control Center / Nexus | Health and diagnostic event metadata |
| Nexus | Intelligence | Allowlisted inventory aggregates and project identifiers |
| All services | Approval Gate | Proposed action metadata only; no implicit execution |

This map is a target interface. It does not assert that these live connections currently exist.

## 6. Reliability and versioning

- Contract version starts at `0.1.0`; incompatible changes require a new major version.
- Use a stable `event_id` and preserve `correlation_id` across retries.
- Consumers must be idempotent; duplicate event IDs must not cause duplicate side effects.
- Event timestamps must be ISO 8601 date-time values in UTC.
- Consumers must reject unsupported contract versions and unknown fields.
- Retries must be bounded and must not bypass authentication or approval controls.

## 7. Current limitations to preserve

- Do not assume in-memory event logs are durable.
- Do not assume process-local rate limits or idempotency controls are distributed across instances.
- Do not assume local SQLite under ephemeral hosting storage is durable.
- Do not claim a health endpoint proves business functionality.
- Do not infer a configured provider is active without a verified, non-billable configuration check or a separately approved test.

## 8. Validation plan

1. Validate the schema as JSON and run the repository's existing test suite.
2. Verify the allowed envelope shape and reject unknown/free-text fields.
3. Add producer/consumer contract tests before implementing runtime calls.
4. Test authentication failure, duplicate event handling, malformed timestamps, oversized payloads, and unknown contract versions.
5. Record test results and evidence; do not publish or deploy from this branch.

## 9. Change boundaries

This branch contains documentation and contract tests only. No production database, secrets, Render service configuration, default branch, deployment, or live integration is changed by this proposal.

---

© M5mOsH All Rights Reserved
