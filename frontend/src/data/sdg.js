// UN Sustainable Development Goals: names and official colours (used only for the reporting cross-walk, never as a model input).
export const SDG_INFO = {
  1: ["No Poverty", "#E5243B"],
  2: ["Zero Hunger", "#DDA63A"],
  3: ["Good Health & Well-being", "#4C9F38"],
  4: ["Quality Education", "#C5192D"],
  6: ["Clean Water & Sanitation", "#26BDE2"],
  7: ["Affordable & Clean Energy", "#FCC30B"],
  8: ["Decent Work & Economic Growth", "#A21942"],
  9: ["Industry, Innovation & Infrastructure", "#FD6925"],
  10: ["Reduced Inequalities", "#DD1367"],
  11: ["Sustainable Cities & Communities", "#FD9D24"],
  13: ["Climate Action", "#3F7E44"],
  15: ["Life on Land", "#56C02B"],
  16: ["Peace, Justice & Strong Institutions", "#00689D"],
};

/** Share of the budget attributed to each SDG: a function's share is split equally among its linked goals (a reporting convention). */
export function sdgShares(components) {
  const out = {};
  for (const c of components || []) {
    const goals = c.sdg && c.sdg.length ? c.sdg : [];
    for (const g of goals) out[g] = (out[g] || 0) + c.recommended_share_pct / goals.length;
  }
  return Object.entries(out)
    .map(([g, v]) => ({ goal: Number(g), share: v, name: SDG_INFO[g]?.[0] || `SDG ${g}`, color: SDG_INFO[g]?.[1] || "#64748b" }))
    .sort((a, b) => b.share - a.share);
}
