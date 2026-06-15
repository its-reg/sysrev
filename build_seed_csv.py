"""
build_seed_csv.py
-----------------
Scans every PDF in seed_papers/ and builds seed_papers.csv.

Pipeline per file
-----------------
1. Parse the Zotero filename for a fallback author/year/title.
2. Use PyMuPDF to extract the first two pages of text.
3. Search that text for a DOI with a regex.
4. Query the CrossRef REST API:
      - by DOI  if one was found  →  very reliable
      - by title if not           →  best-effort; top result is accepted if
                                      the title similarity is ≥ TITLE_SIM_THRESHOLD
5. Merge: CrossRef data wins; PDF-text abstract used as fallback when
   CrossRef does not carry one (common for older papers).
6. Write seed_papers.csv, overwriting the placeholder template.

Requirements
------------
    pip install pymupdf requests   (both already installed in the sysrev env)

Notes
-----
- Empty PDFs (0-byte files) are skipped with a warning.
- CrossRef is rate-limited to ~50 req/s; a 0.25 s sleep keeps us safe.
- Set DRY_RUN = True to print what would happen without writing anything.
"""

import re
import time
import unicodedata
from pathlib import Path

import fitz          # PyMuPDF
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED_DIR            = Path("seed_papers")
OUTPUT_CSV          = Path("seed_papers.csv")
CROSSREF_MAILTO     = "sysrev-script/0.1 (contact via project repository)"
TITLE_SIM_THRESHOLD = 0.60   # minimum token overlap to accept a title-based CR hit
REQUEST_SLEEP       = 0.25   # seconds between CrossRef calls
DRY_RUN             = False  # set True to preview without writing

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
DOI_RE = re.compile(
    r"\b(10\.\d{4,9}/[^\s\"'<>]+)",
    re.IGNORECASE,
)

def _extract_pdf_text(path: Path, max_pages: int = 3) -> str:
    """Return text from the first max_pages of a PDF, or '' on failure."""
    try:
        with fitz.open(str(path)) as doc:
            pages = min(len(doc), max_pages)
            return " ".join(doc[i].get_text() for i in range(pages))
    except Exception as exc:
        print(f"  [PDF error] {path.name}: {exc}")
        return ""


def _find_doi(text: str) -> str | None:
    """Return the first DOI found in text, cleaned of trailing punctuation."""
    m = DOI_RE.search(text)
    if not m:
        return None
    doi = m.group(1).rstrip(".,;:)>")
    # Remove anything that looks like a page reference appended to the DOI
    doi = re.sub(r"\s.*$", "", doi)
    return doi


def _token_overlap(a: str, b: str) -> float:
    """Simple Jaccard token overlap between two strings (lowercased)."""
    ta = set(re.findall(r"[a-z0-9]+", a.lower()))
    tb = set(re.findall(r"[a-z0-9]+", b.lower()))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _clean_text(s) -> str:
    """Strip HTML tags and normalise whitespace."""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", str(s))
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip()


def _crossref_by_doi(doi: str, session: requests.Session) -> dict | None:
    """Query CrossRef by DOI. Returns the 'message' dict or None."""
    url = f"https://api.crossref.org/works/{requests.utils.quote(doi, safe='/')}"
    try:
        r = session.get(url, timeout=15)
        if r.status_code == 200:
            return r.json().get("message")
    except Exception as exc:
        print(f"    [CrossRef DOI error] {doi}: {exc}")
    return None


def _crossref_by_title(title: str, session: requests.Session) -> dict | None:
    """Query CrossRef by title (bibliographic search). Returns best hit or None."""
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": title, "rows": 1, "select": "DOI,title,abstract,author,container-title,published,type"}
    try:
        r = session.get(url, params=params, timeout=15)
        if r.status_code == 200:
            items = r.json().get("message", {}).get("items", [])
            if items:
                cr_title = " ".join(items[0].get("title", []))
                sim = _token_overlap(title, cr_title)
                if sim >= TITLE_SIM_THRESHOLD:
                    return items[0]
                print(f"    [CrossRef title] low similarity ({sim:.2f}) — skipped")
    except Exception as exc:
        print(f"    [CrossRef title error] {title[:60]}: {exc}")
    return None


def _parse_message(msg: dict) -> dict:
    """Extract the fields we care about from a CrossRef 'message' dict."""
    # Authors
    authors_raw = msg.get("author", [])
    author_parts = []
    for a in authors_raw:
        given  = a.get("given", "")
        family = a.get("family", "")
        author_parts.append(f"{family}, {given}".strip(", "))
    authors_str = "; ".join(author_parts)

    # Publication date (prefer print over online)
    date_str = ""
    for field in ("published-print", "published-online", "published"):
        dp = msg.get(field, {}).get("date-parts", [[]])
        if dp and dp[0]:
            parts = [str(x) for x in dp[0] if x]
            date_str = "-".join(parts)
            break

    # Journal / container title
    containers = msg.get("container-title", [])
    journal = containers[0] if containers else ""

    # Keywords (not commonly populated in CrossRef)
    keywords_raw = msg.get("subject", [])
    keywords = "; ".join(keywords_raw)

    return {
        "doi":              msg.get("DOI", ""),
        "title":            _clean_text(" ".join(msg.get("title", []))),
        "abstract":         _clean_text(msg.get("abstract", "")),
        "authors":          authors_str,
        "journal":          journal,
        "publication_date": date_str,
        "keywords":         keywords,
    }


def _parse_filename(path: Path) -> dict:
    """
    Extract author / year / title guess from a Zotero-style filename.
    Format: "Author et al. - YEAR - Title fragment.pdf"
    """
    stem = path.stem
    parts = [p.strip() for p in stem.split(" - ", maxsplit=2)]
    author = parts[0] if len(parts) > 0 else ""
    year   = parts[1] if len(parts) > 1 else ""
    title  = parts[2] if len(parts) > 2 else stem
    return {"filename_author": author, "filename_year": year, "filename_title": title}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    pdfs = sorted(SEED_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDF files found in '{SEED_DIR}/'. Exiting.")
        return

    print(f"Found {len(pdfs)} PDFs in '{SEED_DIR}/'.\n")

    session = requests.Session()
    session.headers.update({"User-Agent": CROSSREF_MAILTO})

    rows = []
    for pdf in pdfs:
        print(f"Processing: {pdf.name}")

        # Skip empty files
        if pdf.stat().st_size == 0:
            print("  [skip] Empty file.")
            fname = _parse_filename(pdf)
            rows.append({
                "title":            fname["filename_title"],
                "abstract":         "",
                "doi":              "",
                "pubmed_id":        "",
                "keywords":         "",
                "authors":          fname["filename_author"],
                "journal":          "",
                "publication_date": fname["filename_year"],
                "file":             pdf.name,
                "notes":            "EMPTY PDF — metadata not extracted",
            })
            continue

        fname      = _parse_filename(pdf)
        pdf_text   = _extract_pdf_text(pdf)
        doi        = _find_doi(pdf_text)
        cr_msg     = None
        source     = ""

        if doi:
            print(f"  DOI found: {doi}")
            cr_msg = _crossref_by_doi(doi, session)
            source = "crossref_doi"
            time.sleep(REQUEST_SLEEP)

        if cr_msg is None:
            # Fall back to title search using the filename title hint
            print(f"  No DOI (or lookup failed) — trying title search: '{fname['filename_title'][:60]}'")
            cr_msg = _crossref_by_title(fname["filename_title"], session)
            source = "crossref_title"
            time.sleep(REQUEST_SLEEP)

        if cr_msg:
            row = _parse_message(cr_msg)
            row["source"] = source
            # Use PDF-extracted text as abstract fallback
            if not row["abstract"] and pdf_text:
                ab_match = re.search(
                    r"abstract[:\s]+(.{100,1500}?)(?:introduction|keywords|background|1\s*\.)",
                    pdf_text, re.IGNORECASE | re.DOTALL,
                )
                if ab_match:
                    row["abstract"] = _clean_text(ab_match.group(1))
                    row["source"]  += "+pdf_abstract"
        else:
            # Full fallback — filename only
            print(f"  [warn] CrossRef lookup failed — using filename metadata only.")
            row = {
                "doi":              doi or "",
                "title":            fname["filename_title"],
                "abstract":         "",
                "authors":          fname["filename_author"],
                "journal":          "",
                "publication_date": fname["filename_year"],
                "keywords":         "",
                "source":           "filename_only",
            }

        row["file"]    = pdf.name
        row["pubmed_id"] = row.get("pubmed_id", "")
        row["notes"]   = ""
        rows.append(row)
        print(f"  -> title: {str(row.get('title',''))[:80]}")

    df = pd.DataFrame(rows)

    # Reorder columns to match seed_papers.csv schema expected by query_refinement.ipynb
    col_order = ["title", "abstract", "doi", "pubmed_id", "keywords",
                 "authors", "journal", "publication_date", "file", "notes", "source"]
    for c in col_order:
        if c not in df.columns:
            df[c] = ""
    df = df[col_order]

    print(f"\n--- Summary ---")
    print(f"  Total PDFs processed : {len(pdfs)}")
    print(f"  Rows generated       : {len(df)}")
    print(f"  With DOI             : {(df['doi'] != '').sum()}")
    print(f"  With abstract        : {(df['abstract'].astype(str).str.strip() != '').sum()}")
    print(f"  Metadata source breakdown:\n{df['source'].value_counts().to_string()}")

    if DRY_RUN:
        print("\n[DRY RUN] — not writing. Set DRY_RUN = False to save.")
        print(df[["title", "doi", "source"]].to_string())
    else:
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\nWrote {len(df)} rows to '{OUTPUT_CSV}'.")


if __name__ == "__main__":
    main()
