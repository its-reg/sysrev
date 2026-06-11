# Systematic Review: Geographic & Environmental Risk Factors in Parkinson's Disease

This project automates a systematic review of the 2020–2025 literature on geographic and
environmental risk factors associated with Parkinson's disease (PD). Environmental exposures
such as air pollutants (nitrogen dioxide, PM10) and chemicals like trichloroethylene have been
implicated in elevated PD risk, yet the literature remains fragmented. The pipeline covers
automated API-based database querying, NLP-driven search refinement (TF-IDF), and an
in-development LLM pre-screening step using a local Ollama model (offline, no API key required).

**STATUS**: In-Progress — PubMed collection and NLP complete; LLM pre-screening in development.

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
- ⏳ SCOPUS — API ready via `pybliometrics`; query translation to SCOPUS syntax pending
- ⬜ EMBASE — coordinate pollution/geo terms with Malcolm & Lukas
- ⬜ Google Scholar / Web of Science — pending access

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
prescreen.ipynb             — (planned) Ollama LLM pre-screening of records
SCOPUS_exploration.ipynb    — SCOPUS API setup and query development (in progress)
pubmed_results_cleaned_2026.csv  — cleaned PubMed results (411 articles)
requirements.txt            — Python dependencies
archive/                    — superseded notebooks (pubmed_pull, pubmed_exploration)
```

---

## How to Run

**Prerequisites:** Python 3, a `.env` file with `PUBMED_EMAIL=your@email.com`,
and [Ollama](https://ollama.ai) installed locally for the pre-screening step.

```bash
pip install -r requirements.txt
```

1. **Collection & NLP** — run `pubmed.ipynb` top-to-bottom. It builds the query from
   `search_strategy.py`, fetches and cleans results, exports to CSV, and runs the TF-IDF
   term-ranking analysis.

2. **Pre-screening** — run `prescreen.ipynb` (in development). It loads the cleaned CSV,
   sends each title + abstract to a local Ollama model, and outputs include/exclude decisions
   with rationale. No API key or internet connection required.

3. **Adjust the search** — edit `search_strategy.py` (`INCLUSION_CRITERIA`, `ALTERNATE_TERMS`,
   `EXCLUSION_TERMS`, `DATE_FILTER`) and re-run step 1.

---

## Next Steps

1. **LLM pre-screening** — implement `prescreen.ipynb` with Ollama for PubMed results.
2. **SCOPUS query** — translate `search_strategy.py` terms to SCOPUS `TITLE-ABS-KEY` syntax.
3. **EMBASE** — expand pollution/geo terms with Malcolm & Lukas; set up database access.
4. **Deduplication** — merge and deduplicate across databases once SCOPUS/EMBASE are queried.
5. **Screening protocol** — formal title/abstract and full-text review workflow.
