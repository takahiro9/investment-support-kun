/* investment-support-kun web app — Claude Code sessions: a live `claude` CLI
   terminal, scoped to one Company (the "concept"). Following the same
   pattern as the sibling project CurioSpector: a single concept can have
   several independent sessions running at once (different angles of
   investigation, or just parallel conversations), switchable from a tab
   strip, renamable, and deletable when no longer needed.

   Backend surface (scripts/serve.py, scripts/claude_sessions.py,
   scripts/pty_runtime.py):
     GET   /api/claude/sessions?conceptType=company&conceptId=   list (+status)
     POST  /api/claude/sessions            {conceptType, conceptId, label?}
     PATCH /api/claude/sessions/:id        {label?, hidden?}   hidden = delete from this list
     GET   /api/claude/sessions/:id/stream  SSE, base64 pty bytes per `data:` line
     POST  /api/claude/sessions/:id/input   {data}   raw bytes from xterm's onData
     POST  /api/claude/sessions/:id/resize  {cols, rows}

   A session's own transcript lives entirely in Claude Code's own
   ~/.claude/projects/.../<id>.jsonl (via --session-id / --resume); nothing
   here duplicates that content — this UI is just the Company-scoped index
   into it plus the live terminal. */

const SESSION_STATUS_LABEL = { thinking: "推論中", waiting: "入力待ち", unread: "未読", idle: "待機", exited: "終了" };

const SessionsCtx = React.createContext(null);
function useSessions() {
  return React.useContext(SessionsCtx);
}

const XTERM_THEME = {
  background: "#0a0d12", foreground: "#e8ecf2", cursor: "#4fb6e0", cursorAccent: "#0a0d12",
  selectionBackground: "rgba(79, 182, 224, 0.28)",
  black: "#0a0d12", red: "#e0705f", green: "#6fbf73", yellow: "#e0a64f",
  blue: "#4fb6e0", magenta: "#a67bb0", cyan: "#8cbbc4", white: "#e8ecf2",
  brightBlack: "#5c6b7d", brightRed: "#e0705f", brightGreen: "#6fbf73",
  brightYellow: "#e0a64f", brightBlue: "#4fb6e0", brightMagenta: "#c4a0d0",
  brightCyan: "#c3e0e5", brightWhite: "#ffffff",
};

function ConfirmDialog({ title, message, confirmLabel, onConfirm, onCancel }) {
  return (
    <div className="confirm-scrim" onClick={onCancel}>
      <div className="confirm-box" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="confirm-actions">
          <button onClick={onCancel}>キャンセル</button>
          <button className="danger" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  );
}

/* Owns one live pty connection: xterm.js instance + SSE subscription +
   input/resize POSTs. Mounted fresh per session (parent keys it on
   sessionId) so switching sessions cleanly tears down the old connection. */
const XtermCtor = window.Terminal;

function SessionTerminal({ sessionId }) {
  const hostRef = React.useRef(null);
  const available = typeof XtermCtor !== "undefined" && typeof window.FitAddon !== "undefined";

  React.useEffect(() => {
    if (!available) return;
    const term = new XtermCtor({
      convertEol: true,
      fontFamily: "\"IBM Plex Mono\", \"SFMono-Regular\", ui-monospace, Menlo, monospace",
      fontSize: 12.5,
      theme: XTERM_THEME,
      scrollback: 5000,
      cursorBlink: true,
    });
    const fit = new window.FitAddon.FitAddon();
    term.loadAddon(fit);
    term.open(hostRef.current);
    fit.fit();
    term.focus();

    const es = new EventSource(`/api/claude/sessions/${sessionId}/stream`);
    es.onmessage = (e) => {
      if (!e.data) return;
      const bin = atob(e.data);
      const bytes = new Uint8Array(bin.length);
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
      term.write(bytes);
    };
    es.addEventListener("closed", () => {
      term.write("\r\n\x1b[2m— セッションが終了しました —\x1b[0m\r\n");
    });

    const dataDisp = term.onData((data) => {
      api("POST", `/api/claude/sessions/${sessionId}/input`, { data }).catch(() => {});
    });
    const resizeDisp = term.onResize(({ cols, rows }) => {
      api("POST", `/api/claude/sessions/${sessionId}/resize`, { cols, rows }).catch(() => {});
    });
    const ro = new ResizeObserver(() => fit.fit());
    ro.observe(hostRef.current);

    return () => {
      ro.disconnect();
      dataDisp.dispose();
      resizeDisp.dispose();
      es.close();
      term.dispose();
    };
  }, [sessionId, available]);

  if (!available) {
    return <div className="terminal-empty">ターミナル UI（xterm.js）を読み込めませんでした。ネット接続を確認してください。</div>;
  }
  return <div className="terminal-host" ref={hostRef} />;
}

function SessionTab({ s, active, onSelect, onRename, onDelete }) {
  const [editing, setEditing] = React.useState(false);
  const [label, setLabel] = React.useState(s.label || "");

  React.useEffect(() => { if (!editing) setLabel(s.label || ""); }, [s.label, editing]);

  const commit = () => {
    setEditing(false);
    const v = label.trim();
    if (v && v !== s.label) onRename(v);
  };

  if (editing) {
    return (
      <input
        className="session-rename-input" autoFocus value={label}
        onChange={(e) => setLabel(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
          if (e.key === "Escape") { setLabel(s.label || ""); setEditing(false); }
        }}
      />
    );
  }

  return (
    <div className={`session-tab ${active ? "active" : ""}`} title={SESSION_STATUS_LABEL[s.status] || s.status}>
      <span className={`status-dot ${s.status}`} />
      <span className="label" onClick={onSelect} onDoubleClick={() => setEditing(true)}>
        {s.label || `セッション ${s.id.slice(0, 8)}`}
      </span>
      <button className="tab-btn" onClick={() => setEditing(true)} aria-label="名前を変更">✎</button>
      <button className="tab-btn" onClick={onDelete} aria-label="削除">×</button>
    </div>
  );
}

/* Owns the Company-scoped session list + which one is active. Wraps *both*
   the dashboard (whose deep-dive buttons call useSessions().seedPrompt) and
   the terminal column itself, so context reaches across that sibling
   boundary — see app.jsx for how the two are laid out side by side inside
   this provider. */
function SessionsProvider({ conceptType, conceptId, conceptTitle, children }) {
  const [sessions, setSessions] = React.useState([]);
  const [selected, setSelected] = React.useState(null);
  const [creating, setCreating] = React.useState(false);
  const [pendingDelete, setPendingDelete] = React.useState(null);

  const refresh = React.useCallback(async () => {
    if (!conceptId) { setSessions([]); return; }
    try {
      const rows = await api("GET", `/api/claude/sessions?conceptType=${encodeURIComponent(conceptType)}&conceptId=${encodeURIComponent(conceptId)}`);
      setSessions(rows);
      setSelected((cur) => (cur && rows.some((r) => r.id === cur)) ? cur : (rows[0] ? rows[0].id : null));
    } catch (ex) {
      // transient network hiccup — keep showing the last known list
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conceptType, conceptId]);

  React.useEffect(() => {
    setSessions([]);
    setSelected(null);
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, [refresh]);

  const create = React.useCallback(async (label) => {
    if (!conceptId) return null;
    setCreating(true);
    try {
      const row = await api("POST", "/api/claude/sessions", { conceptType, conceptId, label: label || "" });
      setSessions((s) => [row, ...s]);
      setSelected(row.id);
      return row;
    } finally {
      setCreating(false);
    }
  }, [conceptType, conceptId]);

  const rename = async (id, label) => {
    const row = await api("PATCH", `/api/claude/sessions/${id}`, { label });
    setSessions((s) => s.map((x) => (x.id === id ? { ...x, label: row.label } : x)));
  };

  const remove = async (id) => {
    await api("PATCH", `/api/claude/sessions/${id}`, { hidden: true });
    setSessions((s) => s.filter((x) => x.id !== id));
    setSelected((cur) => (cur === id ? null : cur));
  };

  // Exposed to the dashboard's deep-dive buttons: make sure a session exists
  // and is active, then type (not submit) the given prompt into it.
  const seedPrompt = React.useCallback(async (text) => {
    let id = selected;
    if (!id) {
      const row = await create("");
      id = row && row.id;
    }
    if (!id) return;
    await api("POST", `/api/claude/sessions/${id}/input`, { data: text }).catch(() => {});
  }, [selected, create]);

  const ctxValue = React.useMemo(
    () => ({ sessions, selected, setSelected, creating, create, rename, requestDelete: setPendingDelete, seedPrompt, conceptTitle }),
    [sessions, selected, creating, create, seedPrompt, conceptTitle]
  );

  return (
    <SessionsCtx.Provider value={ctxValue}>
      {children}
      {pendingDelete && (
        <ConfirmDialog
          title="セッションを削除"
          message="この一覧から削除します（会話履歴自体は claude 側に残るため、必要なら CLI から --resume で復元できます）。"
          confirmLabel="削除する"
          onCancel={() => setPendingDelete(null)}
          onConfirm={async () => { await remove(pendingDelete.id); setPendingDelete(null); }}
        />
      )}
    </SessionsCtx.Provider>
  );
}

/* The visible right-hand column: session tab strip + terminal for whichever
   session is selected. A thin view over SessionsProvider's context. */
function SessionsPanel() {
  const { sessions, selected, setSelected, creating, create, rename, requestDelete, conceptTitle } = useSessions();
  return (
    <aside className="sessions-panel">
      <div className="sessions-header">
        <span className="sessions-title">Claude Code — <b>{conceptTitle || "（未選択）"}</b></span>
        <button className="new-session-btn" onClick={() => create("")} disabled={creating}>+ 新規セッション</button>
      </div>
      <div className="session-tabs">
        {sessions.length === 0 && <span className="sessions-empty">まだセッションがありません。「+ 新規セッション」で開始してください。</span>}
        {sessions.map((s) => (
          <SessionTab
            key={s.id} s={s} active={s.id === selected}
            onSelect={() => setSelected(s.id)}
            onRename={(label) => rename(s.id, label)}
            onDelete={() => requestDelete(s)}
          />
        ))}
      </div>
      <div className="terminal-wrap">
        {selected
          ? <SessionTerminal key={selected} sessionId={selected} />
          : <div className="terminal-empty">セッションを選ぶか、新規に開始してください。<br />ダッシュボードの「深掘り」ボタンからも自動で開始できます。</div>}
      </div>
    </aside>
  );
}

Object.assign(window, { SessionsCtx, useSessions, SessionsProvider, SessionsPanel, SESSION_STATUS_LABEL });
