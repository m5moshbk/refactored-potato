# -*- coding: utf-8 -*-
"""
M5mOsH Nexus — Privacy-Safe Local Preview
Version: 1.2.0
Pythonista 3 / Python 3.10+
READ-ONLY / NO NETWORK / NO TOKEN

Discovers inventory JSON reports by filename OR report structure.
Remembers the selected report path locally beside this script.
Never transmits report contents or local paths.
"""

import os
import json
from datetime import datetime
from pathlib import Path

VERSION = "1.2.0"
DEFAULT_REPORT_PATH = os.path.expanduser(
    "~/Documents/M5mOsH_Control/CodeInventory/code_inventory.json"
)
MAX_FILES = 5000
MAX_SEARCH_DIRS = 12000
MAX_JSON_CANDIDATES = 12000
MAX_JSON_BYTES = 12 * 1024 * 1024
ROOT_LABEL = "Pythonista aggregate code inventory (synthetic paths)"
SETTINGS_NAME = "nexus_preview_settings.json"

ALLOWED_EXTENSIONS = {
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini",
    ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd",
    ".sql", ".php", ".rb", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".dart",
    ".lua", ".pl", ".r", ".ipynb", ".xml"
}

REPORT_MARKERS = {
    "added_since_previous_scan", "changed_since_previous_scan",
    "missing_from_current_scan", "report_time", "root_path",
    "scan_summary", "total_files", "file_count"
}


def now_local():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def settings_path():
    try:
        return Path(__file__).resolve().parent / SETTINGS_NAME
    except Exception:
        return Path.home() / "Documents" / SETTINGS_NAME


def load_settings():
    path = settings_path()
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def remember_report_path(report_path):
    path = settings_path()
    data = {"remembered_report_path": str(Path(report_path).resolve()),
            "saved_at": now_local()}
    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print("Selected report path remembered locally.")
    except Exception as exc:
        print("Note: could not save remembered path:", type(exc).__name__, str(exc))


def is_inventory_report(path):
    """Read a small local JSON file and identify a likely inventory report."""
    try:
        if path.stat().st_size > MAX_JSON_BYTES:
            return False
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return False
        files = data.get("files")
        if not isinstance(files, list):
            return False
        keys = set(data.keys())
        has_inventory_marker = bool(keys.intersection(REPORT_MARKERS))
        has_file_records = any(
            isinstance(item, dict) and (
                isinstance(item.get("path"), str) or
                isinstance(item.get("extension"), str)
            )
            for item in files[:20]
        )
        return has_inventory_marker or has_file_records
    except Exception:
        return False


def discover_reports(search_root=None):
    root = Path(search_root) if search_root else Path.home() / "Documents"
    if not root.is_dir():
        return []

    found = []
    visited_dirs = 0
    inspected_json = 0

    for current, dirs, names in os.walk(str(root)):
        visited_dirs += 1
        if visited_dirs > MAX_SEARCH_DIRS:
            print("Search directory limit reached; results may be partial.")
            break

        dirs[:] = [
            name for name in dirs
            if not name.startswith(".")
            and name not in {
                "__pycache__", ".git", "site-packages",
                "node_modules", ".Trash"
            }
        ]

        for name in names:
            if not name.lower().endswith(".json"):
                continue
            inspected_json += 1
            if inspected_json > MAX_JSON_CANDIDATES:
                print("JSON search limit reached; results may be partial.")
                return sorted(found, key=lambda p: str(p).lower())
            candidate = Path(current) / name
            if name.lower() == "code_inventory.json" or is_inventory_report(candidate):
                found.append(candidate)

    unique = {str(p.resolve()): p for p in found}
    return sorted(unique.values(), key=lambda p: str(p).lower())


def resolve_report_path():
    remembered = load_settings().get("remembered_report_path")
    if isinstance(remembered, str) and remembered.strip():
        remembered_path = Path(os.path.expanduser(remembered))
        if remembered_path.is_file():
            print("Using remembered report:", remembered_path)
            return remembered_path

    default = Path(os.path.expanduser(DEFAULT_REPORT_PATH))
    if default.is_file():
        remember_report_path(default)
        return default

    print("\nSearching Pythonista Documents for inventory JSON reports ...")
    candidates = discover_reports()

    if len(candidates) == 1:
        print("Found likely inventory report:", candidates[0])
        remember_report_path(candidates[0])
        return candidates[0]

    if candidates:
        print("\nPossible inventory reports:")
        for index, candidate in enumerate(candidates, 1):
            print("{}. {}".format(index, candidate))
        choice = input(
            "Select the correct report number, or press Enter for manual path: "
        ).strip()
        if choice.isdigit():
            selected = int(choice)
            if 1 <= selected <= len(candidates):
                remember_report_path(candidates[selected - 1])
                return candidates[selected - 1]

    manual = input(
        "\nPaste full path to the inventory JSON, or press Enter to cancel: "
    ).strip().strip('"').strip("'")
    if not manual:
        return None
    candidate = Path(os.path.expanduser(manual))
    if not candidate.is_file():
        raise FileNotFoundError("The entered report path does not exist: {}".format(candidate))
    if not is_inventory_report(candidate):
        raise ValueError("The selected JSON does not look like an inventory report.")
    remember_report_path(candidate)
    return candidate


def safe_count(report, key):
    value = report.get(key, [])
    if isinstance(value, list):
        return len(value)
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return 0


def get_extension(item):
    ext = item.get("extension")
    if isinstance(ext, str) and ext.strip():
        ext = ext.strip().lower()
        return ext if ext.startswith(".") else "." + ext
    source_path = item.get("path", "")
    return Path(source_path).suffix.lower() if isinstance(source_path, str) else ""


def build_privacy_safe_payload(report):
    if not isinstance(report, dict):
        raise ValueError("Inventory report must be a JSON object.")
    source_files = report.get("files", [])
    if not isinstance(source_files, list):
        raise ValueError("'files' must be a list.")

    safe_files = []
    skipped = 0
    for item in source_files:
        if not isinstance(item, dict):
            skipped += 1
            continue
        ext = get_extension(item)
        if ext not in ALLOWED_EXTENSIONS:
            skipped += 1
            continue
        if len(safe_files) >= MAX_FILES:
            raise ValueError("More than 5,000 code files found; preview stopped.")
        safe_files.append({
            "path": "aggregate/item_{:05d}{}".format(len(safe_files) + 1, ext),
            "extension": ext,
            "size_bytes": 0,
            "modified": ""
        })

    checked_at = report.get("report_time")
    if not isinstance(checked_at, str) or not checked_at.strip():
        checked_at = now_local()

    payload = {
        "checked_at": checked_at[:64],
        "root_label": ROOT_LABEL,
        "files": safe_files,
        "new_count": safe_count(report, "added_since_previous_scan"),
        "changed_count": safe_count(report, "changed_since_previous_scan"),
        "missing_count": safe_count(report, "missing_from_current_scan"),
        "error_count": safe_count(report, "errors")
    }
    audit = {
        "source_file_count": len(source_files),
        "included_code_file_count": len(safe_files),
        "skipped_non_code_or_invalid_count": skipped,
        "contains_original_paths": False,
        "contains_original_file_names": False,
        "contains_file_sizes": False,
        "contains_file_timestamps": False,
        "contains_hashes": False,
        "contains_source_content": False,
        "network_transmission": False
    }
    return payload, audit


def save_preview(payload, audit, report_path):
    folder = Path(report_path).parent
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = folder / ("nexus_privacy_preview_" + stamp + ".json")
    document = {
        "preview_only": True,
        "created_at": now_local(),
        "privacy_audit": audit,
        "payload": payload
    }
    with output_path.open("x", encoding="utf-8") as handle:
        json.dump(document, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return str(output_path)


def main():
    print("M5mOsH Nexus — Privacy-Safe Preview v" + VERSION)
    print("READ-ONLY / NO NETWORK / NO TOKEN")
    print("1) Build local preview")
    print("2) Exit")
    if input("Choose 1 or 2: ").strip() != "1":
        print("Exited; no action taken.")
        return

    try:
        report_path = resolve_report_path()
        if report_path is None:
            print("Cancelled; no file was read or created.")
            return

        with report_path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)

        payload, audit = build_privacy_safe_payload(report)
        print("\nSource report:", report_path)
        print("Source records:", audit["source_file_count"])
        print("Included code records:", audit["included_code_file_count"])
        print("Skipped records:", audit["skipped_non_code_or_invalid_count"])
        print("Privacy audit:", json.dumps(audit, ensure_ascii=False, indent=2))

        saved = save_preview(payload, audit, report_path)
        print("\nPreview saved:", saved)
        print("No network request was made.")
    except Exception as exc:
        print("\nPREVIEW NOT CREATED")
        print(type(exc).__name__ + ":", str(exc))


if __name__ == "__main__":
    main()
