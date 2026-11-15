// Real headline numbers, copied from results/ (leave-country-out / temporal 2020-24).
// No synthetic or demo values live in the dashboard. Cold-start numbers are two-fold-seed means; the five-seed Holm-corrected gains are in the paper (Table holm) and results/15_robustness_holm/holm.csv.
// The annual gain (0.14 pp) is for learner seed 42 only; the five-seed mean is 0.12 pp and not robust (results/19_annual_seed_robustness/summary.json). Hand-copied constants: keep in sync with results/.
export const RESULTS_SOURCE = "from results/ (leave-country-out / temporal 2020-24)";

export const ANNUAL_UPDATE = { persistence: 3.62, hybrid: 3.48, gain: 0.14 };

export const COLD_START = [
  { panel: "16 functions, 36 economies", stack: 10.53, peer: 11.34 },
  { panel: "10 divisions, 85 economies", stack: 13.77, peer: 15.01 },
];

export const R2_BY_FUNCTION = [
  { fn: "Health", model: 0.63, peer: 0.31 },
  { fn: "R&D", model: 0.6, peer: 0.25 },
  { fn: "Education", model: 0.3, peer: 0.02 },
  { fn: "Defence", model: 0.12, peer: -0.02 },
];

export const ERROR_BY_INCOME = [
  { group: "High", tvd: 11.4 },
  { group: "Upper-middle", tvd: 18.5 },
  { group: "Lower-middle", tvd: 22.0 },
  { group: "Low", tvd: 33.4 },
];
