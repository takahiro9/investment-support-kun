/* investment-support-kun web app — data layer: fetch /api/state (read-only
   Vault snapshot) and expose it + small derived lookups to the rest of the
   app via useApp(). */

async function api(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `${method} ${path} failed (${res.status})`);
  return data;
}

function byId(rows) {
  const map = {};
  for (const r of rows || []) map[r.id] = r;
  return map;
}

function groupBy(rows, key) {
  const map = {};
  for (const r of rows || []) {
    const k = r[key];
    if (!k) continue;
    (map[k] = map[k] || []).push(r);
  }
  return map;
}

const AppCtx = React.createContext(null);
function useApp() {
  return React.useContext(AppCtx);
}

function AppProvider({ children }) {
  const [state, setState] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [selectedCompanyId, setSelectedCompanyId] = React.useState(null);

  const refresh = React.useCallback(async () => {
    try {
      const data = await api("GET", "/api/state");
      setState(data);
      setError(null);
      setSelectedCompanyId((cur) => {
        if (cur && (data.companies || []).some((c) => c.id === cur)) return cur;
        return data.companies && data.companies[0] ? data.companies[0].id : null;
      });
    } catch (ex) {
      setError(ex.message || String(ex));
    }
  }, []);

  React.useEffect(() => {
    refresh();
    const t = setInterval(refresh, 15000);
    return () => clearInterval(t);
  }, [refresh]);

  const derive = React.useMemo(() => {
    if (!state) return null;
    return {
      companyById: byId(state.companies),
      sectorById: byId(state.sectors),
      thesesByCompany: groupBy(state.theses, "companyId"),
      signalsByThesis: groupBy(state.signals, "validatesThesisId"),
      predictionsByThesis: groupBy(state.predictions, "thesisId"),
      strategyByCompany: groupBy(state.strategy_recommendations, "companyId"),
      actionsByCompany: groupBy(state.investment_actions, "companyId"),
    };
  }, [state]);

  const value = { state, derive, error, selectedCompanyId, setSelectedCompanyId, refresh };
  return <AppCtx.Provider value={value}>{children}</AppCtx.Provider>;
}

Object.assign(window, { api, byId, groupBy, AppCtx, useApp, AppProvider });
