# Where to publish the GovAlloc-COFOG data paper (free or cheap options)

*Prepared 15 November 2026 from web searches (search snippets, not a read of each publisher's rate card). **Every fee below must be re-checked on the journal page on the submission date**: the figures differ between sources and between years, and many publishers quote a personalised price after acceptance. Waivers and institutional agreements often change the real cost; ask your library before paying.*

## 1. What is being submitted (important for honest framing)
* The new dataset (**GovAlloc-COFOG v1.0**, folder `data/dataset_new/`) is built from **real official statistics**: Eurostat `gov_10a_exp`, OECD National Accounts Table 11, IMF GFS COFOG (targets, never imputed) and World Bank WDI/WGI (features, imputation flagged per cell). It is **not synthetic**.
* The earlier project dataset (`data/dataset_old/`, columns prefixed `legacy_`) **is semi-synthetic** (eleven of fifteen sector columns are exact multiples of one series). The data paper describes it only as a documented cautionary artefact that is not recommended for modelling. Do not present it as a result.
* The files were compiled by scripts through public APIs; scripting and AI-assisted code generation were used and the paper contains a generative-AI use declaration. Most journals require this declaration; some limit what AI use is permitted for text. Read each journal's AI policy before submission.
* Manuscript: `papers/dataset_paper/main_dataset.tex` (Overleaf zip `papers/overleaf_zips/GovAllocXAI_DataPaper_Overleaf.zip`).

## 2. Order of work (do it in this order)
1. **Freeze the dataset** (final file names, `docs/guides/04_dataset_card.md`, licence decision, checksums).
2. **Release on GitHub and deposit on Zenodo first** (see `docs/guides/02_github_and_zenodo_release.md`). This gives the dataset DOI. Zenodo is free; deposit the processed files and, ideally, the raw downloads, with the licence and the source attributions in the record.
3. **Insert the dataset DOI in the data paper** (one place: Data Records, "Versioning and persistent identifier") and in the repository README. Check that source terms (OECD, IMF, institutional files) allow redistribution before choosing the licence.
4. **Post a preprint of the data paper** (Zenodo, SSRN, arXiv or Research Square; section 4) so it has an identifier and a date. Check that the target journal accepts preprints.
5. **Submit the data paper** to a journal (section 3). Journals that run a data-availability check want the repository link and a licence in the first submission.
6. **Update the main benchmark paper** (`papers/main_journal.tex`) so it cites **both** the dataset DOI and the data paper, and mention in the data paper that the benchmark paper exists (already done; update the reference once it has a DOI or preprint link).

## 3. Journals (check scope, fee and AI policy on the page on submission day)
| Journal | Scope fit | Fee as found in searches (verify) | Page to check |
|---|---|---|---|
| **Data in Brief** (Elsevier) | Short data articles describing a dataset and how to reuse it; accepts datasets from many fields, economics/social science included. Co-submission with MethodsX exists. | Sources disagree (about USD 530-700 in listings; Elsevier says the price is personalised after acceptance and depends on country and institution). **Verify on the journal page.** | https://www.sciencedirect.com/journal/data-in-brief/publish/guide-for-authors |
| **Scientific Data** (Nature Portfolio) | Data Descriptors; high bar for documentation, technical validation and repository deposit; the Methods / Data Records / Technical Validation / Usage Notes structure of our manuscript follows it. Most selective of the list. | Open access with a mandatory APC; third-party listings range roughly EUR 1,900-2,400 / USD 2,200-2,700. **Verify on the journal page.** | https://www.nature.com/sdata/publish/open-access (also https://www.nature.com/sdata/for-authors) |
| **Data** (MDPI) | Data papers and dataset articles; fast review. | CHF 1,600 in an MDPI list dated 1 Jan 2023; newer figure not confirmed. **Verify on the journal page.** Vouchers and waivers are sometimes available; MDPI journals are judged differently by different institutions. | https://www.mdpi.com/journal/data/apc |
| **GigaScience** (Oxford University Press) / Data Note | Large-scale data and tools, mostly life sciences, but also broader data; includes hosting in GigaDB. Probably weaker scope fit for government finance. | USD 2,638 on the publisher charges page in the search result (some institutions get a discount). **Verify on the journal page.** GigaByte (separate journal) is a short-article format with a much lower listed APC; check scope. | https://academic.oup.com/gigascience/pages/charges_licensing_and_self_archiving |
| **Earth System Science Data** (Copernicus) | **Earth-system data only**: a government expenditure dataset is out of scope. | EUR 1,400 flat per paper (listed). Preprint stage is free. Listed only for completeness. | https://www.earth-system-science-data.net/about/article_processing_charges.html |
| **Data Science Journal** (CODATA / Ubiquity Press) | Data practice, data management, data papers and research data infrastructure; general scope. | About GBP 350 in older listings, Ubiquity's current list not confirmed. **Verify on the journal page.** | https://datascience.codata.org/ and https://ubiquitypress.com/site/apcs |
| **Journal of Open Humanities Data** (Ubiquity Press) | Humanities data; poor scope fit. | GBP 500 on Ubiquity's list (one other site says 450). Listed because the question asked about the Ubiquity data journals. | https://ubiquitypress.com/site/apcs |
| **Research Data Journal for the Humanities and Social Sciences** (Brill/DANS, now with CESSDA) | **Data papers for social science and humanities**, so a cross-national fiscal dataset can fit. | Diamond open access, no author fees according to DOAJ and the journal platform. **Verify on the journal page** (funding arrangement has changed over time). | https://openjournals.nl/en/journal/research-data-journal |
| **Open Research Europe** (European Commission platform) | Open peer review; data notes are listed among article types in secondary sources (conflicting reports). | Free **but only for authors with a Horizon 2020 / Horizon Europe project**. The authors here do not have one unless a grant exists, so probably not eligible. | https://open-research-europe.ec.europa.eu/ (author guidelines) |

Cheapest realistic routes: **Research Data Journal for the Humanities and Social Sciences** (no fee if still true), **Data Science Journal** and **Data in Brief** (moderate), then **Data** (MDPI) and **Scientific Data** (higher). Scientific Data is the best fit for the manuscript structure; its editors check dataset utility strictly and may ask for the licence to be fully open (CC BY or CC0), which may conflict with the source terms (OECD, IMF). Resolve the licence question before aiming there.

## 4. Free preprint and archive options
| Option | Cost | Notes | Page |
|---|---|---|---|
| **Zenodo** | free | Gives a DOI for the dataset and, separately, for the paper PDF; versioned. Needed anyway. | https://zenodo.org |
| **SSRN** | free | Good visibility among economists; moderated. | https://www.ssrn.com |
| **arXiv** | free | Needs an endorsement for a first submission in a category; categories such as cs.DL (digital libraries), econ.GN or cs.LG. Moderators may reject data descriptions that look like software or dataset announcements. | https://arxiv.org |
| **Research Square** | free preprint (paid optional services) | Fast; DOI; In Review service attached to some journals. | https://www.researchsquare.com |

A preprint is not a publication in the sense of the journal's novelty rules at most journals, but check each journal's preprint policy (Elsevier, Nature, MDPI and Copernicus all allow preprints under conditions).

## 5. What reviewers look at (acceptance considerations)
* **Utility:** who will reuse it, for which questions, and what is new compared with the Eurostat, OECD and IMF portals (the manuscript states: harmonised union with explicit source priority, simplex-ready 16/10 component targets, provenance and imputation flags, coverage reaching lower-middle and low-income economies, cross-source agreement statistics).
* **Documentation:** column dictionary, file inventory, units, versioning, dataset card. Present in the manuscript.
* **Technical validation:** all computed from the files by `pipeline/28_dataset_paper_figures.py` (sums to 100, bounds, negative values, cross-source agreement, jumps, missingness, imputation). Reviewers usually also ask for an independent check or an example reuse case; the benchmark paper is the reuse case.
* **Licence and legal reuse:** the strictest point for this dataset because OECD and IMF terms limit redistribution of derived rows. Say clearly what is redistributed, under which licence, and what users must obtain from the sources.
* **Persistent repository with DOI:** Zenodo record (step 2). Journals do not accept "available on GitHub" alone.
* **Honesty about limits:** EU/OECD-centred coverage, three low-income economies in A10, transductive imputation, negative values in a few cells, jumps in IMF series. All stated in the manuscript.
* **Do not call the new dataset semi-synthetic or the old dataset real.** The first is official data; the second is a legacy artefact.
* **Generative-AI declaration** is present; check each journal's wording requirements.

## 6. Fee disclaimer
Fees, waivers and eligibility change. For each journal: **verify on the journal page on submission date** (URL in the table) and ask for a waiver if the corresponding author's institution or country qualifies.
