# Systematic Review

Why hello there! This is my attempt at creating a living, automated systematic review. This notebook-driven project lets you run reproducible PubMed (for now) queries and export results for downstream analysis.

**STATUS**: In-Progress

✅ PubMed
Medline
Scopus
Google scholar
Web of science


## Project structure

- `pubmed.ipynb` — Jupyter notebook with query, processing, and export cells.
- `clevon.py` — a reference for the data cleaning from my colleague, Clevon.
- `pubmed_results/` — directory where exported NDJSON and query metadata files are saved.
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

I placed it in my notebooks but overall, just getting the search strategy refined and replicable across databases I pick would be pretty good for now.
