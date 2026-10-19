# Render deployment — approval gate

This API is intentionally not wired into the existing Nexus static site yet.

1. Create a separate Render Web Service from this repository and branch.
2. Set Root Directory to the repository root.
3. Build Command: `pip install -r inventory_api/requirements.txt`
4. Start Command: `gunicorn -w 1 -b 0.0.0.0:$PORT inventory_api.app:app`
5. Set `INGEST_TOKEN` to a long random secret in Render Environment. Never commit it.
6. Optional: set `INVENTORY_DB_PATH` to a path on a persistent disk. Without a persistent disk, SQLite under /tmp can be lost on restart.
7. Verify `/healthz` and `/api/v1/status`. A successful health check is not proof of a successful Pythonista sync.
8. Do not attach a custom domain or alter the existing static Nexus service until explicitly approved.
