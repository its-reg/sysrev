# Systematic Review

Why hello there! This is my attempt at creating a living, automated systematic review. This notebook-driven project lets you run reproducible PubMed (for now) queries and export results for downstream analysis.

**STATUS**: In-Progress

## 📊 Project Roadmap

### Milestone 1: PubMed Data Collection
- ✅ Query finalized and validated
- ✅ Results collected (326 total, 138 in last 5 years)
- ✅ Data cleaning applied (154 articles after cleaning, 153 after screening)
- ✅ Exported to CSV: `pubmed_results_cleaned_2025.csv`, `pubmed_results_screened_2025.csv`

**Status**: 100% Complete

---

### Milestone 2: SCOPUS Data Collection
- ✅ API authentication setup (pybliometrics)
- ⬜ Query definition (awaiting translation to SCOPUS syntax)
- ⬜ Results collection
- ⬜ Data cleaning and export
- ⬜ Integration with PubMed results

**Status**: 25% Complete — API ready, query needed

---

### Milestone 3: EMBASE Data Collection
- ⬜ Query strategy design (coordinate with Malcolm and Lukas on pollution/geo terms)
- ⬜ Database access setup
- ⬜ Results collection
- ⬜ Data cleaning and export
- ⬜ Integration with PubMed + SCOPUS results

**Status**: 0% — Not started. Note: Coordinate term expansion with team.

---

### Milestone 4: Additional Databases
- ⬜ Google Scholar (manual or scholarly library integration)
- ⬜ Web of Science (institutional access required)

**Status**: 0% — Pending resource availability

---

### Milestone 5: Study Protocol & Analysis
- ⏳ Selection criteria refinement
- ⏳ Duplicate removal across databases
- ⏳ Formal screening protocol setup
- ⏳ Risk of bias assessment
- ⏳ Data extraction and analysis

**Status**: 15% — Screened list created for PubMed; awaiting additional databases

---

## 🔍 Search Strategy

**All search criteria are now centralized in `search_strategy.py`** to ensure consistency across databases.

**Key parameters:**
- **Date range**: 2020-01-01 onwards (5-year window)
- **Disease focus**: Parkinson's disease, neurodegenerative disease
- **Spatial component**: geospatial, spatial dependence, spatiotemporal, geographic terms
- **Exposure focus**: pollution, chemical, pesticide, air pollution, water pollution, microplastic pollution
- **Exclusions**: animal models, plant studies, in vitro, molecular, protein studies, mechanistic/treatment-focused research

**Import in notebooks:**
```python
from search_strategy import INCLUSION_CRITERIA, EXCLUSION_CRITERIA, DATE_FILTER, DATABASE_CONFIGS
```

---

## Project structure

- `search_strategy.py` — **Centralized configuration** with inclusion/exclusion criteria, date filters, and database-specific query syntax. Import this in all notebooks for consistency.
- `pubmed_pull.ipynb` — Active PubMed query, processing, and export notebook.
- `pubmed_exploration.ipynb` — Exploratory notebook used to develop and refine the search strategy (NLP-driven term ranking, TF-IDF analysis).
- `SCOPUS_exploration.ipynb` — In-progress notebook for SCOPUS API setup and query development.
- `clevon.py` — Reference for data cleaning patterns (e.g., regex-based keyword matching).
- `pubmed_results_cleaned_2025.csv` — Cleaned PubMed results (154 articles).
- `pubmed_results_screened_2025.csv` — Screened PubMed results (153 articles).
- `pubmed_results/` — Directory where exported NDJSON and query metadata files are saved.
- `requirements.txt` — Python dependencies for the project.

## Purpose

Automate queries (via `pymed`, etc) and collect article metadata into NDJSON files. Convert NDJSON into pandas DataFrames for cleaning, analysis, and export. Keep query metadata (timestamp and query string) with each export for reproducibility.

## How to run

1. Create a `.env` file in the project root with your PubMed contact email (this is used by `pymed`):

```
PUBMED_EMAIL=your-email@example.com
```

2. (Optional) Create and activate a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Open and run `pubmed.ipynb` in Jupyter. The notebook contains cells to:
   - build the query string,
   - fetch results from PubMed,
   - convert results to a reusable list,
   - export NDJSON files into `pubmed_results/` (timestamped), and
   - parse the latest NDJSON into a pandas DataFrame for inspection.

4. After running the export cell, NDJSON files and a `query-<timestamp>.txt` describing the query are written to `pubmed_results/`.

## Packages used

This project lists the following dependencies in `requirements.txt`:

```
python-dotenv
pandas
ipykernel
pymed
```

In the running notebook environment, other useful packages are installed (for completeness):
- `python-dotenv` — loads `.env` into environment variables
- `pandas` — data analysis and DataFrame handling
- `pymed` — PubMed client used for querying

For the full environment as used in the notebook kernel, I'll need to add an explicit `environment.yml` or `requirements-full.txt` containing the kernel packages. Be patient with me lol

## Notes & safety

- The notebook saves exports locally — add `pubmed_results/` to `.gitignore` if you don't want to commit large datasets.
- Rewriting git history was used earlier to remove private emails from commits; make sure collaborators update their clones if you force-push history changes.

## Next steps

1. **SCOPUS query translation** — Convert inclusion/exclusion terms from `search_strategy.py` to SCOPUS field syntax (TITLE-ABS-KEY format) and run query in `SCOPUS_exploration.ipynb`.

2. **EMBASE planning** — Coordinate with Malcolm and Lukas to expand pollution and geographic terms for EMBASE MeSH search. Update `search_strategy.py` once terms are finalized.

3. **Duplicate removal** — Implement cross-database deduplication once SCOPUS and EMBASE results are collected.

4. **Formal screening protocol** — Set up structured screening workflow (title/abstract review, full-text review, risk of bias assessment).

5. **Environment documentation** — Generate `environment.yml` from current notebook kernel packages for reproducibility.

**Meeting notes:** Margaret reviewed the study direction and search terms (see `pubmed_pull.ipynb` for notes).

