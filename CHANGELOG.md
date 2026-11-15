# Changelog

How versions are recorded: the **Zenodo archive v1.0.0** (DOI 10.5281/zenodo.24255443; all versions: 10.5281/zenodo.24255442) is a frozen snapshot of the code at the moment the GitHub release `v1.0.0` was published. Every later change is recorded in the Git history of https://github.com/Pranav-chaudhari-2006/GovAllocXAI and listed below. A change that should be archived gets a new GitHub release (e.g. `v1.0.1`), which creates a new Zenodo version under the same "all versions" DOI.

The dataset has its own record: GovAlloc-COFOG v1.0, DOI 10.5281/zenodo.24248316 (all versions: 10.5281/zenodo.24248315). Its files are frozen; corrections need a new Zenodo version.

## Unreleased (after v1.0.0)
* Zenodo code DOI, dataset DOI and Kaggle link inserted in the papers, README and `CITATION.cff` (these lines are not inside the v1.0.0 snapshot).
* Conference paper made self-contained (own generative-AI disclosure); dataset paper cites the benchmark study generically.
* Website: Methodology page redesigned as cards; cover-letter and submission-statement templates added (`docs/templates/`).

## v1.0.0 (15-16 November 2026)
* First public release: numbered pipeline `01-27`, per-experiment results, benchmark journal paper, conference paper and dataset paper sources, FastAPI backend, React website with precomputed results, documentation and audits.
* Dataset GovAlloc-COFOG v1.0 (separate Zenodo record).
