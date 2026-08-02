"""Claude Code session registry — bookkeeping for the web app's embedded
terminal, *not* a Vault entity.

A session here is a running (or resumable) ``claude`` CLI conversation,
launched from a Company's dashboard in the web app (``scripts/serve.py`` +
``webapp/``). Session *content* is not knowledge to store in the Vault —
Claude Code already persists the full transcript itself under
``~/.claude/projects/<encoded-cwd>/<session_id>.jsonl`` and resumes it via
``claude --resume <session_id>``. All this module keeps is the thin mapping
a plain jsonl history doesn't carry: which Company a session belongs to, a
display label, and a soft-hide flag.

Stored as one JSON file (``INVESTMENT_SUPPORT_KUN_SESSIONS_FILE``, default
``data/claude_sessions.json``), sibling to ``data/vault`` and ``data/index``
but distinct from both: it is neither the Vault (git-backed knowledge) nor a
derived LanceDB index, just local operational state for this server process.
Callers should not read/write the file directly — go through the functions
below, which hold a lock around the read-modify-write.
"""
import json
import os
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_FILE = Path(
    os.environ.get(
        "INVESTMENT_SUPPORT_KUN_SESSIONS_FILE",
        Path(__file__).parent.parent / "data" / "claude_sessions.json",
    )
)

_LOCK = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> list:
    if not SESSIONS_FILE.exists():
        return []
    try:
        return json.loads(SESSIONS_FILE.read_text(encoding="utf-8")) or []
    except (json.JSONDecodeError, UnicodeDecodeError):
        return []


def _save(rows: list) -> None:
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = SESSIONS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(SESSIONS_FILE)


def list_sessions(concept_type: str = None, concept_id: str = None, include_hidden: bool = False) -> list:
    with _LOCK:
        rows = _load()
    if concept_type is not None:
        rows = [r for r in rows if r.get("conceptType") == concept_type]
    if concept_id is not None:
        rows = [r for r in rows if r.get("conceptId") == concept_id]
    if not include_hidden:
        rows = [r for r in rows if not r.get("hidden")]
    rows.sort(key=lambda r: r.get("lastActiveAt") or r.get("createdAt") or "", reverse=True)
    return rows


def get(session_id: str) -> dict | None:
    with _LOCK:
        rows = _load()
    return next((r for r in rows if r["id"] == session_id), None)


def create(concept_type: str, concept_id: str, label: str = "") -> dict:
    row = {
        "id": str(uuid.uuid4()),
        "conceptType": concept_type,
        "conceptId": concept_id,
        "label": label or "",
        "createdAt": _now(),
        "lastActiveAt": _now(),
        "hidden": False,
        "unread": False,
    }
    with _LOCK:
        rows = _load()
        rows.append(row)
        _save(rows)
    return row


def _update(session_id: str, **changes) -> dict | None:
    with _LOCK:
        rows = _load()
        row = next((r for r in rows if r["id"] == session_id), None)
        if row is None:
            return None
        row.update(changes)
        _save(rows)
        return dict(row)


def touch(session_id: str) -> dict | None:
    return _update(session_id, lastActiveAt=_now())


def set_hidden(session_id: str, hidden: bool) -> dict | None:
    return _update(session_id, hidden=bool(hidden))


def set_unread(session_id: str, unread: bool) -> dict | None:
    return _update(session_id, unread=bool(unread))


def rename(session_id: str, label: str) -> dict | None:
    return _update(session_id, label=label or "")
