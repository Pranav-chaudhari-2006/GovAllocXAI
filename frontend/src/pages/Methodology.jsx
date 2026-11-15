import React from "react";
import { Database, SlidersHorizontal, FlaskConical, Brain, Zap, ShieldAlert, TrendingDown } from "lucide-react";
import Header from "../components/Header";

const CARDS = [
  { icon: Database, tone: "text-cyan-300 bg-cyan-500/10", title: "What we predict", text: "Official shares of government spending by function (COFOG) from Eurostat, OECD and the IMF, always adding up to 100%. 16 functions for 36 economies, or 10 areas for 85 economies." },
  { icon: SlidersHorizontal, tone: "text-teal-300 bg-teal-500/10", title: "What the model sees", text: "25 economic, demographic, development and governance indicators from the World Bank. No indicator is derived from the spending shares." },
  { icon: FlaskConical, tone: "text-blue-300 bg-blue-500/10", title: "How it is tested", text: "On countries it has never seen (leave-country-out) and on 2020-24 (temporal split), always against two simple baselines: last year's split and the income-group average." },
  { icon: Brain, tone: "text-violet-300 bg-violet-500/10", title: "How it explains", text: "SHAP shows which indicators push a share up or down (in percentage points); LIME gives a second, simpler opinion for one area." },
  { icon: Zap, tone: "text-amber-300 bg-amber-500/10", title: "Stress tests", text: "Recession, stagflation and severe-stress presets show how the reference moves. They are sensitivity checks, not forecasts or causal estimates." },
  { icon: ShieldAlert, tone: "text-rose-300 bg-rose-500/10", title: "Similarity score", text: "Shows how unusual a country is compared with the countries the model learned from. Low similarity means the numbers are an extrapolation." },
  { icon: TrendingDown, tone: "text-emerald-300 bg-emerald-500/10", title: "Honest limits", text: "Last year's actual split is very hard to beat, so gains are small. Errors are largest for low-income countries (about 33 percentage points). Reference only; a human decides." },
];

export default function Methodology() {
  return (
    <div className="space-y-8 max-w-7xl">
      <Header title="Methodology and Limits" subtitle="What the system does, and what it does not claim." />
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {CARDS.map(({ icon: Icon, tone, title, text }) => (
          <div key={title} className="glass-card glass-card-hover p-6">
            <div className={`w-11 h-11 rounded-xl flex items-center justify-center mb-4 ${tone}`}>
              <Icon className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-white">{title}</h3>
            <p className="text-sm text-slate-400 mt-2 leading-relaxed">{text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
