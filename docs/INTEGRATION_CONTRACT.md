# M5mOsH Nexus / Voice Nexus Integration Contract — Initial Draft

**Status:** Internal draft; scope boundary recorded  
**Branch:** integration/m5mosh-unification-20261107  
**Owner:** M5mOsH  
**Rights:** © M5mOsH All Rights Reserved

## Repository scope finding
The default branch inspected for this integration branch documents M5mOsH Voice Nexus / صدى الحرف and contains a separate sada-voice/backend FastAPI application. The Nexus inventory API was found on the separate branch feature/nexus-code-inventory-sync; it is not assumed to be part of this integration branch because this branch was created from main.

Do not merge the inventory feature branch or alter deployment configuration as part of this draft. Reconcile those code lines in a separately reviewed change.

## Role in the wider system
- Voice Nexus: accessibility-focused speech and communication services.
- NEXUS inventory: project and code-inventory metadata, currently maintained on a separate branch/service line.
- Intelligence: may receive explicitly sanitized project metadata; it must not receive source files or local paths.
- SADA: supplies compact diagnostic observations, not approval decisions.

## Proposed cross-service project reference
    {
      "schema_version": "1.0",
      "project_id": "stable-project-id",
      "project_key": "m5mosh-voice-nexus",
      "display_name": "M5mOsH Voice Nexus",
      "capabilities": ["speech-to-text", "accessibility"],
      "lifecycle_state": "prototype",
      "evidence_refs": [],
      "updated_at": "RFC3339-UTC"
    }

## Privacy and accessibility requirements
1. Do not include audio recordings, transcripts, voiceprints, credentials, or personal identifiers in generic project-index events.
2. Voice/audio processing needs a dedicated data contract with explicit purpose, consent, retention, access, and deletion requirements.
3. Do not treat voice biometrics as a generic project metadata field.
4. Accessibility features require evaluation with representative users and clear failure states; a prototype is not a validated accessibility service.
5. Only sanitized project metadata may cross into Intelligence or general Nexus indexing.

## Branch and integration rules
- Keep Voice Nexus and inventory API as separately identified components until code ownership and deployment boundaries are reconciled.
- Do not assume the inventory API SQLite state is durable on an ephemeral filesystem.
- Do not infer that the current Voice Nexus health route verifies database, speech-provider, or authentication readiness.
- Preserve original project history; integration should be additive and reviewable.

## Acceptance checklist
- [ ] Health contract test confirms the current lightweight health response only.
- [ ] Project references contain no personal or sensitive payload.
- [ ] Voice/audio data remains outside the generic project event envelope.
- [ ] Inventory API branch ancestry and Render service mapping are reviewed separately.
- [ ] No database, secret, hosting, or production configuration is changed by this draft.

## Change control
This draft adds documentation and a focused health contract test only. It does not alter application behavior, dependencies, database schemas, secrets, or hosting configuration.
