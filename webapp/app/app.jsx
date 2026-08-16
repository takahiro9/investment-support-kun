/* investment-support-kun web app — bootstrap. Topbar (brand + Company
   switcher) + the Company dashboard on the left, a Claude Code sessions
   panel docked on the right (see claude.jsx) scoped to whichever Company is
   selected. */

function Topbar({ state, selectedCompanyId, onSelectCompany, view, onShowList }) {
  const companies = (state && state.companies) || [];
  return (
    <header className="topbar">
      <div className="brand">investment<span>-support-</span>kun</div>
      <button
        type="button"
        className={`nav-btn ${view === "list" ? "active" : ""}`}
        onClick={onShowList}
      >
        企業一覧
      </button>
      {companies.length > 0 && (
        <select
          className="company-select"
          value={view === "dashboard" ? (selectedCompanyId || "") : ""}
          onChange={(e) => onSelectCompany(e.target.value)}
        >
          <option value="" disabled>企業を選択…</option>
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
  const [view, setView] = React.useState("list");

  if (error) {
    return (
      <div className="app">
        <Topbar state={state} view={view} onShowList={() => setView("list")} />
        <div className="layout"><main className="dashboard"><p className="empty-hint">サーバーに接続できません: {error}</p></main></div>
      </div>
    );
  }

  if (!state || !derive) {
    return (
      <div className="app">
        <Topbar state={null} view={view} onShowList={() => setView("list")} />
        <div className="layout"><main className="dashboard"><p className="empty-hint">読み込み中…</p></main></div>
      </div>
    );
  }

  const openCompany = (id) => { setSelectedCompanyId(id); setView("dashboard"); };
  const company = view === "dashboard" ? derive.companyById[selectedCompanyId] : null;
  const sessionScope = company
    ? { conceptType: "company", conceptId: company.id, conceptTitle: company.name }
    : { conceptType: "global", conceptId: "global", conceptTitle: "全社共通" };

  return (
    <div className="app">
      <Topbar
        state={state}
        selectedCompanyId={selectedCompanyId}
        onSelectCompany={openCompany}
        view={view}
        onShowList={() => setView("list")}
      />
      <SessionsProvider conceptType={sessionScope.conceptType} conceptId={sessionScope.conceptId} conceptTitle={sessionScope.conceptTitle}>
        <div className="layout">
          {company
            ? <CompanyDashboard company={company} />
            : <CompanyList state={state} derive={derive} onOpenCompany={openCompany} />}
        </div>
        <SessionsLauncher />
        <SessionsPanel />
      </SessionsProvider>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<AppProvider><App /></AppProvider>);
