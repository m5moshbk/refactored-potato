import importlib

ALLOWED_ORIGIN = "https://m5mosh-nexus.onrender.com"


def load_app(tmp_path, monkeypatch):
    monkeypatch.setenv("INVENTORY_DB_PATH", str(tmp_path / "inventory.sqlite3"))
    monkeypatch.setenv("INGEST_TOKEN", "ci-test-ingest-token")
    import inventory_api.app as module
    return importlib.reload(module)


def test_status_allows_only_the_nexus_dashboard_origin(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    response = module.app.test_client().get(
        "/api/v1/status",
        headers={"Origin": ALLOWED_ORIGIN},
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert response.headers["Vary"] == "Origin"
    assert response.headers["Cache-Control"] == "no-store"


def test_status_does_not_allow_an_untrusted_origin(tmp_path, monkeypatch):
    module = load_app(tmp_path, monkeypatch)
    response = module.app.test_client().get(
        "/api/v1/status",
        headers={"Origin": "https://untrusted.example"},
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers


def test_inventory_preflight_allows_expected_headers_for_nexus_origin(
    tmp_path, monkeypatch
):
    module = load_app(tmp_path, monkeypatch)
    response = module.app.test_client().options(
        "/api/v1/inventory",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 204
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert response.headers["Access-Control-Allow-Methods"] == "POST, OPTIONS"
    assert response.headers["Access-Control-Allow-Headers"] == "Authorization, Content-Type"


def test_inventory_preflight_does_not_allow_an_untrusted_origin(
    tmp_path, monkeypatch
):
    module = load_app(tmp_path, monkeypatch)
    response = module.app.test_client().options(
        "/api/v1/inventory",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    assert response.status_code == 204
    assert "Access-Control-Allow-Origin" not in response.headers
