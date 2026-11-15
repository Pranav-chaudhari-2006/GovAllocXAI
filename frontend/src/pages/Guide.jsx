import React from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import { GLOSSARY } from "../data/glossary";

const STEPS = [
  ["Pick a country", "Use the drop-down on the first page. Nothing else is required."],
  ["Press 'Get recommendation'", "The AI automatically chooses the model, the level of detail (16 or 10 budget areas) and the latest year. The first request can take about a minute while the models warm up."],
  ["Check the similarity to training economies", "High means the country's indicators look like those of the economies the model learned from. Low means the numbers are an extrapolation. This is a similarity measure, not a probability that the numbers are right."],
  ["Read the colour charts and the difference table", "Green rows are where the model reference is above last year's share, red rows where it is below. This is descriptive, not advice. Click a row to see the main factors."],
  ["Read the main factors", "Blue bars are associated with a higher share, pink bars with a lower share. These are associations learned from other economies, not causes."],
];

export default function Guide() {
  return (
    <div className="space-y-6 max-w-4xl">
      <Header title="How to use this website" subtitle="A two-minute guide for first-time users. No technical knowledge needed." />
      <div className="glass-card p-5 space-y-3">
        <h3 className="text-sm font-semibold text-white">Five simple steps</h3>
        <ol className="space-y-3">
          {STEPS.map(([t, d], i) => (
            <li key={t} className="flex gap-3">
              <span className="w-6 h-6 shrink-0 rounded-full bg-cyan-500/20 text-cyan-300 text-xs flex items-center justify-center">{i + 1}</span>
              <div><div className="text-sm font-medium text-white">{t}</div><div className="text-sm text-slate-400">{d}</div></div>
            </li>
          ))}
        </ol>
        <Link to="/" className="inline-block mt-1 px-4 py-2 rounded-lg bg-cyan-500/20 text-cyan-200 ring-1 ring-cyan-500/30 text-sm">Go to the recommendation page</Link>
      </div>

      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-white mb-1">Why do I not have to choose a model?</h3>
        <p className="text-sm text-slate-400">The website always uses one fixed model (a blend of four learners, weights set by cross-validation; in our tests about as accurate as a simple average of the most similar economies) and picks the amount of detail that the official data allow: 16 detailed COFOG functions where official data cover them, otherwise 10 main COFOG areas. Extra settings are tucked under <i>Advanced options</i> and are only for experts. The allocation always adds up to exactly 100 % and respects sensible upper and lower limits for each area.</p>
      </div>

      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-white mb-3">Glossary (every unfamiliar term)</h3>
        <dl className="grid md:grid-cols-2 gap-x-6 gap-y-3">
          {GLOSSARY.map(([t, d]) => (
            <div key={t}><dt className="text-sm font-medium text-cyan-200">{t}</dt><dd className="text-sm text-slate-400">{d}</dd></div>
          ))}
        </dl>
      </div>

      <div className="glass-card p-5 text-sm text-slate-400">
        <h3 className="text-sm font-semibold text-white mb-1">Important limits</h3>
        Government budgets are decided by people and laws. This tool shows what comparable economies typically do and why; it cannot know a country's politics, treaties or emergencies. Where official history exists, last year's actual budget is a very strong baseline (in our tests a learned correction improved on it by only a fraction of a percentage point), so the model split is a reference point, not a better forecast. For countries that are part of the training data the website shows in-sample fits, which look more accurate than the leave-one-country-out errors in the paper. The 80 % range covered about 80 % of cases on average but only about 47 % for low-income and 61 % for lower-middle-income economies. The data are executed (outturn) spending, not planned budgets. Never apply the numbers automatically.
      </div>
    </div>
  );
}
