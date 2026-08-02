/* investment-support-kun web app — Company dashboard: driver tree, Thesis,
   Signal, Prediction, StrategyRecommendation/InvestmentAction timeline, all
   read live from the Vault. Ported visually from the reviewed UX mockup;
   every "深掘り" button seeds the active Claude Code session (see
   claude.jsx) with a description of what was clicked instead of the
   mockup's fake input box. */

const THESIS_PILL = { seed: "pill-seed", developing: "pill-developing", established: "pill-established", challenged: "pill-challenged", dropped: "pill-dropped" };
const THESIS_LABEL = { seed: "SEED", developing: "DEVELOPING", established: "ESTABLISHED", challenged: "CHALLENGED", dropped: "DROPPED" };
const OUTCOME_PILL = { hit: "pill-hit", miss: "pill-miss", ambiguous: "pill-ambiguous" };
const OUTCOME_LABEL = { hit: "的中", miss: "外れ", ambiguous: "曖昧" };
const PROB_PILL = { high: "pill-prob-high", medium: "pill-prob-medium", low: "pill-prob-low" };
const ACTION_LABEL = { entry: "エントリー", add: "積み増し", hold: "保有継続", reduce: "縮小", exit: "撤退" };

function fmtDate(iso) {
  if (!iso) return "";
  return String(iso).slice(0, 10);
}
function fmtDateTime(iso) {
  if (!iso) return "";
  return String(iso).replace("T", " ").replace("Z", " UTC");
}
function pct(n) {
  if (n === null || n === undefined) return "";
  return `${Math.round(n * 100)}%`;
}

function DeepdiveButton({ label }) {
  const sessions = useSessions();
  return (
    <button className="deepdive-btn" onClick={(e) => { e.stopPropagation(); sessions.seedPrompt(`[${label}] について、もっと深掘りして`); }}>
      深掘り
    </button>
  );
}

function buildForest(nodes) {
  const byParent = {};
  for (const n of nodes || []) {
    const key = n.parentId || "__root__";
    (byParent[key] = byParent[key] || []).push(n);
  }
  return { byParent, roots: byParent["__root__"] || [] };
}

function TreeNode({ node, byParent, sectorById, companyName }) {
  const children = byParent[node.id] || [];
  const isBranch = children.length > 0;
  const sector = node.sectorId ? sectorById[node.sectorId] : null;
  return (
    <li className="deepdive-target">
      <div className={`tree-node ${isBranch ? "branch" : ""}`}>
        {node.label}
        {node.formula && <span className="formula">（{node.formula}）</span>}
        {sector && <span className="sector-tag">{sector.name}</span>}
        <DeepdiveButton label={`DriverTreeNode: ${node.label}${node.formula ? `（${node.formula}）` : ""} / Company: ${companyName}`} />
      </div>
      {isBranch && (
        <ul>
          {children.map((c) => (
            <TreeNode key={c.id} node={c} byParent={byParent} sectorById={sectorById} companyName={companyName} />
          ))}
        </ul>
      )}
    </li>
  );
}

function DriverTree({ company, sectorById }) {
  const { byParent, roots } = buildForest(company.driverTree);
  if (roots.length === 0) {
    return <p className="empty-hint">ドライバーツリーが未設定です。register-company / view-company スキルから追加してください。</p>;
  }
  return (
    <ul className="tree">
      {roots.map((n) => (
        <TreeNode key={n.id} node={n} byParent={byParent} sectorById={sectorById} companyName={company.name} />
      ))}
    </ul>
  );
}

function ThesisSection({ theses, derive }) {
  if (theses.length === 0) {
    return <p className="empty-hint">まだThesisがありません。create-thesis スキルから追加してください。</p>;
  }
  return (
    <div className="thesis-list">
      {theses.map((t) => (
        <div key={t.id} className="thesis-card deepdive-target">
          <div className="thesis-top">
            <span className="thesis-title">{t.statement}</span>
            <span className={`pill ${THESIS_PILL[t.status] || "pill-seed"}`}>{THESIS_LABEL[t.status] || t.status}</span>
          </div>
          <div className="thesis-meta-row">
            <span className="chip">根拠Thought {(t.thoughtIds || []).length}件</span>
            {t.horizon && <span className="chip">時間軸: {fmtDate(t.horizon)}</span>}
          </div>
          <div className="compare-grid">
            <div className="compare-col">
              <div className="compare-label">反証条件（invalidation）</div>
              <div className="compare-body">{t.invalidation}</div>
            </div>
            <div className="compare-col variant">
              <div className="compare-label">確証条件（confirmation）</div>
              <div className="compare-body">{t.confirmation}</div>
            </div>
          </div>
          {t.probability !== null && t.probability !== undefined && (
            <div className="confidence-row">
              <span className="confidence-label">確度 {pct(t.probability)}</span>
              <div className="confidence-bar"><div className="confidence-fill" style={{ width: pct(t.probability) }} /></div>
              <DeepdiveButton label={`Thesis: ${t.statement}（status: ${t.status}, 確度${pct(t.probability)}）`} />
            </div>
          )}
          {(t.probability === null || t.probability === undefined) && (
            <div className="confidence-row">
              <DeepdiveButton label={`Thesis: ${t.statement}（status: ${t.status}）`} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function SignalSection({ theses, derive }) {
  const signals = theses.flatMap((t) => (derive.signalsByThesis[t.id] || []).map((s) => ({ ...s, thesis: t })));
  if (signals.length === 0) {
    return <p className="empty-hint">まだSignalがありません。record-signal スキルから追加してください。</p>;
  }
  signals.sort((a, b) => (a.period < b.period ? 1 : -1));
  return (
    <div className="signal-grid">
      {signals.map((s) => (
        <div key={s.id} className="signal-card deepdive-target">
          <div className="signal-name">{s.metric}</div>
          <div className="signal-value-row">
            <span className="signal-value">{s.value}{s.unit || ""}</span>
            <span className="signal-period">{s.period}</span>
          </div>
          <div className="signal-meta">
            <span className="chip chip-small">{s.category}</span>
            <span className="validates">→ <span className="context-chip">{s.thesis.statement}</span>の前提を検証</span>
          </div>
          <div className="confidence-row" style={{ marginTop: ".4rem" }}>
            <DeepdiveButton label={`Signal: ${s.metric}（${s.value}${s.unit || ""}, ${s.period}, validates: ${s.thesis.statement}）`} />
          </div>
        </div>
      ))}
    </div>
  );
}

function PredictionSection({ theses, derive }) {
  const rows = theses.flatMap((t) => (derive.predictionsByThesis[t.id] || []).map((p) => ({ ...p, thesis: t })));
  if (rows.length === 0) {
    return <p className="empty-hint">まだPredictionがありません。structure-prediction-from-thought スキルから追加してください。</p>;
  }
  rows.sort((a, b) => (a.horizon < b.horizon ? -1 : 1));
  return (
    <div className="table-wrap">
      <table className="predictions">
        <thead><tr><th>予測</th><th>確度</th><th>期限</th><th>状態</th></tr></thead>
        <tbody>
          {rows.map((p) => (
            <tr key={p.id} className="deepdive-target">
              <td className="statement">
                {p.statement}
                <div className="statement-sub">検証: {p.observableText} ／ 由来: {p.thesis.statement}</div>
              </td>
              <td className="num">{pct(p.probability)}</td>
              <td className="num">{fmtDate(p.horizon)}</td>
              <td>
                <span className={`pill ${p.outcome ? (OUTCOME_PILL[p.outcome] || "pill-pending") : "pill-pending"}`}>
                  {p.outcome ? (OUTCOME_LABEL[p.outcome] || p.outcome) : "進行中"}
                </span>{" "}
                <DeepdiveButton label={`Prediction: ${p.statement}（${p.outcome ? OUTCOME_LABEL[p.outcome] : `確度${pct(p.probability)}`}, 由来Thesis: ${p.thesis.statement}）`} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TimelineSection({ companyId, derive }) {
  const strategies = (derive.strategyByCompany[companyId] || []).map((s) => ({ kind: "mgmt", date: s.createdAt, row: s }));
  const actions = (derive.actionsByCompany[companyId] || []).map((a) => ({ kind: "investor", date: a.createdAt, row: a }));
  const items = [...strategies, ...actions].sort((a, b) => (a.date < b.date ? 1 : -1));
  if (items.length === 0) {
    return <p className="empty-hint">まだStrategyRecommendation/InvestmentActionがありません。</p>;
  }
  return (
    <div className="timeline">
      {items.map(({ kind, date, row }) => (
        <div key={row.id} className="timeline-item deepdive-target">
          <div className="timeline-date">{fmtDate(date)}</div>
          <div className="timeline-rail"><div className={`timeline-dot ${kind}`} /></div>
          <div className="timeline-body">
            {kind === "mgmt" ? (
              <>
                <div className="timeline-kind">経営の打ち手（StrategyRecommendation）</div>
                <div className="timeline-text">{row.option}</div>
                <div className="timeline-eval">
                  <span className={`pill ${PROB_PILL[row.executionProbability] || "pill-prob-low"}`}>実行確率: {row.executionProbability}</span>
                  <span className="impact-text">想定インパクト: {row.impactIfExecuted}</span>
                  <DeepdiveButton label={`StrategyRecommendation: ${row.option}（実行確率: ${row.executionProbability}）`} />
                </div>
              </>
            ) : (
              <>
                <div className="timeline-kind">投資家の打ち手（InvestmentAction）</div>
                <div className="timeline-text">
                  {ACTION_LABEL[row.action] || row.action}
                  {row.positionSizePercent !== null && row.positionSizePercent !== undefined && (
                    <span className="chip">目安 {row.positionSizePercent > 0 ? "+" : ""}{row.positionSizePercent}%</span>
                  )}
                </div>
                <div className="timeline-eval">
                  <span className="impact-text">根拠: {row.positionSizingRationale}</span>
                  <span className="impact-text">次の調査: {row.nextResearch}</span>
                  <DeepdiveButton label={`InvestmentAction: ${ACTION_LABEL[row.action] || row.action}（${fmtDate(date)}）`} />
                </div>
              </>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function CompanyDashboard({ company }) {
  const { derive } = useApp();
  const primarySector = derive.sectorById[company.primarySectorId];
  const theses = derive.thesesByCompany[company.id] || [];
  const snapshot = company.currentSnapshot;

  return (
    <main className="dashboard">
      <section className="card company-header">
        <div className="row1">
          <h1 className="company-name">{company.name}</h1>
          <span className="ticker">{company.ticker}</span>
          <span className="chip">{company.market}</span>
          {primarySector && <span className="chip">主セクター: {primarySector.name}</span>}
        </div>
        {snapshot && <p className="snapshot-text">{snapshot.summary}</p>}
        {snapshot && <span className="updated-at">COMPANY SNAPSHOT UPDATED {snapshot.asOf}</span>}
        {!snapshot && <p className="empty-hint">まだスナップショットがありません。update-company-snapshot スキルから追加してください。</p>}
      </section>

      <section className="card">
        <div className="section-label">Driver Tree（事業構造の分解木）</div>
        <DriverTree company={company} sectorById={derive.sectorById} />
      </section>

      <section className="card">
        <div className="section-label">Thesis（投資仮説）</div>
        <ThesisSection theses={theses} derive={derive} />
      </section>

      <section className="card">
        <div className="section-label">Signal（時系列指標）</div>
        <SignalSection theses={theses} derive={derive} />
      </section>

      <section className="card">
        <div className="section-label">Prediction（予測・答え合わせ）</div>
        <PredictionSection theses={theses} derive={derive} />
      </section>

      <section className="card">
        <div className="section-label">StrategyRecommendation（経営の打ち手の評価） / InvestmentAction（投資家自身の打ち手）</div>
        <TimelineSection companyId={company.id} derive={derive} />
      </section>
    </main>
  );
}

Object.assign(window, { CompanyDashboard, fmtDate, fmtDateTime, pct });
