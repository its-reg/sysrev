# Systematic Review: Geographic & Environmental Risk Factors in Parkinson's Disease

Automated pipeline for a systematic review of the 2020–2025 literature on geographic and environmental risk factors in Parkinson's disease (PD) — air pollutants, pesticides, heavy metals, trichloroethylene, and related exposures.

**STATUS**: In progress — PubMed done; seed set collected and search strategy refinement underway; SCOPUS/EMBASE/WoS pipelines built and pending access runs.

---

## Roadmap

### Milestone 1: PubMed Collection & NLP ✅
- Search strategy defined in `search_strategy.py` (single source of truth for all databases)
- 411 articles collected and cleaned via PubMed API → `pubmed_results_cleaned_2026.csv`
- TF-IDF + n-gram analysis surfaces key terms and feeds into query expansion

### Milestone 2: Seed Set & Search Strategy Refinement ⏳
- 55 confirmed-relevant papers collected in `seed_papers/`; metadata auto-extracted to `seed_papers.csv` via `build_seed_csv.py` (PyMuPDF + CrossRef)
- `query_refinement.ipynb` tests three complementary methods against the seed set:
  - **BM25** — term-frequency ranking with length normalisation
  - **KeyBERT + YAKE** — keyphrase extraction to surface new vocabulary for `search_strategy.py`
  - **SPECTER** — semantic similarity to catch conceptually related papers using different terminology
- Findings from this step feed back into `search_strategy.py` before the full database run

### Milestone 3: Additional Databases ⏳
- **SCOPUS** — `scopus.ipynb` uses `elsapy` with year-by-year splitting to stay within the free-tier 5,000-record cap; set `SUBSCRIBER_ACCESS = True` once an InstToken is available for full pagination + abstracts
- **EMBASE** — `embase.ipynb` uses the Embase Search API (same Elsevier key); coordinate Emtree term mapping with Malcolm & Lukas
- **Web of Science** — `web_of_science.ipynb` uses the WoS Starter API (`TS=` query); pending institutional `WOS_API_KEY`
- **Google Scholar** — `google_scholar.ipynb` via `scholarly`; supplementary source only

### Milestone 4: Pre-screening ⬜
- SPECTER/BM25 similarity filter against seed embeddings → cheap first pass
- LLM structured screening (Ollama, local, no API key) on survivors → `prescreen.ipynb`; PICO-style prompts, temperature=0 for reproducibility

### Milestone 5: Synthesis ⬜
- Cross-database deduplication
- Formal title/abstract → full-text → risk-of-bias screening protocol
- Data extraction and synthesis

---

## Project Structure

```
search_strategy.py               — inclusion/exclusion criteria and DB configs (edit here, nowhere else)
build_seed_csv.py                — extracts metadata from PDFs in seed_papers/ → seed_papers.csv
seed_papers/                     — downloaded PDFs of confirmed-relevant seed papers
seed_papers.csv                  — seed paper metadata (title, abstract, DOI, authors, …)
pubmed.ipynb                     — PubMed collection, cleaning, TF-IDF term analysis
query_refinement.ipynb           — BM25 / KeyBERT+YAKE / SPECTER ranking against seed set
scopus.ipynb                     — SCOPUS collection via elsapy (year-by-year, free-tier safe)
embase.ipynb                     — EMBASE collection via Embase Search API
web_of_science.ipynb             — Web of Science collection via WoS Starter API
google_scholar.ipynb             — Google Scholar scrape via scholarly (supplementary)
prescreen.ipynb                  — (planned) Ollama LLM pre-screening
pubmed_results_cleaned_2026.csv  — cleaned PubMed results (411 articles)
requirements.txt                 — Python dependencies
archive/                         — superseded notebooks
```

---

## How to Run

**Prerequisites:** Python 3, `.env` with `PUBMED_EMAIL`, `ELSEVIER_API_KEY`, `ELSEVIER_INSTTOKEN` (optional, for subscriber access), and `WOS_API_KEY` (once granted).

```bash
pip install -r requirements.txt
```

Run in order:

1. `pubmed.ipynb` — collect and clean PubMed results
2. `build_seed_csv.py` — generate `seed_papers.csv` from PDFs in `seed_papers/`
3. `query_refinement.ipynb` — test methods, extract new vocabulary, update `search_strategy.py`
4. `scopus.ipynb` / `embase.ipynb` / `web_of_science.ipynb` / `google_scholar.ipynb` — collect from remaining databases
5. `prescreen.ipynb` — LLM pre-screening (in development)

To adjust the search: edit `search_strategy.py` and re-run the relevant notebooks — everything imports from there.
