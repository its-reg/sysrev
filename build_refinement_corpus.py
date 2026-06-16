"""
build_refinement_corpus.py
--------------------------
Build the refinement corpus from your confirmed seed papers.

Reads seed_papers.csv, repairs encoding (e.g. Parkinsonâ's → Parkinson's),
drops rows without title + abstract, and writes refinement_corpus.csv.

That file is the text corpus query_refinement.ipynb uses for BM25, KeyBERT/YAKE,
and SPECTER during search-strategy refinement — one row per seed paper, same 55
documents, cleaned for NLP.

Usage
-----
    python build_refinement_corpus.py

Run again after updating seed_papers.csv (e.g. via build_seed_csv.py).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED_PATH = Path("seed_papers.csv")
OUTPUT_CSV = Path("refinement_corpus.csv")
DRY_RUN = False

TEXT_COLUMNS = ("title", "abstract", "keywords", "authors", "journal")
OUTPUT_COLUMNS = [
    "title", "abstract", "doi", "pubmed_id", "keywords",
    "authors", "journal", "publication_date",
]


def _fix_mojibake(text: str) -> str:
    """Repair mis-decoded UTF-8/cp1252 text (e.g. Parkinsonâ's → Parkinson's)."""
    if not text:
        return text
    if "â" in text or "Ã" in text:
        try:
            text = text.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    text = (
        text.replace("\x91", "'")
        .replace("\x92", "'")
        .replace("\x93", '"')
        .replace("\x94", '"')
        .replace("\x96", "-")
        .replace("\x97", "-")
    )
    return (
        text.replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )


def _coerce_text(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if isinstance(val, (list, tuple)):
        return _fix_mojibake(" ".join(str(v) for v in val if v))
    return _fix_mojibake(str(val).strip())


def _read_seed_csv(path: Path) -> pd.DataFrame:
    """Read seed CSV; file mixes cp1252 bytes with UTF-8-as-latin-1 mojibake."""
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def _normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in TEXT_COLUMNS:
        if col in df.columns:
            df[col] = df[col].apply(_coerce_text)
    return df


def build_corpus(df_seed: pd.DataFrame) -> pd.DataFrame:
    df = _normalize_text_columns(df_seed)
    df = df[~df["title"].astype(str).str.startswith("REPLACE")]
    df = df[df["title"].astype(str).str.strip().astype(bool)]
    df = df[df["abstract"].astype(str).str.strip().astype(bool)]
    df = df.drop_duplicates(subset=["title"], keep="first")

    for col in OUTPUT_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df[OUTPUT_COLUMNS].reset_index(drop=True)


def main():
    if not SEED_PATH.exists():
        raise FileNotFoundError(f"'{SEED_PATH}' not found — run build_seed_csv.py first.")

    df_seed = _read_seed_csv(SEED_PATH)
    if df_seed.empty:
        raise ValueError("seed_papers.csv is empty.")

    print(f"Loaded {len(df_seed)} rows from '{SEED_PATH}'.", flush=True)

    df_corpus = build_corpus(df_seed)
    if df_corpus.empty:
        raise ValueError(
            "No usable seed papers (need title + abstract on each row). "
            "Re-run build_seed_csv.py or fill in seed_papers.csv."
        )

    if DRY_RUN:
        print(f"[DRY RUN] Would write {len(df_corpus)} rows to '{OUTPUT_CSV}'.")
        return

    df_corpus.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

    print(f"\n--- Summary ---")
    print(f"  Seed rows read      : {len(df_seed)}")
    print(f"  Corpus written      : {len(df_corpus)} rows → '{OUTPUT_CSV}'")
    print(f"  With DOI            : {(df_corpus['doi'].astype(str).str.strip() != '').sum()}")
    print(f"  With abstract       : {len(df_corpus)}")
    print("\nNext: open query_refinement.ipynb and run from the top.")


if __name__ == "__main__":
    main()
