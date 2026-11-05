# -*- coding: utf-8 -*-
"""
M5mOsH Nexus Sync — Privacy-Safe Local Preview
Version: 1.1.0
Pythonista 3 / Python 3.10+
READ-ONLY PREVIEW: no network transmission.

Reads the existing local inventory JSON and creates a preview payload with
synthetic file paths. It never sends data to Render or any other endpoint.
If the default report path is absent, it searches Pythonista Documents and
allows the user to enter the report path manually.
"""

import os
import json
from datetime import datetime
from pathlib import Path

REPORT_PATH = os.path.expanduser(
    "~/Documents/M5mOsH_Control/CodeInventory/code_inventory.json"
)
MAX_FILES = 5000
MAX_SEARCH_DIRS = 10000
ROOT_LABEL = "Pythonista aggregate code inventory (synthetic paths)"

ALLOWED_EXTENSIONS = {
    ".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".json", ".jsonc", ".yaml", ".yml", ".toml", ".ini",
    ".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd",
    ".sql", ".php", ".rb", ".go", ".rs", ".java", ".kt",
    ".c", ".h", ".cpp", ".hpp", ".cs", ".swift", ".dart",
    ".lua", ".pl", ".r", ".ipynb", ".xml"
}


def now_local():
    return datetime.now().astimezone().isoformat(timespec="seconds")


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
    path = item.get("path", "")
    return Path(path).suffix.lower() if isinstance(path, str) else ""


def find_report_candidates(search_root=None):
    """Find exact report filenames under Pythonista Documents only."""
    root = Path(search_root) if search_root else Path.home() / "Documents"
    if not root.is_dir():
        return []

    matches = []
    visited_dirs = 0
    for current, dirs, files in os.walk(str(root)):
        visited_dirs += 1
        if visited_dirs > MAX_SEARCH_DIRS:
            break
        dirs[:] = [
            name for name in dirs
            if not name.startswith(".")
            and name not in {"__pycache__", ".git"}
        ]
        if "code_inventory.json" in files:
            matches.append(Path(current) / "code_inventory.json")
    return sorted(matches, key=lambda item: str(item).lower())


def resolve_report_path():
    default_path = Path(os.path.expanduser(REPORT_PATH))
    if default_path.is_file():
        return default_path

    print("\nDefault report path was not found.")
    print("Searching Pythonista Documents for code_inventory.json ...")
    candidates = find_report_candidates()

    if len(candidates) == 1:
        print("Found report:", candidates[0])
        return candidates[0]

    if len(candidates) > 1:
        print("\nMultiple reports found:")
        for index, candidate in enumerate(candidates, 1):
            print("{}. {}".format(index, candidate))
        choice = input("Select report number (or press Enter to enter a path): ").strip()
        if choice.isdigit():
            selected = int(choice)
            if 1 <= selected <= len(candidates):
                return candidates[selected - 1]

    manual = input(
        "\nPaste the full path to code_inventory.json, or press Enter to cancel: "
    ).strip().strip('"').strip("'")
    if not manual:
        return None
    candidate = Path(os.path.expanduser(manual))
    if not candidate.is_file():
        raise FileNotFoundError("The entered report path does not exist: {}".format(candidate))
    return candidate


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


def load_local_report(report_path):
    path = Path(report_path)
    if not path.is_file():
        raise FileNotFoundError("Inventory report not found: {}".format(path))
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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
    print("M5mOsH Nexus — Privacy-Safe Preview v1.1.0")
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
        report = load_local_report(report_path)
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
