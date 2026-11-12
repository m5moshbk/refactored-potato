# M5mOsH Salla OAuth Refresh Worker — Design Gate

> Status: design only; no worker or outbound OAuth request is implemented.
> Mode: read-only planning; synthetic credentials only.
> Owner: M5mOsH
> Rights: © M5mOsH All Rights Reserved

## Objective

Refresh a merchant's Salla access token without ever using one refresh token concurrently or more than once. Salla documents refresh tokens as single-use, with the previous refresh token invalidated after successful rotation. Reuse can revoke the associated access token and require the merchant to reinstall the app.

## Verified provider facts

- Token endpoint: `https://accounts.salla.sa/oauth2/token`.
- Access tokens expire after 14 days.
- Refresh tokens last one month and are single-use.
- A successful refresh issues a new access token and a new refresh token; the previous refresh token becomes invalid.
- Salla explicitly recommends a mutex/locking mechanism to prevent parallel refresh attempts.
- Easy Mode authorization events can deliver new token pairs after app authorization/update.

Official references:
- Authorization and refresh lifecycle: https://docs.salla.dev/421118m0
- Refresh-token reuse response behavior: https://docs.salla.dev/421123m0

## Request-schema gate

The public authorization page confirms the endpoint and lifecycle but the currently rendered refresh request-body section does not expose all field-level details. Do not guess or hardcode a request payload. Before implementing the HTTP client, verify the exact current request fields, content type, client authentication method, and response schema from Salla's current API reference or a controlled demo-store/Postman request. Never use a real merchant token for this verification.

## Required state model

Each merchant must have a durable state row with at least:
- `merchant_id` (unique)
- encrypted access token and encrypted refresh token
- access-token expiry timestamp
- lifecycle status: `connected`, `refreshing`, `refresh_uncertain`, `reauthorization_required`, or `revoked`
- refresh lease owner / fencing token / lease expiry
- monotonically increasing local credential version
- last successful refresh timestamp and last sanitized error code

All token ciphertext must remain application-encrypted (AES-256-GCM) with keys held outside the database. Never store plaintext tokens, client secrets, or full provider responses in logs.

## Safe refresh algorithm

1. A worker selects only merchants whose access token is nearing expiry and whose state is `connected`.
2. In a short database transaction, acquire a per-merchant lease using an atomic conditional update. Increment a fencing/version value and record the lease expiry. If another worker owns a valid lease, stop without making a provider request.
3. Read and decrypt the current refresh token only inside the worker process. Do not expose it to the dashboard or API response.
4. Send exactly one refresh request to the verified Salla token endpoint. Never launch a parallel request for the same merchant.
5. On a definitive successful response, validate both new tokens and expiry, encrypt both, then atomically replace the old token pair and update expiry/version/state in one database transaction. Commit only if the lease fencing token still matches.
6. Release the lease. Emit a sanitized audit event containing merchant ID, result category, timestamp, and credential version only.
7. If Salla returns a definitive invalid/revoked grant, set `reauthorization_required`; do not retry the old token.
8. If the request times out or the connection fails after the request may have reached Salla, set `refresh_uncertain`. Do not retry the old refresh token: Salla may already have consumed it. Require a new Easy Mode authorization unless provider evidence proves the request was not processed.
9. If the worker crashes after Salla rotates the token but before the new pair is durably committed, treat the credential state as uncertain and require reauthorization. Do not assume the old token remains valid.
10. On `app.uninstalled`, atomically revoke the merchant, clear token ciphertext, and invalidate any outstanding refresh lease/fencing token.

## Concurrency and database requirements

- Use managed PostgreSQL for production state; SQLite is a local prototype only.
- Use row-level locking or an atomic compare-and-swap lease, plus a fencing token. A process-local mutex alone is insufficient across multiple service instances.
- Never hold a database transaction open during the network request.
- Add a unique merchant constraint and atomic credential-pair rotation.
- Use bounded connection/read timeouts; never blindly retry a refresh POST after an ambiguous network outcome.
- Queue retries only for operations known not to have reached Salla. Distinguish safe pre-send failures from ambiguous post-send failures.

## Mandatory tests before implementation approval

- Two workers racing for one merchant: exactly one obtains the lease and sends a request.
- Two different merchants can refresh independently.
- A stale worker cannot commit after its lease/fencing token has been superseded.
- Successful refresh atomically replaces both tokens and expiry.
- Invalid grant transitions to `reauthorization_required`.
- Timeout-after-send transitions to `refresh_uncertain` and never reuses the old refresh token.
- Crash simulation between provider success and DB commit is handled as uncertain.
- Uninstall invalidates the lease and prevents a late worker from restoring credentials.
- Logs, errors, metrics, and audit events contain no token or client-secret material.

## Current status

- Design completed.
- Refresh request field-level schema: **not yet verified**.
- Worker implementation: **not started**.
- PostgreSQL adapter and distributed lease: **not implemented**.
- Live Salla OAuth call: **not performed**.
- Production readiness: **blocked** until all required tests and infrastructure gates pass.

© M5mOsH All Rights Reserved
