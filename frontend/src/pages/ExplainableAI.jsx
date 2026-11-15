import React, { useState } from "react";
import { Play } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts";
import Header from "../components/Header";
import RecommendControls from "../components/RecommendControls";
import useRecommendation from "../components/useRecommendation";
import { ApplicabilityBanner, Disclaimer, Status } from "../components/Banners";

const tip = { background: "#0d1626", border: "1px solid rgba(255,255,255,0.1)", fontSize: 12 };

function ContribChart({ data, valueKey }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 34)}>
      <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis type="number" tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <YAxis type="category" dataKey="label" width={200} tick={{ fill: "#94a3b8", fontSize: 11 }} />
        <ReferenceLine x={0} stroke="#475569" />
        <Tooltip contentStyle={tip} />
        <Bar dataKey={valueKey}>
          {data.map((d, i) => (
            <Cell key={i} fill={d[valueKey] >= 0 ? "#22d3ee" : "#f472b6"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function ExplainableAI() {
  const [sel, setSel] = useState({ iso3: "", panel: "cofog10", shock: "" });
  const [comp, setComp] = useState("");
  const [useLime, setUseLime] = useState(false);
  const { data, loading, warming, error, run, setWarming } = useRecommendation();

  const components = data?.components || [];
  const current = components.find((c) => c.component === comp) || components[0];
  const shap = (current?.top_shap || []).map((s) => ({
    ...s,
    label: `${s.feature} = ${Number(s.feature_value).toFixed(2)}`,
  }));
  const limeOk = data?.lime && data.lime.sector === current?.component;

  const go = (c) =>
    run({ iso3: sel.iso3, panel: sel.panel, shock: sel.shock || undefined, limeSector: useLime ? c || undefined : undefined });

  return (
    <div className="space-y-8">
      <Header
        title="Explainable AI"
        subtitle="SHAP: how much each indicator moved a component's recommended share (percentage points) versus the average economy. LIME: a local linear surrogate for one chosen component."
      />
      <Disclaimer />
      <RecommendControls value={sel} onChange={setSel} onWarming={setWarming} />
      <div className="flex flex-wrap items-center gap-4">
        <label className="flex items-center gap-2 text-xs text-slate-400">
          <input type="checkbox" checked={useLime} onChange={(e) => setUseLime(e.target.checked)} />
          Also compute LIME for the component selected below
        </label>
        <button
          disabled={!sel.iso3 || loading}
          onClick={() => go(current?.component)}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-200 ring-1 ring-cyan-500/30 text-sm font-medium disabled:opacity-40"
        >
          <Play className="w-4 h-4" /> Explain
        </button>
      </div>
      <Status loading={loading} warming={warming} error={error} />

      {data && (
        <>
          <ApplicabilityBanner applicability={data.applicability} />
          <div className="glass-card p-6">
            <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
              <h3 className="text-sm font-semibold text-white">
                SHAP top features (pp): {current?.label || current?.component}
              </h3>
              <select
                className="bg-navy-900 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-slate-200"
                value={current?.component || ""}
                onChange={(e) => setComp(e.target.value)}
              >
                {components.map((c) => (
                  <option key={c.component} value={c.component}>
                    {c.label || c.component}
                  </option>
                ))}
              </select>
            </div>
            {current && (
              <p className="text-xs text-slate-400 mb-2">
                Recommended {current.recommended_share_pct.toFixed(2)}% (raw model {current.raw_model_share_pct.toFixed(2)}%)
                {current.last_observed_share_pct != null && `; last observed ${current.last_observed_share_pct.toFixed(2)}%`}.
              </p>
            )}
            <ContribChart data={shap} valueKey="shap_pp" />
          </div>

          {useLime && (
            <div className="glass-card p-6">
              {limeOk ? (
                <>
                  <h3 className="text-sm font-semibold text-white mb-1">LIME: {data.lime.sector}</h3>
                  <p className="text-xs text-slate-400 mb-2">
                    Local surrogate R-squared {Number(data.lime.local_r2).toFixed(2)}. Low values mean the local
                    explanation is unreliable.
                  </p>
                  <ContribChart
                    data={data.lime.features.map((f) => ({ ...f, label: f.feature }))}
                    valueKey="contribution_pp"
                  />
                </>
              ) : (
                <p className="text-sm text-slate-400">
                  Select a component above, then press Explain again to compute LIME for it.
                </p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
