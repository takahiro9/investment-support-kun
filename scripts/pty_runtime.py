"""Live process runtime for `claude` CLI sessions spawned by the web app.

This is the in-memory half of the Claude Code session feature; the persisted
half is ``scripts/claude_sessions.py``. Nothing here survives a server
restart on purpose — a session's real state of record is the transcript
``claude`` itself keeps under ``~/.claude/projects/<encoded-cwd>/``, which
``--resume <session_id>`` reattaches to. If this server process restarts
while a session's `claude` process is still running, that child simply
becomes unreachable through this module (no in-memory handle) but is not
otherwise disturbed; the next "open" from the browser spawns a fresh
`--resume` for the same session id.

A session is "attached" (has a PtyProcess in ``_RUNTIME``) only while at
least one open/resume has happened since server start. Output is broadcast to
any subscribed browser tabs (Server-Sent Events, see ``serve.py``) and also
kept in a bounded scrollback buffer so a newly-opened tab gets recent context
immediately.
"""
import fcntl
import os
import pty
import queue
import struct
import subprocess
import termios
import threading
import time

import claude_sessions

_RUNTIME_LOCK = threading.Lock()
_RUNTIME: dict = {}

_SCROLLBACK_LIMIT = 200_000  # bytes of recent output kept per session
# Heuristic status: output still trickling in within this window reads as
# "thinking"; once it's been quiet this long, Claude is assumed to be waiting
# on the user. There's no structured signal from an interactive `claude` TUI
# to key off instead — this is a pragmatic approximation.
_QUIET_THRESHOLD = 1.2


class PtyProcess:
    def __init__(self, session_id: str, proc: subprocess.Popen, master_fd: int):
        self.session_id = session_id
        self.proc = proc
        self.master_fd = master_fd
        self.lock = threading.Lock()
        self.scrollback = bytearray()
        self.subscribers: set = set()
        self.last_output_at = time.monotonic()
        self.attached_viewers = 0
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()

    def _read_loop(self):
        while True:
            try:
                chunk = os.read(self.master_fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            with self.lock:
                self.scrollback.extend(chunk)
                overflow = len(self.scrollback) - _SCROLLBACK_LIMIT
                if overflow > 0:
                    del self.scrollback[:overflow]
                self.last_output_at = time.monotonic()
                subs = list(self.subscribers)
                no_viewers = self.attached_viewers == 0
            for q in subs:
                q.put(chunk)
            if no_viewers:
                claude_sessions.set_unread(self.session_id, True)
            claude_sessions.touch(self.session_id)
        self._cleanup()

    def _cleanup(self):
        with _RUNTIME_LOCK:
            _RUNTIME.pop(self.session_id, None)
        try:
            os.close(self.master_fd)
        except OSError:
            pass
        self.proc.wait()
        with self.lock:
            subs = list(self.subscribers)
        for q in subs:
            q.put(None)  # sentinel: stream closed, let SSE handlers finish

    def write(self, data: bytes):
        os.write(self.master_fd, data)

    def resize(self, cols: int, rows: int):
        # Setting the pty's window size via TIOCSWINSZ is enough — the kernel
        # delivers SIGWINCH to the foreground process group itself.
        winsize = struct.pack("HHHH", max(rows, 1), max(cols, 1), 0, 0)
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def subscribe(self):
        """Attach a viewer. Returns (queue, backlog_bytes)."""
        q = queue.Queue()
        with self.lock:
            self.subscribers.add(q)
            backlog = bytes(self.scrollback)
            self.attached_viewers += 1
        claude_sessions.set_unread(self.session_id, False)
        return q, backlog

    def unsubscribe(self, q):
        with self.lock:
            self.subscribers.discard(q)
            self.attached_viewers = max(0, self.attached_viewers - 1)

    def status(self) -> str:
        if self.proc.poll() is not None:
            return "exited"
        idle = time.monotonic() - self.last_output_at
        return "thinking" if idle < _QUIET_THRESHOLD else "waiting"

    def alive(self) -> bool:
        return self.proc.poll() is None


def get(session_id: str) -> "PtyProcess | None":
    with _RUNTIME_LOCK:
        return _RUNTIME.get(session_id)


def spawn(session_id: str, cwd: str, extra_args: list) -> PtyProcess:
    """Start a `claude` CLI process in a pty, attached to ``session_id``.

    A no-op (returns the existing handle) if this session already has a live
    process in this server's memory. Callers decide ``extra_args`` — pass
    ``--session-id <id>`` for a session never launched before, or
    ``--resume <id>`` to reattach to one `claude` already knows about.
    """
    existing = get(session_id)
    if existing is not None and existing.alive():
        return existing

    master_fd, slave_fd = pty.openpty()
    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))
    env = {**os.environ, "TERM": "xterm-256color"}
    proc = subprocess.Popen(
        ["claude", *extra_args],
        cwd=cwd,
        stdin=slave_fd, stdout=slave_fd, stderr=slave_fd,
        preexec_fn=os.setsid,
        close_fds=True,
        env=env,
    )
    os.close(slave_fd)
    pp = PtyProcess(session_id, proc, master_fd)
    with _RUNTIME_LOCK:
        _RUNTIME[session_id] = pp
    return pp
