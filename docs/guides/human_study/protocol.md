# 09. Human-Subject Study Protocol: Do explanations help analysts use GovAllocXAI?

Status: READY TO RUN, NOT YET RUN. No data exist. No human-study result may be claimed in any paper until this study is completed and analysed. The study MUST NOT start before Institutional Ethics Committee approval (Section 9).

Materials: `docs/study_materials/` (consent, instructions, vignettes, questionnaire, response template). Analysis: `pipeline/16_analyze_human_study.py`.

## 1. Background and research questions

GovAllocXAI recommends a split of a government budget (health, education, defence, other), shows last year's split, SHAP and LIME explanations, an applicability warning for cases outside the training range, and what-if shocks. Model accuracy has been evaluated offline; whether explanations help humans decide better, and rely on the model appropriately, is untested.

| ID | Hypothesis (directional, pre-registered) |
|----|------------------------------------------|
| H1 | Decision quality: final-split error (TVD vs actual) is lower in B and C than in A. |
| H2 | Trust calibration: the gap in reliance between correct and incorrect recommendations is larger in B and C than in A (explanations help people follow the model when right and resist it when wrong). |
| H3 | Applicability warning: on extrapolation vignettes, over-reliance (shift toward the model) is lower in C than in B. |
| H4 | Decision time: B and C take longer per case than A (cost of explanations); exploratory on size. |

Secondary (exploratory): trust, usability (SUS), workload (NASA-TLX), explanation understanding quiz, confidence.

## 2. Design

Between-subjects, three conditions, random assignment (block randomisation by role, sequence generated before the study):
- **A**: recommendation only (recommended split next to last year's split).
- **B**: A + SHAP explanation.
- **C**: A + SHAP + LIME + applicability warning.

Justification: a within-subject Latin square would be more powerful per participant, but explanation conditions carry over (a person who has learned to read SHAP cannot "unlearn" it in the recommendation-only condition) and would triple session time beyond a realistic ~35 min. Between-subjects avoids carry-over; power is regained by having each participant do 6 vignettes (repeated measures, analysed with a mixed model). Vignette order is randomised per participant.

## 3. Participants

Inclusion: age 18+; students or staff/faculty in finance, economics, public policy or computer science at PCCOE (or collaborating institutions); basic familiarity with budgets or data analysis. Exclusion: prior involvement in building GovAllocXAI; has seen the vignette answers.

Power analysis (one-way ANOVA, 3 groups, alpha = 0.05, power = 0.80, medium effect f = 0.25): required total N = 159 (about 53 per group); allow about +5-15% for Kruskal-Wallis, so target 56 per group (168) for a fully powered test of H1 on participant means. This may be unrealistic in two weeks. Fallback plan, stated honestly: recruit at least 30 per group (N = 90). At f = 0.25 this gives roughly 0.5-0.55 power on participant-level one-way tests, but the mixed model across 6 vignettes per person has higher power for within-person effects (especially H2/H3, which are condition x vignette-type interactions). If N < 159, report all results as exploratory/under-powered and report effect sizes with confidence intervals rather than relying on p-values. (Authors: verify the numbers with G*Power or `statsmodels.stats.power.FTestAnovaPower`.)

Recruitment: classroom announcements, department mailing lists, posters. No coercion; participation must not affect grades. Report role mix (student/faculty/staff), and note the sample is non-expert students, so generalisation to professional ministry analysts is limited.

## 4. Tasks and materials

Six scored vignettes (V1-V7 in `vignettes.csv`; V8 is the unscored practice case, so pick 6 of V1-V7):
- 2 normal cases where the model is accurate,
- 2 model-wrong cases (model TVD vs actual deliberately large; pick from the largest errors in `results/02_main_experiments/best_predictions.csv`),
- 2 extrapolation cases (outside the training range; applicability warning fires in C),
- (V1-V3 normal pool, V4-V5 wrong, V6-V7 extrapolation; use 2 normal).

Vignette values in `vignettes.csv` are PLACEHOLDERS marked "FILL FROM results/ OR API BEFORE USE". Authors must fill last-year, model and actual splits from the project results or API and verify them against the official source. Anonymise the country/year in the display if the authors worry participants may recall actual budgets (recommended; keep a key).

Per vignette: (1) participant sees last-year split and context, proposes a split (health/education/defence/other, summing to 100) and rates confidence (PRE); (2) sees system output per condition; (3) gives final split and confidence (POST). Ground truth = actual official allocation. Dashboard views must be frozen screenshots or a locked build so all participants of a condition see identical content.

## 5. Measures

| Measure | Definition |
|---------|-----------|
| Decision error | TVD = 0.5 * sum \|participant share - actual share\| over the four sectors; pre and post |
| Improvement | pre error - post error |
| Reliance (shift toward model) | (TVD(pre, model) - TVD(post, model)) / TVD(pre, model), clipped to [-1, 1]; undefined if pre is within 0.01 of the model |
| Trust calibration | mean reliance on correct-model vignettes minus mean reliance on incorrect (model-wrong + extrapolation) vignettes; higher is better |
| Time | seconds from system output shown to final submission |
| Trust | 8-item scale (questionnaire C) |
| Usability | SUS-style, 10 items |
| Workload | NASA-TLX short, six 0-100 items |
| Understanding | 5-item quiz |
| Confidence | 1-5 pre and post per vignette |

## 6. Procedure (about 35 minutes per session, individual or small supervised group on separate screens)

| Min | Step |
|-----|------|
| 0-3 | Welcome, informed consent, ID assigned |
| 3-6 | Background questions, instructions (`participant_instructions.md`) |
| 6-10 | Practice vignette (unscored), interface walk-through for assigned condition |
| 10-28 | 6 scored vignettes (about 3 min each) |
| 28-35 | Questionnaires (trust, SUS, TLX, quiz), open comments, debrief |

Debrief: explain the system can be wrong, reveal the model-wrong/extrapolation design, share contact for questions.

## 7. Data handling and privacy

- Anonymous IDs (P001...). No names, emails or institutional IDs in response data.
- Signed consent sheets stored separately and never linked to the IDs.
- Data in the `response_template.csv` format; stored on encrypted institutional storage; access limited to the investigators.
- Only anonymised data are released (e.g. as a CSV with the paper); free-text comments are screened for identifying content first.

## 8. Analysis plan (pre-register before data collection)

Implemented in `pipeline/16_analyze_human_study.py` (run `--selftest` to check the pipeline on synthetic data; synthetic output is never a result).
- Participant-level: per-condition means and SDs of each outcome; one-way ANOVA with eta-squared and Kruskal-Wallis with epsilon-squared; pairwise Mann-Whitney U with Cohen's d and rank-biserial effect sizes.
- Multiple comparisons: Holm correction over the family of primary outcomes (post error, improvement, reliance on correct, reliance on incorrect, calibration, time); secondary outcomes exploratory.
- Trial-level: mixed model (random intercept per participant) post_error ~ condition + vignette type (+ interaction) when `statsmodels` is installed; otherwise participant means.
- Directional hypotheses: A vs B/C contrasts for H1/H2; B vs C on extrapolation for H3; time for H4.
- Report effect sizes with 95% CIs, exclusions (incomplete sessions, attention failures such as splits not summing to 100), and all deviations from this plan.
- Primary exclusion rule (pre-specify): drop participants who complete fewer than 5 of 6 vignettes.

Pre-registration: submit this protocol, hypotheses and analysis plan to OSF (osf.io) before collecting data and cite the timestamped registration in the paper.

## 9. Ethics

- Approval from the Institutional Ethics Committee (PCCOE) is REQUIRED before recruiting anyone. The authors must submit the protocol, consent form, instructions and questionnaire and record the approval number in the consent form. This document is not an approval.
- Informed consent (`consent_form_template.md`); participation voluntary; right to withdraw at any time without penalty; no grade or employment consequences; no deception beyond not telling participants which conditions exist (debriefed).
- Minimal risk; participants 18+.

## 10. Threats to validity

- Sample is students, not government analysts (external validity); report role and experience and test moderation.
- Small N, low power (Section 3); treat results as exploratory if N < 159.
- Participants may recognise real country-years (knowledge contamination); anonymise or choose obscure cases, record self-reported familiarity.
- Only 2 vignettes per type: effects may depend on the specific cases; include vignette in the mixed model.
- Ground truth is the official allocation, not an optimal allocation; the study measures agreement with actual policy.
- Demand effects and learning across vignettes; randomised order and a practice case.
- Condition C differs from B in several elements (LIME and warning) at once, so effects cannot be attributed to a single component; H3 contrast is therefore B vs C combined, not the warning alone.
- Uncontrolled environment if run remotely; prefer supervised sessions.

## 11. Timeline (2 weeks, starting AFTER ethics approval)

| Days | Activity |
|------|----------|
| Before day 0 | Ethics approval, OSF pre-registration, vignettes filled and verified, pilot with 2-3 people (not included in the data) |
| 1-2 | Final materials, freeze dashboard builds per condition, recruitment |
| 3-10 | Sessions (aim for about 8-12 per day across two facilitators) |
| 11-12 | Data entry, cleaning, run `python pipeline/16_analyze_human_study.py --data <csv>` |
| 13-14 | Write-up (results appended to the paper, deviations logged), data release |

## 12. Pre-run checklist for the authors

1. Obtain ethics approval and fill the reference in the consent form.
2. Fill `vignettes.csv` from `results/` or the API; verify against official sources; remove placeholder status.
3. Fill the quiz answer key from the real dashboard.
4. Pre-register on OSF.
5. Pilot, then collect data in `response_template.csv` format (delete the example row).
6. Run the analysis script; report only real data results.
