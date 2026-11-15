// Plain-language explanations shown inside the website (first-time-user manual).
export const GLOSSARY = [
  ["Budget share", "The slice of total government spending that goes to one area (for example health = 12 % means 12 out of every 100 units spent). All shares add up to 100 %."],
  ["COFOG", "The United Nations list of government functions (health, education, defence, social protection ...). It lets us compare countries on the same footing."],
  ["Recommended share", "The share the model gives as typical for this country, learned from how comparable countries really spent their money. A reference point, not advice."],
  ["Last observed share", "What the country actually spent last time official statistics were published. This is the 'starting point' to compare against."],
  ["Difference (pp)", "Model reference minus last observed share, in percentage points (pp). +2 pp means the model reference is 2 points above last year's share; it does not say the budget should change."],
  ["Difference from last year (TVD)", "Total variation distance (TVD): the percentage of the whole budget that would have to be shifted between areas to turn one split into the other. Small = the two splits are close."],
  ["Similarity to training economies (applicability)", "How similar this country's indicators are to the economies the model learned from. 'High' = well covered; 'Low' = unusual country, so the numbers are an extrapolation. It is a similarity score, not a probability of being right."],
  ["Nominal 80 % range", "A band around each reference share, calibrated to cover 80 % of cases. In our tests it covered about 80 % on average but only about 47 % for low-income and 61 % for lower-middle-income economies, so it is not reliable for those groups."],
  ["Why? (SHAP)", "Shows which facts about the country (for example older population, GDP per person) pushed a share up or down, in percentage points."],
  ["LIME", "A second, simpler explanation method. We show where it agrees with SHAP; agreement on direction is more reliable than on exact ranking."],
  ["Similar economies", "The real countries that look most like yours (income, population structure, governance). Their actual budgets drive the recommendation."],
  ["Stress test", "What-if view: how the recommendation shifts under a recession or stagflation. It is a sensitivity check, not a forecast."],
  ["Annual update vs cold start", "If a country has official history, last year's actual split is shown next to the model reference (and is itself a very strong baseline). If it has none, the model learns only from peers (cold start). The website picks the level of detail automatically (16 areas where official data cover them, otherwise 10)."],
  ["Human approval", "The tool only gives a reference. A person must review and decide; the numbers are never applied automatically."],
];

const FEATURE_NAMES = {
  log_gdp: "Size of the economy (GDP)", log_pop: "Population size", gdp_per_capita_usd: "Income per person",
  gdp_growth_pct: "Economic growth", inflation_pct: "Inflation", urban_pop_pct: "Share living in cities",
  pop_65plus_pct: "Share aged 65+", pop_0_14_pct: "Share aged 0-14", tax_revenue_pct_gdp: "Tax revenue (% GDP)",
  central_gov_debt_pct_gdp: "Government debt (% GDP)", total_expense_pct_gdp: "Total spending (% GDP)",
  unemployment_pct: "Unemployment", life_expectancy: "Life expectancy", under5_mortality: "Child mortality (under 5)",
  internet_users_pct: "Internet users", electricity_access_pct: "Access to electricity", basic_water_access_pct: "Access to clean water",
  co2_per_capita_t: "CO2 per person", agri_value_added_pct_gdp: "Agriculture share of economy",
  industry_value_added_pct_gdp: "Industry share of economy", trade_pct_gdp: "Trade openness",
  gov_effectiveness_wgi: "Government effectiveness", control_corruption_wgi: "Control of corruption",
  rule_of_law_wgi: "Rule of law", regulatory_quality_wgi: "Regulatory quality",
};
export const friendly = (f) => FEATURE_NAMES[f] || f.replace(/_/g, " ");

// Colour-blind-friendly categorical palette, one colour per budget area.
export const PALETTE = ["#22d3ee", "#f59e0b", "#a78bfa", "#34d399", "#f472b6", "#60a5fa", "#fb7185", "#facc15", "#2dd4bf", "#c084fc", "#4ade80", "#f97316", "#38bdf8", "#e879f9", "#a3e635", "#94a3b8"];
