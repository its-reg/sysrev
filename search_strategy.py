"""
Centralized search strategy for the systematic review.

Holds the inclusion/exclusion criteria, date filter, cleaning rules, and per-database
syntax so every query notebook stays consistent.
Terms tagged ``# NLP`` were surfaced by the TF-IDF / n-gram analysis in pubmed.ipynb.
"""

# --- Inclusion criteria: (disease) AND (spatial) AND (exposure) -------------
INCLUSION_CRITERIA = {
    "disease": [
        "parkinson* disease",
        "neurodegenerative disease",
    ],
    "spatial": [
        "geospatial",
        "spatial dependence",
        "spatiotemporal",
        "geographic",
        "environment*",
        "atmospheric",
        "spatial analysis",
    ],
    "exposure": [
        "pollution",
        "chemical",
        "pesticide",
        "air pollution",
        "microplastic pollution",
        "traffic pollution",
        "water pollution",
        "trichloroethylene",
    ],
}

# --- Exclusion criteria -----------------------------------------------------
EXCLUSION_TERMS = [
    # mechanism / physiology / clinical
    "pathology", "treatment", "therapy", "intervention", "physiology", "monitoring", "biosensor",
    # experimental systems
    "animal", "plant", "in vitro", "molecular", "protein", "mice",
    # off-topic conditions / studies
    "parkinson* disease model", "respiratory", "resistance training", "aggression",
]

# --- Alternate / expansion terms (for sensitivity analyses) -----------------
# `# NLP` = surfaced by suggest_expansions() in pubmed.ipynb.
ALTERNATE_TERMS = {
    "disease": [
        "movement disorders",
        "extrapyramidal disorders",
        "dementia",                       # NLP
        "alzheimer*",                     # NLP
        "cognitive impairment",           # NLP
        "amyotrophic lateral sclerosis",  # NLP
    ],
    "spatial": [
        "spatial analysis",
        "geospatial analysis",
        "geographic information systems",
        "GIS",
        "spatial epidemiology",
    ],
    "exposure": [
        "air quality",
        "environmental exposure",
        "occupational exposure",
        "heavy metals",
        "pesticide exposure",
        "particulate matter",      # NLP
        "nitrogen dioxide",        # NLP
        "ambient air pollution",   # NLP
        "long-term exposure",      # NLP
        "air pollution exposure",  # NLP
    ],
}

# Raw top-ranked terms from suggest_expansions() (pubmed.ipynb), kept for provenance.
# Domain-relevant ones are folded into ALTERNATE_TERMS above; the rest are generic
# methodology words (study, review, analysis, ...) that are not search-worthy.
NLP_SUGGESTED_EXPANSIONS = [
    "exposure", "air", "parkinson", "risk", "dementia", "study", "factors",
    "environmental", "neurodegenerative", "association", "studies", "pesticides",
    "diseases", "alzheimer", "particulate", "term", "associated", "review", "analysis",
    "matter", "long term", "particulate matter", "pesticide exposure",
    "cognitive impairment", "nitrogen dioxide", "ambient air pollution",
    "amyotrophic lateral sclerosis", "air pollution exposure",
]

# --- Date filter & cleaning rules -------------------------------------------
DATE_FILTER = {
    "start_date": "2020-01-01",
    "end_date": "2025-12-31",  # None = no upper limit
    "reason": "5-year window; revisit recency-cutoff justification",
}

CLEANING_RULES = {
    "remove_duplicate_titles": True,
    "require_pubmed_id": True,
    "require_doi": True,
    "description": "Drop duplicate titles; keep only records with a PubMed ID and DOI",
}

# --- Per-database query syntax ----------------------------------------------
# All follow the template: (disease) AND (spatial) AND (exposure) NOT (exclusions)
DATABASE_CONFIGS = {
    "pubmed": {
        "client": "pymed",
        "fields": {"title_abstract": "[TIAB]", "mesh": "[MH]"},
        "status": "queried",
    },
    "scopus": {
        "client": "pybliometrics",
        "fields": {"title_abstract_keyword": "TITLE-ABS-KEY()"},
        "date_syntax": "PUBYEAR > {year}",
        "status": "in progress — pybliometrics (see scopus.ipynb)",
    },
    "embase": {
        "client": "requests (Embase Search API)",
        "fields": {"title_abstract": ":ti,ab"},
        "date_syntax": "[{start}-{end}]/py",
        "status": (
            "in progress — Embase Search API (see embase.ipynb); "
            "requires ELSEVIER_API_KEY (+ ELSEVIER_INSTTOKEN off-campus) in .env; "
            "coordinate Emtree terms with Malcolm & Lukas"
        ),
    },
    "google_scholar": {
        "client": "scholarly",
        "query_note": (
            "Flat OR-joined string — no boolean NOT or field specifiers supported. "
            "Exclusion terms applied post-hoc on title/abstract. "
            "Year range passed via year_low/year_high parameters."
        ),
        "status": "in progress — scholarly (see google_scholar.ipynb)",
    },
    "web_of_science": {
        "client": "requests (WoS Starter API)",
        "fields": {"topic": "TS()"},
        "date_syntax": "PY=({start}-{end})",
        "status": "in progress — WoS Starter API (see web_of_science.ipynb); institutional API key required",
    },
}

# --- Query results log (informational) --------------------------------------
QUERY_RESULTS = {
    "pubmed": {"total": 326, "last_5_years": 138, "after_cleaning": 154,
               "after_screening": 153, "date_queried": "2025-04-22"},
    "scopus": {"status": "not yet queried"},
    "embase": {"status": "not yet queried"},
    "web_of_science": {"status": "not yet queried"},
}
