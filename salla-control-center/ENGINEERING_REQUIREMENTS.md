# M5mOsH Salla Control Center — Engineering Requirements

> Status: design baseline for implementation; not a live integration.
> Target store: `https://salla.sa/botektop.com`
> Related gateway review: PR #33 — `feat/salla-webhook-gateway-20261112`
> Owner: M5mOsH
> Rights: © M5mOsH All Rights Reserved

## 1. Product outcome

Deliver one responsive Arabic-first web control center for the merchant to inspect and manage the connected Salla store remotely. The UI must never imply that a capability is connected or successful until the backend confirms it from Salla.

The control center is a separate product surface from the existing Nexus Inventory API. The inventory API remains dedicated to code-inventory summaries; it is not the Salla business-data store.

## 2. Integration model — two separate concerns

### 2.1 Partner App and OAuth (required for Merchant API access)

A merchant-facing control center that reads or writes store resources must be registered as a Salla Partner App and obtain merchant consent through OAuth 2.0. Never ask for or store the merchant's Salla password.

Required implementation stages:
1. Create a Private Salla Partner App for the M5mOsH-controlled store integration, subject to the Partner account's eligibility and Salla's app rules.
2. Register a stable HTTPS callback URL and the selected OAuth mode.
3. Request only the minimum scopes needed for the first usable release; expand only when a feature is approved and justified.
4. Use OAuth `state` with cryptographically random, single-use, short-lived server-side state to prevent CSRF and replay.
5. Exchange the authorization code server-side only. Never expose client secret, access token, or refresh token to browser JavaScript.
6. Encrypt tokens at rest with a managed secret/key. Redact tokens from logs and error reports.
7. Refresh tokens server-side, handle revoked/expired authorization, and provide a disconnect/revoke path.
8. Bind every stored credential to the verified Salla merchant/store identity returned by the authorized flow; do not trust a browser-supplied store identifier.

OAuth endpoints documented by Salla:
- Authorization: `https://accounts.salla.sa/oauth2/auth`
- Token: `https://accounts.salla.sa/oauth2/token`
- User info: `https://accounts.salla.sa/oauth2/user/info`
- Merchant API base: `https://api.salla.dev/admin/v2`

Salla documents OAuth scopes as the boundary for merchant data access. The exact scope strings must be copied from the current endpoint documentation for each implemented operation; do not guess scope names or request a blanket set.

### 2.2 Webhook receiver (event notifications, not an API credential)

The existing PR #33 adds a separate `POST /webhooks/salla` receiver. A webhook is a notification channel; it does not grant the dashboard permission to list or mutate merchant resources. Keep webhook authentication separate from OAuth.

Salla documents:
- Signature headers: `X-Salla-Security-Strategy` and `X-Salla-Signature`.
- Custom Token strategy is also supported.
- Signature verification must be performed before trusting/parsing the event.
- Acknowledge quickly, enqueue verified events, and process asynchronously/idempotently.
- Salla may retry unsuccessful deliveries; duplicate handling is required.

The current PR is an initial receipt-only gateway. It does not yet provide a durable queue, event processing, API synchronization, or a live merchant connection. Do not configure the store webhook to point at this endpoint until the PR has been reviewed, separately deployed, supplied with a durable database path, and verified with a controlled test delivery.

## 3. Feature modules and operation policy

| Module | Initial capability | Mutating actions |
|---|---|---|
| Overview | Store connection state, daily totals, alerts | None |
| Orders | List, search, detail, timeline, status | Explicit preview + confirmation |
| Products | List, search, details, status, price, SKU | Explicit preview + confirmation |
| Inventory | Current quantities and low-stock view | Explicit preview + confirmation |
| Customers | Search and view permitted customer fields | Restricted; no bulk export by default |
| Shipments | Shipment state and tracking | Explicit preview + confirmation |
| Payments/refunds | Read transaction/payment state where scoped | High-risk; separate confirmation |
| Reports | Sales/order/product summaries | None |
| Webhook monitor | Event receipts, failures, duplicate counts | No store mutation |
| Audit | Actor, action, target, before/after summary, timestamp, result | Append-only |

All actions must be allow-listed server-side. The browser must not be able to select arbitrary API paths, HTTP methods, or scopes. Never expose a generic unrestricted proxy to Salla APIs.

## 4. Approval and audit model

- Default mode is read-only.
- Every write operation requires a server-issued, short-lived action preview bound to the authenticated user, target resource, intended values, and idempotency key.
- The final execution request must revalidate permissions and the preview; it must not trust client-supplied before-state.
- High-impact operations (refunds, cancellations, deleting products/customers, bulk price/quantity changes, shipping cancellation, store-wide settings) require an additional explicit confirmation and must be excluded from bulk automation by default.
- Record successful and failed attempts without storing secrets or unnecessary customer PII.
- Use role-based access control and least privilege. Require strong authentication for the control center itself.
- Provide session expiry, CSRF protection, secure cookies, rate limits, and account disconnect.

## 5. Data and reliability requirements

- Use a durable database for OAuth credentials, event receipts, job state, and audit records. Do not use `/tmp` for production state.
- Separate secrets from database records where feasible; encrypt tokens at rest and restrict decryption to the backend service.
- Store only the minimum customer/order information needed for the feature and retention period.
- Redact phone, email, address, access tokens, refresh tokens, signatures, and webhook secrets from logs.
- Webhook handler: authenticate raw bytes, validate schema/size, persist receipt and enqueue atomically, return a fast 2xx only after durable acceptance.
- Queue workers: retry transient errors with bounded exponential backoff; dead-letter terminal failures; preserve event ordering where the operation requires it.
- Idempotency: prefer Salla event/delivery identifiers when documented and present. Do not use body hash as the sole business-event identity; retain it only as a payload fingerprint/fallback.
- Reconcile missed events through scoped API reads and incremental sync; webhooks alone are not a complete source of truth.
- Respect Salla rate limits and pagination requirements. Use bounded concurrency and backoff.

## 6. Deployment topology

Recommended separation:
1. `salla-control-api`: private business API, OAuth callback, session/auth, Salla API client, policy engine.
2. `salla-control-worker`: asynchronous event and sync processing.
3. `salla-control-web`: Arabic RTL responsive dashboard.
4. Managed PostgreSQL: durable multi-tenant records, OAuth token ciphertext, webhook receipts, queue/outbox, audit trail.
5. Secret manager/environment: OAuth client secret, encryption key, session signing key, webhook secret.

Do not attach this project to the existing `m5mosh-nexus-inventory-api` Render service. The existing service is on a Render auto-deploy branch; merging PR #33 into its base may deploy that service. A new service topology and its environment/disk/database changes require a separate release plan.

## 7. Acceptance gates

### Gate A — OAuth foundation
- OAuth state tests: missing, mismatched, expired, replayed.
- Callback validates state and handles provider errors.
- Authorization code exchange is server-side; no secrets in HTML, browser storage, URLs, or logs.
- Merchant identity and granted scopes are persisted and shown accurately.
- Token refresh, expiry, revocation, and disconnect are tested.

### Gate B — webhook reliability
- Official Salla signature/token verification tests using documented headers and raw request bytes.
- Invalid signature, invalid JSON, oversized payload, duplicate delivery, database outage, and retry behavior tests.
- Durable receipt + queue transaction; quick acknowledgement only after durable acceptance.
- No raw payload or PII in logs.

### Gate C — dashboard and read-only API
- Arabic RTL, responsive mobile/desktop, accessible labels and keyboard support.
- Explicit loading/empty/error/disconnected states; never fabricate store data.
- Read-only orders/products/inventory first, scoped by actual OAuth grants.
- Pagination, rate limits, and bounded query windows covered.

### Gate D — controlled writes
- Server-side allow-listed operations only.
- Preview/confirm workflow and audit trail.
- Tests prove unapproved or replayed writes are rejected.
- High-risk actions require step-up confirmation.

### Gate E — production readiness
- Separate service and durable database.
- Secrets configured out of source control.
- Health/readiness checks, backups, restore test, monitoring, alerting, and rollback plan.
- Controlled test-store install and webhook delivery before connecting the target store.
- Production deployment and target-store authorization are separate approval gates.

## 8. Current verified status (2026-11-12)

- PR #33 exists and is open as a draft.
- Its current gateway implementation has receipt-only behavior and exact-body fingerprint deduplication.
- The PR description records 23 passing tests on head `d994ce9d65a22335be07fa91c31f9905bae9fc12`; no live Salla delivery or HTTP test was performed.
- The Render service `m5mosh-nexus-inventory-api` is configured to deploy from `feature/nexus-code-inventory-sync` with auto-deploy enabled. Do not merge PR #33 without evaluating this deployment coupling.
- OAuth, the dashboard UI, a durable queue, API resource synchronization, and controlled write actions are not implemented by PR #33.
- No target-store webhook has been saved or activated and no production service has been deployed for this integration.

## 9. Official references

- Salla Platform Docs — Get Started: https://docs.salla.dev/
- Salla Platform Docs — Authorization: https://docs.salla.dev/421118m0
- Salla Platform Docs — Webhooks and security headers: https://docs.salla.dev/421119m0
- Salla Playbook — Core Development and reliable webhook handling: https://docs.salla.dev/2316085m0
- Salla Merchant API — List Orders: https://docs.salla.dev/orders/list

## الحقوق

© M5mOsH All Rights Reserved
