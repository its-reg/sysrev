# Systematic Review: Geographic & Environmental Risk Factors in Parkinson's Disease

This project automates a systematic review of the 2020–2025 literature on geographic and
environmental risk factors associated with Parkinson's disease (PD). Environmental exposures
such as air pollutants (nitrogen dioxide, PM10) and chemicals like trichloroethylene have been
implicated in elevated PD risk, yet the literature remains fragmented. The pipeline covers
automated API-based database querying, NLP-driven search refinement (TF-IDF), and an
in-development LLM pre-screening step using a local Ollama model (offline, no API key required).

**STATUS**: In-Progress — PubMed collection and NLP complete; additional-database pipelines
(SCOPUS, EMBASE, Web of Science) built and pending data-access runs; LLM pre-screening in development.

---

## Roadmap

### Milestone 1: PubMed Collection & NLP
- ✅ Search strategy defined in `search_strategy.py`
- ✅ Results collected via PubMed API — 411 articles cleaned (`pubmed_results_cleaned_2026.csv`)
- ✅ NLP pipeline (TF-IDF + n-gram ranking) identifies key terms and informs query expansion

### Milestone 2: LLM Pre-screening *(in development)*
- ⏳ Local Ollama model classifies each record (title + abstract) against inclusion/exclusion criteria
- ⬜ Outputs a `screened` flag and rationale per article
- ⬜ Human review of borderline cases

### Milestone 3: Additional Databases
- ⏳ SCOPUS — pipeline built in `scopus.ipynb` (`pybliometrics`, `TITLE-ABS-KEY` query); needs a full run on an institutional token for abstracts
- ⏳ Google Scholar — in progress via `scholarly` (see `google_scholar.ipynb`); supplementary source only
- ⏳ EMBASE — query builder + export loader in `embase.ipynb`; no open API, so it uses a manual Embase/Ovid export workflow (coordinate Emtree terms with Malcolm & Lukas)
- ⏳ Web of Science — pipeline built in `web_of_science.ipynb` (WoS Starter API, `TS=()` query); pending institutional API key

### Milestone 4: Analysis & Protocol
- ⬜ Cross-database deduplication
- ⬜ Formal screening protocol (title/abstract → full-text → risk of bias)
- ⬜ Data extraction and synthesis

---

## Search Strategy

All criteria live in [`search_strategy.py`](search_strategy.py) — edit there to keep every notebook in sync.

| Parameter | Summary |
|---|---|
| Date range | 2020-01-01 to 2025-12-31 |
| Disease | Parkinson's disease, neurodegenerative disease (+ NLP-expanded alternates) |
| Spatial | geospatial, spatiotemporal, geographic, environment*, atmospheric, … |
| Exposure | pollution, air pollution, pesticide, particulate matter, NO2, trichloroethylene, … |
| Exclusions | animal/in vitro/molecular studies; treatment/therapy-focused research |

---

## Project Structure

```
search_strategy.py          — centralized inclusion/exclusion criteria and DB configs
pubmed.ipynb                — PubMed collection, cleaning, NLP term analysis
google_scholar.ipynb        — Google Scholar collection via scholarly (supplementary)
scopus.ipynb                — SCOPUS collection via pybliometrics (TITLE-ABS-KEY query)
embase.ipynb                — EMBASE query builder + RIS/CSV export loader (manual export workflow)
web_of_science.ipynb        — Web of Science collection via the WoS Starter API (TS= query)
prescreen.ipynb             — (planned) Ollama LLM pre-screening of records
SCOPUS_exploration.ipynb    — early SCOPUS API setup scratchpad (superseded by scopus.ipynb)
pubmed_results_cleaned_2026.csv  — cleaned PubMed results (411 articles)
requirements.txt            — Python dependencies
archive/                    — superseded notebooks (pubmed_pull, pubmed_exploration)
```

---

## How to Run

**Prerequisites:** Python 3, a `.env` file with `PUBMED_EMAIL=your@email.com` (and
`WOS_API_KEY=...` once Web of Science access is granted), a configured Elsevier API key for
SCOPUS (`pybliometrics.init()`), and [Ollama](https://ollama.ai) installed locally for the
pre-screening step.

```bash
pip install -r requirements.txt
```

1. **Collection & NLP** — run `pubmed.ipynb` top-to-bottom. It builds the query from
   `search_strategy.py`, fetches and cleans results, exports to CSV, and runs the TF-IDF
   term-ranking analysis.

2. **Google Scholar (supplementary)** — run `google_scholar.ipynb`. Uses the `scholarly`
   package to scrape Scholar (no API key needed). Note: Google rate-limits scrapers, so
   results may be partial without a proxy — the notebook handles this gracefully.

3. **SCOPUS** — run `scopus.ipynb`. It builds the `TITLE-ABS-KEY` query from `search_strategy.py`,
   queries the SCOPUS API via `pybliometrics`, cleans, and exports `scopus_results_2026.csv`.
   Use the `COMPLETE` view on an institutional token to also capture abstracts.

4. **EMBASE** — run `embase.ipynb`. EMBASE has no open API, so the notebook prints the query in
   Ovid (`.ti,ab.`) and Embase.com (`:ti,ab`) syntax to paste into the platform, then loads the
   exported RIS/CSV back into the shared schema and exports `embase_results_2026.csv`.

5. **Web of Science** — run `web_of_science.ipynb`. It builds the `TS=()` query, pages through the
   WoS Starter API (reads `WOS_API_KEY` from `.env`), cleans, and exports
   `web_of_science_results_2026.csv`.

6. **Pre-screening** — run `prescreen.ipynb` (in development). It loads the cleaned CSV,
   sends each title + abstract to a local Ollama model, and outputs include/exclude decisions
   with rationale. No API key or internet connection required.

7. **Adjust the search** — edit `search_strategy.py` (`INCLUSION_CRITERIA`, `ALTERNATE_TERMS`,
   `EXCLUSION_TERMS`, `DATE_FILTER`) and re-run the affected collection notebooks. Every database
   notebook imports from `search_strategy.py`, so one edit keeps them all in sync.

---

## Next Steps

1. **LLM pre-screening** — implement `prescreen.ipynb` with Ollama for PubMed results.
2. **SCOPUS run** — execute `scopus.ipynb` on an institutional token (`COMPLETE` view) to capture abstracts.
3. **EMBASE** — expand pollution/geo + Emtree terms with Malcolm & Lukas; secure Embase/Ovid access, then run the export through `embase.ipynb`.
4. **Web of Science** — obtain the institutional `WOS_API_KEY` and run `web_of_science.ipynb`.
5. **Deduplication** — merge and deduplicate across all databases once SCOPUS/EMBASE/WoS are queried.
6. **Screening protocol** — formal title/abstract and full-text review workflow.
