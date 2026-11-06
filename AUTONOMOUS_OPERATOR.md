# M5mOsH Autonomous Operator — Nexus

**Status:** Implementation foundation / review required  
**Date:** 2026-11-03  
**Scope:** Nexus repository and its development workflow  
**Rights:** © M5mOsH All Rights Reserved

## Operating objective

Maintain continuity for M5mOsH Nexus, inspect the current project state, select the highest-value safe task, implement bounded improvements, run relevant tests, and prepare evidence for review.

## Standing authority granted

The operator may perform these actions without requesting a separate approval for each routine step:

- Read repository files, commit history, pull requests, workflow results, and available Render service metadata.
- Create isolated development branches.
- Edit application code, tests, documentation, and non-production development configuration on those branches.
- Run local or CI tests, static checks, and non-destructive validation.
- Fix low-risk defects when the expected behavior is supported by tests or documented requirements.
- Commit changes to the isolated development branch and open or update a pull request for review.
- Record evidence, risks, blockers, and the next action.

## Mandatory approval gates

The operator must stop and request a separate, specific approval before:

- Merging any pull request, especially into `main` or `feature/nexus-code-inventory-sync`.
- Triggering, changing, or approving a production deployment.
- Changing Render service settings, environment variables, secrets, domains, access rules, billing, or account permissions.
- Reading or modifying production customer data, production databases, migrations, backups, or persistent storage.
- Deleting, suspending, resuming, restarting, or replacing any service, resource, branch, file, or data.
- Performing an irreversible or externally consequential action.

## Nexus-specific deployment boundary

The Render service `m5mosh-nexus-inventory-api` is configured to follow branch `feature/nexus-code-inventory-sync` with automatic deployment enabled.

Therefore:

1. Do all autonomous code work on a separate branch.
2. Open pull requests against `feature/nexus-code-inventory-sync` for review.
3. Do not merge those pull requests without explicit approval; merging would update the branch watched by Render and may trigger deployment.
4. Do not change the Render configuration to bypass this boundary.

The static `m5mosh-nexus` dashboard follows `main`. Changes to `main` also require explicit approval before merge.

## Execution loop

1. Restore the latest verified continuity notes and inspect repository/service state.
2. Separate confirmed evidence from historical notes, assumptions, and untested claims.
3. Choose one bounded task with clear acceptance criteria.
4. Create or reuse an isolated development branch.
5. Implement the smallest safe change and add or update regression tests.
6. Run the relevant test suite and inspect the complete diff.
7. Record exact commit, test result, CI evidence, risks, and remaining uncertainty.
8. Open a pull request for human review; do not merge or deploy.
9. Resume from the last verified checkpoint on the next run.

## Evidence and reporting

Use these labels consistently: `VERIFIED`, `USER_REPORTED`, `NEEDS_VERIFICATION`, `IN_PROGRESS`, `BLOCKED`, `PROPOSED`, and `NOT_TESTED`.

Never treat a successful build or a Render deployment marked `live` as proof that all application features or data integrations work. Never print secret values, tokens, database URLs, or credentials. If a tool or test is unavailable, report that limitation instead of implying success.

## Current baseline

- Repository: `m5moshbk/refactored-potato`
- Inventory API service branch: `feature/nexus-code-inventory-sync`
- Inventory API service: `m5mosh-nexus-inventory-api`
- Render auto-deploy for that service: enabled
- Current approved execution mode: automatic routine tests and development-branch edits; review required for merge and deployment.

## Next work items

1. Reconcile `inventory_api/STATUS.md` with the merged PR #9 and current deployed commit.
2. Verify CI on the latest relevant commit rather than relying on historical run references.
3. Evaluate the ephemeral SQLite default under `/tmp`; document the data-loss risk and present persistence options without changing production storage.
4. Add tests for stale status, malformed timestamps, and service behavior where requirements are clear.
5. Keep the inventory API and static dashboard release paths separate until explicitly reviewed.
