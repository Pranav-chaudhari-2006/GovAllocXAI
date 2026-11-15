// API client for the GovAllocXAI v2 backend (official COFOG data, no demo numbers).
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/+$/, "");

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * Fetch JSON, retrying on network errors / 502 / 503 / 504 (backend cold start can take ~60 s).
 * onRetry(attempt) is called before each retry so the UI can show a "warming up" message.
 */
async function request(path, options = {}, { onRetry, retries = 12, delayMs = 5000 } = {}) {
  let lastError;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(`${API_BASE_URL}${path}`, options);
      if (res.ok) return await res.json();
      if (![502, 503, 504].includes(res.status)) {
        let detail = `${res.status} ${res.statusText}`;
        try {
          const body = await res.json();
          if (body?.detail) detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
        } catch { /* not JSON */ }
        const err = new Error(detail);
        err.fatal = true;
        throw err;
      }
      lastError = new Error("The backend is still starting up.");
    } catch (e) {
      if (e.fatal) throw e;
      lastError = e;
    }
    if (attempt < retries) {
      onRetry?.(attempt + 1);
      await sleep(delayMs);
    }
  }
  throw new Error(`Backend unreachable after several attempts (${lastError?.message ?? "unknown error"}). Is it running?`);
}

export const getHealth = (opts) => request("/v2/health", {}, opts);
export const getEconomies = (opts) => request("/v2/economies", {}, opts);

/** POST /api/v2/recommend */
export function recommendBudget({ iso3, year, panel = "cofog10", shock, overrides, limeSector, totalBudgetUsd }, opts) {
  const body = { iso3, panel };
  if (year) body.year = Number(year);
  if (shock) body.shock = shock;
  if (overrides && Object.keys(overrides).length) body.overrides = overrides;
  if (limeSector) body.lime_sector = limeSector;
  if (totalBudgetUsd) body.total_budget_usd = totalBudgetUsd;
  return request(
    "/v2/recommend",
    { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) },
    opts,
  );
}

export const PANELS = {
  cofog10: "10 COFOG divisions (85 economies, incl. developing)",
  cofog16: "16 COFOG functions (36 Eurostat/OECD economies)",
};
export const SHOCK_LABELS = {
  recession: "Recession (GDP -5 pp, unemployment +3 pp, debt +15 pp)",
  stagflation: "Stagflation (GDP -2 pp, inflation +8 pp, unemployment +2 pp)",
  severe_stress: "Severe stress (GDP -15 pp, inflation +12 pp, debt +35 pp)",
};
export const DISCLAIMER =
  "Decision-support recommendation learned from peer economies; not a causal estimate and not a decision.";
