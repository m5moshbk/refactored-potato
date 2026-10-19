# Nexus Code Inventory API

Authenticated metadata-only ingest endpoint for the Pythonista inventory client.

- `POST /api/v1/inventory`: requires `Authorization: Bearer <INGEST_TOKEN>`.
- `GET /api/v1/status`: aggregate summary only.
- `GET /healthz`: health check.
- Only allow-listed code extensions accepted.
- Rejects unexpected fields and absolute/traversal paths.
- Stores aggregate counts only; file paths and source contents are not stored.
- Set `INGEST_TOKEN` in the service environment.
- SQLite defaults to `/tmp/nexus_inventory.sqlite3`; storage may be ephemeral on Render unless a persistent disk is configured.
- Start command: `gunicorn -w 1 -b 0.0.0.0:$PORT inventory_api.app:app`.
