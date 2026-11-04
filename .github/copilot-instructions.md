# M5mOsH repository instructions

## Product truth
M5mOsH Voice Nexus (صدى الحرف) is an Arabic-first accessibility and voice communication MVP. Do not describe server-side speech recognition, speaker verification, anti-spoofing, organization tenancy, or production readiness as implemented unless the code and passing checks prove it.

## Security and privacy
- Never commit credentials, API keys, database URLs containing passwords, personal data, or real user audio.
- Treat audio and voice-derived data as sensitive personal data.
- Do not use file hashes as speaker identity.
- Keep biometric enrollment and verification disabled until consent, revocation/deletion, encryption, anti-spoof evaluation, and FAR/FRR evidence exist.
- Do not add paid providers or paid fallback without explicit approval.
- Review authentication for brute-force protection, account enumeration, password handling, token expiry, and session lifecycle.
- Production configuration must fail closed if secrets, persistent database configuration, or exact CORS origins are missing.

## Engineering quality
- Review API contracts, SQLAlchemy/Alembic parity, PostgreSQL behavior, error handling, and rollback.
- Review Next.js TypeScript correctness, browser compatibility, keyboard accessibility, focus, contrast, and Arabic RTL.
- Keep readiness/self-evaluation deterministic, evidence-based, and non-mutating. Never imply autonomous code changes.
- Prefer small, focused, reviewable changes.
- Do not move or delete legacy files without an explicit task and evidence that they are unused.

## Verification and operations
- Never claim tests, builds, migrations, security reviews, or deployments succeeded without an actual result.
- Keep deployment automation disabled unless the task explicitly authorizes a deployment.
- Do not merge pull requests or modify Render/Vercel services as part of code review.
- Every review finding should include severity, exact path/symbol, evidence, impact, reproduction, a concrete fix, and verification.
