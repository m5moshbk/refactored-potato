import importlib
import json

import pytest


def load_app(tmp_path, monkeypatch, token="ci-test-ingest-token"):
    monkeypatch.setenv("INVENTORY_DB_PATH", str(tmp_path / "inventory.sqlite3"))
    monkeypatch.setenv("INGEST_TOKEN", token)
    import inventory_api.app as module
    importlib.reload(module)
    return module


def metadata(path="src/main.py", size_bytes=123):
    return {
        "path": path,
        "extension": ".py",
        "size_bytes": size_bytes,
        "modified": "2026-10-28T00:00:00Z",
    }


def payload(files=None, **overrides):
    body = {
        "checked_at": "2026-10-28T00:00:00Z",
        "root_label": "Pythonista accessible code folders",
        "files": [metadata()] if files is None else files,
        "new_count": 1,
        "changed_count": 2,
        "missing_count": 0,
        "error_count": 0,
    }
    body.update(overrides)
    return body


def ingest(client, body, token="ci-test-ingest-token"):
    return client.post(
        "/api/v1/inventory",
        headers={"Authorization": f"Bearer {token}"},
        json=body,
    )


def test_health_root_and_empty_status(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()

    assert client.get("/").status_code == 200
    health = client.get("/healthz")
    assert health.status_code == 200
    assert health.get_json()["ok"] is True

    status = client.get("/api/v1/status")
    assert status.status_code == 200
    assert status.get_json()["connected"] is False


def test_ingest_fails_closed_when_token_missing(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch, token="")
    response = module.app.test_client().post(
        "/api/v1/inventory", json=payload()
    )
    assert response.status_code == 503
    assert response.get_json()["error"] == "ingestion_not_configured"


def test_ingest_requires_bearer_token(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    response = module.app.test_client().post(
        "/api/v1/inventory", json=payload()
    )
    assert response.status_code == 401


def test_valid_ingest_stores_aggregate_only(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    client = module.app.test_client()
    response = ingest(client, payload())

    assert response.status_code == 202
    assert response.get_json()["stored_file_paths"] is False
    assert response.get_json()["stored_source_contents"] is False

    status = client.get("/api/v1/status")
    data = status.get_json()
    assert data["connected"] is True
    assert data["file_count"] == 1
    assert data["extension_counts"] == {".py": 1}
    assert data["new_count"] == 1
    assert data["changed_count"] == 2
    assert data["stored_file_paths"] is False
    assert data["stored_source_contents"] is False
    assert "src/main.py" not in json.dumps(data)


@pytest.mark.parametrize(
    "bad_path",
    [
        "/absolute/main.py",
        r"\absolute\main.py",
        r"C:\temp\main.py",
        "src/../secret.py",
        "./src/main.py",
        r"src\main.py",
        "src//main.py",
    ],
)
def test_ingest_rejects_non_normalized_or_absolute_paths(
    tmp_path, monkeypatch, bad_path
):
    module = load_app(tmp_path, monkeypatch)
    response = ingest(module.app.test_client(), payload(files=[metadata(bad_path)]))
    assert response.status_code == 400
    assert response.get_json()["error"] == "path_must_be_relative"


def test_ingest_rejects_boolean_as_file_size(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    response = ingest(
        module.app.test_client(),
        payload(files=[metadata(size_bytes=True)]),
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_size"


def test_ingest_rejects_unexpected_fields(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    body = payload()
    body["source_contents"] = "must not be accepted"
    response = ingest(module.app.test_client(), body)
    assert response.status_code == 400
    assert response.get_json()["error"] == "unexpected_fields"


def test_ingest_rejects_invalid_metadata_schema(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    item = metadata()
    item["source"] = "unexpected"
    response = ingest(module.app.test_client(), payload(files=[item]))
    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_file_metadata_schema"
