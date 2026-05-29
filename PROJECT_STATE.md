# Project State

Date reviewed: 2026-05-29

This repository is a local, file-based academic research workflow. It is currently strongest at defining a cautious staged process and partially automating paper discovery, AI-assisted query generation, candidate screening, controlled legal OA PDF queueing/downloading, metadata checking, evidence extraction, Stage 06 synthesis, Stage 07 gap analysis, Stage 07B project-context refinement, Stage 08 outline generation, Stage 08B human input checkpointing, and Stage 10A statistical results ingestion/interpretation. It is not yet an autonomous research agent or manuscript writer.

## Current Purpose

The project helps turn study notes, local source files, and statistical outputs into a structured manuscript workflow. The sample project is about predicting Radiologic Technologist Licensure Examination performance and licensure success from clustered academic grades and pre-board grades per cluster across batches.

The workflow is intentionally conservative:

- It keeps intermediate artifacts in project folders.
- It avoids inventing citations, papers, metadata, statistics, and conclusions.
- It separates search planning, source collection, ingestion, metadata extraction, evidence extraction, synthesis, drafting, and audits.
- It treats missing information as `To be confirmed.`
- It permits stable local paper IDs for manually supplied no-DOI sources, but those IDs must be propagated consistently through metadata, evidence, synthesis, and gap-analysis outputs.

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
- `scripts/ai/`: shared OpenAI Responses API client, structured schemas, prompt builders, and concise AI run logging for bounded local AI scripts.
- `scripts/citation_metadata/`: deterministic citation metadata extraction plus optional AI checking from local markdown and project CSVs.
- `scripts/document_ingestion/`: local PDF-to-markdown conversion helpers.
- `scripts/evidence_extraction/`: AI-assisted evidence extraction from local markdown and verified metadata.
- `scripts/synthesis/`: AI-assisted Stage 06 synthesis from extracted evidence and paper summaries.
- `scripts/gap_analysis/`: AI-assisted Stage 07 gap analysis from synthesis outputs.
- `scripts/project_update/`: AI-assisted Stage 07B project-context refinement for outline and writing handoff.
- `scripts/outline/`: AI-assisted Stage 08 manuscript and section outline generation.
- `scripts/human_input/`: deterministic Stage 08B human input packet building and answer application.
- `scripts/results/`: deterministic Stage 10A statistical results ingestion and AI-assisted interpretation notes from supplied local outputs.
- `scripts/paper_discovery/legacy/`: archived OpenAlex-first discovery scripts retained for reference only.
- `tests/`: provider, schema, pipeline, shared AI helper, AI query generation, AI screening, queue builder, downloader, ingestion, metadata, evidence extraction, synthesis, gap-analysis, project-context update, and secret-protection tests.

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

Most later writing/audit stages remain prompt-guided. Stage 07 gap analysis, Stage 07B project-context refinement, Stage 08 outline generation, Stage 08B human input checkpointing, and Stage 10A statistical results interpretation now have bounded Python scripts that write structured intermediate outputs before drafting.

### Paper Discovery Scripts

There is now one recommended discovery pipeline:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50 --skip-download
```

The main pipeline reads `01_literature_search/search_queries.md`, creates a query template if the file is missing, searches the newer multi-provider layer, normalizes records into the canonical candidate schema, merges them into `01_literature_search/candidate_papers.csv`, preserves existing human review fields, and logs to `logs/paper_discovery_log.md`.

It does not automatically run Unpaywall queue generation or PDF download. This is intentional. Legal PDF download remains explicit through `build_download_queue_from_ai.py` and `download_pdfs.py`, and only for legal OA `pdf_url` values recorded in `02_sources/download_queue.csv`.

Current AI-assisted legal OA workflow:

```powershell
python -m scripts.paper_discovery.run_discovery_pipeline --project projects/sample_project --max-results 50 --skip-download
python -m scripts.paper_discovery.ai_screen_candidates --project projects/sample_project --limit 50 --batch-size 10
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant --overwrite
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant,possibly_relevant --overwrite
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant,possibly_relevant,background_only --actions screen_full_text,keep_for_background --overwrite
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant,possibly_relevant --overwrite
python -m scripts.paper_discovery.download_pdfs --project projects/sample_project
```

The queue builder reads AI tags directly from `01_literature_search/candidate_papers.csv`, writes `02_sources/download_queue.csv`, tag-specific review files, and `02_sources/download_queue_excluded.csv`, and does not modify candidate metadata. The downloader writes `02_sources/download_results/success.csv` and `failed.csv` for manual ingestion decisions. AI labels are prioritization suggestions only, not final inclusion decisions.

First-pass discovery queries can be generated locally from stage 00 brief outputs:

```powershell
python scripts\paper_discovery\generate_search_queries.py --project projects/sample_project --max-queries 24
```

This helper reads `00_brief/_ai_response.md`, `research_brief.md`, `research_questions.md`, `search_keywords.md`, and `source_strategy.md`. It is deterministic local code and does not call an AI API.

AI-assisted query generation is implemented as:

```powershell
python -m scripts.paper_discovery.ai_query_generation --project projects/sample_project --limit 40 --dry-run
python -m scripts.paper_discovery.ai_query_generation --project projects/sample_project --limit 40
python -m scripts.paper_discovery.ai_query_generation --project projects/sample_project --limit 40 --apply
```

It uses `scripts/ai/` to generate a query plan and provider-specific query variants from Stage 00 local brief files. It writes `01_literature_search/ai_query_plan.md`, `01_literature_search/ai_query_variants.csv`, `01_literature_search/search_queries_ai.md`, and `logs/ai_query_generation_log.md`. These are search suggestions only, not source records. The deterministic discovery pipeline still owns provider search, normalization, deduplication, and candidate CSV creation.

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

## Document Ingestion and Citation Metadata

Text-bearing PDFs can be converted locally:

```powershell
python -m scripts.document_ingestion.pdf_to_markdown --project projects/sample_project
```

This writes raw markdown, cleaned markdown, `03_markdown/ingestion_manifest.csv`, and `03_markdown/ingestion_log.md`. It does not OCR scanned PDFs or interpret evidence.

First-pass citation metadata can be generated deterministically:

```powershell
python -m scripts.citation_metadata.extract_metadata --project projects/sample_project --overwrite
```

This reads local markdown plus candidate/download metadata and writes `04_metadata/metadata_table.csv`, `citation_key_map.csv`, `references_apa7.md`, `references.bib`, and `metadata_issues.md`. Unknown or unresolved fields are marked `To be confirmed.`

Optional AI checking now exists for Stage 04 metadata:

```powershell
python -m scripts.citation_metadata.ai_check_metadata --project projects/sample_project --limit 19
```

The AI checker requires `OPENAI_API_KEY` and sends each metadata row plus its corresponding cleaned markdown to the OpenAI Responses API using a strict JSON schema. It is instructed to use only the supplied local evidence, revise fields only when supported or contradicted by the markdown, preserve local file paths, and keep unresolved fields as `To be confirmed.` It writes checked outputs separately:

```text
projects/sample_project/04_metadata/metadata_table_ai_checked.csv
projects/sample_project/04_metadata/metadata_ai_check_report.csv
projects/sample_project/04_metadata/citation_key_map_ai_checked.csv
projects/sample_project/04_metadata/references_apa7_ai_checked.md
projects/sample_project/04_metadata/references_ai_checked.bib
projects/sample_project/04_metadata/metadata_ai_check_log.md
```

Use `--apply` only after inspecting the checked files; it backs up and replaces `metadata_table.csv`.

## Evidence Extraction

Stage 05 now has an OpenAI-backed local script:

```powershell
python -m scripts.evidence_extraction.ai_extract_evidence --project projects/sample_project --limit 19 --overwrite
```

The script prefers `04_metadata/metadata_table_ai_checked.csv` when present, otherwise `04_metadata/metadata_table.csv`. It reads Stage 00 brief context, metadata rows, and each row's local cleaned markdown file. It sends one paper at a time to the OpenAI Responses API using a strict JSON schema and defaults to `AI_EVIDENCE_MODEL=gpt-5-mini`, which is intentionally stronger than the screening and metadata defaults because evidence extraction reads longer paper text and extracts methods, variables, findings, limitations, relevance notes, and source locations.

Outputs:

```text
projects/sample_project/05_evidence_extraction/evidence_table.csv
projects/sample_project/05_evidence_extraction/paper_summaries/
projects/sample_project/05_evidence_extraction/extraction_log.md
```

The evidence table uses the prompt contract columns exactly:

```csv
paper_id,citation_key,theme,study_design,population,variables,key_finding,relevance_to_current_study,source_location,confidence_rating,notes
```

The script is constrained to local markdown and metadata only. It must mark unverifiable details as `To be confirmed.` and does not perform synthesis or manuscript drafting.

## Synthesis

Stage 06 now has an OpenAI-backed local script:

```powershell
python -m scripts.synthesis.ai_build_synthesis --project projects/sample_project --dry-run
python -m scripts.synthesis.ai_build_synthesis --project projects/sample_project --overwrite
```

It uses `scripts/ai/` and reads Stage 05 evidence outputs rather than raw PDFs by default. Inputs are `05_evidence_extraction/evidence_table.csv`, available files under `05_evidence_extraction/paper_summaries/`, and brief/metadata context when present. It writes:

```text
projects/sample_project/06_synthesis/synthesis_matrix.csv
projects/sample_project/06_synthesis/theme_matrix.md
projects/sample_project/06_synthesis/literature_map.md
projects/sample_project/06_synthesis/synthesis_notes.md
projects/sample_project/logs/ai_synthesis_log.md
```

This is structured intermediate synthesis only. It must not invent evidence or citations, must keep uncertain information as `To be confirmed.`, and does not draft the manuscript.

The implementation has been exercised with mocked AI responses and is considered a good bounded handoff from Stage 05 into Stage 06. It validates citation keys and paper IDs against supplied inputs, coerces invalid enum values to `to_be_confirmed`, writes blocked notes when Stage 05 evidence is missing, supports dry runs without an OpenAI key, and refuses to overwrite existing synthesis outputs unless `--overwrite` is supplied.

## Gap Analysis

Stage 07 now has an OpenAI-backed local script:

```powershell
python -m scripts.gap_analysis.ai_gap_analysis --project projects/sample_project --dry-run
python -m scripts.gap_analysis.ai_gap_analysis --project projects/sample_project --overwrite
```

It uses `scripts/ai/` and reads Stage 06 synthesis outputs, plus available Stage 00 brief, Stage 05 evidence, and Stage 04 metadata context. Inputs are `06_synthesis/synthesis_matrix.csv`, `theme_matrix.md`, `literature_map.md`, and `synthesis_notes.md`. It writes:

```text
projects/sample_project/07_gap_analysis/research_gap_analysis.md
projects/sample_project/07_gap_analysis/study_contribution.md
projects/sample_project/07_gap_analysis/problem_statement_refined.md
projects/sample_project/07_gap_analysis/gap_matrix.csv
projects/sample_project/logs/ai_gap_analysis_log.md
```

This is structured intermediate research positioning only. It must not draft the Introduction, Review of Related Literature, Discussion, or full manuscript. It validates gap classifications, contribution types, caution levels, and recommended uses; coerces unsupported enum values to `to_be_confirmed`; writes blocked notes when Stage 06 synthesis is missing; supports dry runs without an OpenAI key; and refuses to overwrite existing Stage 07 outputs unless `--overwrite` is supplied.

## Project Context Update

Stage 07B now has an OpenAI-backed local script:

```powershell
python -m scripts.project_update.ai_update_project_context --project projects/sample_project --dry-run
python -m scripts.project_update.ai_update_project_context --project projects/sample_project --overwrite
```

It uses `scripts/ai/` and reads the original Stage 00 brief files, Stage 06 synthesis outputs, and Stage 07 gap-analysis outputs. Optional context comes from Stage 05 evidence and Stage 04 metadata when present. It writes refined project-context files without modifying original Stage 00 files by default:

```text
projects/sample_project/00_brief/research_brief_refined.md
projects/sample_project/00_brief/research_questions_refined.md
projects/sample_project/00_brief/writing_scope_refined.md
projects/sample_project/00_brief/agent_instructions_refined.md
projects/sample_project/08_outline/_context_for_outline.md
projects/sample_project/09_drafts/_context_for_writers.md
projects/sample_project/00_brief/project_context_update_summary.md
projects/sample_project/00_brief/project_context_changes.csv
projects/sample_project/logs/ai_project_context_update_log.md
```

This is a structured pass-through feedback loop from synthesis/gap analysis into outline and writing. It updates framing and downstream instructions; it does not draft manuscript prose. It refuses to overwrite refined outputs unless `--overwrite` is supplied, writes blocked status when Stage 07 is missing, supports dry runs without an OpenAI key, validates project-context change rows, sanitizes unsupported citation markers, and preserves original Stage 00 files unless `--overwrite --apply-to-originals` is explicitly used.

## Outline Generation

Stage 08 now has an OpenAI-backed local script:

```powershell
python -m scripts.outline.ai_build_outline --project projects/sample_project --dry-run
python -m scripts.outline.ai_build_outline --project projects/sample_project --overwrite
```

It uses `scripts/ai/` and reads refined Stage 00/Stage 07B context first when present, then falls back to original Stage 00 files. It also reads Stage 06 synthesis, Stage 07 gap-analysis outputs, study notes, optional statistical results/raw tables, and supporting metadata/evidence context. It writes:

```text
projects/sample_project/08_outline/manuscript_outline.md
projects/sample_project/08_outline/introduction_outline.md
projects/sample_project/08_outline/rrl_outline.md
projects/sample_project/08_outline/methodology_outline.md
projects/sample_project/08_outline/results_outline.md
projects/sample_project/08_outline/discussion_outline.md
projects/sample_project/08_outline/outline_map.csv
projects/sample_project/08_outline/outline_readiness_checklist.md
projects/sample_project/logs/ai_outline_log.md
```

This is structured outline planning only. It must not draft manuscript prose, invent citations, invent methods details, or claim study results. If statistical results or raw tables are missing, Results and result-dependent Discussion items are marked blocked, partial, or `To be confirmed.` It validates outline readiness statuses, backs up existing Stage 08 outputs on overwrite, supports dry runs without an OpenAI key, and sanitizes unsupported citation markers.

## Human Input Checkpoint

Stage 08B now has deterministic local scripts:

```powershell
python -m scripts.human_input.build_input_packet --project projects/sample_project
python -m scripts.human_input.apply_input_packet --project projects/sample_project
```

`build_input_packet.py` scans Stage 08 outlines and available project context for missing human-dependent details, then writes:

```text
projects/sample_project/human_input/human_input_packet.md
projects/sample_project/human_input/human_input_questions.csv
projects/sample_project/human_input/human_input_answers.md
projects/sample_project/human_input/human_input_status.csv
projects/sample_project/logs/human_input_packet_log.md
```

`apply_input_packet.py` parses completed QID answer sections and writes explicit local inputs for later stages:

```text
projects/sample_project/input/human_confirmed_context.md
projects/sample_project/input/methodology_details.md
projects/sample_project/input/statistical_results.md
projects/sample_project/input/results_availability.md
projects/sample_project/human_input/human_input_apply_report.md
projects/sample_project/logs/human_input_apply_log.md
```

This checkpoint is mostly deterministic and file-based. It does not invent human-only details; blank answers remain unanswered, `To be confirmed` is preserved, and `N/A` is tracked as not applicable. Optional AI use is limited to question wording/grouping and is not used in tests.

## Statistical Results Ingestion and Interpretation

Stage 10A now has a deterministic ingestion script and an OpenAI-backed interpretation script:

```powershell
python -m scripts.results.ingest_statresults --project projects/sample_project --overwrite
python -m scripts.results.ai_interpret_results --project projects/sample_project --dry-run
python -m scripts.results.ai_interpret_results --project projects/sample_project --overwrite
```

`ingest_statresults.py` reads AI-readable files from `projects/sample_project/statresults/` and optionally `input/raw_tables/`, then writes:

```text
projects/sample_project/input/statistical_results_manifest.csv
projects/sample_project/input/statistical_results_compiled.md
projects/sample_project/input/results_availability.md
projects/sample_project/logs/statresults_ingest_log.md
```

`ai_interpret_results.py` uses `scripts/ai/` to map supplied statistical outputs to study objectives without drafting polished Results prose. It reads human-confirmed context, methodology details, results availability, compiled statistical outputs, and Stage 08 Results/Discussion outlines. It writes:

```text
projects/sample_project/09_drafts/results/results_interpretation_notes.md
projects/sample_project/09_drafts/results/results_table_notes.md
projects/sample_project/09_drafts/results/missing_results_to_confirm.md
projects/sample_project/09_drafts/results/results_by_objective.csv
projects/sample_project/09_drafts/results/statistical_findings_matrix.csv
projects/sample_project/logs/ai_results_interpretation_log.md
```

This stage creates result mapping, interpretation notes, table notes, and missing-results checklists only. It does not run statistical analyses, invent statistical values, infer significance without supplied support, draft final Results prose, or draft Discussion.

## Sample Project Citation Repair

After manually supplied PDFs/markdowns were added, several downstream artifacts had correct citation keys but unresolved or mismatched `paper_id` values. A manual repair pass normalized those project artifacts without changing source evidence content.

Repair log:

```text
projects/sample_project/logs/citation_key_repair_log.md
```

Repairs performed:

- Assigned stable local paper IDs for no-DOI local sources:
  - `Cabatingan2024AdmissionTestProfessionalLicensure` -> `local:admission-test-professional-licensure`
  - `Tulud2023PerceivedFactorsPerformanceGraduates` -> `local:perceived-factors-performance-graduates`
  - `Barymon2022PredictionRadiographyCertificationExamination` -> `local:prediction-radiography-certification-examination-scores`
- Restored exact synthesis citation keys for DOI-backed rows involving `Rabinoa2025MockBoardExaminationResult` and `ChristineGouveia2024PredictiveValidityHesiRadiography`.
- Renamed affected Stage 05 paper summary files away from `to-be-confirmed_*` and updated their Paper ID headers.
- Repaired stale `C:\MEGA Cloud\...` metadata path prefixes to the current workspace path under `C:\MEGASync\...`.
- Removed stale Stage 06/07 validation warnings caused by prior citation-key mismatches.
- Wrote `.citation_repair.bak` and `.path_repair.bak` backups beside touched files.

Current manual verification:

- No exact `To be confirmed.` values remain in `paper_id`, `citation_key`, or `supporting_synthesis_source` fields across the Stage 04 metadata tables/maps, Stage 05 evidence table, Stage 06 synthesis matrix, and Stage 07 gap matrix.
- Current `local_source_file` and `local_markdown_file` paths in `metadata_table_ai_checked.csv` resolve on disk.
- No current Stage 05 summary markdown files start with `to-be-confirmed_`; only repair backups preserve the old filenames.

## Configuration and Environment

Dependencies:

```text
requests
pandas
PyYAML
python-slugify
tqdm
pytest
pypdf
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
- `OPENAI_API_KEY`
- `AI_SCREENING_MODEL`
- `AI_METADATA_MODEL`
- `AI_EVIDENCE_MODEL`
- `AI_SYNTHESIS_MODEL`
- `AI_DISCOVERY_MODEL`
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
tests/test_ai_build_synthesis.py
tests/test_ai_check_metadata.py
tests/test_ai_client.py
tests/test_ai_extract_evidence.py
tests/test_ai_gap_analysis.py
tests/test_ai_logging.py
tests/test_ai_query_generation.py
tests/test_ai_schemas.py
tests/test_ai_screen_candidates.py
tests/test_build_download_queue_from_ai.py
tests/test_candidate_schema.py
tests/test_discovery_pipeline.py
tests/test_download_pdfs.py
tests/test_extract_metadata.py
tests/test_generate_search_queries.py
tests/test_provider_layer.py
tests/test_pdf_to_markdown.py
tests/test_secret_protection.py
```

Coverage includes:

- Canonical candidate schema columns, defaults, and stable candidate ID generation.
- Adapters for legacy OpenAlex rows, multi-provider `Paper` records, and compact provider exports.
- Candidate merge behavior, including DOI/title-year deduplication and preservation of human review fields.
- Main discovery pipeline import and missing-query template behavior.
- Main discovery pipeline candidate CSV output using mocked provider results.
- Partial pipeline results when a query/provider call fails.
- Shared AI client payload construction, schema definitions, and run-log writing.
- AI query generation prompt/request behavior, dry-run behavior, and output contracts.
- AI screening helper behavior without live OpenAI calls.
- AI metadata checking request construction, local-evidence guardrails, revision application, checked output files, and dry-run behavior without live OpenAI calls.
- AI evidence extraction request construction, local-evidence guardrails, metadata source preference, output files, evidence table schema, and dry-run behavior without live OpenAI calls.
- AI synthesis request construction, dry-run behavior, blocked-output behavior, overwrite/backups, output file contracts, enum normalization, and citation/paper-ID guardrails without live OpenAI calls.
- AI gap-analysis request construction, dry-run behavior, blocked-output behavior, partial Stage 06 behavior, overwrite/backups, output file contracts, enum normalization, and citation-marker guardrails without live OpenAI calls.
- Manual sample-project citation repair was verified outside live API calls by checking `paper_id`, `citation_key`, and `supporting_synthesis_source` fields across Stage 04-07 CSV artifacts.
- AI-tag download queue filtering, exclusions, tag-specific files, dry-run behavior, and overwrite protection.
- PDF download success/failure behavior with mocked HTTP responses, SHA-256 hashing, dry-run behavior, tag filtering, and overwrite protection.
- Deterministic citation metadata extraction output contract, candidate matching, DOI fallback, overwrite protection, dry-run behavior, and conservative filename matching.
- PDF-to-markdown ingestion success, failed no-text PDFs, dry-run behavior, and overwrite protection.
- Semantic Scholar, PubMed, Europe PMC, arXiv, and CORE provider parsing.
- Deduplication across DOI, PMID, and arXiv ID.
- `.env.example` variable coverage.
- `.gitignore` protection for `scripts/paper_discovery/config.yaml`, `.env`, `.env.local`, `*.key`, and `*.pem`.

The tests do not currently cover:

- Real network calls to scholarly APIs.
- Real project discovery runs with live credentials.
- Archived legacy script behavior.
- Live Unpaywall queue generation from real records.
- Live PDF download behavior against publisher/repository hosts.
- Live OpenAI API screening calls.
- Live OpenAI API metadata checking calls.
- Live OpenAI API evidence extraction calls.
- Live OpenAI API synthesis calls.
- Live OpenAI API gap-analysis calls.
- Live OpenAI API outline-generation calls.
- Prompt file output validation.
- Automated tests for manual citation-repair scripts; the current repair is logged as a project-specific maintenance action rather than a reusable command.

## Known Gaps

Current AI/API boundaries and gaps:

- `ai_query_generation.py` calls the OpenAI Responses API for query plans and provider-specific search variants only.
- `ai_screen_candidates.py` calls the OpenAI Responses API for candidate screening suggestions only.
- `ai_check_metadata.py` calls the OpenAI Responses API to check first-pass citation metadata against local markdown evidence.
- `ai_extract_evidence.py` calls the OpenAI Responses API to extract structured evidence from local markdown.
- `ai_build_synthesis.py` calls the OpenAI Responses API to organize Stage 05 evidence into Stage 06 synthesis artifacts, not manuscript prose.
- `ai_gap_analysis.py` calls the OpenAI Responses API to organize Stage 06 synthesis into Stage 07 research-positioning artifacts, not manuscript prose.
- `ai_update_project_context.py` calls the OpenAI Responses API to refine Stage 00 project context from Stage 06/07 outputs for outline/writing handoff, not manuscript prose.
- `ai_build_outline.py` calls the OpenAI Responses API to create Stage 08 outline artifacts from refined context, synthesis, gap analysis, and available results context, not manuscript prose.
- `ai_interpret_results.py` calls the OpenAI Responses API to map supplied statistical outputs to objectives and table notes, not polished Results prose or Discussion.
- These OpenAI-backed scripts share `scripts/ai/` for client behavior, schemas, prompt text, and concise run metadata logs. Logs record paths and counts, not full paper text.
- `build_download_queue_from_ai.py` turns AI tags into a legal OA download queue without treating them as human inclusion decisions.
- `download_pdfs.py` downloads only queued rows with explicit PDF URLs and records success only when a local file exists.
- The AI layer is intentionally lightweight and schema-dict based; no shared Pydantic model exists for AI outputs.
- No automatic parsing of `_ai_response.md` into stage 00 files.
- Prompt stages are hard-coded to `projects/sample_project/`.
- Legacy OpenAlex-first scripts are archived for reference and should not be used as the main workflow.
- Basic local PDF-to-markdown conversion is implemented in `scripts/document_ingestion/pdf_to_markdown.py` for text-bearing PDFs.
- First-pass deterministic citation metadata extraction is implemented in `scripts/citation_metadata/extract_metadata.py`.
- Optional AI metadata checking is implemented in `scripts/citation_metadata/ai_check_metadata.py`.
- AI evidence extraction from cleaned markdown is implemented in `scripts/evidence_extraction/ai_extract_evidence.py`.
- AI-assisted Stage 06 synthesis is implemented in `scripts/synthesis/ai_build_synthesis.py` as structured intermediate outputs.
- AI-assisted Stage 07 gap analysis is implemented in `scripts/gap_analysis/ai_gap_analysis.py` as structured intermediate outputs.
- AI-assisted Stage 07B project context refinement is implemented in `scripts/project_update/ai_update_project_context.py` as a structured pass-through after gap analysis.
- AI-assisted Stage 08 outline generation is implemented in `scripts/outline/ai_build_outline.py` as structured intermediate outputs.
- Stage 08B human input collection and application is implemented in `scripts/human_input/build_input_packet.py` and `scripts/human_input/apply_input_packet.py`.
- Stage 10A statistical results ingestion and interpretation is implemented in `scripts/results/ingest_statresults.py` and `scripts/results/ai_interpret_results.py`.
- Results writing, methodology writing, discussion writing, audits, and final assembly remain prompt-guided unless implemented later.
- No human review workflow is encoded for accepting or rejecting AI screening suggestions.
- No caching layer exists for provider responses or LLM responses.
- Cost/token reporting and batch resume ergonomics are still minimal.
- Manual citation/path repairs are currently project-specific maintenance steps. If this recurs across projects, add a reusable audit/repair script for metadata path validity, no-DOI local paper IDs, and citation-key propagation.

## Implemented AI Integration Path

The first AI integration path targeted paper discovery, then extended the same bounded pattern through metadata checking, evidence extraction, synthesis, gap analysis, project-context refinement, and outline generation rather than full manuscript writing.

Reason:

- Discovery has bounded inputs and outputs.
- Existing scripts already handle deterministic provider work.
- AI can add value by generating queries, explaining relevance, checking local metadata, extracting evidence, organizing synthesis, structuring research positioning, feeding evidence-informed context into downstream instructions, and building auditable outlines before drafting.
- Bad AI behavior can be contained if suggestions are separated from accepted screening decisions.

### Implemented Scope

Implemented AI assistance now covers:

1. Query generation from `00_brief/`.
2. Query expansion into provider-specific variants.
3. Candidate relevance review from normalized metadata.
4. Screening suggestions with explicit reasons.
5. Metadata conflict notes where provider records disagree.
6. Metadata checking against local markdown.
7. Evidence extraction from cleaned local markdown.
8. Stage 06 synthesis from Stage 05 evidence outputs.
9. Stage 07 gap analysis from Stage 06 synthesis outputs.
10. Stage 07B project-context refinement from Stage 00, Stage 06, and Stage 07 outputs.
11. Stage 08 outline generation from refined context, synthesis, gap analysis, and available study/results context.
12. Stage 08B human input packet building and answer application before drafting.
13. Stage 10A statistical results ingestion and interpretation from `statresults/` and human-confirmed inputs.

Current implementation status: AI-assisted query generation and provider-specific query expansion are implemented as `scripts/paper_discovery/ai_query_generation.py`. Candidate relevance review and screening suggestions are implemented as `scripts/paper_discovery/ai_screen_candidates.py`. Controlled legal OA queue generation from AI tags is implemented as `scripts/paper_discovery/build_download_queue_from_ai.py`, and queued explicit PDF URLs can be downloaded with `scripts/paper_discovery/download_pdfs.py`. AI metadata checking against local markdown is implemented as `scripts/citation_metadata/ai_check_metadata.py`. AI evidence extraction is implemented as `scripts/evidence_extraction/ai_extract_evidence.py`. AI-assisted Stage 06 synthesis is implemented as `scripts/synthesis/ai_build_synthesis.py`. AI-assisted Stage 07 gap analysis is implemented as `scripts/gap_analysis/ai_gap_analysis.py`. AI-assisted Stage 07B project context refinement is implemented as `scripts/project_update/ai_update_project_context.py`. AI-assisted Stage 08 outline generation is implemented as `scripts/outline/ai_build_outline.py`. Stage 08B human input checkpointing is implemented as `scripts/human_input/build_input_packet.py` and `scripts/human_input/apply_input_packet.py`. Stage 10A statistical results ingestion and interpretation is implemented as `scripts/results/ingest_statresults.py` and `scripts/results/ai_interpret_results.py`.

Do not add:

- Automatic inclusion or exclusion without human review.
- Automatic manuscript drafting.
- Automatic unsupported citation generation.
- Automatic PDF downloading beyond current OA queue rules.

### AI Discovery Output Files

For AI discovery work, outputs live under:

```text
projects/sample_project/01_literature_search/
```

Files:

- `ai_query_plan.md`
- `ai_query_variants.csv`
- `search_queries_ai.md`
- AI suggestion columns in `candidate_papers.csv`
- `logs/ai_query_generation_log.md`

AI screening is stored in AI-only candidate CSV columns rather than a separate accepted-decision file. Expected screening fields include:

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

### Implemented Shared AI Files

The shared AI layer keeps provider logic out of LLM-facing scripts:

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
  citation_metadata/
    ai_check_metadata.py
  evidence_extraction/
    ai_extract_evidence.py
  synthesis/
    ai_build_synthesis.py
  gap_analysis/
    ai_gap_analysis.py
  project_update/
    ai_update_project_context.py
  outline/
    ai_build_outline.py
  human_input/
    build_input_packet.py
    apply_input_packet.py
```

Current responsibilities:

- `client.py`: wraps the selected LLM provider, environment variables, retries, and JSON response validation.
- `schemas.py`: contains structured output schemas for query plans, screening suggestions, metadata checks, evidence extraction, synthesis, gap analysis, project-context updates, outline generation, and results interpretation.
- `prompts.py`: stores prompt templates as versioned strings or loads markdown templates.
- `logging.py`: writes model, prompt version, input file hashes, output file paths, and errors.
- `ai_query_generation.py`: reads `00_brief/`, writes query plan and query variants.
- `ai_screen_candidates.py`: reads canonical candidate CSV and writes AI suggestions only.
- `ai_check_metadata.py`: checks deterministic metadata against supplied markdown evidence.
- `ai_extract_evidence.py`: extracts Stage 05 evidence from local cleaned markdown.
- `ai_build_synthesis.py`: builds Stage 06 synthesis artifacts from Stage 05 evidence outputs.
- `ai_gap_analysis.py`: builds Stage 07 gap-analysis artifacts from Stage 06 synthesis outputs.
- `ai_update_project_context.py`: builds Stage 07B refined project-context files and downstream handoff context from Stage 00, Stage 06, and Stage 07 outputs.
- `ai_build_outline.py`: builds Stage 08 manuscript and section outlines from refined context, synthesis, gap analysis, and available results context.
- `build_input_packet.py` / `apply_input_packet.py`: build and apply Stage 08B human answer packets before drafting.
- `ingest_statresults.py`: compiles AI-readable statistical outputs from `statresults/` into a local handoff.
- `ai_interpret_results.py`: maps supplied statistical outputs to objectives, table notes, and missing-results checklists.

### AI Environment Variables

Supported AI environment variables include:

```text
OPENAI_API_KEY=
AI_SCREENING_MODEL=gpt-5-nano
AI_METADATA_MODEL=gpt-5-nano
AI_EVIDENCE_MODEL=gpt-5-mini
AI_SYNTHESIS_MODEL=gpt-5-mini
AI_GAP_MODEL=gpt-5-mini
AI_PROJECT_UPDATE_MODEL=gpt-5-mini
AI_OUTLINE_MODEL=gpt-5-mini
AI_RESULTS_MODEL=gpt-5-mini
AI_DISCOVERY_MODEL=gpt-5-mini
```

The API key belongs in the shell environment or a local ignored `.env` file. Do not commit real API keys.

## Recommended Technical Sequence

1. Run or refresh the main discovery pipeline against a real project query set and inspect canonical `candidate_papers.csv`.
2. Run AI screening only as a suggestion layer and keep human decisions in separate fields.
3. Build the legal OA queue from accepted AI tags and manually inspect failed or missing-PDF rows.
4. Convert text-bearing PDFs to markdown and run deterministic metadata extraction.
5. Run AI metadata checking and apply only after reviewing checked outputs.
6. Run AI evidence extraction from local markdown.
7. Run AI synthesis from Stage 05 outputs, then manually review Stage 06 before gap analysis.
8. Run AI gap analysis from reviewed Stage 06 outputs, then manually review Stage 07 before context refinement.
9. Run `python -m scripts.project_update.ai_update_project_context --project projects/sample_project --overwrite`, then review refined Stage 00/context files.
10. Run `python -m scripts.outline.ai_build_outline --project projects/sample_project --overwrite`, then review Stage 08 outputs before Stage 09 writing.
11. Run `python -m scripts.human_input.build_input_packet --project projects/sample_project`, fill `projects/sample_project/human_input/human_input_answers.md`, then run `python -m scripts.human_input.apply_input_packet --project projects/sample_project`.
12. Place AI-readable statistical outputs in `projects/sample_project/statresults/`.
13. Run `python -m scripts.results.ingest_statresults --project projects/sample_project --overwrite`.
14. Run `python -m scripts.results.ai_interpret_results --project projects/sample_project --overwrite`, then review the Stage 10A notes under `09_drafts/results/`.
15. Keep prompt-guided writing and audits separate from AI intermediate-file generation.

## Current Best Next Task

Run the full implemented chain on a real project subset and review each intermediate artifact: discovery candidates, AI screening suggestions, legal OA queue, markdown ingestion, metadata, evidence extraction, Stage 06 synthesis, Stage 07 gap analysis, Stage 07B refined context, Stage 08 outlines, Stage 08B human-confirmed inputs, and Stage 10A statistical interpretation notes. The next development work should focus on bounded Results/Discussion writing support or human review ergonomics for accepting AI suggestions.
