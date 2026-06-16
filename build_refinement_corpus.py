"""
build_refinement_corpus.py
--------------------------
Build a candidate corpus for search-strategy refinement testing.

Reads the confirmed-relevant seed set (seed_papers.csv), extracts the most
characteristic vocabulary from seed abstracts, queries PubMed for related
literature, removes the seed papers themselves, and writes refinement_corpus.csv.

That file is the pool query_refinement.ipynb ranks against your 55 seeds with
BM25, KeyBERT/YAKE, and SPECTER — separate from any full-database export.

Usage
-----
    python build_refinement_corpus.py

Requires PUBMED_EMAIL in .env (same as pubmed.ipynb).
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from pymed import PubMed
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from search_strategy import DATE_FILTER, EXCLUSION_TERMS, INCLUSION_CRITERIA

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED_PATH = Path("seed_papers.csv")
OUTPUT_CSV = Path("refinement_corpus.csv")
TOP_TERMS = 25          # seed-derived terms to OR together in the PubMed query
MAX_RESULTS = 500       # PubMed fetch cap (same default as pubmed.ipynb)
RELATED_PER_SEED = 15   # related articles to pull per seed DOI (0 to disable)
TITLE_SIM_THRESHOLD = 0.85  # treat as seed duplicate if title overlap ≥ this
REQUEST_SLEEP = 0.34    # NCBI etiquette (~3 req/s without API key)
DRY_RUN = False

GENERIC_TERMS = {
    "study", "studies", "review", "results", "result", "analysis", "data",
    "method", "methods", "background", "objective", "objectives", "aim",
    "aims", "conclusion", "conclusions", "introduction", "discussion",
    "findings", "associated", "association", "risk", "factors", "factor",
    "patients", "patient", "cases", "case", "control", "controls",
    "cohort", "population", "health", "disease", "diseases", "related",
    "including", "among", "using", "used", "based", "however", "also",
    "significant", "increased", "decreased", "compared", "may", "well",
    "use", "age", "people", "new", "years", "care", "access", "research",
    "models", "model", "levels", "level", "genetic", "report", "reports",
}


def _coerce_text(val) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    if isinstance(val, (list, tuple)):
        return " ".join(str(v) for v in val if v)
    return str(val).strip()


def _normalize_doi(doi) -> str:
    doi = _coerce_text(doi).lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi.rstrip(".,;)")


def _token_overlap(a: str, b: str) -> float:
    ta = set(re.findall(r"[a-z0-9]+", a.lower()))
    tb = set(re.findall(r"[a-z0-9]+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _strategy_terms() -> set[str]:
    """Lowercase tokens already covered by search_strategy.py."""
    terms: set[str] = set()
    for group in INCLUSION_CRITERIA.values():
        for t in group:
            terms.update(re.findall(r"[a-z0-9]+", t.lower()))
    for t in EXCLUSION_TERMS:
        terms.update(re.findall(r"[a-z0-9]+", t.lower()))
    return terms


def _row_text(row) -> str:
    return " ".join(
        p for p in (
            _coerce_text(row.get("title")),
            _coerce_text(row.get("abstract")),
            _coerce_text(row.get("keywords")),
        ) if p
    )


def extract_seed_terms(df_seed: pd.DataFrame, top_n: int = TOP_TERMS) -> list[str]:
    """Rank 1–2 grams from seed abstracts; return top_n not already in the strategy."""
    texts = [_coerce_text(r.get("abstract")) for r in df_seed.to_dict("records")]
    texts = [t for t in texts if len(t.split()) >= 20]
    if not texts:
        raise ValueError(
            "Seed abstracts are too short for term extraction. "
            "Re-run build_seed_csv.py or add abstracts to seed_papers.csv."
        )

    vec = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words=list(ENGLISH_STOP_WORDS | GENERIC_TERMS),
        min_df=2,
        max_df=0.85,
        token_pattern=r"(?u)\b[a-z][a-z0-9\-]{2,}\b",
    )
    matrix = vec.fit_transform(texts)
    scores = matrix.sum(axis=0).A1
    feature_names = vec.get_feature_names_out()

    strategy_tokens = _strategy_terms()
    ranked: list[tuple[float, str]] = []
    for score, term in zip(scores, feature_names):
        term_tokens = set(re.findall(r"[a-z0-9]+", term.lower()))
        if term_tokens & strategy_tokens and len(term.split()) == 1:
            continue
        if term in GENERIC_TERMS:
            continue
        ranked.append((float(score), term))

    ranked.sort(reverse=True)
    chosen: list[str] = []
    seen: set[str] = set()
    for _, term in ranked:
        key = term.lower()
        if key in seen:
            continue
        # Drop short unigrams unless they look like pollutant/metric tokens (e.g. no2, pm2).
        if " " not in term and len(term) < 4 and not re.fullmatch(r"[a-z]+\d+", term):
            continue
        seen.add(key)
        chosen.append(term)
        if len(chosen) >= top_n:
            break

    if len(chosen) < 5:
        raise ValueError(
            f"Only extracted {len(chosen)} usable seed terms — need at least 5. "
            "Check seed abstract quality or lower min_df in the vectorizer."
        )
    return chosen


def or_group(terms: list[str]) -> str:
    return "(" + " OR ".join(f'"{t}"' for t in terms) + ")"


def build_query(seed_terms: list[str]) -> str:
    """Seed-vocabulary query anchored on core disease terms, with exclusions."""
    disease_anchor = or_group(INCLUSION_CRITERIA["disease"][:2])
    return (
        f"{or_group(seed_terms)} AND {disease_anchor} "
        f"NOT {or_group(EXCLUSION_TERMS)}"
    )


def article_to_flat_dict(article) -> dict:
    try:
        raw = article.toJSON()
        if isinstance(raw, str):
            return json.loads(raw)
        if isinstance(raw, dict):
            return raw
    except Exception:
        pass
    return {
        "pubmed_id": getattr(article, "pubmed_id", None),
        "title": getattr(article, "title", None),
        "publication_date": str(getattr(article, "publication_date", "") or ""),
        "keywords": getattr(article, "keywords", None),
        "abstract": getattr(article, "abstract", None),
        "doi": getattr(article, "doi", None),
        "authors": getattr(article, "authors", None),
        "journal": getattr(article, "journal", None),
    }


def _ncbi_get(url: str, params: dict, email: str) -> dict | None:
    params = {**params, "email": email, "tool": "sysrev_refinement_corpus"}
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"  [NCBI error] {exc}")
        return None


def pmids_for_doi(doi: str, email: str) -> list[str]:
    data = _ncbi_get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        {"db": "pubmed", "term": f"{doi}[doi]", "retmode": "json", "retmax": 1},
        email,
    )
    if not data:
        return []
    return data.get("esearchresult", {}).get("idlist", [])


def related_pmids(pmid: str, email: str, max_related: int) -> list[str]:
    data = _ncbi_get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi",
        {
            "dbfrom": "pubmed",
            "db": "pubmed",
            "id": pmid,
            "linkname": "pubmed_pubmed",
            "retmode": "json",
        },
        email,
    )
    if not data:
        return []
    links = data.get("linksets", [{}])[0].get("linksetdbs", [])
    for block in links:
        if block.get("linkname") == "pubmed_pubmed":
            raw_links = block.get("links", [])
            ids = []
            for x in raw_links:
                if isinstance(x, dict):
                    if x.get("id"):
                        ids.append(str(x["id"]))
                elif x:
                    ids.append(str(x))
            return [i for i in ids if i != pmid][:max_related]
    return []


def fetch_by_pmids(pmids: list[str], pubmed: PubMed) -> list[dict]:
    if not pmids:
        return []
    rows: list[dict] = []
    for pmid in pmids:
        try:
            hits = list(pubmed.query(f"{pmid}[uid]", max_results=1))
            rows.extend(article_to_flat_dict(a) for a in hits)
        except Exception as exc:
            print(f"  [fetch PMID {pmid}] {exc}")
        time.sleep(REQUEST_SLEEP)
    return rows


def is_seed_row(row: dict, seed_dois: set[str], seed_titles: list[str]) -> bool:
    doi = _normalize_doi(row.get("doi"))
    if doi and doi in seed_dois:
        return True
    title = _coerce_text(row.get("title"))
    if not title:
        return False
    return any(_token_overlap(title, st) >= TITLE_SIM_THRESHOLD for st in seed_titles)


def clean_corpus(df: pd.DataFrame, df_seed: pd.DataFrame) -> pd.DataFrame:
    seed_dois = {_normalize_doi(d) for d in df_seed["doi"] if _normalize_doi(d)}
    seed_titles = [_coerce_text(t) for t in df_seed["title"] if _coerce_text(t)]

    df = df.copy()
    df = df[df["title"].astype(str).str.strip().astype(bool)]
    df = df[df["abstract"].astype(str).str.strip().astype(bool)]
    df = df[~df.apply(lambda r: is_seed_row(r, seed_dois, seed_titles), axis=1)]
    df = df.drop_duplicates(subset=["title"], keep="first")

    df["publication_date"] = pd.to_datetime(
        df["publication_date"], format="ISO8601", errors="coerce"
    )
    start = pd.Timestamp(DATE_FILTER["start_date"])
    end_raw = DATE_FILTER.get("end_date")
    end = pd.Timestamp(end_raw) if end_raw else None

    mask = df["publication_date"] >= start
    if end is not None:
        mask &= df["publication_date"] <= end
    df = df[mask | df["publication_date"].isna()]

    col_order = [
        "title", "abstract", "doi", "pubmed_id", "keywords",
        "authors", "journal", "publication_date",
    ]
    for c in col_order:
        if c not in df.columns:
            df[c] = ""
    return df[col_order].reset_index(drop=True)


def main():
    load_dotenv()
    email = os.getenv("PUBMED_EMAIL")
    if not email:
        raise EnvironmentError("Set PUBMED_EMAIL in .env before running.")

    if not SEED_PATH.exists():
        raise FileNotFoundError(f"'{SEED_PATH}' not found — run build_seed_csv.py first.")

    df_seed = pd.read_csv(SEED_PATH, encoding="latin-1")
    df_seed = df_seed[~df_seed["title"].astype(str).str.startswith("REPLACE")]
    if df_seed.empty:
        raise ValueError("seed_papers.csv has no real entries.")

    print(f"Loaded {len(df_seed)} seed papers from '{SEED_PATH}'.")

    seed_terms = extract_seed_terms(df_seed)
    query = build_query(seed_terms)
    print(f"\nSeed-derived terms ({len(seed_terms)}):")
    print(", ".join(seed_terms))
    print(f"\nPubMed query:\n{query}\n")

    if DRY_RUN:
        print("[DRY RUN] — not querying PubMed or writing output.")
        return

    pubmed = PubMed(tool="SystematicReview", email=email)
    rows = [article_to_flat_dict(a) for a in pubmed.query(query, max_results=MAX_RESULTS)]
    print(f"PubMed keyword search returned {len(rows)} articles.")

    if RELATED_PER_SEED > 0:
        related_ids: set[str] = set()
        seed_dois = [_normalize_doi(d) for d in df_seed["doi"] if _normalize_doi(d)]
        print(f"Fetching up to {RELATED_PER_SEED} related articles per seed DOI ...")
        for i, doi in enumerate(seed_dois, 1):
            pmids = pmids_for_doi(doi, email)
            time.sleep(REQUEST_SLEEP)
            if not pmids:
                continue
            for rel in related_pmids(pmids[0], email, RELATED_PER_SEED):
                related_ids.add(rel)
            time.sleep(REQUEST_SLEEP)
            if i % 10 == 0:
                print(f"  ... processed {i}/{len(seed_dois)} seed DOIs")
        print(f"  Found {len(related_ids)} unique related PMIDs.")
        rows.extend(fetch_by_pmids(sorted(related_ids), pubmed))
        print(f"Combined pool before cleaning: {len(rows)} rows.")

    df = pd.json_normalize(rows)
    if df.empty:
        raise RuntimeError("PubMed returned no articles — try broadening TOP_TERMS or MAX_RESULTS.")

    df_clean = clean_corpus(df, df_seed)
    df_clean.to_csv(OUTPUT_CSV, index=False)

    print(f"\n--- Summary ---")
    print(f"  Seed papers excluded : {len(df_seed)}")
    print(f"  Corpus written       : {len(df_clean)} rows → '{OUTPUT_CSV}'")
    print(f"  With DOI             : {(df_clean['doi'].astype(str).str.strip() != '').sum()}")
    print(f"  With PubMed ID       : {(df_clean['pubmed_id'].astype(str).str.strip() != '').sum()}")
    print("\nNext: open query_refinement.ipynb and run from the top.")


if __name__ == "__main__":
    main()
