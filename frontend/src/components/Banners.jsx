import React from "react";
import { AlertTriangle, Info, Loader2 } from "lucide-react";
import { DISCLAIMER } from "../services/api";

export function Disclaimer() {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-slate-500/20 bg-white/[0.03] px-3 py-2 text-xs text-slate-300">
      <Info className="w-4 h-4 shrink-0 mt-0.5 text-cyan-300" />
      <span>{DISCLAIMER}</span>
    </div>
  );
}

export function ApplicabilityBanner({ applicability }) {
  if (!applicability) return null;
  const { status, novelty_score, percentile_among_training_economies } = applicability;
  const typical = status === "typical";
  const severe = status?.startsWith("outside");
  const cls = typical
    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-200"
    : severe
      ? "border-rose-500/40 bg-rose-500/10 text-rose-200"
      : "border-amber-500/40 bg-amber-500/10 text-amber-200";
  return (
    <div className={`flex items-start gap-3 rounded-xl border px-4 py-3 ${cls}`}>
      <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
      <div className="text-sm">
        <div className="font-semibold">Applicability: {status}</div>
        <div className="text-xs opacity-80 mt-0.5">
          Novelty score {Number(novelty_score).toFixed(2)}; more unusual than{" "}
          {Number(percentile_among_training_economies).toFixed(0)}% of training economies.
        </div>
      </div>
    </div>
  );
}

export function Status({ loading, warming, error }) {
  if (error) {
    return (
      <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200">{error}</div>
    );
  }
  if (!loading) return null;
  return (
    <div className="flex items-center gap-2 rounded-lg border border-cyan-500/20 bg-cyan-500/5 px-3 py-2 text-sm text-cyan-200">
      <Loader2 className="w-4 h-4 animate-spin" />
      {warming
        ? "The backend is warming up (the first request can take about a minute). Retrying automatically..."
        : "Computing..."}
    </div>
  );
}
