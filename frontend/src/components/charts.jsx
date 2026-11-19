import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, Sankey, ReferenceLine,
} from "recharts";

export const tip = {
  background: "#0d1626",
  border: "1px solid rgba(255,255,255,0.22)",
  fontSize: 12,
  borderRadius: 10,
  padding: "8px 12px",
  color: "#f8fafc",
  boxShadow: "0 10px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.7)"
};
export const itemStyle = { color: "#f8fafc", fontSize: 12 };
export const labelStyle = { color: "#38bdf8", fontWeight: 600, fontSize: 12, marginBottom: 4 };
export const axis = { fill: "#94a3b8", fontSize: 11 };
const grid = "rgba(255,255,255,0.06)";

/** Card with a title, a one-line subtitle and an optional collapsible explanation (keeps the page light on text). */
export function ChartCard({ title, subtitle, about, children, className = "" }) {
  return (
    <div className={`glass-card p-6 ${className}`}>
      <h3 className="text-base font-semibold text-white">{title}</h3>
      {subtitle && <p className="text-sm text-slate-400 mt-1 mb-4">{subtitle}</p>}
      {children}
      {about && (
        <details className="mt-4 text-xs text-slate-400">
          <summary className="cursor-pointer text-cyan-300/90 hover:text-cyan-200">What does this show?</summary>
          <p className="mt-2 leading-relaxed">{about}</p>
        </details>
      )}
    </div>
  );
}

export function Donut({ rows, height = 280 }) {
  const top = [...rows].sort((a, b) => b.rec - a.rec)[0];
  return (
    <div className="flex flex-col gap-5">
      <div className="relative mx-auto w-full" style={{ maxWidth: 360 }}>
        <ResponsiveContainer width="100%" height={height}>
          <PieChart>
            <Pie data={rows} dataKey="rec" nameKey="name" innerRadius="60%" outerRadius="94%" paddingAngle={3} stroke="none" cornerRadius={4}>
              {rows.map((r) => <Cell key={r.key} fill={r.color} />)}
            </Pie>
            <Tooltip contentStyle={tip} itemStyle={itemStyle} labelStyle={labelStyle} formatter={(v) => `${Number(v).toFixed(1)}%`} />
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-3xl font-bold text-white">{top ? `${top.rec.toFixed(0)}%` : ""}</span>
          <span className="text-[11px] text-slate-400 text-center max-w-[100px] leading-tight">{top?.name}</span>
        </div>
      </div>
      <ul className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1.5 text-sm">
        {[...rows].sort((a, b) => b.rec - a.rec).map((r) => (
          <li key={r.key} className="flex items-center gap-2 text-slate-300 min-w-0">
            <i className="w-3 h-3 rounded-sm shrink-0" style={{ background: r.color }} />
            <span className="truncate">{r.name}</span>
            <span className="ml-auto text-slate-400 tabular-nums">{r.rec.toFixed(1)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function RankedBars({ rows }) {
  const data = [...rows].sort((a, b) => b.rec - a.rec);
  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} horizontal={false} />
        <XAxis type="number" tick={axis} unit="%" axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="name" width={170} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={tip} itemStyle={itemStyle} labelStyle={labelStyle} cursor={{ fill: "rgba(255,255,255,0.04)" }} formatter={(v) => `${Number(v).toFixed(1)}%`} />
        <Bar dataKey="rec" name="Model reference" radius={[0, 8, 8, 0]} barSize={20}>
          {data.map((r) => <Cell key={r.key} fill={r.color} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Difference between the model reference and last year's actual share (only when official history exists). */
export function DiffBars({ rows }) {
  const data = rows.filter((r) => r.diff != null).sort((a, b) => b.diff - a.diff);
  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} horizontal={false} />
        <XAxis type="number" tick={axis} unit=" pp" axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="name" width={170} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
        <ReferenceLine x={0} stroke="#64748b" />
        <Tooltip contentStyle={tip} itemStyle={itemStyle} labelStyle={labelStyle} cursor={{ fill: "rgba(255,255,255,0.04)" }} formatter={(v) => `${v > 0 ? "+" : ""}${Number(v).toFixed(2)} pp`} />
        <Bar dataKey="diff" name="Model minus last year" radius={4} barSize={18}>
          {data.map((r) => <Cell key={r.key} fill={r.diff >= 0 ? "#34d399" : "#fb7185"} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Reference split vs the weighted average of the most similar economies (top areas only, to stay readable). */
export function PeerBars({ data }) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 52)}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 24 }} barGap={3}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} horizontal={false} />
        <XAxis type="number" tick={axis} unit="%" axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="name" width={170} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={tip} itemStyle={itemStyle} labelStyle={labelStyle} cursor={{ fill: "rgba(255,255,255,0.04)" }} formatter={(v) => `${Number(v).toFixed(1)}%`} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar dataKey="rec" name="Model reference" fill="#22d3ee" radius={[0, 6, 6, 0]} barSize={14} />
        <Bar dataKey="peer" name="Similar economies (average)" fill="#a78bfa" radius={[0, 6, 6, 0]} barSize={14} />
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Nominal 80 % band around each reference share: a darker segment below and a lighter one above the reference value. */
export function RangeBars({ rows }) {
  const data = [...rows].filter((r) => r.lo != null).sort((a, b) => b.rec - a.rec).map((r) => ({
    name: r.name, base: r.lo, down: Math.max(0, r.rec - r.lo), up: Math.max(0, r.hi - r.rec), rec: r.rec, lo: r.lo, hi: r.hi, color: r.color,
  }));
  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 36)}>
      <BarChart data={data} layout="vertical" margin={{ left: 10, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} horizontal={false} />
        <XAxis type="number" tick={axis} unit="%" axisLine={false} tickLine={false} />
        <YAxis type="category" dataKey="name" width={170} tick={{ fill: "#cbd5e1", fontSize: 12 }} axisLine={false} tickLine={false} />
        <Tooltip
          cursor={{ fill: "rgba(255,255,255,0.04)" }}
          content={({ active, payload }) => {
            if (!active || !payload?.length) return null;
            const p = payload[0].payload;
            return (
              <div style={tip}>
                <div style={{ color: "#fff", fontWeight: 600 }}>{p.name}</div>
                <div style={{ color: "#cbd5e1" }}>Reference {p.rec.toFixed(1)}%</div>
                <div style={{ color: "#94a3b8" }}>Nominal 80% range {p.lo.toFixed(1)}-{p.hi.toFixed(1)}%</div>
              </div>
            );
          }}
        />
        <Bar dataKey="base" stackId="r" fill="transparent" />
        <Bar dataKey="down" stackId="r" name="Reference" barSize={16}>
          {data.map((r, i) => <Cell key={i} fill={r.color} fillOpacity={0.9} />)}
        </Bar>
        <Bar dataKey="up" stackId="r" radius={[0, 8, 8, 0]} barSize={16}>
          {data.map((r, i) => <Cell key={i} fill={r.color} fillOpacity={0.35} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/** Budget flow: total budget -> budget areas -> SDGs (reporting cross-walk). Redraws with every prediction. */
export function FlowSankey({ rows, sdgInfo, height = 420 }) {
  const areas = [...rows].sort((a, b) => b.rec - a.rec);
  const goals = new Map();
  areas.forEach((r) => (r.sdg || []).forEach((g) => { if (!goals.has(g)) goals.set(g, goals.size); }));
  const nodes = [{ name: "Total budget", color: "#22d3ee" }, ...areas.map((r) => ({ name: r.name, color: r.color })), ...[...goals.keys()].map((g) => ({ name: `SDG ${g}`, color: sdgInfo[g]?.[1] || "#64748b" }))];
  const links = [];
  areas.forEach((r, i) => links.push({ source: 0, target: i + 1, value: Math.max(r.rec, 0.05), color: r.color }));
  areas.forEach((r, i) => (r.sdg || []).forEach((g) => links.push({ source: i + 1, target: 1 + areas.length + goals.get(g), value: Math.max(r.rec / (r.sdg.length || 1), 0.05), color: r.color })));
  const Node = ({ x, y, width, height: h, index, payload }) => {
    const c = nodes[index]?.color || "#64748b";
    const right = index > areas.length;
    return (
      <g>
        <rect x={x} y={y} width={width} height={h} fill={c} rx={3} />
        {index !== 0 && (
          <text x={right ? x - 6 : x + width + 6} y={y + h / 2} textAnchor={right ? "end" : "start"} dominantBaseline="middle" fontSize={11} fill="#cbd5e1">{payload.name}</text>
        )}
        {index === 0 && <text x={x + width + 6} y={y + h / 2} dominantBaseline="middle" fontSize={11} fill="#e2e8f0">Total budget</text>}
      </g>
    );
  };
  const Link = ({ sourceX, targetX, sourceY, targetY, sourceControlX, targetControlX, linkWidth, index }) => (
    <path d={`M${sourceX},${sourceY} C${sourceControlX},${sourceY} ${targetControlX},${targetY} ${targetX},${targetY}`} fill="none" stroke={links[index]?.color || "#64748b"} strokeWidth={Math.max(linkWidth, 1)} strokeOpacity={0.35} />
  );
  return (
    <ResponsiveContainer width="100%" height={height}>
      <Sankey data={{ nodes, links }} node={<Node />} link={<Link />} nodePadding={14} nodeWidth={10} margin={{ left: 100, right: 100, top: 10, bottom: 10 }}>
        <Tooltip contentStyle={tip} itemStyle={itemStyle} labelStyle={labelStyle} />
      </Sankey>
    </ResponsiveContainer>
  );
}

export function Steps({ steps }) {
  return (
    <div className="flex flex-col md:flex-row md:items-stretch gap-3">
      {steps.map((s, i) => (
        <React.Fragment key={s.title}>
          <div className="flex-1 glass-card p-5">
            <div className="text-xs font-semibold text-cyan-300 mb-1">STEP {i + 1}</div>
            <div className="text-sm font-semibold text-white">{s.title}</div>
            <div className="text-xs text-slate-400 mt-1">{s.text}</div>
          </div>
          {i < steps.length - 1 && <div className="hidden md:flex items-center text-slate-500 text-xl">&rarr;</div>}
        </React.Fragment>
      ))}
    </div>
  );
}
