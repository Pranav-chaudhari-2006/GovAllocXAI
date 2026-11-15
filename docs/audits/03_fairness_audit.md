# 08 - Fairness / Group-Error Audit (and low-income coverage check)

Scripts: `pipeline/15_fairness_audit.py` (audit), `pipeline/14_low_income_expansion.py` (coverage expansion + cold-start by income group).
Results: `results/12_fairness_audit/*.csv|json` (audit), `results/10_low_income_expansion/*.csv|json` (coverage). All numbers below are read from those files.

## 1. What was audited

Predictions are **out-of-fold, cold-start (leave-country-out, 6 folds grouped by iso3, seed 0)**, i.e. each economy is predicted by a model that never saw it.

* **Panel A10** (10 COFOG divisions, % of total expenditure; 85 economies, 1,526 country-years; Eurostat + OECD + IMF S13). Model: XGBoost on raw targets (same hyper-parameters as the paper, same folds as `07_cold_start_by_income.py`), compared with the **income-group peer-mean** baseline.
* **Panel B** (WDI health, education, defence, R&D as % of GDP; 211 economies). Same protocol, XGBoost vs. income-group peer mean.
* **Groups**: World Bank income group and region. Metrics: TVD (percentage points of the budget that would have to be moved), per-target MAE, worst-group error, max/min ratio ("disparate error ratio"), **signed bias** (predicted minus actual, pp), and a need-versus-allocation diagnostic. All intervals are 95% **cluster (country) bootstraps**.

## 2. Results

### 2.1 Error by income group (A10, TVD in pp, 95% CI)

| Income group | Economies | Country-years | XGBoost TVD | Peer-mean TVD | XGB minus peer (CI) |
|---|---|---|---|---|---|
| Low | 3 | 30 | 33.4 (23.7-40.9) | 32.1 (28.8-34.6) | +1.3 (-5.1, +6.4) |
| Lower-middle | 9 | 61 | 22.0 (18.7-26.2) | 28.1 (20.2-33.2) | -6.1 (-9.0, -0.5) |
| Upper-middle | 23 | 371 | 18.4 (16.2-20.7) | 18.3 (16.0-20.6) | +0.2 (-1.3, +1.7) |
| High | 50 | 1,064 | 11.4 (9.8-13.2) | 12.5 (11.0-14.3) | -1.2 (-2.0, -0.4) |

* **Worst-group error**: low income, 33.4 pp. **Disparate error ratio** (worst/best income group) = **2.94** (CI 2.09-3.85) for XGBoost vs 2.56 for the peer mean. By region the ratio is 1.94 (East Asia & Pacific worst at 21.2 pp, Europe & Central Asia best at 10.9 pp).
* ML reduces error for lower-middle and high income relative to the peer mean, and is statistically indistinguishable from it for low and upper-middle income. So **ML does not close the gap for low-income economies; the gap in absolute error is large with either method** and is, in ratio terms, slightly wider for XGBoost (2.94 vs 2.56) because XGBoost helps the data-rich groups most.
* Regions with fewer than ~10 economies (South Asia 2, North America 2, Sub-Saharan Africa 6, MENA+AP 7) have very wide intervals; see `12_fairness_audit/A10_group_error.csv`.

### 2.2 Signed bias for health, education, social protection (A10, XGBoost, pp of total expenditure; positive = model over-predicts the share)

| Group | Health GF07 | Education GF09 | Social prot. GF10 |
|---|---|---|---|
| Low (n=3) | +1.5 (-0.9, 4.8) on actual 3.8 | +1.7 (-8.3, 8.4) on 10.0 | **+4.1 (2.5, 7.0)** on 3.0 |
| Lower-middle (n=9) | +0.9 (-0.7, 2.4) on 8.3 | +0.3 (-2.6, 2.6) on 15.9 | -1.6 (-7.1, 4.3) on 14.6 |
| Upper-middle (n=23) | 0.0 (-1.7, 1.9) | +0.5 (-1.1, 2.1) | -0.3 (-3.3, 2.8) |
| High (n=50) | 0.0 (-0.9, 1.0) | -0.1 (-0.7, 0.6) | +0.4 (-1.5, 2.3) |

The peer-mean baseline is essentially unbiased by construction (|bias| < 1 pp in all cells). The only bias whose interval excludes zero among these is **social protection in low-income economies**: the cold-start model predicts about 7 percent of the budget where the observed value is about 3 percent. Read in plain terms, the model "expects" low-income governments to spend more on social protection than the three observed ones actually do (the model leans on features shared with richer economies). The health and education signs are also positive for low-income economies but not distinguishable from zero. Per-division bias for all 10 divisions and all groups is in `12_fairness_audit/A10_signed_bias.csv`; per-target MAE in `12_fairness_audit/A10_mae_by_target.csv`.

### 2.3 Need-versus-allocation (A10, country-mean Spearman within group)

| Area / need proxy | Group | rho(need, actual share) | rho(need, predicted share) | rho(pred, actual) |
|---|---|---|---|---|
| Health / under-5 mortality | Lower-middle (n=9) | 0.20 | 0.10 | 0.70 |
| | Upper-middle (23) | -0.19 | -0.36 | 0.09 |
| | High (50) | -0.19 | -0.45 | 0.34 |
| Education / % pop. 0-14 | Lower-middle (9) | 0.73 | 0.50 | 0.55 |
| | Upper-middle (23) | 0.38 | 0.64 | 0.34 |
| | High (50) | 0.38 | 0.46 | 0.48 |

Low income has n=3, so no within-group correlation is computed (the script returns NaN). The bootstrap CIs on "rho(need,pred) minus rho(need,actual)" include zero in every group (e.g. lower-middle education -0.82 to +0.22), so there is **no evidence that the model amplifies or dampens the (weak) link between need and allocation**. The more important point is that the link in the *actual* data is weak or even negative for health (richer, lower-mortality countries spend a larger share on health), so "matching actual allocation" is not the same as "matching need" - a model that reproduces actual behaviour inherits that.

### 2.4 Panel B (WDI, % of GDP, income groups with 14+ economies)

Absolute MAE grows with the size of the spending item, so we also report error relative to the group mean actual value.

| Target | Low: MAE (rel.) | Lower-mid | Upper-mid | High | Signed bias (all groups) |
|---|---|---|---|---|---|
| Health | 0.45 pp (38%) | 0.87 (43%) | 1.01 (31%) | 1.11 (22%) | -0.19 to +0.05; all CIs include 0 |
| Education | 1.13 (36%) | 1.50 (34%) | 1.21 (27%) | 1.04 (23%) | -0.16 to +0.13, CIs include 0 |
| Defence | 1.17 (59%) | 0.88 (49%) | 1.11 (58%) | 0.95 (47%) | within +/-0.05 |
| R&D | 0.11 (50%) | 0.17 (57%) | 0.22 (51%) | 0.54 (37%) | within +/-0.03 |

Relative to what is being predicted, errors are roughly 1.3-1.9 times larger in poorer groups (relative-MAE ratio: health 1.93, education 1.59, defence 1.28, R&D 1.54), even where absolute MAE is smaller. XGBoost beats the peer mean in most cells. At income-group level no systematic over- or under-prediction is detectable (all intervals include zero). At region level, MENA (defence -0.68 pp, R&D -0.41 pp) and Latin America (health -0.35, defence +0.57) show some bias, and North America (n=2 economies) is badly under-predicted for health (-2.05, a US outlier); see `12_fairness_audit/B_wdi_group_error.csv`.

### 2.5 Does adding low-income data or re-weighting help? (`10_low_income_expansion/*`)

* **Why coverage is thin.** Of 25 low-income and 47 lower-middle-income economies, the IMF S13 COFOG raw files contain **no values at all** for 22 and 35 respectively. Only 3 low-income and 12 lower-middle economies report a general-government breakdown; 9 pass the A10 filter (2 fail the 97-103 sum window, 1 never reports all ten divisions). The gap is a reporting gap, not a pipeline filter (`10_low_income_expansion/diagnosis_S13.csv`).
* **Expansion.** Central-government (S1311) data and a relaxed 90-110 window add only **13 rows / 5 new economies** (low income 3 -> 6 economies, 30 -> 37 rows; lower-middle 9 -> 11, 61 -> 67). 12 of 13 are central-government only. For the 78 country-years where both scopes exist, central and general-government shares differ by a mean TVD of 7.5 pp (median 5.2), so they are **not comparable** and are flagged (`cofog10_scope`, `cofog10_strict`) in `data/dataset_new/govallocxai_new_cofog10x_panel.csv`. This expansion is too small to change conclusions and should not be used for headline claims.
* **Method fixes (6 folds x seeds 0,1; TVD pp on the 30 original low-income rows).**

| Training data | XGBoost | + inverse-frequency weights | + income one-hot | Peer mean |
|---|---|---|---|---|
| A10 only | 33.1 (21.9-41.2) | 32.0 (23.2-39.0) | 33.9 | 32.1 |
| Expanded | 32.8 (23.1-42.9) | 29.2 (18.4-40.2) | 32.9 | 31.1 |

Weighting reduces low-income error by 1.1 pp (CI -2.9 to +1.3) on A10 only and by 3.7 pp (CI -4.7 to -2.7) with the expanded data. The latter paired interval excludes zero, but it comes from three economies and comparison across 3 variants x 2 regimes, so it should be treated as suggestive. Income one-hot features do nothing (+0.1 to +0.7). Even the best variant (29.2) is far above the high-income error (11.6). On the 7 added low-income central-government rows, all models score around 24.5-25.2 TVD, which is on a different (central-government) target definition and not comparable.

## 3. Interpretation (plain language)

1. The system is **not equally reliable for everyone**. For low-income economies a cold-start prediction misallocates roughly a third of the budget (33 pp), about three times the error for high-income economies (11 pp). Using a peer-group average is no better.
2. The headline systematic bias that we can detect is that the model over-predicts social-protection share in low-income economies. We cannot say whether that is a model artefact or reflects the three observed countries' genuinely low social-protection spending.
3. For health and education, the model does not show detectable group bias, but it also does not track need (child mortality) better than the observed data do.
4. Relative errors on WDI series are larger for poorer groups too, even where absolute errors are smaller.
5. Data, not modelling, is the main bottleneck: re-weighting or group indicators help little, and extra data are nearly unavailable because many low-income governments report no COFOG breakdown.

## 4. Limitations

* **Small n.** Low income has only 3 economies / 30 country-years in A10 (bootstrap CI 23.7-40.9). Cluster bootstrap with 3 clusters is crude; results for this group are indicative, and many regional cells have 2-9 economies.
* **Selection bias.** Economies that publish a COFOG breakdown are probably better governed/statistically stronger than the 57 that do not, so the audit likely **understates** low-income error and bias for the truly unobserved population.
* **Groups.** World Bank income groups change over time (the master table uses one label per economy) and are a crude proxy for need or vulnerability; no within-country (regional, gender, ethnic) analysis is possible with national aggregates.
* **Actual allocation is not "right" allocation.** Errors measure distance from what governments did, not from what populations needed. Need proxies (under-5 mortality, % aged 0-14) are crude, and the diagnostic uses country means.
* **Composition and scale.** Shares of total expenditure say nothing about the absolute amounts; a small share of a small budget can be a large per-capita gap.
* Multiple comparisons (many groups x divisions) were not corrected; intervals are not simultaneous. Only one model seed and one fold split are used in the audit (the coverage experiment uses two).
* Panel B includes economies whose totals are estimated, and error ratios there are partly driven by scale.

## 5. Recommended mitigations and monitoring

* Report group-wise errors (income group, region) with intervals in every release, together with the disparate error ratio; set an explicit tolerance and flag outputs for economies far from training data (the applicability score in `expF`).
* For low-income economies, present predictions as **ranges / scenario baselines with a caution flag**, not point recommendations; require human review before use in allocation advice.
* Prioritise data collection: negotiate COFOG submissions from low-income reporters (GFSM 2014 level-1 reporting) and add national budget documents; track new IMF S13 releases and re-run `pipeline/14_low_income_expansion.py`.
* Keep general- and central-government series separate; do not pool them in headline metrics.
* Consider constraints that guard against implausible shares for low-income economies (e.g. bounds anchored to observed low-income ranges), and calibrate or post-correct the social-protection prediction for low-income groups once more data exist.
* Monitor signed bias per division per group over time, and re-run this audit after each data update.
