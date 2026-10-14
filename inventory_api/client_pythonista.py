# Pythonista client: send aggregate metadata only.
# Set API_URL and INGEST_TOKEN locally before running.
# Never paste the token into chat or commit it to GitHub.

import os, json, time, urllib.request, urllib.error
from datetime import datetime

API_URL = ""  # e.g. https://YOUR-NEW-API.onrender.com/api/v1/inventory
INGEST_TOKEN = ""  # enter locally in Pythonista; do not commit/share
REPORT_PATH = os.path.expanduser(
    "~/Documents/M5mOsH_Control/CodeInventory/code_inventory.json"
)
INTERVAL_SECONDS = 300

def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")

def build_payload(report):
    files = []
    for item in report.get("files", []):
        path = item.get("path", "")
        ext = item.get("extension", "")
        # The server accepts metadata for code files only.
        files.append({
            "path": path,
            "extension": ext,
            "size_bytes": int(item.get("size_bytes", 0)),
            "modified": str(item.get("modified", ""))
        })
    return {
        "checked_at": str(report.get("report_time") or now()),
        "files": files,
        "new_count": len(report.get("added_since_previous_scan", [])),
        "changed_count": len(report.get("changed_since_previous_scan", [])),
        "missing_count": len(report.get("missing_from_current_scan", [])),
        "error_count": len(report.get("errors", []))
    }

def send_once():
    if not API_URL.startswith("https://") or not INGEST_TOKEN:
        print("Configure API_URL and INGEST_TOKEN locally first.")
        return
    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        report = json.load(f)
    payload = json.dumps(build_payload(report)).encode("utf-8")
    req = urllib.request.Request(
        API_URL, data=payload, method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + INGEST_TOKEN
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            print(now(), "HTTP", response.status, response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        print(now(), "HTTP ERROR", exc.code, exc.read().decode("utf-8"))
    except Exception as exc:
        print(now(), "SYNC ERROR", repr(exc))

if __name__ == "__main__":
    while True:
        send_once()
        time.sleep(INTERVAL_SECONDS)
