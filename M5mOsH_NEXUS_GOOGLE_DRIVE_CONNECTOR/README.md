# M5mOsH Nexus Google Drive Connector — MOCK

**Version:** 0.1.0  
**Mode:** MOCK only  
**Rights:** © M5mOsH All Rights Reserved

## Purpose

A local, deterministic prototype for validating Google Drive metadata models, policy gates, in-memory indexing, pagination, and folder hierarchy. It does not connect to Google Drive.

## Safety boundary

- No Google OAuth, API client, HTTP requests, network access, or credentials.
- No filesystem scanning, upload, download, move, delete, or persistent database.
- Only synthetic metadata supplied by the caller is accepted.
- Policy permits only MOCK metadata reads and in-memory indexing.
- A future live connector requires a separate design and explicit approval.

## Layout

- `src/nexus_drive/models.py`: validated immutable metadata model.
- `src/nexus_drive/policy.py`: explicit operation allow-list.
- `src/nexus_drive/indexer.py`: atomic in-memory indexing, generation-aware pagination, hierarchy validation.
- `tests/`: model, policy, and indexer tests.

## Requirements

Python 3.10 or newer. Runtime code uses only the Python standard library. Pytest is needed for tests.

## Run locally

From this directory:

```bash
python -m pip install -e ".[test]"
python -m pytest -q
```

## Pagination contract

A page token is `generation:offset`. Any successful index mutation increments the generation. A token from an older generation raises `StalePageTokenError` instead of silently mixing different index snapshots.

## Status

This is a MOCK prototype. Passing tests validates local code behavior only; it does not validate Google APIs, OAuth, Render deployment, or production readiness.
