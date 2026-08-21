"""
logger.py
---------
Logs every generation locally to a JSON file (a simple, human-readable
"database" that's easy to explain in an interview and easy to later swap
for a real database). Each entry is one full record: inputs, outputs,
timestamp, and approval status.
"""

import json
import os
from datetime import datetime, timezone

LOG_FILE = "generation_log.json"


def _load_log() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # If the log file somehow got corrupted, don't crash the app —
        # start a fresh in-memory list rather than losing the ability to log.
        return []


def _save_log(entries: list) -> None:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


def log_generation(brand: str, audience: str, source_type: str,
                    outputs: dict, approval_status: str = "pending",
                    revision_notes: str = "") -> str:
    """
    Appends a new record and returns its id, so the UI can later update
    that same record's approval_status via update_approval_status().
    """
    entries = _load_log()
    entry_id = f"gen_{len(entries) + 1}_{int(datetime.now(timezone.utc).timestamp())}"

    entries.append({
        "id": entry_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "brand": brand,
        "target_audience": audience,
        "source_type": source_type,
        "outputs": outputs,
        "approval_status": approval_status,
        "revision_notes": revision_notes,
    })
    _save_log(entries)
    return entry_id


def update_approval_status(entry_id: str, status: str, notes: str = "") -> None:
    """Updates an existing log entry's approval status and optional notes."""
    entries = _load_log()
    for entry in entries:
        if entry["id"] == entry_id:
            entry["approval_status"] = status
            entry["revision_notes"] = notes
            break
    _save_log(entries)


def get_all_logs() -> list:
    """Returns all logged generations, most recent first."""
    return list(reversed(_load_log()))
