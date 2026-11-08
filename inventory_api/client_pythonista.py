# Pythonista client: send privacy-minimized aggregate metadata only.
# Original local paths, filenames, file sizes, and modification times are never sent.
# Set API_URL and INGEST_TOKEN locally before running. Never commit/share the token.

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from urllib.parse import urlsplit

API_URL = ""  # e.g. https://YOUR-API.onrender.com/api/v1/inventory
INGEST_TOKEN = ""  # enter locally in Pythonista; do not commit/share
REPORT_PATH = os.path.expanduser(
    "~/Documents/M5mOsH_Control/CodeInventory/code_inventory.json"
)
INTERVAL_SECONDS = 300
MAX_FILES = 5000

ALLOWED_EXTENSIONS = {
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini",
    ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd",
    ".sql", ".php", ".rb", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".dart",
    ".lua", ".pl", ".r", ".ipynb", ".xml"
}


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject redirects so the Bearer token is never forwarded to another host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_payload(report):
    if not isinstance(report, dict):
        raise ValueError("Inventory report must be a JSON object.")

    source_files = report.get("files", [])
    if not isinstance(source_files, list):
        raise ValueError("Inventory report files must be a list.")

    files = []
    skipped = 0
    for item in source_files:
        if not isinstance(item, dict):
            skipped += 1
            continue

        # Read the original path locally only to infer an extension when needed.
        extension = item.get("extension")
        if not isinstance(extension, str) or not extension.strip():
            original_path = item.get("path", "")
            extension = (
                os.path.splitext(str(original_path))[1]
                if isinstance(original_path, str) else ""
            )

        extension = extension.strip().lower()
        if extension and not extension.startswith("."):
            extension = "." + extension
        if extension not in ALLOWED_EXTENSIONS:
            skipped += 1
            continue

        if len(files) >= MAX_FILES:
            raise ValueError("More than 5,000 code files found; sync stopped.")

        # Synthetic identifier only. No original path, name, size, or mtime leaves the device.
        files.append({
            "path": "aggregate/item_{:05d}{}".format(len(files) + 1, extension),
            "extension": extension,
            "size_bytes": 0,
            "modified": ""
        })

    return {
        "checked_at": str(report.get("report_time") or now())[:64],
        "root_label": "Pythonista aggregate code inventory (synthetic paths)",
        "files": files,
        "new_count": len(report.get("added_since_previous_scan", [])),
        "changed_count": len(report.get("changed_since_previous_scan", [])),
        "missing_count": len(report.get("missing_from_current_scan", [])),
        "error_count": len(report.get("errors", []))
    }


def send_once():
    parsed = urlsplit(API_URL)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or not INGEST_TOKEN
    ):
        print("Configure a valid HTTPS API_URL and INGEST_TOKEN locally first.")
        return

    with open(REPORT_PATH, "r", encoding="utf-8") as handle:
        report = json.load(handle)

    payload = json.dumps(build_payload(report)).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + INGEST_TOKEN
        }
    )

    opener = urllib.request.build_opener(NoRedirectHandler())
    try:
        with opener.open(req, timeout=20) as response:
            print(now(), "HTTP", response.status, response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # A 3xx is intentionally surfaced as an error; redirects are not followed.
        print(now(), "HTTP ERROR", exc.code, exc.read().decode("utf-8"))
    except Exception as exc:
        print(now(), "SYNC ERROR", type(exc).__name__)


if __name__ == "__main__":
    while True:
        send_once()
        time.sleep(INTERVAL_SECONDS)
