# Salla Control API — Deployment Readiness Evidence

> Checked: 2026-11-12
> Mode: Render read-only inventory review
> No Render resources or settings were changed.

## Current resource findings

| Resource | Observed state | Suitability |
|---|---|---|
| Render Postgres `M5` (`dpg-db4e6gijnfac73b3kf7g-a`) | Free plan; status suspended; suspenders include billing; expiry recorded as 2026-11-08; public IP allow-list `0.0.0.0/0` | **Not usable** for Salla credentials or durable events until separately restored/replaced and access restricted |
| Render Key Value `M5-Frankfurt` (`red-db4dsiu7bikc73ee1br0`) | Available; Free; persistence mode `off`; LRU eviction | **Not suitable** as durable OAuth token/event storage |
| `m5mosh-nexus-inventory-api` (`srv-db7ejh5g1s2s73a85otg`) | Existing web service; branch `feature/nexus-code-inventory-sync`; auto-deploy enabled; public IP allow-list | **Do not reuse** for the Salla Control API; it is the Inventory API deployment target |
| Salla Control API | No dedicated Render service found in the returned service inventory | Not deployed |

## Required deployment topology

1. A dedicated Salla Control API service sourced from `salla_control_api/`, not the Inventory API service.
2. A durable encrypted managed PostgreSQL database for merchant credentials, event receipts, refresh locks, audit records, and queue/outbox state.
3. A separate worker for serialized refresh-token rotation and event processing.
4. A static or separately served dashboard with strong operator authentication.
5. Private network/database access where supported; remove broad public database access and apply least-privilege credentials.
6. Store Salla webhook signature secret, AES-256-GCM encryption key, session-signing secret, and database credentials in the service secret manager only.

## Release blockers

- The existing M5 Postgres resource is suspended and expired; do not point the Salla app at it.
- The available Key Value resource has persistence disabled and an eviction policy; do not store OAuth credentials there.
- The existing Inventory API service auto-deploys from the PR base branch; do not merge PR #33 into that branch as a way to deploy the Salla API.
- The Salla Control API is not production-ready: token refresh locking/rotation, replay ordering protection, managed database adapter, operator auth/RBAC, merchant API client, dashboard API, audit controls, and operational monitoring remain incomplete.

## Safe next infrastructure action

Prepare a separate Render Blueprint/service and database plan with auto-deploy disabled initially. Review exact resource type, region, plan/cost, network exposure, backup/restore, and environment variable names before approval. Do not create or approve the infrastructure until the plan is presented and explicitly accepted.

## Rights

© M5mOsH All Rights Reserved
