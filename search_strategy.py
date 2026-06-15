"""
search_strategy.py
------------------
Single source of truth for the systematic review search strategy.
Every database notebook imports from here — edit terms here, nowhere else.

Query structure:  (disease) AND (spatial) AND (exposure) NOT (exclusions)

Sections
--------
1.  Core inclusion criteria       — manually defined, peer-reviewed
2.  NLP-expanded terms            — surfaced by TF-IDF / n-gram analysis in pubmed.ipynb;
                                    domain-relevant ones are folded into the query,
                                    full raw list kept for provenance
3.  Exclusion terms
4.  Date filter & cleaning rules
5.  Database configurations
"""


# =============================================================================
# 1. CORE INCLUSION CRITERIA
#    Manually defined terms that anchor the review scope.
#    All notebooks fold ALTERNATE_TERMS (Section 2) in by default;
#    set INCLUDE_ALTERNATE_TERMS = False to use these alone.
# =============================================================================

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


# =============================================================================
# 2. NLP-EXPANDED TERMS
#    Surfaced by suggest_expansions() (TF-IDF / n-gram) in pubmed.ipynb and
#    further tested in query_refinement.ipynb (BM25 / KeyBERT / SPECTER).
#
#    ALTERNATE_TERMS are folded into the live query alongside INCLUSION_CRITERIA.
#    NLP_SUGGESTED_EXPANSIONS is the full raw output — kept for provenance;
#    generic methodology words (study, review, analysis…) were intentionally
#    left out of ALTERNATE_TERMS as non-search-worthy.
# =============================================================================

ALTERNATE_TERMS = {
    "disease": [
        "movement disorders",
        "extrapyramidal disorders",
        "dementia",
        "alzheimer*",
        "cognitive impairment",
        "amyotrophic lateral sclerosis",
    ],
    "spatial": [
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
        "particulate matter",
        "nitrogen dioxide",
        "ambient air pollution",
        "long-term exposure",
        "air pollution exposure",
    ],
}

# Full raw TF-IDF output from pubmed.ipynb — for provenance only, not used in queries.
NLP_SUGGESTED_EXPANSIONS = [
    "exposure", "air", "parkinson", "risk", "dementia", "study", "factors",
    "environmental", "neurodegenerative", "association", "studies", "pesticides",
    "diseases", "alzheimer", "particulate", "term", "associated", "review", "analysis",
    "matter", "long term", "particulate matter", "pesticide exposure",
    "cognitive impairment", "nitrogen dioxide", "ambient air pollution",
    "amyotrophic lateral sclerosis", "air pollution exposure",
]


# =============================================================================
# 3. EXCLUSION TERMS
# =============================================================================

EXCLUSION_TERMS = [
    # Mechanism / physiology / clinical focus
    "pathology", "treatment", "therapy", "intervention",
    "physiology", "monitoring", "biosensor",
    # Experimental systems
    "animal", "plant", "in vitro", "molecular", "protein", "mice",
    # Off-topic conditions or study types
    "parkinson* disease model", "respiratory", "resistance training", "aggression",
]


# =============================================================================
# 4. DATE FILTER & CLEANING RULES
# =============================================================================

DATE_FILTER = {
    "start_date": "2020-01-01",
    "end_date":   "2025-12-31",   # set to None for no upper limit
    "reason":     "5-year window; revisit recency-cutoff justification",
}

CLEANING_RULES = {
    "remove_duplicate_titles": True,
    "require_pubmed_id":       True,
    "require_doi":             True,
    "description": "Drop duplicate titles; keep only records with both a PubMed ID and a DOI",
}


# =============================================================================
# 5. DATABASE CONFIGURATIONS
#    Field syntax and client notes for each database notebook.
#    Query results / run logs live in logs/query_results.json — not here.
# =============================================================================

DATABASE_CONFIGS = {
    "pubmed": {
        "client": "pymed",
        "fields": {"title_abstract": "[TIAB]", "mesh": "[MH]"},
        "status": "queried — see pubmed.ipynb",
    },
    "scopus": {
        "client": "elsapy (Scopus Search API)",
        "fields": {"title_abstract_keyword": "TITLE-ABS-KEY()"},
        "date_syntax": "PUBYEAR > {start-1} AND PUBYEAR < {end+1}",
        "status": "in progress — year-by-year collection; see scopus.ipynb",
    },
    "embase": {
        "client": "requests (Embase Search API)",
        "fields": {"title_abstract": ":ti,ab"},
        "date_syntax": "[{start}-{end}]/py",
        "status": "in progress — see embase.ipynb; coordinate Emtree terms with Malcolm & Lukas",
    },
    "google_scholar": {
        "client": "scholarly",
        "query_note": (
            "Flat OR-joined string — boolean NOT and field specifiers not supported. "
            "Exclusion terms applied post-hoc. Year range via year_low/year_high."
        ),
        "status": "in progress — supplementary source; see google_scholar.ipynb",
    },
    "web_of_science": {
        "client": "requests (WoS Starter API)",
        "fields": {"topic": "TS()"},
        "date_syntax": "PY=({start}-{end})",
        "status": "in progress — see web_of_science.ipynb; institutional API key required",
    },
}
