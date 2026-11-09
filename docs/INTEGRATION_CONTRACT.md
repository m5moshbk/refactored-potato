# M5mOsH Nexus / Voice Nexus Integration Contract — Initial Draft

**Status:** Internal draft; scope boundary recorded  
**Branch:** `integration/m5mosh-unification-20261107`  
**Owner:** M5mOsH  
**Rights:** © M5mOsH All Rights Reserved

## Repository scope finding

The default branch inspected for this integration branch documents M5mOsH Voice Nexus / صدى الحرف and contains a separate `sada-voice/backend` FastAPI application. The Nexus inventory API was found on the separate branch `feature/nexus-code-inventory-sync`; it is not assumed to be part of this integration branch because this branch was created from `main`.

Do not merge the inventory feature branch or alter deployment configuration as part of this draft. Reconcile those code lines in a separately reviewed change.

## Role in the wider system

- Voice Nexus: accessibility-focused speech and communication services.
- NEXUS inventory: a separately identified project/code inventory component.
- Intelligence: may receive explicitly sanitized project metadata; it must not receive source files or local paths.
- SADA: supplies compact diagnostic observations, not approval decisions.

## Canonical event envelope

The canonical metadata envelope is defined by `contracts/event-envelope.schema.json` (JSON Schema 2020-12). A Voice Nexus liveness observation can use this shape:

```json
{
  "event_id": "evt-voice-health-0001",
  "event_type": "service.health_observed",
  "occurred_at": "2026-11-07T16:00:00Z",
  "correlation_id": "corr-voice-0001",
  "source": {
    "project_id": "m5mosh-voice-nexus",
    "component": "health"
  },
  "classification": "observed",
  "payload": {
    "status": "ok",
    "counts": {"checks": 1},
    "result_code": "LIVENESS_OBSERVED"
  }
}
```

Audio recordings, transcripts, voiceprints, credentials, personal identifiers, source files, and local paths are outside this generic event envelope. A dedicated accessibility/audio data contract requires separate purpose, consent, retention, access, and deletion review.

## Privacy and accessibility requirements

1. Do not include audio recordings, transcripts, voiceprints, credentials, or personal identifiers in generic project-index events.
2. Voice/audio processing needs a dedicated data contract with explicit purpose, consent, retention, access, and deletion requirements.
3. Do not treat voice biometrics as a generic project metadata field.
4. Accessibility features require evaluation with representative users and clear failure states; a prototype is not a validated accessibility service.
5. Only sanitized project metadata may cross into Intelligence or general Nexus indexing.

## Branch and integration rules

- Keep Voice Nexus and inventory API as separately identified components until code ownership and deployment boundaries are reconciled.
- Do not assume inventory API SQLite state is durable on ephemeral hosting storage.
- Do not infer that a lightweight health route verifies database, speech-provider, or authentication readiness.
- Preserve original project history; integration should be additive and reviewable.

## Acceptance checklist

- [ ] Event metadata conforms to the canonical schema.
- [ ] Project references contain no personal or sensitive payload.
- [ ] Voice/audio data remains outside the generic project event envelope.
- [ ] Inventory API branch ancestry and Render service mapping are reviewed separately.
- [ ] No database, secret, hosting, or production configuration is changed by this draft.

## Change control

Documentation and a focused health contract test only. This draft does not alter application behavior, dependencies, database schemas, secrets, or hosting configuration.

---

© M5mOsH All Rights Reserved
