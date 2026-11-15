[Date]

[Editor-in-Chief / Handling Editor name]
[Journal name]
[Publisher]

**Submission: "GovAllocXAI: A Benchmark of Explainable Machine Learning for Predicting Functional Government Expenditure Shares from Official Multi-Country Data"** ([Research article / Full-length article])

Dear [Dr / Prof] [Editor surname],

We submit the above manuscript for consideration in *[Journal name]*.

**The question.** Governments divide public money among health, education, defence, social protection and other functions, largely by adjusting last year's split. We ask how much machine learning can add to last year's allocation, and what comparable economies and model explanations can tell an analyst when there is no last year at all.

**What we did.** We built an open benchmark on official statistics (Eurostat, OECD, IMF, World Bank): 825 complete country-years for 36 economies with 16 COFOG functions, a ten-division panel for 85 economies, and a World Bank sector panel for 211 economies. We evaluate persistence and peer baselines, boosted trees, a stacked learner, nearest-economy, Dirichlet, neural and econometric models under temporal, leave-country-out and leave-region-out protocols, with cluster-bootstrap intervals and Holm correction, and we quantitatively test SHAP and LIME explanations (agreement, stability, deletion faithfulness and a synthetic ground-truth test).

**Main findings (stated plainly, including negative results).** Last year's allocation is a strong baseline: a learned correction lowers the share of the budget to be moved from 3.62 to 3.48 percentage points, but the gain is small and not robust across learner seeds. Without history, a stacked learner and a nearest-economies average beat the income-group mean on the ten-division panel by about 1.3 points (Holm-adjusted), but not robustly on the 16-function panel; errors are two to three times larger for lower-income economies. SHAP and LIME agree more on direction than on ranking. We also report a forensic audit showing that an earlier semi-synthetic benchmark of ours reached R-squared above 0.99 because eleven of its fifteen targets were exact multiples of one series.

**Why this journal.** [Two or three sentences linking the paper to the journal's scope, e.g. for *Socio-Economic Planning Sciences*: public-sector resource allocation and decision-support analytics; cite one recent paper from the journal that is close to ours.]

**Novelty, stated carefully.** We do not claim to be the first to predict budgets with machine learning. The contribution is the combination of an official multi-country functional-composition target, practitioner baselines with corrected inference, and a quantitative evaluation of explanations, together with open data and code. Closest prior studies are discussed in Section 2 of the manuscript.

**Open data and code.** The harmonised data are archived on Zenodo (https://doi.org/10.5281/zenodo.24248315) and the code on Zenodo (https://doi.org/10.5281/zenodo.24255442) and GitHub (https://github.com/Pranav-chaudhari-2006/GovAllocXAI). A web demo is at https://govallocxai-xi.vercel.app.

**Related work by the authors.** A companion data paper describing the GovAlloc-COFOG dataset is [submitted to / in preparation for] [venue]; it describes the data only and reports no results from this manuscript. [If applicable: a shorter version of this work is not under review elsewhere.] This manuscript is original, has not been published, and is not under consideration by another journal.

**Use of generative AI.** As stated in the manuscript, generative AI (Anthropic's Claude) was used for code scaffolding, drafting and editing support; the authors reviewed all content and take full responsibility for it.

All authors have approved the manuscript and declare no competing interests. The work received no external funding.

[Optional: Suggested reviewers (name, affiliation, e-mail, reason) - see `04_submission_statements.md`.]

Sincerely,

[Corresponding author name]
[Department of Computer Engineering, Pimpri Chinchwad College of Engineering, Pune, India]
[e-mail] · [ORCID]
On behalf of Pranav S. Chaudhari, Aditi H. Joshi, Gaurav M. Jaypatre and Digvijay P. Birajdar
