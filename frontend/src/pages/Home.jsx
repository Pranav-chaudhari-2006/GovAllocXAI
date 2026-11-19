import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, ChevronDown, ArrowUp, ArrowDown, Minus, ShieldCheck, Users, BookOpen, PieChart as PieIcon, Wallet, GitCompareArrows, Info } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts";
import Header from "../components/Header";
import KPICard from "../components/KPICard";
import useRecommendation from "../components/useRecommendation";
import { Status } from "../components/Banners";
import { ChartCard, Donut, RankedBars, DiffBars, PeerBars, RangeBars, FlowSankey, Steps, tip, itemStyle, labelStyle, axis } from "../components/charts";
import { getEconomies, getHealth, SHOCK_LABELS } from "../services/api";
import { friendly, PALETTE } from "../data/glossary";
import { SDG_INFO } from "../data/sdg";
import { useSharedResult } from "../state/ResultContext";

const inp = "w-full bg-navy-900 border border-white/10 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/40";

function similarity(app) {
  const s = app?.status || "";
  if (s === "typical") return { label: "High", accent: "teal" };
  if (s.startsWith("unusual")) return { label: "Medium", accent: "amber" };
  return { label: "Low", accent: "blue" };
}

const shareClass = (v) => (v >= 15 ? ["Large", "bg-cyan-500/10 text-cyan-300 border-cyan-500/30"] : v >= 5 ? ["Medium", "bg-amber-500/10 text-amber-300 border-amber-500/30"] : ["Small", "bg-slate-500/10 text-slate-300 border-slate-500/30"]);

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
  const [customGdpGrowth, setCustomGdpGrowth] = useState("");
  const [customInflation, setCustomInflation] = useState("");
  const [customUnemployment, setCustomUnemployment] = useState("");
  const [customPop65, setCustomPop65] = useState("");
  const [customDebt, setCustomDebt] = useState("");
  const [sort, setSort] = useState({ key: "rec", dir: -1 });
  const { data, loading, warming, error, run, setWarming } = useRecommendation();
  const { setShared } = useSharedResult();

  useEffect(() => {
    let live = true;
    getHealth({ retries: 0 }).catch(() => {}); // wakes the free API server in the background for the advanced options
    getEconomies({ onRetry: () => live && setWarming(true) })
      .then((e) => live && (setWarming(false), setEconomies([...e].sort((a, b) => a.country.localeCompare(b.country)))))
      .catch(() => live && setWarming(false));
    return () => { live = false; };
  }, [setWarming]);
  useEffect(() => { if (data) setShared(data); }, [data, setShared]);

  const eco = economies.find((e) => e.iso3 === iso3);
  const panel = detail === "auto" ? (eco?.has_official_cofog_history ? "cofog16" : "cofog10") : detail;

  const getOverrides = () => {
    const ov = {};
    if (customGdpGrowth.trim() !== "") ov.gdp_growth_pct = Number(customGdpGrowth);
    if (customInflation.trim() !== "") ov.inflation_pct = Number(customInflation);
    if (customUnemployment.trim() !== "") ov.unemployment_pct = Number(customUnemployment);
    if (customPop65.trim() !== "") ov.pop_65plus_pct = Number(customPop65);
    if (customDebt.trim() !== "") ov.central_gov_debt_pct_gdp = Number(customDebt);
    return ov;
  };

  const submit = () => {
    setComp("");
    const ov = getOverrides();
    run({
      iso3,
      panel,
      shock: shock || undefined,
      year: year || undefined,
      overrides: Object.keys(ov).length ? ov : undefined,
      totalBudgetUsd: budget ? Number(budget) : undefined,
    });
  };

  const applyPreset1 = () => {
    setIso3("IND");
    setDetail("cofog10");
    setBudget("450000000000");
    setCustomGdpGrowth("8.2");
    setCustomInflation("4.5");
    setCustomUnemployment("4.0");
    setCustomPop65("6.8");
    setCustomDebt("55.0");
    setShock("");
    setYear("");
    setAdv(true);
  };

  const applyPreset2 = () => {
    setIso3("DEU");
    setDetail("cofog16");
    setBudget("600000000000");
    setCustomGdpGrowth("1.2");
    setCustomInflation("2.0");
    setCustomUnemployment("3.5");
    setCustomPop65("24.5");
    setCustomDebt("85.0");
    setShock("");
    setYear("");
    setAdv(true);
  };

  const clearManual = () => {
    setCustomGdpGrowth("");
    setCustomInflation("");
    setCustomUnemployment("");
    setCustomPop65("");
    setCustomDebt("");
    setBudget("");
    setShock("");
    setYear("");
  };

  const rows = useMemo(() => (data?.components || []).map((c, i) => ({
    key: c.component, name: c.label || c.component.replace(/_/g, " "), color: PALETTE[i % PALETTE.length], sdg: c.sdg || [],
    rec: Number(c.recommended_share_pct.toFixed(2)),
    obs: c.last_observed_share_pct == null ? null : Number(c.last_observed_share_pct.toFixed(2)),
    diff: c.last_observed_share_pct == null ? null : Number((c.recommended_share_pct - c.last_observed_share_pct).toFixed(2)),
    lo: c.interval_80_pp?.[0], hi: c.interval_80_pp?.[1], amount: c.amount_usd, shap: c.top_shap || [],
  })), [data]);

  const hasObs = rows.some((r) => r.obs != null);
  const toMove = hasObs ? rows.reduce((s, r) => s + Math.abs(r.diff || 0), 0) / 2 : null;
  const top = [...rows].sort((a, b) => b.rec - a.rec)[0];
  const sim = similarity(data?.applicability);
  const sel = rows.find((r) => r.key === comp) || (hasObs ? [...rows].sort((a, b) => Math.abs(b.diff) - Math.abs(a.diff))[0] : top);
  const shapData = (sel?.shap || []).map((s) => ({ label: `${friendly(s.feature)} (${Number(s.feature_value).toFixed(1)})`, v: Number(s.shap_pp.toFixed(2)) }));

  const peerBars = useMemo(() => {
    const peers = data?.similar_economies || [];
    if (!peers.length) return [];
    const wsum = peers.reduce((s, p) => s + p.weight, 0) || 1;
    return [...rows].sort((a, b) => b.rec - a.rec).slice(0, 8).map((r) => ({
      name: r.name, rec: r.rec, peer: Number((peers.reduce((s, p) => s + p.weight * (p.shares_pct?.[r.key] ?? 0), 0) / wsum).toFixed(2)),
    }));
  }, [data, rows]);

  const sorted = useMemo(() => [...rows].sort((a, b) => {
    const va = a[sort.key] ?? -Infinity, vb = b[sort.key] ?? -Infinity;
    return typeof va === "string" ? sort.dir * va.localeCompare(vb) : sort.dir * (va - vb);
  }), [rows, sort]);
  const th = (key, label, right = true) => (
    <th className={`py-3 px-3 font-semibold cursor-pointer select-none ${right ? "text-right" : "text-left"}`} onClick={() => setSort((s) => ({ key, dir: s.key === key ? -s.dir : -1 }))}>
      {label} <span className="text-slate-600">{sort.key === key ? (sort.dir < 0 ? "↓" : "↑") : "↕"}</span>
    </th>
  );

  return (
    <div className="space-y-8 max-w-7xl">
      <Header
        title="Budget Explorer"
        subtitle="Pick a country to see the reference split of its government budget, learned from comparable economies' real spending."
        badge={<span className="badge-implemented">Official data</span>}
      />

      <div className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 text-sm text-slate-300">
        <Info className="w-4 h-4 mt-0.5 shrink-0 text-cyan-300" />
        <span>Reference values from executed spending of comparable economies, not a recommendation to change a budget. A human reviews and decides. <Link to="/guide" className="text-cyan-300 underline-offset-2 hover:underline">How to read this page</Link></span>
      </div>

      {/* controls */}
      <div className="glass-card p-6">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-4 items-end">
          <label className="text-sm text-slate-300 space-y-2 block">
            Country <span className="text-slate-500">({economies.length || "..."} economies)</span>
            <select className={inp} value={iso3} onChange={(e) => setIso3(e.target.value)}>
              {economies.length === 0 && <option value="IND">India</option>}
              {economies.map((e) => <option key={e.iso3} value={e.iso3}>{e.country}</option>)}
            </select>
          </label>
          <button onClick={submit} disabled={loading}
            className="inline-flex items-center justify-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-teal-500 text-navy-950 font-semibold text-sm shadow-glow disabled:opacity-50">
            <Sparkles className="w-4 h-4" /> Show reference split
          </button>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-3 mt-4 text-xs text-slate-400">
          <span>Automatic: <b className="text-slate-200">{panel === "cofog16" ? "16 detailed areas" : "10 main areas"}</b> · latest year · best model. {eco && !eco.has_official_cofog_history && "No official spending history for this country: learned from similar countries only."}</span>
          <button onClick={() => setAdv(!adv)} className="text-cyan-300 inline-flex items-center gap-1">
            <ChevronDown className={`w-3.5 h-3.5 transition ${adv ? "rotate-180" : ""}`} /> Advanced options
          </button>
        </div>
        {adv && (
          <div className="space-y-5 pt-5 mt-4 border-t border-white/[0.06]">
            {/* Quick Presets for Live Evaluator Demos */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-cyan-950/30 border border-cyan-500/20 text-xs">
              <span className="font-medium text-cyan-300">Live Evaluator Presets:</span>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={applyPreset1}
                  className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-200 border border-cyan-500/30 font-medium transition"
                >
                  Preset 1: Developing Growth & Fiscal Push (India)
                </button>
                <button
                  type="button"
                  onClick={applyPreset2}
                  className="px-2.5 py-1 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 text-teal-200 border border-teal-500/30 font-medium transition"
                >
                  Preset 2: Aging & Fiscal Consolidation (Germany)
                </button>
                <button
                  type="button"
                  onClick={clearManual}
                  className="px-2 py-1 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 border border-white/10 transition"
                >
                  Reset
                </button>
              </div>
            </div>

            {/* General Settings */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <label className="text-xs text-slate-400 space-y-1.5">
                Year of indicators
                <input className={inp} placeholder="latest" inputMode="numeric" value={year} onChange={(e) => setYear(e.target.value)} />
              </label>
              <label className="text-xs text-slate-400 space-y-1.5">
                Level of detail
                <select className={inp} value={detail} onChange={(e) => setDetail(e.target.value)}>
                  <option value="auto">Automatic</option>
                  <option value="cofog16">16 detailed areas</option>
                  <option value="cofog10">10 main areas</option>
                </select>
              </label>
              <label className="text-xs text-slate-400 space-y-1.5">
                Stress test (what-if)
                <select className={inp} value={shock} onChange={(e) => setShock(e.target.value)}>
                  <option value="">None</option>
                  {Object.entries(SHOCK_LABELS).map(([k, v]) => (
                    <option key={k} value={k}>{v}</option>
                  ))}
                </select>
              </label>
              <label className="text-xs text-slate-400 space-y-1.5">
                Your total budget (US$)
                <input className={inp} placeholder="model estimate (e.g. 450000000000)" inputMode="decimal" value={budget} onChange={(e) => setBudget(e.target.value)} />
              </label>
            </div>

            {/* Manual Indicator Overrides for Custom Simulation */}
            <div className="rounded-xl p-4 bg-white/[0.02] border border-white/[0.05] space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-200">Manual Macroeconomic Simulation (Custom Indicator Overrides)</span>
                <span className="text-[11px] text-slate-500">Leave blank to use country's official values</span>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                <label className="text-[11px] text-slate-400 space-y-1">
                  GDP growth (%)
                  <input className={inp} placeholder="e.g. 8.2" inputMode="decimal" value={customGdpGrowth} onChange={(e) => setCustomGdpGrowth(e.target.value)} />
                </label>
                <label className="text-[11px] text-slate-400 space-y-1">
                  Inflation (%)
                  <input className={inp} placeholder="e.g. 4.5" inputMode="decimal" value={customInflation} onChange={(e) => setCustomInflation(e.target.value)} />
                </label>
                <label className="text-[11px] text-slate-400 space-y-1">
                  Unemployment (%)
                  <input className={inp} placeholder="e.g. 4.0" inputMode="decimal" value={customUnemployment} onChange={(e) => setCustomUnemployment(e.target.value)} />
                </label>
                <label className="text-[11px] text-slate-400 space-y-1">
                  Population 65+ (%)
                  <input className={inp} placeholder="e.g. 6.8" inputMode="decimal" value={customPop65} onChange={(e) => setCustomPop65(e.target.value)} />
                </label>
                <label className="text-[11px] text-slate-400 space-y-1">
                  Central debt (% GDP)
                  <input className={inp} placeholder="e.g. 55.0" inputMode="decimal" value={customDebt} onChange={(e) => setCustomDebt(e.target.value)} />
                </label>
              </div>
            </div>
          </div>
        )}
      </div>

      <Status loading={loading} warming={warming} error={error} />

      {!data && !loading && !error && (
        <Steps steps={[
          { title: "Pick a country", text: "One choice is all that is needed." },
          { title: "Press the button", text: "Results load instantly for the default view." },
          { title: "Explore the charts", text: "Split, budget flow, peers, ranges and reasons update for each country." },
        ]} />
      )}

      {data && (
        <>
          <div>
            <h2 className="text-xl font-bold text-white">{data.country}</h2>
            <p className="text-sm text-slate-400 mt-1">Indicators from {data.feature_year} · learned from {data.training_economies} economies{data.shock ? ` · stress test: ${data.shock}` : ""}</p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
            <KPICard label="Similarity to training economies" value={sim.label} icon={ShieldCheck} accent={sim.accent} sublabel={`Novelty score ${Number(data.applicability?.novelty_score ?? 0).toFixed(2)}`} />
            <KPICard label="Difference from last year" value={toMove == null ? "n/a" : `${toMove.toFixed(1)}%`} icon={GitCompareArrows} accent="blue" sublabel={toMove == null ? "No official history" : "of the budget would move"} />
            <KPICard label="Largest area" value={top ? `${top.rec.toFixed(1)}%` : "-"} icon={PieIcon} accent="cyan" sublabel={top?.name} />
            <KPICard label="Total budget" value={data.total_budget ? `$${(data.total_budget.used_total_usd / 1e9).toFixed(0)}B` : "-"} icon={Wallet} accent="teal" sublabel={data.total_budget?.source?.startsWith("user") ? "your input" : "model estimate"} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartCard title="Reference split" subtitle="Share of the total budget by area" about="Each colour is one budget area (UN COFOG classification). The shares add up to 100%. Hover a slice for the exact share.">
              <Donut rows={rows} />
            </ChartCard>
            <ChartCard title="Ranked areas" subtitle="Largest to smallest" about="The same split as bars, sorted by size.">
              <RankedBars rows={rows} />
            </ChartCard>
          </div>

          <ChartCard title="Budget flow" subtitle="Total budget, then areas, then Sustainable Development Goals" about="The width of each band is its share of the budget. The link from areas to goals is a reporting cross-walk chosen by the authors (a function's share is split equally among its linked goals); it is not a model input.">
            <FlowSankey rows={rows} sdgInfo={SDG_INFO} />
          </ChartCard>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {hasObs ? (
              <ChartCard title="Difference from last year" subtitle="Model reference minus last actual share (pp)" about="Green: the reference is above last year's actual share. Red: below. Last year's actual split is itself a very strong baseline, so differences are usually small.">
                <DiffBars rows={rows} />
              </ChartCard>
            ) : (
              <ChartCard title="Compared with similar economies" subtitle="Reference vs average of the most similar countries (top areas)" about="Similar economies are found from income, population structure and governance indicators; their actual budgets drive the reference.">
                <PeerBars data={peerBars} />
              </ChartCard>
            )}
            <ChartCard title="Uncertainty" subtitle="Nominal 80% range per area" about="Calibrated to cover 80% of cases on average, but coverage was only about 47% for low-income and 61% for lower-middle-income economies, so treat the ranges for those groups as optimistic.">
              <RangeBars rows={rows} />
            </ChartCard>
          </div>
          {hasObs && peerBars.length > 0 && (
            <ChartCard title="Compared with similar economies" subtitle="Reference vs average of the most similar countries (top areas)">
              <PeerBars data={peerBars} />
            </ChartCard>
          )}

          <div className="glass-card p-6">
            <h3 className="text-base font-semibold text-white">Detailed table</h3>
            <p className="text-sm text-slate-400 mt-1 mb-4">Click a column to sort, click a row for its main factors.</p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead><tr className="text-[11px] uppercase tracking-wide text-slate-500 border-b border-white/[0.08]">
                  {th("name", "Area", false)}{th("rec", "Reference")}{hasObs && th("obs", "Last actual")}{hasObs && th("diff", "Difference")}{th("lo", "80% range")}{data.total_budget && th("amount", "US$ bn")}<th className="py-3 px-3 text-left font-semibold">Size</th><th className="py-3 px-3 text-left font-semibold">SDG</th>
                </tr></thead>
                <tbody>
                  {sorted.map((r) => {
                    const [cls, tone] = shareClass(r.rec);
                    return (
                      <tr key={r.key} className="border-b border-white/[0.05] text-slate-300 hover:bg-white/[0.03] cursor-pointer" onClick={() => setComp(r.key)}>
                        <td className="py-3.5 px-3"><i className="inline-block w-2.5 h-2.5 rounded-sm mr-2.5" style={{ background: r.color }} /><span className="font-medium text-white">{r.name}</span></td>
                        <td className="py-3.5 px-3 text-right font-semibold text-white">{r.rec.toFixed(1)}%</td>
                        {hasObs && <td className="py-3.5 px-3 text-right">{r.obs == null ? "n/a" : `${r.obs.toFixed(1)}%`}</td>}
                        {hasObs && (
                          <td className={`py-3.5 px-3 text-right font-medium ${r.diff > 0.2 ? "text-emerald-300" : r.diff < -0.2 ? "text-rose-300" : "text-slate-400"}`}>
                            <span className="inline-flex items-center gap-1">{r.diff > 0.2 ? <ArrowUp className="w-3 h-3" /> : r.diff < -0.2 ? <ArrowDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}{r.diff > 0 ? "+" : ""}{r.diff.toFixed(1)} pp</span>
                          </td>
                        )}
                        <td className="py-3.5 px-3 text-right text-slate-400">{r.lo == null ? "n/a" : `${r.lo.toFixed(1)}-${r.hi.toFixed(1)}%`}</td>
                        {data.total_budget && <td className="py-3.5 px-3 text-right">{r.amount == null ? "n/a" : (r.amount / 1e9).toFixed(2)}</td>}
                        <td className="py-3.5 px-3"><span className={`px-2 py-0.5 rounded-md text-[11px] font-semibold border ${tone}`}>{cls}</span></td>
                        <td className="py-3.5 px-3 text-slate-400">{r.sdg.map((g) => `SDG ${g}`).join(", ") || "-"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {data.total_budget && <p className="text-xs text-slate-500 mt-4">Total budget used: US$ {(data.total_budget.used_total_usd / 1e9).toFixed(1)} bn ({data.total_budget.source}).</p>}
          </div>

          <ChartCard title={`Main factors: ${sel?.name}`} subtitle="Indicators associated with a higher (blue) or lower (pink) share, in percentage points"
            about="Associations learned from other economies, not causes. The bars explain one tree-based member of the blend, not the blend itself. The number in brackets is the country's own value.">
            <div className="flex flex-wrap items-center justify-end gap-3 mb-2">
              <select className="bg-navy-900 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200" value={sel?.key || ""} onChange={(e) => setComp(e.target.value)}>
                {rows.map((r) => <option key={r.key} value={r.key}>{r.name}</option>)}
              </select>
            </div>
            <ResponsiveContainer width="100%" height={Math.max(240, shapData.length * 40)}>
              <BarChart data={shapData} layout="vertical" margin={{ left: 10, right: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" tick={axis} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="label" width={240} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
                <ReferenceLine x={0} stroke="#64748b" />
                <Tooltip contentStyle={tip} itemStyle={itemStyle} labelStyle={labelStyle} cursor={{ fill: "rgba(255,255,255,0.04)" }} formatter={(v) => `${v} pp`} />
                <Bar dataKey="v" radius={5} barSize={18}>{shapData.map((d, i) => <Cell key={i} fill={d.v >= 0 ? "#60a5fa" : "#f472b6"} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
            <label className="mt-4 flex items-center gap-2 text-sm text-slate-400">
              <input type="checkbox" checked={useLime} onChange={(e) => { setUseLime(e.target.checked); if (e.target.checked) run({ iso3, panel, shock: shock || undefined, year, limeSector: sel?.key, totalBudgetUsd: budget ? Number(budget) : undefined }); }} />
              Also show a second opinion (LIME) for this area
            </label>
            {useLime && data.lime && data.lime.sector === sel?.key && (
              <p className="mt-3 text-sm text-slate-400">LIME fit {Number(data.lime.local_r2).toFixed(2)} (closer to 1 is more trustworthy). Top factors: {data.lime.features.slice(0, 4).map((f) => `${friendly(f.feature)} (${f.contribution_pp >= 0 ? "+" : ""}${f.contribution_pp.toFixed(2)} pp)`).join(", ")}.</p>
            )}
          </ChartCard>

          {data.similar_economies?.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="text-base font-semibold text-white flex items-center gap-2"><Users className="w-4 h-4 text-cyan-300" /> Most similar economies</h3>
              <p className="text-sm text-slate-400 mt-1 mb-4">Their actual budgets drive the reference.</p>
              <div className="flex flex-wrap gap-3">
                {data.similar_economies.map((p) => (
                  <span key={p.iso3} className="px-4 py-2 rounded-full text-sm bg-white/[0.05] border border-white/10 text-slate-200">{p.country} <span className="text-slate-500">· {(p.weight * 100).toFixed(0)}%</span></span>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <div className="flex flex-wrap gap-5 text-xs text-slate-400 pt-2 pb-6">
        <Link to="/guide" className="inline-flex items-center gap-1.5 text-cyan-300"><BookOpen className="w-3.5 h-3.5" /> Guide and glossary</Link>
        <span className="inline-flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-amber-300" /> Reference only; human review required.</span>
      </div>
    </div>
  );
}
