# M5mOsH Salla Control API — Partner Event Foundation

> State: isolated implementation foundation; not production-ready or connected to a store.
> Owner: M5mOsH
> Rights: © M5mOsH All Rights Reserved

## Purpose

This service is separate from `inventory_api`. It receives Salla Partner App lifecycle events and safely stores the credentials delivered by the `app.store.authorize` event.

Salla's documented Easy Mode flow sends the authorization result through the app webhook. The documented payload includes `merchant`, `created_at`, and `data.access_token`, `data.refresh_token`, `data.expires`, `data.scope`, and `data.token_type`.

## Implemented

- `GET /healthz`: basic process health only.
- `POST /webhooks/salla/partner-app`: Salla Signature strategy only.
- Verifies `X-Salla-Security-Strategy: Signature` and `X-Salla-Signature` against HMAC-SHA256 of the raw request bytes using `SALLA_WEBHOOK_SECRET`.
- Accepts `app.store.authorize` only when merchant ID, access token, refresh token, expiry, bearer type, and `offline_access` scope are valid.
- Encrypts access and refresh tokens using AES-256-GCM before persistence. The encryption key is supplied separately from the database.
- Records exact-body delivery fingerprints for retry suppression.
- Handles `app.uninstalled` by clearing encrypted token material and marking the merchant disconnected.
- Does not return or log token values.

## Required configuration

Do not deploy until all of these are provisioned in a secret manager / service environment:

- `SALLA_WEBHOOK_SECRET`: the signature secret configured for the Salla Partner App webhook.
- `SALLA_TOKEN_ENCRYPTION_KEY`: Base64 encoding of exactly 32 cryptographically random bytes. Generate locally:
  ```bash
  python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
  ```
- `SALLA_TOKEN_DB_PATH`: absolute path on a durable encrypted disk for the SQLite prototype. Do not use `/tmp`.

The service fails closed if a required secret or durable database path is absent. Never place any secret in GitHub, source files, the browser, or a chat message.

## Important limits — not production ready

1. This is a token-ingestion foundation, not a complete OAuth or merchant control API.
2. No access-token refresh worker exists. Salla refresh tokens are single-use; a serialized refresh lock and atomic rotation must be implemented before the first access token expires.
3. No authenticated operator session, RBAC, dashboard API, Salla Merchant API client, or action-approval service exists yet.
4. No managed PostgreSQL integration, backup/restore, queue, dead-letter handling, or operational alerting exists yet.
5. Exact-body hashing suppresses exact retries only. The public event contract documents `created_at` and `merchant` but does not establish a universal delivery ID. A stale signed authorization event replay after a later uninstall is not fully prevented yet; add and test monotonic event sequencing/replay policy before production.
6. The service has not been deployed, connected to a demo store, or tested against a live Salla Partner App.
7. The SQLite path must be replaced with managed PostgreSQL or a verified durable encrypted volume before production.

## Verification

The isolated tests use synthetic credentials only. They must prove:
- invalid/missing signature is rejected before database creation;
- `app.store.authorize` persists encrypted data, not plaintext;
- exact retry is idempotent;
- refresh token and `offline_access` are required;
- `app.uninstalled` clears stored credentials;
- missing encryption key fails closed.

GitHub Actions runs these tests separately from the Inventory API test suite.

## Official Salla references

- Authorization / Easy Mode / token lifecycle: https://docs.salla.dev/421118m0
- Partner App event catalog and `app.store.authorize` payload: https://docs.salla.dev/421413m0
- Webhook signature headers and delivery retries: https://docs.salla.dev/421119m0

## Rights

© M5mOsH All Rights Reserved
