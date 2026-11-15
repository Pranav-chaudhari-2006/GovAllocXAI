# Journals and conferences: where to submit

Free-to-publish venues and the submission guide.


---

## A. Submission guide

**First, a clarification.** Scopus and Web of Science are *databases of papers and journals*. You use them for two things: (1) **literature search** (to check that nobody has done exactly this — queries are in `docs/07`), and (2) **checking that a journal is indexed and its quartile** (Q1–Q4). They are *not* where you submit. You submit on the journal's own website (e.g. Elsevier Editorial Manager).

## 1. The money question — how to publish for free
* **Elsevier "hybrid" journals (most applied-AI / public-sector ones): you can publish for free** by choosing the normal *subscription* route. Elsevier states that authors in hybrid journals can publish under the subscription model at no cost; open access is an optional paid add-on (several thousand USD — do **not** choose it). There is **no submission fee** at Elsevier journals.
* **Fully open-access journals** (IEEE Access, MDPI, Frontiers, most PLOS/Scientific Reports-type) **charge an APC** (typically 1,000–3,000+ USD; waivers are rare) → avoid unless your college pays.
* **Conferences:** no APC but **registration fees** apply (and some require a presenter). IEEE-style conference proceedings are indexed in Scopus/IEEE Xplore if the conference is technically co-sponsored — check the call for papers.
* *Always confirm on the journal's own "Guide for Authors / Open access" page before submitting* (policies change; I could not retrieve every page automatically).

## 2. Shortlist (free-to-publish via the subscription route, indexed; verify quartile on SCImago/JCR)
| Priority | Journal (publisher) | Why it fits | Risk / note |
|---|---|---|---|
| **1** | **Socio-Economic Planning Sciences** (Elsevier, hybrid) | Public-sector planning, resource allocation, OR/analytics for government; published *Caravaggio et al. 2025* ("Predicting policy funding allocation with ML"), which we cite | Wants clear planning/policy relevance; expects stronger external validity (low-income pilot helps) |
| **2** | **Expert Systems with Applications** (Elsevier, hybrid) | Accepts applied ML + XAI; very high volume | High desk-reject rate; needs methodological depth (robustness, baselines — now added); optional OA ≈ $3k (don't pay) |
| **3** | **Government Information Quarterly** (Elsevier, hybrid) | Published *Valle-Cruz et al. 2022* ("smart budgeting"), our closest "AI for budgets" paper | Policy/governance angle required; technical papers often desk-rejected → only after strengthening policy discussion and (ideally) a user study |
| **4** | **Decision Support Systems** (Elsevier, hybrid) | Published an R&D budget-allocation ML + optimisation framework (2019) | Wants decision-support evidence (user study) |
| **5** | **Applied Soft Computing / Knowledge-Based Systems** (Elsevier, hybrid) | ML-methodology-friendly | Prefer methodological novelty — ours is mostly evaluation |
| Conference now | An applied AI / e-government / data-science conference (6 pages, IEEE format) | Matches the conference zip | Check CFP for Scopus indexing and registration fee |

**My recommendation:** conference first (fast, low-risk, gives feedback), then **Socio-Economic Planning Sciences** as the primary Q1 target, **Expert Systems with Applications** as the fallback. Look up each journal's current quartile on SCImago (scimagojr.com, free) and Clarivate's Master Journal List (free to search) — that is what "Scopus/WoS" is useful for here.

## 3. Practical submission checklist (all Elsevier journals)
Cover letter (novelty statement from `docs/07` §7; no "first" claims) · highlights (in the journal zip) · declaration of competing interests · funding statement ("no external funding") · data & code availability (repository DOI, e.g. Zenodo — free) · generative-AI declaration · CRediT roles per author · suggested reviewers (3–5 from public-finance + XAI; not collaborators) · convert `elsarticle` zip to the journal's template if asked (body is class-independent).

## 4. Avoid
Predatory or "fast-publication" journals that email you; any venue asking for a fee for peer review; journals not listed in Scopus/WoS (check before submitting).


---

## B. Target venues

**Rules of thumb for students without funding:** (1) publish in **Elsevier/Springer/IEEE "hybrid" journals via the normal subscription route — no publication charge** (Elsevier states hybrid-journal authors can publish under the subscription model at no cost; there is no submission fee); (2) never tick the paid open-access option; (3) fully open-access journals (IEEE Access, MDPI, Frontiers, PLOS…) charge APCs; (4) conferences charge **registration fees**, not APCs. **Always re-check each journal's "Guide for authors/Open access" page and each conference's CFP — dates and policies below come from web searches (Nov 2026) and may have changed.** Quartile: look up on SCImago (scimagojr.com, free).

## A. Journals (submit on the journal's own site; free via subscription route)
| Rank | Journal | Publisher / model | Fit | Notes |
|---|---|---|---|---|
| 1 | **Socio-Economic Planning Sciences** | Elsevier, hybrid | Public-sector planning, resource allocation, analytics; published the funding-allocation ML paper we cite | Best primary target; add low-income pilot / stronger external validation if possible |
| 2 | **Expert Systems with Applications** | Elsevier, hybrid (optional paid OA ≈ $3k — do not pay) | Applied ML + XAI | High volume, desk-rejects; ensure robustness section (5-seed/Holm) is included |
| 3 | **Government Information Quarterly** | Elsevier, hybrid | AI in government; published the "smart budgeting" paper we cite; has AI/government special-issue calls | Needs policy/governance framing; technical-only papers are often desk-rejected |
| 4 | **Decision Support Systems** | Elsevier, hybrid | Decision-support evaluation | Reviewers will want user evidence (human study) |
| 5 | **IEEE Transactions on Computational Social Systems** | IEEE, hybrid | Special issue on explainable/trustworthy AI and governance (submission deadline **1 Dec 2026**, first decision 1 Mar 2027 — verify) | Tight timeline; check whether the SI scope matches |
| 6 | **Applied Soft Computing / Knowledge-Based Systems** | Elsevier, hybrid | ML-methodology-friendly | Prefers methodological novelty |
| 7 | **Information Systems Frontiers / Computational Economics** | Springer, hybrid | Applied analytics / computational economics | Verify scope and OA policy |
| 8 | **Digital Government: Research and Practice** | ACM | Digital-government research | Verify current ACM publishing model/fees before submitting |
| Fast / broad | IEEE Access | IEEE, **fully OA with APC** | Broad scope | Not free unless waived — only if the college pays |

## B. Conferences (registration fee applies; check indexing in the CFP)
| Conference | When / deadline (as found) | Fit | Indexing / notes |
|---|---|---|---|
| **dg.o 2027** — 28th Int. Conf. on Digital Government Research (Seoul) | 28 Jun–1 Jul 2027; **research papers due 17 Jan 2027** (EasyChair `dgo2027`) | Core digital-government venue; theme AI & government innovation | Proceedings via ACM/DG Society — verify indexing |
| **EGOV-CeDEM-ePart (IFIP EGOV)** | 2026 edition: submissions 16 Mar 2026; 2027 CFP not yet found | E-government / e-participation research | Springer LNCS series — verify |
| **ICEGOV** (Int. Conf. on Theory and Practice of Electronic Governance) | 2026 CFP seen (acceptance ≈ 42 %); 2027 not yet found | Governance + digital technology, strong Global South focus | ACM proceedings — verify; no simultaneous submissions |
| **HICSS (Digital Government track)** | HICSS-59 deadline was 15 Jun 2025; next cycle ≈ June 2027 (unconfirmed) | Digital government / decision analytics | Broad indexing; January in Hawaii |
| **ACM TRUST 2027** (Washington DC) | 7–9 Mar 2027; 9-page double-blind papers (deadline not retrieved) | Trustworthy AI, public-sector AI systems | ACM — check Scopus status |
| **ESCI (IEEE Int. Conf. on Emerging Smart Computing and Informatics), Pune** | 2026 edition 11–13 Mar 2026 (deadline was 15 Nov 2025) → **2027 edition likely has a deadline around Nov–Dec 2026** (unconfirmed) | Local, annual, Pune | IEEE Xplore + Scopus "subject to IEEE approval"; similarity must be < 20 % |
| **IGNITE / ICoICET / ICSFT (Pune IEEE-sponsored series)** | 2026 editions: Jun, Sep, Apr; 2027 calls not yet found | Local AI/data-science conferences | IEEE Xplore (Scopus often claimed — confirm in each CFP); only presented papers are published |
| Other: IEEE INDICON / PuneCon / ICCCNT (India) | typically Q3–Q4 | Generic AI/ML | Check Scopus/IEEE Xplore statement in each CFP |

**Recommendation:** (1) *Conference first:* ESCI/IEEE-Pune series if a 2027 CFP is open (short turnaround, local, Xplore) **or** dg.o 2027 (deadline 17 Jan 2027, stronger topic fit — use the conference zip, adapt to their template). (2) *Journal:* **Socio-Economic Planning Sciences**, fallback **Expert Systems with Applications**; **Government Information Quarterly** only with a stronger policy discussion. (3) Do not submit the same text to a conference and a journal at the same time without checking the venue's overlap/"extended version" rules (the journal version should add ≥ 30 % new content — it does: extensions, robustness, fairness).

## C. Before you submit anywhere
Run your similarity/AI-writing check · replace the `[Authors: …]` placeholders (CRediT roles, competing-interest, acknowledgements) · repeat the Scopus/WoS literature strings from `docs/07` · confirm the venue's template (swap the `\documentclass` line; body is class-independent) · upload the dataset/code to Zenodo (free DOI) and add it to the data-availability statement.
