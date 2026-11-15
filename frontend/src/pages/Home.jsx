import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, ChevronDown, ArrowUp, ArrowDown, Minus, ShieldCheck, Users, BookOpen } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, ReferenceLine,
} from "recharts";
import Header from "../components/Header";
import useRecommendation from "../components/useRecommendation";
import { Status } from "../components/Banners";
import { getEconomies, SHOCK_LABELS } from "../services/api";
import { friendly, PALETTE } from "../data/glossary";

const tip = { background: "#0d1626", border: "1px solid rgba(255,255,255,0.12)", fontSize: 12, borderRadius: 8 };
const inp = "w-full bg-navy-900 border border-white/10 rounded-lg px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/40";

// This is a similarity (novelty) bucket, NOT a calibrated probability of being right.
function similarity(app) {
  const s = app?.status || "";
  if (s === "typical") return { label: "High", cls: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30", text: "This country's indicators look like those of the training economies. This is a similarity measure, not a probability that the numbers are right." };
  if (s.startsWith("unusual")) return { label: "Medium", cls: "text-amber-300 bg-amber-500/10 border-amber-500/30", text: "This country is somewhat unlike the training economies. Use the reference values with care." };
  return { label: "Low", cls: "text-rose-300 bg-rose-500/10 border-rose-500/30", text: "This country is outside the typical range of the training economies; the numbers are an extrapolation and tested errors are much larger for such economies." };
}

function Stat({ title, value, sub, cls = "" }) {
  return (
    <div className="glass-card p-4">
      <div className="text-[11px] uppercase tracking-wide text-slate-400">{title}</div>
      <div className={`mt-1 text-xl font-bold ${cls || "text-white"}`}>{value}</div>
      {sub && <div className="mt-1 text-xs text-slate-400 leading-snug">{sub}</div>}
    </div>
  );
}

export default function Home() {
  const [economies, setEconomies] = useState([]);
  const [iso3, setIso3] = useState("IND");
  const [adv, setAdv] = useState(false);
  const [year, setYear] = useState("");
  const [shock, setShock] = useState("");
  const [detail, setDetail] = useState("auto");
  const [budget, setBudget] = useState("");
  const [comp, setComp] = useState("");
  const [useLime, setUseLime] = useState(false);
  const { data, loading, warming, error, run, setWarming } = useRecommendation();

  useEffect(() => {
    let live = true;
    getEconomies({ onRetry: () => live && setWarming(true) })
      .then((e) => live && (setWarming(false), setEconomies([...e].sort((a, b) => a.country.localeCompare(b.country)))))
      .catch(() => live && setWarming(false));
    return () => { live = false; };
  }, [setWarming]);

  const eco = economies.find((e) => e.iso3 === iso3);
  // The model decides the level of detail: 16 functions where official data allow it, otherwise 10 divisions.
  const panel = detail === "auto" ? (eco?.has_official_cofog_history ? "cofog16" : "cofog10") : detail;

  const submit = () => {
    setComp("");
    run({ iso3, panel, shock: shock || undefined, year, limeSector: undefined, totalBudgetUsd: budget ? Number(budget) : undefined });
  };

  const rows = useMemo(() => (data?.components || []).map((c, i) => ({
    key: c.component, name: c.label || c.component.replace(/_/g, " "), color: PALETTE[i % PALETTE.length],
    rec: Number(c.recommended_share_pct.toFixed(2)),
    obs: c.last_observed_share_pct == null ? null : Number(c.last_observed_share_pct.toFixed(2)),
    diff: c.last_observed_share_pct == null ? null : Number((c.recommended_share_pct - c.last_observed_share_pct).toFixed(2)),
    lo: c.interval_80_pp?.[0], hi: c.interval_80_pp?.[1], amount: c.amount_usd, shap: c.top_shap || [], raw: c,
  })), [data]);

  const hasObs = rows.some((r) => r.obs != null);
  const budgetToMove = hasObs ? rows.reduce((s, r) => s + Math.abs(r.diff || 0), 0) / 2 : null;
  const sortedDiff = [...rows].filter((r) => r.diff != null).sort((a, b) => b.diff - a.diff);
  const up = sortedDiff[0], down = sortedDiff[sortedDiff.length - 1];
  const sel = rows.find((r) => r.key === comp) || (hasObs ? [...rows].sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff))[0] : [...rows].sort((a, b) => b.rec - a.rec)[0]);
  const conf = similarity(data?.applicability);
  const inTraining = !!eco?.has_official_cofog_history;
  const shapData = (sel?.shap || []).map((s) => ({ label: `${friendly(s.feature)} (${Number(s.feature_value).toFixed(1)})`, v: Number(s.shap_pp.toFixed(2)) }));
  const pos = shapData.filter((s) => s.v > 0)[0], neg = shapData.filter((s) => s.v < 0)[0];

  return (
    <div className="space-y-6 max-w-6xl">
      <Header
        title="Peer-based reference budget split in one click"
        subtitle="Pick a country. The AI chooses the model, the level of detail and the year by itself, then shows a reference split of the government budget (what comparable economies typically spend) and explains the main factors. It is a benchmark for a human reviewer, not a recommendation to change a budget."
      />

      {/* STEP 1: single input */}
      <div className="glass-card p-5 space-y-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-300 text-xs flex items-center justify-center">1</span>
          Choose a country
        </div>
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-3 items-end">
          <label className="text-xs text-slate-400 space-y-1">
            Country (all {economies.length || "~"} economies in the data)
            <select className={inp} value={iso3} onChange={(e) => setIso3(e.target.value)}>
              {economies.length === 0 && <option value="IND">India (IND)</option>}
              {economies.map((e) => <option key={e.iso3} value={e.iso3}>{e.country}</option>)}
            </select>
          </label>
          <button
            onClick={submit}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-teal-500 text-navy-950 font-semibold text-sm shadow-glow disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" /> Get recommendation
          </button>
        </div>
        <p className="text-xs text-slate-400">
          Automatic settings: <b className="text-slate-200">{panel === "cofog16" ? "16 detailed budget areas" : "10 main budget areas"}</b> ·
          latest available year · a blend of four learners (in our tests about as accurate as a simple nearest-economies average). The 16 detailed areas are used where official data cover them, otherwise 10 main areas. {eco && !eco.has_official_cofog_history && "This country has no official spending breakdown on record, so the suggestion is learned only from similar countries."}
        </p>
        <button onClick={() => setAdv(!adv)} className="text-xs text-cyan-300 inline-flex items-center gap-1">
          <ChevronDown className={`w-3.5 h-3.5 transition ${adv ? "rotate-180" : ""}`} /> Advanced options (optional)
        </button>
        {adv && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-1">
            <label className="text-xs text-slate-400 space-y-1">Year of indicators
              <input className={inp} placeholder="latest" inputMode="numeric" value={year} onChange={(e) => setYear(e.target.value)} />
            </label>
            <label className="text-xs text-slate-400 space-y-1">Level of detail
              <select className={inp} value={detail} onChange={(e) => setDetail(e.target.value)}>
                <option value="auto">Automatic (recommended)</option>
                <option value="cofog16">16 detailed areas</option>
                <option value="cofog10">10 main areas</option>
              </select>
            </label>
            <label className="text-xs text-slate-400 space-y-1">Stress test (what-if)
              <select className={inp} value={shock} onChange={(e) => setShock(e.target.value)}>
                <option value="">None</option>
                {Object.entries(SHOCK_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </label>
            <label className="text-xs text-slate-400 space-y-1">Your total budget (US$, optional)
              <input className={inp} placeholder="use model estimate" inputMode="decimal" value={budget} onChange={(e) => setBudget(e.target.value)} />
            </label>
          </div>
        )}
      </div>

      <Status loading={loading} warming={warming} error={error} />

      {!data && !loading && !error && (
        <div className="grid md:grid-cols-3 gap-4 text-sm">
          {[["1", "Pick a country", "Only one input is needed."], ["2", "Press the button", "The model selects the detail by itself (16 detailed areas where official data allow, otherwise 10 main areas; about a minute the first time)."], ["3", "Read the result", "Colour charts, a short list of changes and a plain-language 'why'."]].map(([n, t, d]) => (
            <div key={n} className="glass-card p-4"><div className="text-cyan-300 font-bold">{n}. {t}</div><div className="text-slate-400 mt-1">{d}</div></div>
          ))}
        </div>
      )}

      {data && (
        <>
          {/* STEP 2: headline */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            <Stat title="Similarity to training economies" value={conf.label} cls={conf.cls.split(" ")[0]} sub={conf.text} />
            <Stat title="Difference from last year" value={budgetToMove == null ? "n/a" : `${budgetToMove.toFixed(1)}%`}
              sub={budgetToMove == null ? "No official history for this country, so no comparison." : "of the total budget differs between the model reference and last year's actual split."} />
            <Stat title="Model above last year (largest)" value={!hasObs ? "n/a" : up && up.diff > 0 ? `+${up.diff.toFixed(1)} pp` : "none"} cls="text-emerald-300" sub={!hasObs ? "Needs last year's actual budget." : up && up.diff > 0 ? up.name : "No area is above last year."} />
            <Stat title="Model below last year (largest)" value={!hasObs ? "n/a" : down && down.diff < 0 ? `${down.diff.toFixed(1)} pp` : "none"} cls="text-rose-300" sub={!hasObs ? "Needs last year's actual budget." : down && down.diff < 0 ? down.name : "No area is below last year."} />
          </div>
          <p className="text-xs text-slate-400">
            {data.country} · indicators from {data.feature_year} · learned from {data.training_economies} economies{data.shock ? ` · stress test: ${data.shock}` : ""}. These are descriptive reference values (executed spending of comparable economies), never an automatic decision.
          </p>
          {hasObs && (
            <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-100 leading-snug">
              <b>Last year's actual budget is a very strong baseline.</b> Where official history exists, repeating last year's split was hard to beat in our tests (on the 16-area panel it misses by 3.6 percentage points of the budget; the best learned correction by 3.5, a small gain that is not stable across model seeds). Treat the model split as a reference point to question, not as a better forecast. The model also uses the same year's indicators (a nowcast), which are not known when a budget is drafted.
            </div>
          )}
          {inTraining && (
            <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3 text-xs text-slate-300 leading-snug">
              <b>In-sample note.</b> {data.country} is part of the data the models were trained on, so the model split shown here is an in-sample fit and looks more accurate than the leave-one-country-out errors reported in the paper. The nearest-economies list excludes {data.country}.
            </div>
          )}

          {/* charts */}
          <div className="grid lg:grid-cols-5 gap-4">
            <div className="glass-card p-5 lg:col-span-2">
              <h3 className="text-sm font-semibold text-white">Reference split of the budget</h3>
              <p className="text-xs text-slate-400 mb-2">Each colour is one budget area; hover for the exact share.</p>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={rows} dataKey="rec" nameKey="name" innerRadius={62} outerRadius={105} paddingAngle={2} stroke="none">
                    {rows.map((r) => <Cell key={r.key} fill={r.color} />)}
                  </Pie>
                  <Tooltip contentStyle={tip} formatter={(v) => `${v}%`} />
                </PieChart>
              </ResponsiveContainer>
              <div className="flex flex-wrap gap-x-3 gap-y-1">
                {rows.map((r) => (
                  <span key={r.key} className="inline-flex items-center gap-1.5 text-[11px] text-slate-300">
                    <i className="w-2.5 h-2.5 rounded-sm" style={{ background: r.color }} />{r.name}
                  </span>
                ))}
              </div>
            </div>
            <div className="glass-card p-5 lg:col-span-3">
              <h3 className="text-sm font-semibold text-white">{hasObs ? "Model reference vs last year's actual share (%)" : "Model reference share per area (%)"}</h3>
              <p className="text-xs text-slate-400 mb-2">{hasObs ? "Teal = model reference (what comparable economies typically spend); amber = what the country actually spent last time." : "No official history exists for this country, so only the model reference is shown."}</p>
              <ResponsiveContainer width="100%" height={Math.max(300, rows.length * (hasObs ? 38 : 30))}>
                <BarChart data={rows} layout="vertical" margin={{ left: 10, right: 20 }} barGap={2}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                  <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} unit="%" />
                  <YAxis type="category" dataKey="name" width={170} tick={{ fill: "#cbd5e1", fontSize: 11 }} />
                  <Tooltip contentStyle={tip} formatter={(v) => `${v}%`} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="rec" name="Model reference" fill="#2dd4bf" radius={[0, 4, 4, 0]} />
                  {hasObs && <Bar dataKey="obs" name="Last actual" fill="#f59e0b" radius={[0, 4, 4, 0]} />}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* what to change */}
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-white mb-1">{hasObs ? "Difference from last year" : "Model reference allocation"}</h3>
            <p className="text-xs text-slate-400 mb-3">
              {hasObs ? "Green = model reference is above last year's share, red = below (descriptive, not advice). pp = percentage points of the total budget." : "Shares sum to 100 %."} The range column is a nominal 80 % band. In our tests it covered about 80 % of cases on average, but only about 47 % for low-income and 61 % for lower-middle-income economies, so it is not a reliable 8-in-10 range for those groups.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="text-left text-[11px] uppercase tracking-wide text-slate-500">
                  <th className="py-2">Area</th><th className="text-right">Model reference</th>{hasObs && <th className="text-right">Last actual</th>}{hasObs && <th className="text-right">Difference</th>}<th className="text-right">Nominal 80 % range</th>{data.total_budget && <th className="text-right">Amount (US$ bn)</th>}
                </tr></thead>
                <tbody>
                  {[...rows].sort((a, b) => (hasObs ? Math.abs(b.diff) - Math.abs(a.diff) : b.rec - a.rec)).map((r) => (
                    <tr key={r.key} className="border-t border-white/[0.06] text-slate-300 cursor-pointer hover:bg-white/[0.03]" onClick={() => setComp(r.key)}>
                      <td className="py-2"><i className="inline-block w-2.5 h-2.5 rounded-sm mr-2" style={{ background: r.color }} />{r.name}</td>
                      <td className="text-right font-medium text-white">{r.rec.toFixed(1)}%</td>
                      {hasObs && <td className="text-right">{r.obs == null ? "n/a" : `${r.obs.toFixed(1)}%`}</td>}
                      {hasObs && (
                        <td className={`text-right font-medium ${r.diff > 0.2 ? "text-emerald-300" : r.diff < -0.2 ? "text-rose-300" : "text-slate-400"}`}>
                          <span className="inline-flex items-center gap-1">{r.diff > 0.2 ? <ArrowUp className="w-3 h-3" /> : r.diff < -0.2 ? <ArrowDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}{r.diff > 0 ? "+" : ""}{r.diff.toFixed(1)} pp</span>
                        </td>
                      )}
                      <td className="text-right text-slate-400">{r.lo == null ? "n/a" : `${r.lo.toFixed(1)}-${r.hi.toFixed(1)}%`}</td>
                      {data.total_budget && <td className="text-right">{r.amount == null ? "n/a" : (r.amount / 1e9).toFixed(2)}</td>}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {data.total_budget && <p className="text-[11px] text-slate-500 mt-2">Total budget used: US$ {(data.total_budget.used_total_usd / 1e9).toFixed(1)} bn ({data.total_budget.source}).</p>}
          </div>

          {/* why */}
          <div className="glass-card p-5">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-1">
              <h3 className="text-sm font-semibold text-white">Main factors behind the model reference &mdash; {sel?.name}</h3>
              <select className="bg-navy-900 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-slate-200" value={sel?.key || ""} onChange={(e) => setComp(e.target.value)}>
                {rows.map((r) => <option key={r.key} value={r.key}>{r.name}</option>)}
              </select>
            </div>
            <p className="text-xs text-slate-400 mb-2">
              Each bar is one indicator of the country. Pink bars are associated with a <b>lower</b> share of this area, blue bars with a <b>higher</b> share, compared with an average economy (percentage points; the number in brackets is the country's own value). These are associations learned from other economies, not causes. The bars explain one tree-based member of the blend, not the blend itself.
            </p>
            <ResponsiveContainer width="100%" height={Math.max(220, shapData.length * 32)}>
              <BarChart data={shapData} layout="vertical" margin={{ left: 10, right: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                <YAxis type="category" dataKey="label" width={230} tick={{ fill: "#cbd5e1", fontSize: 11 }} />
                <ReferenceLine x={0} stroke="#475569" />
                <Tooltip contentStyle={tip} formatter={(v) => `${v} pp`} />
                <Bar dataKey="v" radius={[0, 4, 4, 0]}>{shapData.map((d, i) => <Cell key={i} fill={d.v >= 0 ? "#60a5fa" : "#f472b6"} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-sm text-slate-300 mt-2">
              In short: {pos ? <>the strongest push up comes from <b>{pos.label.split(" (")[0].toLowerCase()}</b></> : "no strong upward factor"}
              {neg ? <>, and the strongest push down from <b>{neg.label.split(" (")[0].toLowerCase()}</b></> : ""}.
            </p>
            <label className="mt-3 flex items-center gap-2 text-xs text-slate-400">
              <input type="checkbox" checked={useLime} onChange={(e) => { setUseLime(e.target.checked); if (e.target.checked) run({ iso3, panel, shock: shock || undefined, year, limeSector: sel?.key, totalBudgetUsd: budget ? Number(budget) : undefined }); }} />
              Also show a second opinion (LIME) for this area
            </label>
            {useLime && data.lime && data.lime.sector === sel?.key && (
              <div className="mt-2 text-xs text-slate-400">
                LIME fit {Number(data.lime.local_r2).toFixed(2)} (closer to 1 = more trustworthy). Top factors: {data.lime.features.slice(0, 4).map((f) => `${friendly(f.feature)} (${f.contribution_pp >= 0 ? "+" : ""}${f.contribution_pp.toFixed(2)} pp)`).join(", ")}.
              </div>
            )}
          </div>

          {/* similar */}
          {data.similar_economies?.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2"><Users className="w-4 h-4 text-cyan-300" /> Most similar countries</h3>
              <p className="text-xs text-slate-400 mb-2">These real countries look most like {data.country}; their actual budgets guide the model reference.</p>
              <div className="flex flex-wrap gap-2">
                {data.similar_economies.map((p) => (
                  <span key={p.iso3} className="px-3 py-1.5 rounded-full text-xs bg-white/[0.05] border border-white/10 text-slate-200">{p.country} <span className="text-slate-500">({(p.weight * 100).toFixed(0)}% weight)</span></span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <div className="flex flex-wrap gap-4 text-xs text-slate-400 pt-2">
        <Link to="/guide" className="inline-flex items-center gap-1.5 text-cyan-300"><BookOpen className="w-3.5 h-3.5" /> New here? Read the 2-minute guide and glossary</Link>
        <span className="inline-flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-amber-300" /> Executed (not planned) spending of general government; reference only, human judgment required.</span>
      </div>
    </div>
  );
}
