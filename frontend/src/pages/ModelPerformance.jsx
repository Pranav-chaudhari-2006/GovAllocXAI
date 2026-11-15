import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import Header from "../components/Header";
import { ANNUAL_UPDATE, COLD_START, R2_BY_FUNCTION, ERROR_BY_INCOME, RESULTS_SOURCE } from "../data/results";

const tip = { background: "#0d1626", border: "1px solid rgba(255,255,255,0.1)", fontSize: 12 };
const axis = { fill: "#94a3b8", fontSize: 11 };

function Card({ title, note, children }) {
  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-white mb-1">{title}</h3>
      <p className="text-xs text-slate-500 mb-3">{note}</p>
      {children}
    </div>
  );
}

function Chart({ data, xKey, bars }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
        <XAxis dataKey={xKey} tick={axis} />
        <YAxis tick={axis} />
        <Tooltip contentStyle={tip} />
        {bars.length > 1 && <Legend />}
        {bars.map((b) => (
          <Bar key={b.key} dataKey={b.key} name={b.name} fill={b.fill} />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

export default function ModelPerformance() {
  return (
    <div className="space-y-5">
      <Header
        title="Model Performance"
        subtitle={`Held-out evaluation, ${RESULTS_SOURCE}. Gains over simple baselines are modest; this is not a high-accuracy forecaster.`}
      />
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card title="Annual update (TVD, pp; lower is better)" note="Temporal split 2020-24: persistence vs learned hybrid.">
          <Chart
            data={[{ name: "Annual update", persistence: ANNUAL_UPDATE.persistence, hybrid: ANNUAL_UPDATE.hybrid }]}
            xKey="name"
            bars={[
              { key: "persistence", name: "Persistence", fill: "#64748b" },
              { key: "hybrid", name: "Learned hybrid", fill: "#22d3ee" },
            ]}
          />
          <p className="text-xs text-slate-400 mt-2">Paired gain {ANNUAL_UPDATE.gain} pp.</p>
        </Card>
        <Card title="Cold start (TVD, pp; lower is better)" note="Leave-country-out: stack vs peer-mean baseline.">
          <Chart
            data={COLD_START}
            xKey="panel"
            bars={[
              { key: "peer", name: "Peer mean", fill: "#64748b" },
              { key: "stack", name: "Stack", fill: "#22d3ee" },
            ]}
          />
        </Card>
        <Card title="Global panel R-squared by function" note="Model vs peer baseline; weak for defence and education.">
          <Chart
            data={R2_BY_FUNCTION}
            xKey="fn"
            bars={[
              { key: "peer", name: "Peer", fill: "#64748b" },
              { key: "model", name: "Model", fill: "#2dd4bf" },
            ]}
          />
        </Card>
        <Card title="Error by income group (TVD, pp, XGBoost)" note="Accuracy degrades sharply for lower-income economies.">
          <Chart data={ERROR_BY_INCOME} xKey="group" bars={[{ key: "tvd", name: "TVD (pp)", fill: "#f59e0b" }]} />
        </Card>
      </div>
    </div>
  );
}
