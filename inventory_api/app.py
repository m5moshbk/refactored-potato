import os
import json
import hmac
import sqlite3
from datetime import datetime, timezone
from collections import Counter
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024

DB_PATH = os.environ.get("INVENTORY_DB_PATH", "/tmp/nexus_inventory.sqlite3")
INGEST_TOKEN = os.environ.get("INGEST_TOKEN", "")
ALLOWED_ORIGIN = "https://m5mosh-nexus.onrender.com"
ALLOWED_EXTENSIONS = {
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini",
    ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd",
    ".sql", ".php", ".rb", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".dart",
    ".lua", ".pl", ".r", ".ipynb", ".xml"
}

def connect():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    parent = os.path.dirname(DB_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS latest_summary (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                checked_at TEXT NOT NULL,
                received_at TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                extension_counts TEXT NOT NULL,
                new_count INTEGER NOT NULL,
                changed_count INTEGER NOT NULL,
                missing_count INTEGER NOT NULL,
                error_count INTEGER NOT NULL,
                root_label TEXT NOT NULL
            )
        """)

def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def cors(response):
    origin = request.headers.get("Origin", "")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Vary"] = "Origin"
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.after_request
def add_headers(response):
    return cors(response)

@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"ok": True, "service": "M5mOsH Nexus code inventory API"})

@app.route("/api/v1/status", methods=["GET"])
def status():
    with connect() as con:
        row = con.execute("SELECT * FROM latest_summary WHERE id=1").fetchone()
    if row is None:
        return jsonify({
            "connected": False,
            "message": "لم تصل مزامنة من Pythonista بعد",
            "service": "nexus-code-inventory"
        })
    return jsonify({
        "connected": True,
        "checked_at": row["checked_at"],
        "received_at": row["received_at"],
        "file_count": row["file_count"],
        "extension_counts": json.loads(row["extension_counts"]),
        "new_count": row["new_count"],
        "changed_count": row["changed_count"],
        "missing_count": row["missing_count"],
        "error_count": row["error_count"],
        "root_label": row["root_label"],
        "stored_file_paths": False,
        "stored_source_contents": False
    })

@app.route("/api/v1/inventory", methods=["POST", "OPTIONS"])
def receive_inventory():
    if request.method == "OPTIONS":
        response = make_response("", 204)
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        return response

    if not INGEST_TOKEN:
        return jsonify({"error": "ingestion_not_configured"}), 503

    supplied = request.headers.get("Authorization", "")
    expected = "Bearer " + INGEST_TOKEN
    if not hmac.compare_digest(supplied, expected):
        return jsonify({"error": "unauthorized"}), 401

    if not request.is_json:
        return jsonify({"error": "json_required"}), 415

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "invalid_json"}), 400

    # Strict allow-list: file/source content and arbitrary fields are rejected.
    allowed_top = {
        "checked_at", "root_label", "files",
        "new_count", "changed_count", "missing_count", "error_count"
    }
    if set(data) - allowed_top:
        return jsonify({"error": "unexpected_fields", "accepted_fields": sorted(allowed_top)}), 400

    files = data.get("files")
    if not isinstance(files, list) or len(files) > 5000:
        return jsonify({"error": "files_must_be_list_max_5000"}), 400

    extension_counts = Counter()
    for item in files:
        if not isinstance(item, dict) or set(item) != {
            "path", "extension", "size_bytes", "modified"
        }:
            return jsonify({"error": "invalid_file_metadata_schema"}), 400

        path = item.get("path")
        ext = item.get("extension")
        size = item.get("size_bytes")
        modified = item.get("modified")

        # Only relative, normalized paths. Never accept absolute paths or traversal.
        if not isinstance(path, str) or not path or len(path) > 500:
            return jsonify({"error": "invalid_relative_path"}), 400
        if path.startswith(("/", "\\\\")) or ".." in path.replace("\\\\", "/").split("/"):
            return jsonify({"error": "path_must_be_relative"}), 400
        if not isinstance(ext, str) or ext.lower() not in ALLOWED_EXTENSIONS:
            return jsonify({"error": "extension_not_allowed"}), 400
        if not isinstance(size, int) or size < 0 or size > 2**63 - 1:
            return jsonify({"error": "invalid_size"}), 400
        if not isinstance(modified, str) or len(modified) > 64:
            return jsonify({"error": "invalid_modified_time"}), 400
        extension_counts[ext.lower()] += 1

    def bounded_count(key):
        value = data.get(key, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value > 100000:
            raise ValueError(key)
        return value

    try:
        new_count = bounded_count("new_count")
        changed_count = bounded_count("changed_count")
        missing_count = bounded_count("missing_count")
        error_count = bounded_count("error_count")
    except ValueError:
        return jsonify({"error": "invalid_event_count"}), 400

    checked_at = data.get("checked_at")
    if not isinstance(checked_at, str) or len(checked_at) > 64:
        return jsonify({"error": "invalid_checked_at"}), 400

    root_label = data.get("root_label", "Pythonista accessible code folders")
    if not isinstance(root_label, str) or len(root_label) > 80:
        return jsonify({"error": "invalid_root_label"}), 400

    # Deliberately discard all paths and file metadata after validating the payload.
    summary = (
        checked_at, utc_now(), len(files),
        json.dumps(dict(extension_counts), ensure_ascii=False),
        new_count, changed_count, missing_count, error_count, root_label
    )
    init_db()
    with connect() as con:
        con.execute("""
            INSERT INTO latest_summary
            (id, checked_at, received_at, file_count, extension_counts,
             new_count, changed_count, missing_count, error_count, root_label)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
              checked_at=excluded.checked_at,
              received_at=excluded.received_at,
              file_count=excluded.file_count,
              extension_counts=excluded.extension_counts,
              new_count=excluded.new_count,
              changed_count=excluded.changed_count,
              missing_count=excluded.missing_count,
              error_count=excluded.error_count,
              root_label=excluded.root_label
        """, summary)

    return jsonify({
        "accepted": True,
        "file_count": len(files),
        "stored_file_paths": False,
        "stored_source_contents": False,
        "received_at": summary[1]
    }), 202

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
