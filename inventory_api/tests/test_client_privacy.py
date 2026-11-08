import json

from inventory_api.client_pythonista import NoRedirectHandler, build_payload


def test_client_transmits_synthetic_metadata_not_local_file_details():
    original_path = "/private/var/mobile/Documents/Client Projects/secret.py"
    original_name = "secret.py"
    original_modified = "2026-11-08T10:00:00+03:00"
    report = {
        "report_time": "2026-11-08T10:05:00+03:00",
        "files": [{
            "path": original_path,
            "extension": ".py",
            "size_bytes": 987654,
            "modified": original_modified,
        }],
        "added_since_previous_scan": [],
        "changed_since_previous_scan": [],
        "missing_from_current_scan": [],
        "errors": [],
    }

    payload = build_payload(report)
    serialized = json.dumps(payload)

    assert payload["files"] == [{
        "path": "aggregate/item_00001.py",
        "extension": ".py",
        "size_bytes": 0,
        "modified": "",
    }]
    assert payload["root_label"] == "Pythonista aggregate code inventory (synthetic paths)"
    assert original_path not in serialized
    assert original_name not in serialized
    assert original_modified not in serialized
    assert "987654" not in serialized


def test_client_skips_non_code_file_extensions():
    payload = build_payload({
        "files": [
            {"path": "data/archive.sqlite3", "extension": ".sqlite3"},
            {"path": "src/module.py", "extension": ".py"},
        ]
    })

    assert len(payload["files"]) == 1
    assert payload["files"][0]["path"] == "aggregate/item_00001.py"


def test_client_rejects_redirects_before_forwarding_bearer_token():
    handler = NoRedirectHandler()
    assert handler.redirect_request(
        req=None,
        fp=None,
        code=302,
        msg="Found",
        headers={},
        newurl="https://unexpected.example/collect",
    ) is None
