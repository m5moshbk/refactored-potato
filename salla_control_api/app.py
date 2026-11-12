import base64
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024

SIGNATURE_HEADER = "X-Salla-Signature"
STRATEGY_HEADER = "X-Salla-Security-Strategy"
MAX_BODY_BYTES = 512 * 1024
AAD_PREFIX = b"M5mOsH:SallaOAuth:v1:"


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError("integration_not_configured")
    return value


def _encryption_key():
    encoded = _required_env("SALLA_TOKEN_ENCRYPTION_KEY")
    try:
        key = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise RuntimeError("invalid_encryption_key") from exc
    if len(key) != 32:
        raise RuntimeError("invalid_encryption_key")
    return key


def _database_path():
    path = _required_env("SALLA_TOKEN_DB_PATH")
    if path == ":memory:" or not os.path.isabs(path):
        raise RuntimeError("durable_absolute_database_path_required")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path


def _connect():
    return sqlite3.connect(_database_path(), timeout=10)


def _event_created_at(payload):
    """Parse Salla's event timestamp and normalize it to UTC microseconds."""
    value = payload.get("created_at")
    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        raise ValueError("invalid_event_timestamp")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("invalid_event_timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.astimezone(timezone.utc).timestamp() * 1_000_000)


def init_db():
    with _connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS salla_merchant_credentials (
                merchant_id TEXT PRIMARY KEY,
                token_ciphertext BLOB,
                scopes TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                token_type TEXT NOT NULL,
                connected_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                revoked_at TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS salla_merchant_event_state (
                merchant_id TEXT PRIMARY KEY,
                last_event_at INTEGER NOT NULL,
                last_event_name TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS salla_partner_event_receipts (
                payload_sha256 TEXT PRIMARY KEY,
                event_name TEXT NOT NULL,
                merchant_id TEXT NOT NULL,
                received_at TEXT NOT NULL
            )
        """)


def verify_signature(raw_body):
    secret = _required_env("SALLA_WEBHOOK_SECRET")
    strategy = request.headers.get(STRATEGY_HEADER, "").strip().lower()
    supplied = request.headers.get(SIGNATURE_HEADER, "").strip().lower()
    if strategy != "signature" or len(supplied) != 64:
        return False
    try:
        int(supplied, 16)
    except ValueError:
        return False
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(supplied, expected)


def encrypt_tokens(merchant_id, access_token, refresh_token):
    key = _encryption_key()
    nonce = os.urandom(12)
    plaintext = json.dumps(
        {"access_token": access_token, "refresh_token": refresh_token},
        separators=(",", ":"),
    ).encode("utf-8")
    ciphertext = AESGCM(key).encrypt(
        nonce, plaintext, AAD_PREFIX + merchant_id.encode("ascii")
    )
    return nonce + ciphertext


def _validate_authorize_payload(payload):
    merchant = payload.get("merchant")
    if isinstance(merchant, bool) or not isinstance(merchant, (str, int)):
        raise ValueError("invalid_merchant")
    merchant_id = str(merchant).strip()
    if not merchant_id.isdigit() or int(merchant_id) <= 0:
        raise ValueError("invalid_merchant")

    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("invalid_token_payload")

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    expires = data.get("expires")
    scopes = data.get("scope")
    token_type = data.get("token_type", "bearer")

    if not isinstance(access_token, str) or not access_token or len(access_token) > 8192:
        raise ValueError("invalid_token_payload")
    if not isinstance(refresh_token, str) or not refresh_token or len(refresh_token) > 8192:
        raise ValueError("refresh_token_required")
    if not isinstance(expires, int) or isinstance(expires, bool) or expires <= 0:
        raise ValueError("invalid_expiry")
    if not isinstance(scopes, str) or len(scopes) > 4096:
        raise ValueError("invalid_scopes")
    if "offline_access" not in scopes.split():
        raise ValueError("offline_access_required")
    if not isinstance(token_type, str) or token_type.lower() != "bearer":
        raise ValueError("unsupported_token_type")

    return merchant_id, access_token, refresh_token, expires, scopes, "bearer"


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "m5mosh-salla-partner-events"})


@app.post("/webhooks/salla/partner-app")
def receive_partner_event():
    raw_body = request.get_data(cache=True, as_text=False)
    if len(raw_body) > MAX_BODY_BYTES:
        return jsonify({"error": "payload_too_large"}), 413

    try:
        authenticated = verify_signature(raw_body)
    except RuntimeError:
        return jsonify({"error": "integration_not_configured"}), 503
    if not authenticated:
        return jsonify({"error": "unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "json_required"}), 415
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return jsonify({"error": "invalid_json"}), 400
    if not isinstance(payload, dict):
        return jsonify({"error": "json_object_required"}), 400

    event_name = payload.get("event")
    merchant = payload.get("merchant")
    if not isinstance(event_name, str) or not event_name.strip():
        return jsonify({"error": "invalid_event"}), 400
    if isinstance(merchant, bool) or not isinstance(merchant, (str, int)):
        return jsonify({"error": "invalid_merchant"}), 400
    merchant_id = str(merchant).strip()
    if not merchant_id.isdigit() or int(merchant_id) <= 0:
        return jsonify({"error": "invalid_merchant"}), 400

    event_name = event_name.strip()
    if event_name in {"app.store.authorize", "app.uninstalled"}:
        try:
            event_time = _event_created_at(payload)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
    else:
        event_time = None
    payload_hash = hashlib.sha256(raw_body).hexdigest()
    received_at = utc_now()

    try:
        if event_name == "app.store.authorize":
            values = _validate_authorize_payload(payload)
            merchant_id, access_token, refresh_token, expires, scopes, token_type = values
            encrypted = encrypt_tokens(merchant_id, access_token, refresh_token)
        else:
            encrypted = None
            expires = 0
            scopes = ""
            token_type = "bearer"

        init_db()
        with _connect() as con:
            inserted = con.execute(
                """INSERT OR IGNORE INTO salla_partner_event_receipts
                   (payload_sha256, event_name, merchant_id, received_at)
                   VALUES (?, ?, ?, ?)""",
                (payload_hash, event_name[:120], merchant_id, received_at),
            ).rowcount == 1

            if not inserted:
                return jsonify({"accepted": True, "duplicate": True}), 200

            # Salla lifecycle events can arrive late or be replayed. Apply only
            # strictly newer events for each merchant; equal timestamps are
            # ambiguous because the public payload has no universal sequence ID.
            if event_time is not None:
                previous = con.execute(
                    "SELECT last_event_at FROM salla_merchant_event_state WHERE merchant_id=?",
                    (merchant_id,),
                ).fetchone()
                if previous is not None and event_time <= previous[0]:
                    return jsonify({
                        "accepted": True,
                        "duplicate": False,
                        "ignored": "stale_or_ambiguous_event",
                    }), 202
                con.execute(
                    """INSERT INTO salla_merchant_event_state
                       (merchant_id, last_event_at, last_event_name, updated_at)
                       VALUES (?, ?, ?, ?)
                       ON CONFLICT(merchant_id) DO UPDATE SET
                         last_event_at=excluded.last_event_at,
                         last_event_name=excluded.last_event_name,
                         updated_at=excluded.updated_at""",
                    (merchant_id, event_time, event_name, received_at),
                )

            if event_name == "app.store.authorize":
                con.execute(
                    """INSERT INTO salla_merchant_credentials
                       (merchant_id, token_ciphertext, scopes, expires_at,
                        token_type, connected_at, updated_at, revoked_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                       ON CONFLICT(merchant_id) DO UPDATE SET
                         token_ciphertext=excluded.token_ciphertext,
                         scopes=excluded.scopes,
                         expires_at=excluded.expires_at,
                         token_type=excluded.token_type,
                         updated_at=excluded.updated_at,
                         revoked_at=NULL""",
                    (
                        merchant_id, encrypted, scopes, expires, token_type,
                        received_at, received_at,
                    ),
                )
            elif event_name == "app.uninstalled":
                con.execute(
                    """UPDATE salla_merchant_credentials
                       SET token_ciphertext=NULL, scopes='', expires_at=0,
                           revoked_at=?, updated_at=?
                       WHERE merchant_id=?""",
                    (received_at, received_at, merchant_id),
                )
    except (RuntimeError, sqlite3.Error, OSError):
        return jsonify({"error": "secure_storage_unavailable"}), 503
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    # Never return, log, or persist the received OAuth token values in plaintext.
    return jsonify({
        "accepted": True,
        "duplicate": False,
        "event": event_name,
        "merchant": merchant_id,
        "credentials_updated": event_name == "app.store.authorize",
        "connection_revoked": event_name == "app.uninstalled",
    }), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
