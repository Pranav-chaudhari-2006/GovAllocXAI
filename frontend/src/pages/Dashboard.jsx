import React from "react";
import { Link } from "react-router-dom";
import { Activity, Snowflake, Globe2 } from "lucide-react";
import Header from "../components/Header";
import KPICard from "../components/KPICard";
import { Disclaimer } from "../components/Banners";
import { ANNUAL_UPDATE, COLD_START, RESULTS_SOURCE } from "../data/results";

export default function Dashboard() {
  const [c16, c10] = COLD_START;
  return (
    <div className="space-y-6">
      <Header
        title="GovAllocXAI: Budget Decision Support"
        subtitle="Peer-based reference shares of government expenditure by COFOG function, learned from official data of peer economies, with SHAP/LIME associations."
        badge={<span className="badge-implemented">Official data (Eurostat, OECD, IMF, WDI)</span>}
      />
      <Disclaimer />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <KPICard
          label="Annual update error (TVD)"
          value={`${ANNUAL_UPDATE.hybrid} pp`}
          sublabel={`Learned hybrid vs ${ANNUAL_UPDATE.persistence} pp persistence (paired gain ${ANNUAL_UPDATE.gain} pp for one learner seed; about 0.12 pp averaged over five seeds, not robust)`}
          icon={Activity}
          accent="cyan"
        />
        <KPICard
          label="Cold-start TVD, 16 functions"
          value={`${c16.stack} pp`}
          sublabel={`Stack vs ${c16.peer} pp peer-mean (${c16.panel})`}
          icon={Snowflake}
          accent="teal"
        />
        <KPICard
          label="Cold-start TVD, 10 divisions"
          value={`${c10.stack} pp`}
          sublabel={`Stack vs ${c10.peer} pp peer-mean (${c10.panel})`}
          icon={Globe2}
          accent="blue"
        />
      </div>
      <p className="text-xs text-slate-500">
        Total variation distance (TVD, percentage points of the budget misallocated; lower is better). {RESULTS_SOURCE}.
        The gain over simple baselines is small, and for the 16-function panel it does not survive multiple-comparison correction; see Model Performance for per-function and per-income-group results.
      </p>

      <div className="glass-card p-6 text-sm text-slate-300 space-y-2">
        <h3 className="text-sm font-semibold text-white">Where to go</h3>
        <p>
          <Link className="text-cyan-300 underline" to="/">Get recommendation</Link>: pick an economy,
          panel and optional shock; compare recommended vs last observed shares.
        </p>
        <p>
          <Link className="text-cyan-300 underline" to="/explainable-ai">Explainable AI</Link>: SHAP top features per
          component and optional LIME.
        </p>
        <p>
          <Link className="text-cyan-300 underline" to="/model-performance">Model Performance</Link> and{" "}
          <Link className="text-cyan-300 underline" to="/methodology">Methodology</Link>: honest evaluation and limits.
        </p>
      </div>
    </div>
  );
}
