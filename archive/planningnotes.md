## NLP alternatives to TF-IDF for building criteria from seed papers

TF-IDF treats terms as independent and misses semantic relationships. Stronger alternatives:

- **BM25** — a direct upgrade to TF-IDF; adds document length normalization and term saturation, so frequent terms don't drown signal. Same interpretability, better ranking.
- **KeyBERT / YAKE** — extract keyphrases using contextual embeddings rather than raw frequency. Better at surfacing multi-word concepts like "fine particulate matter" or "mortality displacement."
- **SPECTER or SciBERT embeddings** — encode full abstracts into dense vectors; semantic similarity in that space finds conceptually related papers even when they use different terminology. SciBERT is trained on scientific text; SPECTER is specifically designed for document-level scientific similarity.
- **Topic modelling (LDA/NMF)** — if your 7 seed papers cover multiple sub-themes (e.g. exposure measurement + health outcomes), topic modelling can decompose them and let you screen against each theme separately, rather than treating the seed set as a single monolithic concept.
- **Controlled vocabularies / ontologies** — for biomedical/environmental topics especially, MeSH, UMLS, or domain-specific ontologies give you synonym expansion for free (PM2.5 → "fine particles" → "particulate matter 2.5"). This is query-side augmentation, not a replacement for TF-IDF, but very high ROI.

---

## Assessment of your LLM implementation idea

The core intuition — use seed papers to anchor the "relevance concept" and score incoming papers against it — is sound and increasingly common in systematic review tooling. A few observations:

**What's strong about it:** LLMs can reason about *why* a paper is relevant beyond keyword overlap. A paper might not contain your exact search terms but could still describe the same phenomenon under different nomenclature. That's where keyword-based screening leaks and LLMs recover.

**Where it gets tricky:**
- 7 seed papers is a thin prior. If they share incidental characteristics (e.g. all from EU studies, all using a specific PM metric), the LLM might screen for those rather than the true inclusion criterion. You'd want to be explicit about *which* aspects of the seed papers define inclusion.
- Reproducibility is a real concern for systematic reviews — LLM outputs vary across runs and model versions. You'd need to log prompts, model version, and outputs, and treat LLM screening as one layer in a pipeline, not the sole arbiter.
- "How closely does this follow the core research idea" is ambiguous as a prompt. Structured prompts that decompose the question (population? exposure? outcome? study design?) will outperform an open-ended similarity question.

**RAG vs. reasoning:** RAG gives you retrieval-with-grounding (good for scale, consistent), but pure RAG scores don't give you an audit trail. A better framing might be: use semantic similarity (SPECTER/SBERT) as a *ranker* to cut the top-N candidates cheaply, then use an LLM with chain-of-thought to make the actual include/exclude decision with explanation on that smaller set. That's cheaper and more auditable.

---

## Recommended pipeline sketch

**Collection augmentation:**
- Use controlled vocabularies to expand your keyword search (MeSH if PubMed, domain ontologies otherwise)
- SPECTER or Semantic Scholar's built-in semantic search as a parallel collection channel alongside your keyword search

**Pre-screening (replacing or augmenting manual title/abstract screening):**
1. **SBERT / SPECTER similarity** against seed paper embeddings → fast, cheap first filter; set a similarity threshold to remove obvious noise
2. **BM25 against a query built from seed keyphrases** → catches keyword-relevant papers the embedder might miss (complementary recall)
3. **LLM structured screening** on the survivors → prompt it with explicit PICO-style criteria derived from your seed set, ask for a binary decision + one-sentence reason; use temperature=0 for reproducibility

**Calibration step:** before running at scale, test your LLM screener against a held-out manually-labelled set (even 50-100 papers) to measure precision/recall and tune your similarity thresholds. This is the step most implementations skip and regret.

The biggest risk is treating any single method as a filter rather than a ranker — keeping a human in the loop on borderline cases is both good practice and a PRISMA requirement.