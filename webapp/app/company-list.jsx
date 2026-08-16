/* investment-support-kun web app — Company list: an overview table of every
   registered Company, plus "企業を追加". Adding a Company does not write to
   the Vault directly (this server is a read-only viewer, see serve.py) —
   the form opens a live Claude Code session (a real pty console, via
   claude.jsx's SessionTerminal) so the investor types the instruction
   straight into the `claude` CLI itself, and the actual write still goes
   through the register-company skill's validation/dedup/driver-tree
   bootstrap. */

function CompanyRow({ company, sectorById, thesisCount, onOpen }) {
  const primarySector = sectorById[company.primarySectorId];
  const snapshot = company.currentSnapshot;
  return (
    <tr className="company-row" onClick={() => onOpen(company.id)}>
      <td className="company-cell">
        <div className="company-cell-name">{company.name}</div>
        <div className="company-cell-sub">{company.ticker}／{company.market}</div>
      </td>
      <td>{primarySector ? <span className="chip">{primarySector.name}</span> : <span className="empty-hint">—</span>}</td>
      <td className="num">{thesisCount}</td>
      <td>
        {snapshot
          ? <>
              <div className="snapshot-snip">{snapshot.summary}</div>
              <span className="updated-at">{snapshot.asOf}</span>
            </>
          : <span className="empty-hint">未設定</span>}
      </td>
    </tr>
  );
}

const ADD_COMPANY_PLACEHOLDER = "例: トヨタ自動車（証券コード7203、東証プライム、決算期3月末）を自動車セクターで登録して";

/* Opens a dedicated Claude Code session the moment the form mounts and
   embeds its live terminal inline — no staging textarea, no separate
   "send" step. The investor types the registration instruction straight
   into the real `claude` CLI pty, exactly as if they'd opened a console. */
function AddCompanyForm({ sectors, onClose }) {
  const sessions = useSessions();
  const [sessionId, setSessionId] = React.useState(null);
  const [error, setError] = React.useState(null);
  const startedRef = React.useRef(false);

  React.useEffect(() => {
    if (startedRef.current) return;
    startedRef.current = true;
    if (sessions.selected) {
      setSessionId(sessions.selected);
      return;
    }
    sessions.create("企業を追加")
      .then((row) => setSessionId(row && row.id))
      .catch((ex) => setError(String(ex)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="card add-company-form">
      <div className="section-label">企業を追加</div>
      {sectors.length > 0
        ? (
          <div className="form-field">
            <div className="form-label">登録済みのSector（参考。プロンプト中で指定してください）</div>
            <div className="sector-check-list">
              {sectors.map((s) => <span key={s.id} className="chip">{s.name}</span>)}
            </div>
          </div>
        )
        : <p className="empty-hint">まだSectorが登録されていません。「◯◯セクターも一緒に登録して」のようにプロンプトに含めても構いません。</p>}
      <p className="empty-hint">下のコンソールに直接指示を入力してください（例: {ADD_COMPANY_PLACEHOLDER}）</p>
      <div className="add-company-console">
        {error
          ? <div className="terminal-empty">セッションを開始できませんでした: {error}</div>
          : sessionId
            ? <SessionTerminal key={sessionId} sessionId={sessionId} />
            : <div className="terminal-empty">セッションを準備しています…</div>}
      </div>
      <div className="form-actions">
        <button type="button" onClick={onClose}>閉じる</button>
      </div>
    </div>
  );
}

function CompanyList({ state, derive, onOpenCompany }) {
  const [showForm, setShowForm] = React.useState(false);
  const companies = (state && state.companies) || [];
  const sectors = (state && state.sectors) || [];

  return (
    <main className="dashboard">
      <section className="card list-header">
        <div className="row1">
          <h1 className="company-name">企業一覧</h1>
          <span className="chip">{companies.length}社</span>
        </div>
        <div className="form-actions">
          <button type="button" className="primary-btn" onClick={() => setShowForm((v) => !v)}>
            {showForm ? "閉じる" : "+ 企業を追加"}
          </button>
        </div>
      </section>

      {showForm && <AddCompanyForm sectors={sectors} onClose={() => setShowForm(false)} />}

      <section className="card">
        {companies.length === 0
          ? <p className="empty-hint">まだCompanyが登録されていません。「+ 企業を追加」から追加してください。</p>
          : (
            <div className="table-wrap">
              <table className="companies">
                <thead><tr><th>企業</th><th>主セクター</th><th>Thesis</th><th>スナップショット</th></tr></thead>
                <tbody>
                  {companies.map((c) => (
                    <CompanyRow
                      key={c.id} company={c} sectorById={derive.sectorById}
                      thesisCount={(derive.thesesByCompany[c.id] || []).length}
                      onOpen={onOpenCompany}
                    />
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </section>
    </main>
  );
}

Object.assign(window, { CompanyList });
