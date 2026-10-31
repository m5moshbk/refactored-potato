# Voice Nexus — Deployment Guide

This repository contains deployment configuration only. No service has been created, changed, or deployed by adding these files.

## 1. API on Render

The root `render.yaml` describes a free web service with automatic deploys disabled.

Before applying the Blueprint:
1. Prepare a PostgreSQL database you are authorized to use and review its cost, retention, backup, and expiry terms. The Blueprint intentionally does not create a database.
2. Set `DATABASE_URL` in the Render service environment to the database's private connection string.
3. Set `CORS_ORIGINS` to the exact deployed frontend origin (no wildcard).
4. Keep the generated `SECRET_KEY` private and do not paste it into chat or source control.
5. Review the service's region, plan, logs, network exposure, and provider terms.

The service start command runs `alembic upgrade head` before Uvicorn. If no valid database URL is supplied, startup should fail rather than silently falling back to an ephemeral local database.

## 2. Frontend on Vercel

Create a Vercel project from this repository and set its **Root Directory** to:

```text
sada-voice/frontend
```

Set this public environment variable:

```text
NEXT_PUBLIC_API_URL=https://YOUR-API-HOST
```

Replace the example with the actual API origin. Then configure the same origin in the API's `CORS_ORIGINS` setting. Do not place secrets in `NEXT_PUBLIC_*` variables.

## 3. Local PostgreSQL

Copy `sada-voice/.env.docker.example` to `sada-voice/.env`, set a strong local database password, then run Docker Compose from `sada-voice/`.

The database port is bound to localhost only. Configure the backend's `DATABASE_URL` to match the chosen local database credentials if you use PostgreSQL instead of the default SQLite development database.

## 4. Release gates

Do not treat a successful health endpoint as production certification. Before public production use, complete:
- API and frontend build checks.
- Database migration and restore testing.
- Authentication abuse/rate-limit review.
- Security headers, HTTPS, CORS, and session review.
- Accessibility and Arabic browser compatibility checks.
- Privacy review for browser speech services.
- Independent evaluation before enabling any voice biometric or anti-spoofing feature.

Voice biometrics and server-side transcription are disabled in this version. The readiness endpoint is advisory and never deploys or modifies code.
