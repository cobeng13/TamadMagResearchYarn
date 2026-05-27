# Project State

Date reviewed: 2026-05-27

This repository is a local, file-based academic research workflow. It is currently strongest at defining a cautious staged process and partially automating paper discovery. It is not yet an autonomous research agent, manuscript writer, PDF parser, or OpenAI-integrated application.

## Current Purpose

The project helps turn study notes, local source files, and statistical outputs into a structured manuscript workflow. The sample project is about predicting Radiologic Technologist Licensure Examination success from academic performance, pre-board results, and related academic indicators.

The workflow is intentionally conservative:

- It keeps intermediate artifacts in project folders.
- It avoids inventing citations, papers, metadata, statistics, and conclusions.
- It separates search planning, source collection, ingestion, metadata extraction, evidence extraction, synthesis, drafting, and audits.
- It treats missing information as `To be confirmed.`

## Repository Structure

Main files and folders:

- `README.md`: user-facing guide and full workflow documentation.
- `PROJECT_STATE.md`: this handoff document.
- `requirements.txt`: Python dependencies for paper discovery and tests.
- `.env.example`: environment variables for API keys, contact emails, and provider toggles.
- `agents/research_brief_agent.py`: local script that creates a prompt from `projects/sample_project/input/study_notes.md`.
- `agents/prompts/`: staged prompt files for the end-to-end academic writing workflow.
- `projects/sample_project/`: sample project input and generated stage 00 brief files.
- `scripts/paper_discovery/`: API-assisted paper discovery tools.
- `scripts/paper_discovery/legacy/`: archived OpenAlex-first discovery scripts retained for reference only.
- `tests/`: provider, schema, pipeline, and secret-protection tests.

## Implemented Workflow Pieces

### Stage 00 Research Brief

Implemented as a local helper:

- Reads `projects/sample_project/input/study_notes.md`.
- Writes `projects/sample_project/00_brief/_prompt_for_ai.md`.
- Does not call an LLM.
- Requires the user to paste the prompt into an LLM and save or split the response manually.

Generated sample brief files already exist in `projects/sample_project/00_brief/`.

### Prompt-Guided Agent Stages

The following stages are defined as prompts under `agents/prompts/`:

- Research brief
- Literature search
- Source collection
- Document ingestion
- Citation metadata
- Evidence extraction
- Synthesis matrix
- Gap analysis
- Manuscript outline
- Introduction and RRL writing
- Results interpretation
- Results writing
- Discussion writing
- Citation audit
- Claim audit
- Style and formatting review
- Final assembly

These are not currently automated Python agents. They are detailed prompts that expect an LLM-capable environment to read local files and write local outputs.

### Paper Discovery Scripts

There is now one recommended discovery pipeline:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50 --skip-download
```

The main pipeline reads `01_literature_search/search_queries.md`, creates a query template if the file is missing, searches the newer multi-provider layer, normalizes records into the canonical candidate schema, merges them into `01_literature_search/candidate_papers.csv`, preserves existing human review fields, and logs to `logs/paper_discovery_log.md`.

It does not automatically run Unpaywall queue generation or PDF download. This is intentional. Legal PDF download remains explicit through `download_pdfs.py`, and only for legal OA `pdf_url` values already recorded in `02_sources/download_queue.csv`.

First-pass discovery queries can be generated locally from stage 00 brief outputs:

```powershell
python scripts\paper_discovery\generate_search_queries.py --project projects/sample_project --max-queries 24
```

This helper reads `00_brief/_ai_response.md`, `research_brief.md`, `research_questions.md`, `search_keywords.md`, and `source_strategy.md`. It is deterministic local code and does not call an AI API.

Candidate screening suggestions can be generated with:

```powershell
python scripts\paper_discovery\ai_screen_candidates.py --project projects/sample_project --limit 50 --batch-size 10
```

This is the first OpenAI-backed step. It reads `00_brief/research_brief.md` and `01_literature_search/candidate_papers.csv`, then writes AI-only suggestion columns. It must not overwrite `screening_status`, `human_decision`, or `human_notes`.

#### Multi-Provider Search Layer

Entry point:

```powershell
python -m scripts.paper_discovery.search "query text" --limit 20
```

Implemented providers:

- OpenAlex
- Crossref
- Semantic Scholar
- PubMed
- Europe PMC
- arXiv
- CORE

Capabilities:

- Normalizes provider records into the shared `Paper` dataclass.
- Deduplicates by DOI, PMID, PMCID, arXiv ID, exact normalized title/year, and high-confidence fuzzy title match.
- Ranks papers using query overlap, abstract overlap, citation counts, recency, full-text availability, and biomedical-provider boost.
- Allows selected providers with `--providers`.
- Allows year bounds with `--year-from` and `--year-to`.
- Exports CSV with `--export`.
- Continues returning partial results if one provider fails.

#### Legacy Archive

The old OpenAlex-first scripts are archived under:

```text
scripts/paper_discovery/legacy/
```

Archived scripts:

- `run_discovery_pipeline_legacy.py`
- `search_openalex.py`
- `enrich_crossref.py`
- `find_oa_pdfs.py`

They are retained for reference only and are not the recommended workflow.

## Discovery Data Models and Schemas

### Shared `Paper` Model

The normalized multi-provider model lives in:

```text
scripts/paper_discovery/models/paper.py
```

It includes:

- title, abstract, authors, year, publication date
- journal/source and publisher
- DOI, PMID, PMCID, arXiv ID, Semantic Scholar ID, OpenAlex ID, CORE ID
- landing page URL, PDF URL, OA status, license
- source provider and source provider list
- citation, reference, and influential citation counts
- fields of study, keywords, publication types
- raw provider payloads
- computed ranking score

### Canonical Candidate CSV Schema

The schema mismatch has been patched by adding:

```text
scripts/paper_discovery/candidate_schema.py
```

Canonical columns:

```csv
candidate_id,title,authors,year,publication_date,journal_or_repository,publisher,source_type,database_or_source,source_providers,search_query,doi,pmid,pmcid,arxiv_id,semantic_scholar_id,openalex_id,core_id,url,pdf_url,is_open_access,oa_status,license,abstract,keywords,fields_of_study,publication_types,citation_count,reference_count,influential_citation_count,ranking_score,access_type,screening_status,screening_reason,human_decision,human_notes,metadata_warnings,date_added,date_updated
```

Rules:

- New rows default to `screening_status=unscreened`.
- `human_decision` and `human_notes` default to blank.
- Existing human review fields are preserved during merge.
- `candidate_id` is generated from DOI first, then PMID, PMCID, arXiv ID, OpenAlex ID, Semantic Scholar ID, CORE ID, and finally title/year.
- Semicolon-separated values are used for provider and list-like fields.
- Missing unknown values remain blank.
- Abstracts are preserved when available but are not fabricated.

Adapters now exist for:

- legacy `search_openalex.py` rows
- multi-provider `Paper` dataclass records
- older compact provider export rows

The direct multi-provider export command now writes the canonical candidate schema by default:

```powershell
python -m scripts.paper_discovery.search "query text" --export projects/sample_project/01_literature_search/candidate_papers.csv
```

Use `--export-format provider` for the older compact export.

## Configuration and Environment

Dependencies:

```text
requests
pandas
PyYAML
python-slugify
tqdm
pytest
```

Configuration files:

- `scripts/paper_discovery/config.example.yaml`
- optional local `scripts/paper_discovery/config.yaml`
- `.env.example`

Secret-bearing local files are intentionally ignored by git:

- `scripts/paper_discovery/config.yaml`
- `.env`
- `.env.local`
- `*.key`
- `*.pem`

Do not commit real API keys.

Supported environment variables include:

- `OPENALEX_API_KEY`
- `SEMANTIC_SCHOLAR_API_KEY`
- `NCBI_API_KEY`
- `NCBI_TOOL`
- `CONTACT_EMAIL`
- `CORE_API_KEY`
- `CROSSREF_EMAIL`
- `CROSSREF_PLUS_API_KEY`
- `UNPAYWALL_EMAIL`
- `ENABLE_OPENALEX`
- `ENABLE_CROSSREF`
- `ENABLE_UNPAYWALL`
- `ENABLE_SEMANTIC_SCHOLAR`
- `ENABLE_PUBMED`
- `ENABLE_EUROPE_PMC`
- `ENABLE_ARXIV`
- `ENABLE_CORE`

## Tests

Current test files:

```text
tests/test_candidate_schema.py
tests/test_discovery_pipeline.py
tests/test_provider_layer.py
tests/test_secret_protection.py
```

Coverage includes:

- Canonical candidate schema columns, defaults, and stable candidate ID generation.
- Adapters for legacy OpenAlex rows, multi-provider `Paper` records, and compact provider exports.
- Candidate merge behavior, including DOI/title-year deduplication and preservation of human review fields.
- Main discovery pipeline import and missing-query template behavior.
- Main discovery pipeline candidate CSV output using mocked provider results.
- Partial pipeline results when a query/provider call fails.
- Semantic Scholar, PubMed, Europe PMC, arXiv, and CORE provider parsing.
- Deduplication across DOI, PMID, and arXiv ID.
- `.env.example` variable coverage.
- `.gitignore` protection for `scripts/paper_discovery/config.yaml`, `.env`, `.env.local`, `*.key`, and `*.pem`.

The tests do not currently cover:

- Real network calls to scholarly APIs.
- Real project discovery runs with live credentials.
- Archived legacy script behavior.
- Unpaywall queue generation from live records.
- PDF download behavior.
- Live OpenAI API screening calls.
- Prompt file output validation.

## Known Gaps

Current AI/API gaps:

- `ai_screen_candidates.py` calls the OpenAI Responses API for candidate screening suggestions only.
- No general-purpose structured LLM client exists yet.
- No persistent AI run log exists.
- The screening script uses a JSON schema request, but no shared Pydantic model exists for AI outputs.
- No automatic parsing of `_ai_response.md` into stage 00 files.
- Prompt stages are hard-coded to `projects/sample_project/`.
- Legacy OpenAlex-first scripts are archived for reference and should not be used as the main workflow.
- No local PDF or HTML to markdown converter is implemented.
- No automated evidence extraction from PDFs or markdown is implemented.
- No human review workflow is encoded for accepting or rejecting AI screening suggestions.
- No caching layer exists for provider responses or LLM responses.
- Cost/token reporting and batch resume ergonomics are still minimal.

## Recommended First AI Integration

The first AI integration should target paper discovery, not full manuscript writing.

Reason:

- Discovery has bounded inputs and outputs.
- Existing scripts already handle deterministic provider work.
- AI can add value by generating queries and explaining relevance.
- Bad AI behavior can be contained if suggestions are separated from accepted screening decisions.

### Proposed Scope

Add AI assistance for:

1. Query generation from `00_brief/`.
2. Query expansion into provider-specific variants.
3. Candidate relevance review from normalized metadata.
4. Screening suggestions with explicit reasons.
5. Metadata conflict notes where provider records disagree.

Current implementation status: candidate relevance review and screening suggestions are implemented as `scripts/paper_discovery/ai_screen_candidates.py`. Query generation is still deterministic local code, not an AI API call.

Do not initially add:

- Automatic inclusion or exclusion without human review.
- Automatic manuscript drafting.
- Automatic unsupported citation generation.
- Automatic PDF downloading beyond current OA queue rules.

### Suggested Output Files

For AI discovery work, add outputs under:

```text
projects/sample_project/01_literature_search/
```

Suggested files:

- `ai_query_plan.md`
- `ai_query_variants.csv`
- `ai_screening_suggestions.csv`
- `ai_discovery_run_log.md`

Suggested `ai_screening_suggestions.csv` fields:

```csv
candidate_id,title,doi,source_providers,ai_relevance_label,ai_confidence,ai_reason,suggested_action,metadata_warnings,human_decision,human_notes
```

Suggested labels:

- `highly_relevant`
- `possibly_relevant`
- `background_only`
- `out_of_scope`
- `insufficient_metadata`

Suggested actions:

- `screen_full_text`
- `keep_for_background`
- `exclude_after_human_review`
- `needs_metadata_check`
- `needs_query_followup`

### Suggested Implementation Files

Add a small AI integration layer rather than embedding provider logic in LLM code:

```text
scripts/
  ai/
    __init__.py
    client.py
    schemas.py
    prompts.py
    logging.py

scripts/
  paper_discovery/
    ai_query_generation.py
    ai_screen_candidates.py
```

Suggested responsibilities for a future shared AI layer:

- `client.py`: wraps the selected LLM provider, environment variables, retries, and JSON response validation.
- `schemas.py`: contains typed output schemas for query plans and screening suggestions.
- `prompts.py`: stores prompt templates as versioned strings or loads markdown templates.
- `logging.py`: writes model, prompt version, input file hashes, output file paths, and errors.
- `ai_query_generation.py`: reads `00_brief/`, writes query plan and query variants.
- `ai_screen_candidates.py`: already reads canonical candidate CSV and writes AI suggestions only; it can later be refactored to use a shared client.

### Suggested Environment Variables

Add later when AI integration begins:

```text
OPENAI_API_KEY=
OPENAI_MODEL=
OPENAI_DISCOVERY_MODEL=
AI_MAX_CANDIDATES_PER_BATCH=
AI_DRY_RUN=true
```

Current screening default:

```text
AI_SCREENING_MODEL=gpt-5-nano
```

The API key belongs in the shell environment or a local ignored `.env` file. Do not commit real API keys.

## Recommended Technical Sequence

1. Run the main discovery pipeline against a real project query set and inspect canonical `candidate_papers.csv`.
2. Decide whether legal OA queue generation should be rebuilt around the canonical schema or kept as a manual/legacy step.
3. Add AI query generation in dry-run mode that writes prompts and expected output paths without calling an API.
4. Add an LLM client with structured JSON output and tests using fake responses.
5. Add AI candidate screening suggestions.
6. Keep human decisions in separate fields from AI suggestions.
7. Add README instructions for the AI-assisted discovery mode.

## Current Best Next Task

Before calling an AI API, run `run_discovery_pipeline.py` on real search queries and review the resulting canonical `candidate_papers.csv`. The next implementation step can then add AI query generation or AI screening suggestions without changing the discovery foundation again.
