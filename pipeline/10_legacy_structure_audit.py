"""Legacy v1 forensic check #2: are the 'constant-share' sectors exact multiples of one latent series?  -> results/01_legacy_audit/legacy_structure.json"""
import json, sys
import numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from gov_common import OLD, RES
d = pd.read_csv(OLD / "govallocxai_old_dataset.csv")
syn = ['infrastructure_usd', 'agriculture_usd', 'rural_development_usd', 'social_welfare_freebies_usd', 'energy_usd', 'transport_usd',
       'housing_urban_development_usd', 'water_sanitation_usd', 'environment_climate_usd', 'digital_it_usd', 'industry_msme_usd']
mult = {t: {"multiple_of_agriculture": float((d[t] / d.agriculture_usd).mean()), "std_of_multiple": float((d[t] / d.agriculture_usd).std())} for t in syn}
tot = d[syn].sum(axis=1) / d.gdp_usd * 100
share = d[syn].div(d[syn].sum(axis=1), axis=0)
out = {"sectors": syn, "exact_multiples": mult, "max_std_of_multiple": max(v["std_of_multiple"] for v in mult.values()),
       "latent_total_pct_gdp": {"mean": float(tot.mean()), "sd": float(tot.std()), "min": float(tot.min()), "max": float(tot.max())},
       "within_group_share_sd_across_rows": float(share.std().max()),
       "corr_latent_ratio_vs_gdp_growth": float(np.corrcoef(tot, d.gdp_growth_percent)[0, 1]),
       "n_rows": int(len(d)), "n_distinct_country_year_mixes": int(share.round(9).drop_duplicates().shape[0])}
json.dump(out, open(RES / "01_legacy_audit/legacy_structure.json", "w"), indent=1); print(json.dumps(out, indent=1)[:1500])
