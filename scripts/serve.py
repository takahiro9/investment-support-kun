"""investment-support-kun web app — local HTTP server.

A small read-only surface over the Vault for the ``webapp/`` front-end (a
Company dashboard), plus a Claude Code session manager: from a Company's
dashboard you can launch multiple independent ``claude`` CLI conversations
scoped to that Company, switch between them in a live terminal, rename them,
and delete the ones you no longer need — mirroring the pattern used by the
sibling project CurioSpector (see ``scripts/claude_sessions.py`` /
``scripts/pty_runtime.py`` for the session bookkeeping + pty plumbing this
borrows from).

Design
------
- **Reads** come straight from the Vault (``vault.list_entities``), which is
  the single source of truth. This module never writes to ``data/vault`` —
  all mutation of investment knowledge stays in the existing CLI
  scripts/skills (``companies.py``, ``theses.py``, ...); this server is a
  viewer, not an editor.
- **Claude sessions** are not Vault entities — see ``claude_sessions.py``.

Run:  ``uv run python scripts/serve.py [port]``  (default 8787)
"""
import json
import os
import queue
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import vault
import claude_sessions
import pty_runtime

WEBAPP_DIR = Path(__file__).resolve().parent.parent / "webapp"

# A "concept" a Claude session can be scoped to. Only Company for now — the
# dashboard's home entity — but kept as a table (not a hardcoded string) so
# it's cheap to open sessions on other entities later.
CONCEPT_ENTITY = {"company": "companies"}

_STATE_ENTITIES = [
    "companies", "sectors", "themes", "theses", "signals",
    "predictions", "strategy_recommendations", "investment_actions",
    "sources", "findings", "thoughts",
]

_CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".jsx": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".json": "application/json; charset=utf-8",
    ".png": "image/png",
    ".ico": "image/x-icon",
}


def _read_entity(entity_type: str) -> list:
    return [fm for (_id, fm, _body) in vault.list_entities(entity_type)]


def read_state() -> dict:
    """Full dashboard state, read directly from the Vault (camelCase keys, as
    stored in frontmatter)."""
    return {key: _read_entity(key) for key in _STATE_ENTITIES}


# --- Claude sessions ---------------------------------------------------------

def _concept_title(concept_type: str, concept_id: str) -> str | None:
    entity_type = CONCEPT_ENTITY.get(concept_type)
    if entity_type is None:
        return None
    try:
        fm, _body = vault.read_entity(entity_type, concept_id)
    except FileNotFoundError:
        return None
    return fm.get("name") or fm.get("title") or fm.get("statement") or "（無題）"


def _claude_context(concept_type: str, concept_id: str) -> str:
    """A short system-prompt addendum so a freshly spawned `claude` session
    already knows which Company it's discussing, instead of the user having
    to paste an id."""
    entity_type = CONCEPT_ENTITY.get(concept_type)
    if entity_type is None:
        return ""
    try:
        fm, _body = vault.read_entity(entity_type, concept_id)
    except FileNotFoundError:
        return ""
    if concept_type == "company":
        snapshot = (fm.get("currentSnapshot") or {}).get("summary", "")
        lines = [
            f"## このセッションの対象Company: {fm.get('name', '')}（{fm.get('ticker', '')}）",
            f"id: {concept_id}",
            f"市場: {fm.get('market', '')}",
        ]
        if snapshot:
            lines += ["", "現在地スナップショット:", snapshot]
        return "\n".join(lines)
    return ""


def _open_pty(session_id: str, is_new: bool):
    row = claude_sessions.get(session_id)
    if row is None:
        raise KeyError(f"unknown session {session_id}")
    args = ["--session-id", session_id] if is_new else ["--resume", session_id]
    context = _claude_context(row["conceptType"], row["conceptId"])
    if context:
        args += ["--append-system-prompt", context]
    return pty_runtime.spawn(session_id, str(WEBAPP_DIR.parent), args)


def _session_status(row: dict) -> str:
    pp = pty_runtime.get(row["id"])
    if pp is not None:
        return pp.status()
    return "unread" if row.get("unread") else "idle"


def _create_claude_session(body: dict) -> dict:
    concept_type = body.get("conceptType")
    concept_id = body.get("conceptId")
    if concept_type not in CONCEPT_ENTITY or not concept_id:
        raise ValueError(f"conceptType ({'|'.join(CONCEPT_ENTITY)}) と conceptId が必要です")
    row = claude_sessions.create(concept_type, concept_id, body.get("label", "") or "")
    _open_pty(row["id"], is_new=True)
    return {**row, "status": "thinking"}


def _list_claude_sessions(query: dict) -> list:
    concept_type = (query.get("conceptType") or [None])[0]
    concept_id = (query.get("conceptId") or [None])[0]
    rows = claude_sessions.list_sessions(concept_type, concept_id)
    return [{**r, "status": _session_status(r)} for r in rows]


def _input_claude_session(session_id: str, body: dict) -> dict:
    pp = pty_runtime.get(session_id)
    if pp is None or not pp.alive():
        pp = _open_pty(session_id, is_new=False)
    pp.write((body.get("data") or "").encode("utf-8"))
    return {"ok": True}


def _resize_claude_session(session_id: str, body: dict) -> dict:
    pp = pty_runtime.get(session_id)
    if pp is None:
        return {"ok": False}
    pp.resize(int(body.get("cols") or 80), int(body.get("rows") or 24))
    return {"ok": True}


def _patch_claude_session(session_id: str, body: dict) -> dict:
    if "label" in body:
        claude_sessions.rename(session_id, body["label"])
    if "hidden" in body:
        claude_sessions.set_hidden(session_id, bool(body["hidden"]))
    row = claude_sessions.get(session_id)
    if row is None:
        raise KeyError(f"unknown session {session_id}")
    return {**row, "status": _session_status(row)}


def dispatch_claude(method: str, segments: list, body: dict, query: dict) -> dict:
    """Route ``/api/claude/...`` (``segments`` is the path after ``/api/claude/``)."""
    if segments[:1] != ["sessions"]:
        raise KeyError(f"no route for {method} /api/claude/{'/'.join(segments)}")
    rest = segments[1:]
    if not rest:
        if method == "GET":
            return _list_claude_sessions(query)
        if method == "POST":
            return _create_claude_session(body)
    elif len(rest) == 1:
        if method == "PATCH":
            return _patch_claude_session(rest[0], body)
    elif len(rest) == 2:
        sid, action = rest
        if method == "POST" and action == "input":
            return _input_claude_session(sid, body)
        if method == "POST" and action == "resize":
            return _resize_claude_session(sid, body)
    raise KeyError(f"no route for {method} /api/claude/{'/'.join(segments)}")


class Handler(BaseHTTPRequestHandler):
    server_version = "investment-support-kun/1.0"

    def log_message(self, fmt, *args):  # quieter logs
        sys.stderr.write("  %s - %s\n" % (self.address_string(), fmt % args))

    # -- helpers --
    def _send_json(self, obj, status=200):
        payload = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8")) or {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    def _serve_static(self, path: str):
        if path == "/":
            path = "/index.html"
        rel = path.lstrip("/")
        full = (WEBAPP_DIR / rel).resolve()
        if WEBAPP_DIR.resolve() not in full.parents and full != WEBAPP_DIR.resolve():
            self.send_error(403)
            return
        if not full.is_file():
            self.send_error(404)
            return
        data = full.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", _CONTENT_TYPES.get(full.suffix, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _api(self, method: str):
        path = urlparse(self.path).path
        try:
            if path == "/api/state" and method == "GET":
                return self._send_json(read_state())
            self.send_error(404)
        except Exception as ex:  # noqa: BLE001
            self._send_json({"error": str(ex)}, status=400)

    def _api_claude(self, method: str):
        parsed = urlparse(self.path)
        segments = [s for s in parsed.path[len("/api/claude/"):].split("/") if s]
        query = parse_qs(parsed.query)
        body = self._read_body() if method in ("POST", "PATCH") else {}
        try:
            result = dispatch_claude(method, segments, body, query)
            self._send_json(result)
        except KeyError as ex:
            self._send_json({"error": str(ex)}, status=404)
        except ValueError as ex:
            self._send_json({"error": str(ex)}, status=400)
        except Exception as ex:  # noqa: BLE001
            self._send_json({"error": str(ex)}, status=500)

    def _write_sse(self, chunk: bytes, event: str = None):
        if event:
            self.wfile.write(f"event: {event}\n".encode("ascii"))
        import base64
        b64 = base64.b64encode(chunk).decode("ascii")
        self.wfile.write(f"data: {b64}\n\n".encode("ascii"))
        self.wfile.flush()

    def _serve_claude_stream(self, session_id: str):
        """SSE stream of a session's pty output. Bytes ride base64-encoded in
        each `data:` line — raw terminal output can split multi-byte UTF-8
        sequences across read() chunks and contains bare newlines, neither of
        which SSE's line-oriented framing tolerates directly. The client
        base64-decodes and hands xterm.js the raw bytes."""
        row = claude_sessions.get(session_id)
        if row is None:
            self.send_error(404)
            return
        pp = pty_runtime.get(session_id)
        if pp is None or not pp.alive():
            try:
                pp = _open_pty(session_id, is_new=False)
            except Exception:
                self.send_error(500)
                return
        q, backlog = pp.subscribe()
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            if backlog:
                self._write_sse(backlog)
            while True:
                try:
                    chunk = q.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": keepalive\n\n")
                    self.wfile.flush()
                    continue
                if chunk is None:
                    self._write_sse(b"", event="closed")
                    break
                self._write_sse(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            pp.unsubscribe(q)

    # -- verbs --
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/state":
            self._api("GET")
        elif path.startswith("/api/claude/sessions/") and path.endswith("/stream"):
            segments = [s for s in path[len("/api/claude/sessions/"):].split("/") if s]
            if len(segments) == 2:
                self._serve_claude_stream(segments[0])
            else:
                self.send_error(404)
        elif path.startswith("/api/claude/"):
            self._api_claude("GET")
        elif path.startswith("/api/"):
            self.send_error(404)
        else:
            self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith("/api/claude/"):
            self._api_claude("POST")
        else:
            self.send_error(404)

    def do_PATCH(self):
        path = urlparse(self.path).path
        if path.startswith("/api/claude/"):
            self._api_claude("PATCH")
        else:
            self.send_error(404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    host = os.environ.get("INVESTMENT_SUPPORT_KUN_WEBAPP_HOST", "127.0.0.1")
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"investment-support-kun web app → http://{host}:{port}")
    print(f"  vault:  {vault.VAULT_ROOT}")
    print(f"  webapp: {WEBAPP_DIR}")
    print("  Ctrl-C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
