/* investment-support-kun web app — bootstrap. Topbar (brand + Company
   switcher) + the Company dashboard on the left, a Claude Code sessions
   panel docked on the right (see claude.jsx) scoped to whichever Company is
   selected. */

function Topbar({ state, selectedCompanyId, setSelectedCompanyId }) {
  const companies = (state && state.companies) || [];
  return (
    <header className="topbar">
      <div className="brand">investment<span>-support-</span>kun</div>
      {companies.length > 0 && (
        <select
          className="company-select"
          value={selectedCompanyId || ""}
          onChange={(e) => setSelectedCompanyId(e.target.value)}
        >
          {companies.map((c) => (
            <option key={c.id} value={c.id}>{c.name}（{c.ticker}）</option>
          ))}
        </select>
      )}
      <div className="topbar-spacer" />
      <span className="topbar-meta">Vault を live 表示 ／ 15秒ごとに更新</span>
    </header>
  );
}

function App() {
  const { state, derive, error, selectedCompanyId, setSelectedCompanyId } = useApp();

  if (error) {
    return (
      <div className="app">
        <Topbar state={state} selectedCompanyId={selectedCompanyId} setSelectedCompanyId={setSelectedCompanyId} />
        <div className="layout"><main className="dashboard"><p className="empty-hint">サーバーに接続できません: {error}</p></main></div>
      </div>
    );
  }

  if (!state || !derive) {
    return (
      <div className="app">
        <Topbar state={null} />
        <div className="layout"><main className="dashboard"><p className="empty-hint">読み込み中…</p></main></div>
      </div>
    );
  }

  const company = derive.companyById[selectedCompanyId];

  return (
    <div className="app">
      <Topbar state={state} selectedCompanyId={selectedCompanyId} setSelectedCompanyId={setSelectedCompanyId} />
      <SessionsProvider conceptType="company" conceptId={company ? company.id : null} conceptTitle={company ? company.name : null}>
        <div className="layout">
          {company
            ? <CompanyDashboard company={company} />
            : <main className="dashboard"><p className="empty-hint">まだCompanyが登録されていません。register-company スキルから追加してください。</p></main>}
          <SessionsPanel />
        </div>
      </SessionsProvider>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<AppProvider><App /></AppProvider>);
