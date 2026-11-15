import React from "react";
import Header from "../components/Header";
import { Disclaimer } from "../components/Banners";

const POINTS = [
  "Targets are official COFOG expenditure shares (Eurostat, OECD, IMF), normalised to sum to 100%: 16 functions for 36 economies, or 10 divisions for 85 economies including developing ones.",
  "Predictors are 25 macro, demographic, development and governance indicators (World Bank WDI/WGI); no feature derived from the target is used (earlier synthetic-data versions leaked one and were retired).",
  "Models are evaluated leave-country-out (cold start) and on a temporal split 2020-24 (annual update), against persistence and peer-mean baselines.",
  "Explanations: SHAP values (in percentage points) per component and LIME local surrogates for a chosen component.",
  "Shock presets (recession, stagflation, severe stress) are counterfactual sensitivity checks, not causal estimates.",
  "The applicability banner reports how unusual an economy's indicators are versus the training economies; treat 'unusual' or 'outside typical range' recommendations as extrapolations.",
  "Error is highest for low-income economies (TVD about 33 pp) and gains over baselines are small.",
];

export default function Methodology() {
  return (
    <div className="space-y-5">
      <Header title="Methodology and Limits" subtitle="What the system does, and what it does not claim." />
      <Disclaimer />
      <ul className="glass-card p-5 space-y-3 text-sm text-slate-300 list-disc list-inside">
        {POINTS.map((p) => (
          <li key={p}>{p}</li>
        ))}
      </ul>
    </div>
  );
}
