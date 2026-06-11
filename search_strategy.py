"""
Centralized search strategy configuration for systematic review.
Defines inclusion/exclusion criteria, date filters, and database-specific syntax.
Used across all database query notebooks (PubMed, SCOPUS, EMBASE, etc.)
"""

# ============================================================================
# INCLUSION CRITERIA
# ============================================================================

DISEASE_TERMS = [
    "parkinson* disease",
    "neurodegenerative disease",
]

SPATIAL_TERMS = [
    "geospatial",
    "spatial dependence",
    "spatiotemporal",
    "geographic",
    "environment*",
    "atmospheric",
    "spatial analysis",
]

EXPOSURE_TERMS = [
    "pollution",
    "chemical",
    "pesticide",
    "air pollution",
    "microplastic pollution",
    "traffic pollution",
    "water pollution",
    "trichloroethylene",
]

INCLUSION_CRITERIA = {
    "disease": DISEASE_TERMS,
    "spatial": SPATIAL_TERMS,
    "exposure": EXPOSURE_TERMS,
}

# ============================================================================
# EXCLUSION CRITERIA
# ============================================================================

EXCLUSION_TERMS = [
    # Mechanism/physiology studies
    "pathology",
    "treatment",
    "therapy",
    "intervention",
    "physiology",
    "monitoring",
    "biosensor",
    # Experimental systems
    "animal",
    "plant",
    "in vitro",
    "molecular",
    "protein",
    "mice",
    # Irrelevant conditions/studies
    "parkinson* disease model",
    "respiratory",
    "resistance training",
    "aggression",
]

# ============================================================================
# DATE FILTER
# ============================================================================

DATE_FILTER = {
    "start_date": "2020-01-01",
    "end_date": "2025-12-31",  # None would mean no upper limit
    "reason": "5-year window; review justification of recency cutoff",
}

# ============================================================================
# DATA CLEANING RULES
# ============================================================================

CLEANING_RULES = {
    "remove_duplicate_titles": True,
    "require_pubmed_id": True,
    "require_doi": True,
    "description": "Remove duplicates by title, filter for records with pubmed_id and DOI",
}

# ============================================================================
# DATABASE-SPECIFIC QUERY SYNTAX
# ============================================================================

DATABASE_CONFIGS = {
    "pubmed": {
        "description": "PubMed/Medline via pymed",
        "query_template": "(disease) AND (spatial) AND (exposure) NOT (exclusions)",
        "operators": {
            "AND": "AND",
            "OR": "OR",
            "NOT": "NOT",
            "wildcard": "*",
            "phrase": '"..."',
        },
        "field_syntax": {
            "title_abstract": "[TIAB]",  # Title/Abstract field
            "mesh": "[MH]",  # MeSH terms
        },
        "example_query": '("parkinson* disease" OR "neurodegenerative disease") AND ("geospatial" OR "spatial dependence" OR "spatiotemporal" OR "geographic" OR "environment*" OR "atmospheric") AND ("pollution" OR "chemical" OR "pesticide") NOT ("pathology" OR "treatment" OR "therapy" OR "intervention" OR "physiology" OR "monitoring" OR "biosensor") NOT ("animal" OR "plant" OR "in vitro" OR "molecular" OR "protein" OR "mice") NOT ("parkinson* disease model" OR "respiratory" OR "resistance training" OR "aggression")',
    },
    "scopus": {
        "description": "SCOPUS via pybliometrics",
        "query_template": "TITLE-ABS-KEY((disease) AND (spatial) AND (exposure) AND NOT (exclusions))",
        "operators": {
            "AND": "AND",
            "OR": "OR",
            "NOT": "NOT",
            "wildcard": "*",
            "phrase": '"..."',
        },
        "field_syntax": {
            "title_abstract_keyword": "TITLE-ABS-KEY()",
            "title": "TITLE()",
            "abstract": "ABS()",
        },
        "date_syntax": "PUBYEAR > {year}",
        "note": "TODO: Translate inclusion/exclusion terms to SCOPUS format",
    },
    "embase": {
        "description": "EMBASE (not yet implemented)",
        "query_template": "Emtree terms or free text search",
        "field_syntax": {
            "title_abstract": ".ti,ab.",
        },
        "suggested_mesh_terms": [
            "air pollution",
            "microplastic",
            "traffic pollution",
            "water pollution",
            "trichloroethylene",
            "parkinsons disease",
            "neurodegenerative disorder",
        ],
        "note": "Coordinate with Malcolm and Lukas to expand pollution and geo terms",
    },
    "google_scholar": {
        "description": "Google Scholar (not yet implemented)",
        "note": "Requires manual search or scholarly library integration",
    },
    "web_of_science": {
        "description": "Web of Science (not yet implemented)",
        "note": "May require institutional access",
    },
}

# ============================================================================
# ALTERNATE/EXPANSION TERMS
# ============================================================================
# For future database exploration and sensitivity analyses

ALTERNATE_TERMS = {
    "disease": [
        "movement disorders",
        "extrapyramidal disorders",
        # NLP-suggested (see NLP_SUGGESTED_EXPANSIONS):
        "dementia",
        "alzheimer disease",
        "cognitive impairment",
        "amyotrophic lateral sclerosis",
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
        # NLP-suggested (see NLP_SUGGESTED_EXPANSIONS):
        "particulate matter",
        "nitrogen dioxide",
        "ambient air pollution",
        "long-term exposure",
        "air pollution exposure",
    ],
}

# ============================================================================
# NLP-SUGGESTED EXPANSION TERMS
# ============================================================================
# Raw output of suggest_expansions() from pubmed.ipynb, captured here for
# provenance. These are the highest-scoring candidate n-grams (blend of TF-IDF
# importance and raw frequency) found in the cleaned PubMed corpus that are NOT
# already in the query. I use them to inform sensitivity analyses and query
# refinement. The domain-relevant ones have been folded into ALTERNATE_TERMS
# above; generic methodology terms (e.g. "study", "review", "meta analysis",
# "95 ci") are retained here for transparency but are not search-worthy.

NLP_SUGGESTED_EXPANSIONS = {
    "source": "pubmed.ipynb -> suggest_expansions()",
    "corpus": "pubmed_results_cleaned_2025.csv (154 documents)",
    "method": "TF-IDF (0.7) + normalized frequency (0.3) over 1-3 grams, min_count=2",
    # Default call: suggest_expansions(n=20, min_count=2)
    "top_20": [
        "exposure", "air", "parkinson", "risk", "dementia", "study", "factors",
        "environmental", "neurodegenerative", "association", "studies",
        "pesticides", "diseases", "alzheimer", "particulate", "term",
        "associated", "review", "analysis", "matter",
    ],
    # By n-gram length, for readability
    "unigrams": [
        "exposure", "air", "parkinson", "risk", "dementia", "study", "factors",
        "environmental", "neurodegenerative", "association", "studies",
        "pesticides", "diseases", "alzheimer", "particulate",
    ],
    "bigrams": [
        "alzheimer disease", "long term", "particulate matter", "disease pd",
        "pesticide exposure", "95 ci", "neurodegenerative diseases",
        "risk factors", "environmental factors", "term exposure",
        "meta analysis", "systematic review", "cognitive impairment",
        "nitrogen dioxide", "pd risk",
    ],
    "trigrams": [
        "parkinson disease pd", "long term exposure", "disease parkinson disease",
        "ambient air pollution", "air pollution parkinson",
        "air pollution exposure", "amyotrophic lateral sclerosis",
        "pollution parkinson disease", "case control study",
        "particulate matter pm",
    ],
}

# ============================================================================
# QUERY RESULTS SUMMARY (informational)
# ============================================================================

QUERY_RESULTS = {
    "pubmed": {
        "total_results": 326,
        "results_last_5_years": 138,
        "after_cleaning": 154,
        "after_screening": 153,
        "date_queried": "2025-04-22",
    },
    "scopus": {
        "status": "Not yet queried",
    },
    "embase": {
        "status": "Not yet queried",
    },
}
