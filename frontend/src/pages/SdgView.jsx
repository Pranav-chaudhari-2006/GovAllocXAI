import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import Header from "../components/Header";
import { ChartCard, tip, axis } from "../components/charts";
import { recommendBudget } from "../services/api";
import { SDG_INFO, sdgShares } from "../data/sdg";
import { PALETTE } from "../data/glossary";
import { useSharedResult } from "../state/ResultContext";

export default function SdgView() {
  const { shared, setShared } = useSharedResult();
  const [fallback, setFallback] = useState(null);

  useEffect(() => {
    if (!shared) recommendBudget({ iso3: "IND", panel: "cofog10" }, { retries: 2 }).then(setFallback).catch(() => {});
  }, [shared]);

  const data = shared || fallback;
  const goals = useMemo(() => sdgShares(data?.components), [data]);
  const byGoal = useMemo(() => {
    const m = {};
    (data?.components || []).forEach((c, i) => (c.sdg || []).forEach((g) => { (m[g] = m[g] || []).push({ name: c.label, color: PALETTE[i % PALETTE.length] }); }));
    return m;
  }, [data]);

  return (
    <div className="space-y-8 max-w-7xl">
      <Header
        title="SDG View"
        subtitle="How the reference split of the selected country maps to the Sustainable Development Goals."
        badge={<span className="badge-demo">Reporting cross-walk</span>}
      />
      <div className="rounded-xl border border-white/10 bg-white/[0.03] px-5 py-3 text-sm text-slate-300">
        {data ? <>Showing <b className="text-white">{data.country}</b>. Change the country on the <Link to="/" className="text-cyan-300">Budget Explorer</Link> page and come back.</> : "Loading an example country..."}
        {" "}The link from budget areas to goals is illustrative: each area's share is split equally among its linked goals. It is not a validated SDG assessment.
      </div>

      {data && (
        <>
          <ChartCard title="Budget share attributed to each goal" subtitle="Percent of the total budget">
            <ResponsiveContainer width="100%" height={Math.max(280, goals.length * 44)}>
              <BarChart data={goals} layout="vertical" margin={{ left: 10, right: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
                <XAxis type="number" tick={axis} unit="%" axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="name" width={230} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={tip} cursor={{ fill: "rgba(255,255,255,0.04)" }} formatter={(v) => `${Number(v).toFixed(1)}%`} />
                <Bar dataKey="share" radius={[0, 8, 8, 0]} barSize={22}>{goals.map((g) => <Cell key={g.goal} fill={g.color} />)}</Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {goals.map((g) => (
              <div key={g.goal} className="glass-card glass-card-hover p-5">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shrink-0" style={{ background: g.color }}>{g.goal}</div>
                  <div className="min-w-0">
                    <div className="text-xs text-slate-400">SDG {g.goal}</div>
                    <div className="text-sm font-semibold text-white leading-snug">{SDG_INFO[g.goal]?.[0]}</div>
                  </div>
                  <div className="ml-auto text-right">
                    <div className="text-xl font-bold text-white">{g.share.toFixed(1)}%</div>
                    <div className="text-[11px] text-slate-500">of the budget</div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/[0.06]">
                  {(byGoal[g.goal] || []).map((a) => (
                    <span key={a.name} className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white/[0.05] text-[11px] text-slate-300"><i className="w-2 h-2 rounded-sm" style={{ background: a.color }} />{a.name}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
