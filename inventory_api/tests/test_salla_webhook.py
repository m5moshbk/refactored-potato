import hashlib
import hmac
import importlib
import json
import sqlite3


def load_salla_app(tmp_path, monkeypatch, *, mode="token", token="ci-salla-test-token", secret=""):
    monkeypatch.setenv("SALLA_WEBHOOK_DB_PATH", str(tmp_path / "salla.sqlite3"))
    monkeypatch.setenv("SALLA_WEBHOOK_AUTH_MODE", mode)
    monkeypatch.setenv("SALLA_WEBHOOK_TOKEN", token)
    monkeypatch.setenv("SALLA_WEBHOOK_SECRET", secret)
    import inventory_api.app as module
    importlib.reload(module)
    return module


def token_headers(token="ci-salla-test-token"):
    return {"X-M5mOsH-Webhook-Token": token}


def signature_headers(raw_body, secret="ci-salla-signature-secret"):
    signature = hmac.new(
        secret.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()
    return {
        "X-Salla-Security-Strategy": "Signature",
        "X-Salla-Signature": signature,
    }


def test_salla_webhook_fails_closed_when_token_is_not_configured(tmp_path, monkeypatch):
    module = load_salla_app(tmp_path, monkeypatch, token="")
    response = module.app.test_client().post(
        "/webhooks/salla",
        json={"event": "product.created"},
        headers=token_headers(""),
    )

    assert response.status_code == 503
    assert response.get_json()["error"] == "not_configured"


def test_salla_webhook_requires_custom_token_header(tmp_path, monkeypatch):
    module = load_salla_app(tmp_path, monkeypatch)
    response = module.app.test_client().post(
        "/webhooks/salla",
        json={"event": "product.created"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_salla_webhook_rejects_wrong_custom_token(tmp_path, monkeypatch):
    module = load_salla_app(tmp_path, monkeypatch)
    response = module.app.test_client().post(
        "/webhooks/salla",
        json={"event": "product.created"},
        headers=token_headers("wrong-token"),
    )

    assert response.status_code == 401


def test_salla_webhook_accepts_event_and_persists_metadata_only(tmp_path, monkeypatch):
    module = load_salla_app(tmp_path, monkeypatch)
    client = module.app.test_client()
    body = {
        "event": "customer.created",
        "data": {
            "customer": {
                "name": "Private Customer",
                "email": "private@example.test",
                "mobile": "+966500000000",
            }
        },
    }
    raw_body = json.dumps(body, separators=(",", ":")).encode("utf-8")

    response = client.post(
        "/webhooks/salla",
        data=raw_body,
        content_type="application/json",
        headers=token_headers(),
    )

    assert response.status_code == 202
    assert response.get_json()["accepted"] is True
    assert response.get_json()["stored_payload"] is False

    db_path = tmp_path / "salla.sqlite3"
    with sqlite3.connect(db_path) as con:
        rows = con.execute(
            "SELECT payload_sha256, event_name, received_at "
            "FROM salla_webhook_receipts"
        ).fetchall()

    assert len(rows) == 1
    assert rows[0][1] == "customer.created"
    stored_bytes = db_path.read_bytes()
    assert b"private@example.test" not in stored_bytes
    assert b"+966500000000" not in stored_bytes
    assert b"Private Customer" not in stored_bytes


def test_salla_webhook_deduplicates_exact_retries(tmp_path, monkeypatch):
    module = load_salla_app(tmp_path, monkeypatch)
    client = module.app.test_client()
    raw_body = b'{"event":"product.created","data":{"id":123}}'

    first = client.post(
        "/webhooks/salla",
        data=raw_body,
        content_type="application/json",
        headers=token_headers(),
    )
    retry = client.post(
        "/webhooks/salla",
        data=raw_body,
        content_type="application/json",
        headers=token_headers(),
    )

    assert first.status_code == 202
    assert first.get_json()["duplicate"] is False
    assert retry.status_code == 200
    assert retry.get_json()["duplicate"] is True

    with sqlite3.connect(tmp_path / "salla.sqlite3") as con:
        count = con.execute(
            "SELECT COUNT(*) FROM salla_webhook_receipts"
        ).fetchone()[0]
    assert count == 1


def test_salla_webhook_signature_mode_verifies_exact_raw_body(tmp_path, monkeypatch):
    secret = "ci-salla-signature-secret"
    module = load_salla_app(
        tmp_path, monkeypatch, mode="signature", secret=secret
    )
    raw_body = b'{ "event" : "product.created", "data" : {"id": 7} }'

    response = module.app.test_client().post(
        "/webhooks/salla",
        data=raw_body,
        content_type="application/json",
        headers=signature_headers(raw_body, secret),
    )

    assert response.status_code == 202
    assert response.get_json()["event"] == "product.created"


def test_salla_webhook_signature_mode_rejects_invalid_signature(tmp_path, monkeypatch):
    module = load_salla_app(
        tmp_path,
        monkeypatch,
        mode="signature",
        secret="ci-salla-signature-secret",
    )
    response = module.app.test_client().post(
        "/webhooks/salla",
        json={"event": "product.created"},
        headers={
            "X-Salla-Security-Strategy": "Signature",
            "X-Salla-Signature": "0" * 64,
        },
    )

    assert response.status_code == 401


def test_salla_webhook_signature_mode_requires_signature_strategy(tmp_path, monkeypatch):
    module = load_salla_app(
        tmp_path,
        monkeypatch,
        mode="signature",
        secret="ci-salla-signature-secret",
    )
    raw_body = b'{"event":"product.created"}'
    signature = hmac.new(
        b"ci-salla-signature-secret", raw_body, hashlib.sha256
    ).hexdigest()

    response = module.app.test_client().post(
        "/webhooks/salla",
        data=raw_body,
        content_type="application/json",
        headers={"X-Salla-Signature": signature},
    )

    assert response.status_code == 401


def test_salla_webhook_rejects_non_json_body(tmp_path, monkeypatch):
    module = load_salla_app(tmp_path, monkeypatch)
    response = module.app.test_client().post(
        "/webhooks/salla",
        data="event=product.created",
        content_type="application/x-www-form-urlencoded",
        headers=token_headers(),
    )

    assert response.status_code == 415
