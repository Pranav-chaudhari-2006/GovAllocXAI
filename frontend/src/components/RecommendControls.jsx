import React, { useEffect, useState } from "react";
import { getEconomies, PANELS, SHOCK_LABELS } from "../services/api";

const sel = "w-full bg-navy-900 border border-white/10 rounded-lg px-3 py-2 text-sm text-slate-200";

/** Shared selectors: economy, panel, shock. Calls onChange({iso3, panel, shock}). */
export default function RecommendControls({ value, onChange, onWarming, extra }) {
  const [economies, setEconomies] = useState([]);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let live = true;
    getEconomies({ onRetry: () => live && onWarming?.(true) })
      .then((e) => {
        if (!live) return;
        onWarming?.(false);
        setEconomies(e);
        if (!value.iso3) onChange({ ...value, iso3: e.find((x) => x.iso3 === "IND")?.iso3 || e[0]?.iso3 });
      })
      .catch((e) => live && (onWarming?.(false), setErr(e.message)));
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="glass-card p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
      <label className="text-xs text-slate-400 space-y-1">
        Economy
        <select className={sel} value={value.iso3 || ""} onChange={(e) => onChange({ ...value, iso3: e.target.value })}>
          {economies.map((e) => (
            <option key={e.iso3} value={e.iso3}>
              {e.country} ({e.iso3}){e.has_official_cofog_history ? "" : " - no official history"}
            </option>
          ))}
        </select>
      </label>
      <label className="text-xs text-slate-400 space-y-1">
        Panel
        <select className={sel} value={value.panel} onChange={(e) => onChange({ ...value, panel: e.target.value })}>
          {Object.entries(PANELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </label>
      <label className="text-xs text-slate-400 space-y-1">
        Shock preset (sensitivity only)
        <select className={sel} value={value.shock || ""} onChange={(e) => onChange({ ...value, shock: e.target.value })}>
          <option value="">None</option>
          {Object.entries(SHOCK_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
        </select>
      </label>
      {extra}
      {err && <div className="md:col-span-3 text-sm text-rose-300">{err}</div>}
    </div>
  );
}
