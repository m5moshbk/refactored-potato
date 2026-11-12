import base64
import hashlib
import hmac
import importlib
import json
import sqlite3

import pytest


def load_module(tmp_path, monkeypatch):
    monkeypatch.setenv("SALLA_WEBHOOK_SECRET", "test-webhook-secret")
    monkeypatch.setenv("SALLA_TOKEN_ENCRYPTION_KEY", base64.b64encode(b"K" * 32).decode())
    monkeypatch.setenv("SALLA_TOKEN_DB_PATH", str(tmp_path / "salla-tokens.sqlite3"))
    import salla_control_api.app as module
    importlib.reload(module)
    return module


def signed_headers(raw):
    signature = hmac.new(b"test-webhook-secret", raw, hashlib.sha256).hexdigest()
    return {
        "X-Salla-Security-Strategy": "Signature",
        "X-Salla-Signature": signature,
    }


def authorize_payload(merchant=1234509876):
    return {
        "event": "app.store.authorize",
        "merchant": merchant,
        "created_at": "2026-11-12 05:00:00",
        "data": {
            "access_token": "test-access-token-never-store-plain",
            "expires": 2000000000,
            "refresh_token": "test-refresh-token-never-store-plain",
            "scope": "products.read orders.read offline_access",
            "token_type": "bearer",
        },
    }


def post_signed(client, payload):
    raw = json.dumps(payload, separators=(",", ":")).encode()
    return client.post(
        "/webhooks/salla/partner-app",
        data=raw,
        content_type="application/json",
        headers=signed_headers(raw),
    )


def test_health_is_available():
    import salla_control_api.app as module
    assert module.app.test_client().get("/healthz").status_code == 200


def test_partner_event_rejects_missing_signature(tmp_path, monkeypatch):
    module = load_module(tmp_path, monkeypatch)
    response = module.app.test_client().post(
        "/webhooks/salla/partner-app",
        json=authorize_payload(),
    )
    assert response.status_code == 401


def test_authorize_event_encrypts_and_persists_credentials(tmp_path, monkeypatch):
    module = load_module(tmp_path, monkeypatch)
    response = post_signed(module.app.test_client(), authorize_payload())
    assert response.status_code == 202
    assert response.get_json()["credentials_updated"] is True

    db_path = tmp_path / "salla-tokens.sqlite3"
    raw_db = db_path.read_bytes()
    assert b"test-access-token-never-store-plain" not in raw_db
    assert b"test-refresh-token-never-store-plain" not in raw_db

    with sqlite3.connect(db_path) as con:
        row = con.execute(
            "SELECT token_ciphertext, scopes, expires_at FROM salla_merchant_credentials"
        ).fetchone()
    assert row is not None
    assert row[0] is not None
    assert row[1] == "products.read orders.read offline_access"
    assert row[2] == 2000000000


def test_authorize_event_exact_retry_is_idempotent(tmp_path, monkeypatch):
    module = load_module(tmp_path, monkeypatch)
    client = module.app.test_client()
    payload = authorize_payload()
    first = post_signed(client, payload)
    retry = post_signed(client, payload)
    assert first.status_code == 202
    assert retry.status_code == 200
    assert retry.get_json()["duplicate"] is True
    with sqlite3.connect(tmp_path / "salla-tokens.sqlite3") as con:
        assert con.execute("SELECT COUNT(*) FROM salla_partner_event_receipts").fetchone()[0] == 1


def test_authorize_requires_refresh_token_and_offline_access(tmp_path, monkeypatch):
    module = load_module(tmp_path, monkeypatch)
    payload = authorize_payload()
    payload["data"]["refresh_token"] = ""
    response = post_signed(module.app.test_client(), payload)
    assert response.status_code == 422
    payload = authorize_payload()
    payload["data"]["scope"] = "products.read orders.read"
    response = post_signed(module.app.test_client(), payload)
    assert response.status_code == 422


def test_uninstall_event_revokes_stored_credentials(tmp_path, monkeypatch):
    module = load_module(tmp_path, monkeypatch)
    client = module.app.test_client()
    assert post_signed(client, authorize_payload()).status_code == 202
    response = post_signed(client, {
        "event": "app.uninstalled",
        "merchant": 1234509876,
        "created_at": "2026-11-12 05:05:00",
        "data": {"app_name": "M5mOsH"},
    })
    assert response.status_code == 202
    with sqlite3.connect(tmp_path / "salla-tokens.sqlite3") as con:
        row = con.execute(
            "SELECT token_ciphertext, revoked_at FROM salla_merchant_credentials"
        ).fetchone()
    assert row[0] is None
    assert row[1]


def test_bad_signature_does_not_create_database(tmp_path, monkeypatch):
    module = load_module(tmp_path, monkeypatch)
    response = module.app.test_client().post(
        "/webhooks/salla/partner-app",
        data=b'{"event":"app.store.authorize"}',
        content_type="application/json",
        headers={
            "X-Salla-Security-Strategy": "Signature",
            "X-Salla-Signature": "0" * 64,
        },
    )
    assert response.status_code == 401
    assert not (tmp_path / "salla-tokens.sqlite3").exists()


@pytest.mark.parametrize("bad_payload", [
    {"event": "app.store.authorize", "merchant": 0, "data": {}},
    {"event": "app.store.authorize", "merchant": 123, "data": {"access_token": "x"}},
])
def test_invalid_authorize_payload_is_rejected(tmp_path, monkeypatch, bad_payload):
    module = load_module(tmp_path, monkeypatch)
    response = post_signed(module.app.test_client(), bad_payload)
    assert response.status_code == 422


def test_token_storage_fails_closed_without_encryption_key(tmp_path, monkeypatch):
    monkeypatch.setenv("SALLA_WEBHOOK_SECRET", "test-webhook-secret")
    monkeypatch.delenv("SALLA_TOKEN_ENCRYPTION_KEY", raising=False)
    monkeypatch.setenv("SALLA_TOKEN_DB_PATH", str(tmp_path / "salla-tokens.sqlite3"))
    import salla_control_api.app as module
    importlib.reload(module)
    response = post_signed(module.app.test_client(), authorize_payload())
    assert response.status_code == 503
