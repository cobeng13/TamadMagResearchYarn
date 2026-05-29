# Research Agent

Research Agent is a local, file-based academic writing workflow for turning study notes, source documents, statistical outputs, and evidence tables into a structured manuscript draft. It is designed for cautious research writing: each stage reads local files, writes explicit intermediate artifacts, and avoids inventing sources, citations, statistics, findings, or conclusions.

The included sample project is focused on predicting Radiologic Technologist Licensure Examination success from academic performance and pre-board examination results, but the workflow can be adapted to other research topics by changing the project brief and prompts.

## What This Repository Can Do

This repository provides a staged research writer agent system that can:

- Convert rough study notes into a structured research brief, research questions, variables, inclusion criteria, search keywords, source strategy, writing scope, and downstream agent instructions.
- Build reproducible literature search plans and ready-to-run Boolean search strings for databases and repositories.
- Optionally run API-assisted paper discovery from local search queries using the multi-provider discovery layer.
- Organize candidate papers, included sources, excluded sources, download queues, and source notes without fabricating source records.
- Prepare local source folders for PDFs, HTML captures, and other source documents.
- Convert available source documents into raw and cleaned markdown for downstream reading.
- Extract citation metadata into APA 7 references, BibTeX entries, metadata tables, and citation key maps, with an optional AI check against local markdown evidence.
- Extract structured evidence from papers into per-paper summaries and a machine-readable evidence table using local markdown and verified metadata.
- Build synthesis matrices, theme maps, literature maps, and synthesis notes.
- Identify research gaps, refine the problem statement, and write a contribution statement.
- Produce an IMRaD-style manuscript outline, including Introduction, Review of Related Literature, Methodology, Results, Discussion, Conclusion, and Recommendations planning.
- Draft the Introduction and Review of Related Literature from verified local synthesis and citation metadata.
- Interpret user-supplied statistical outputs and prepare result-writing notes.
- Draft Results prose and table notes from verified statistical outputs.
- Draft Discussion, limitations, conclusion, and recommendation notes from verified results and literature synthesis.
- Audit citations against local metadata and evidence files.
- Audit claims against local evidence, synthesis, and statistical results.
- Review academic tone, APA 7 consistency, organization, headings, table and figure callouts, and final assembly readiness.
- Assemble an editable full manuscript draft from locally available draft sections and final-ready references.

## What It Does Not Do Automatically

This is not a fully automated web research bot or submission system. The prompt-agent workflow remains local and file-based by default. The repository also includes optional API-assisted paper discovery scripts under `scripts/paper_discovery/`; those scripts run only when you explicitly execute them.

- It does not automatically search the web unless a user explicitly asks an agent to browse in the current task or runs the paper discovery scripts.
- It does not download papers by default. The optional downloader only downloads legal open-access PDF URLs found through Unpaywall.
- It does not bypass publisher access controls, use Sci-Hub, or fetch illegal copies.
- It does not call OpenAI by default. The prompt agents generate or define prompts, but a user still runs most prompts in an LLM environment and saves the resulting files. Optional explicit scripts can call OpenAI for query generation, candidate screening, citation metadata checking, evidence extraction, synthesis, and gap analysis.
- It includes a basic local PDF-to-markdown converter for text-bearing PDFs, but scanned/image-only files and complex tables may still need manual review or OCR.
- It does not invent missing source metadata, citations, DOIs, URLs, statistics, sample sizes, p-values, coefficients, or conclusions.
- It does not run statistical analysis unless explicitly extended or instructed to do so.
- It does not submit, publish, email, or upload manuscripts.
- It does not currently include a dedicated Methodology Writer Agent. The workflow defines a standard manual methodology draft path: `projects/sample_project/09_drafts/methodology/methodology_draft.md`.

## Current Automation Status

The repository currently has two levels of automation:

- **Implemented local/API scripts**: the research brief helper creates a prompt file from study notes; paper discovery scripts can query scholarly APIs, normalize metadata, deduplicate/rank candidate papers, and write canonical candidate records; AI-assisted query generation and candidate screening are available; legal OA PDF queueing/downloading remains explicit; text-bearing PDFs can be converted to raw and cleaned markdown; deterministic citation metadata can be AI-checked against local markdown; cleaned markdown can be used for AI evidence extraction; Stage 05 evidence can be organized into Stage 06 synthesis artifacts; Stage 06 synthesis can be turned into Stage 07 gap-analysis artifacts.
- **Prompt-guided workflow stages**: source collection decisions, manual cleanup, drafting, outline creation, and audits are still specified by agent prompts. A user or LLM environment must run those prompts and save the requested files.

In practical terms, discovery, ingestion, metadata checking, evidence extraction, synthesis, and gap analysis now have bounded script support. Manuscript writing, statistical interpretation, outline creation, and final review are not autonomous.

### Shared AI Integration Layer

Optional OpenAI-backed scripts use `scripts/ai/` for the Responses API client, structured-output schemas, prompt builders, and concise run logs. This shared layer is used by AI query generation, candidate screening, citation metadata checking, evidence extraction, synthesis, and gap analysis.

The boundary remains conservative: deterministic scripts still own provider search, metadata normalization, deduplication, legal OA queueing/downloading, and local file creation. AI is bounded to suggestions, metadata checking against supplied markdown, structured evidence extraction from local files, structured synthesis from Stage 05 evidence, and structured research-positioning notes from Stage 06 synthesis. Human review fields remain separate from AI suggestion fields.

For a detailed implementation handoff, current gaps, and the implemented AI integration path, see:

```text
PROJECT_STATE.md
```

### Current AI-Assisted Workflow

The implemented AI layer is designed around intermediate artifacts, not autonomous manuscript writing. It can:

- Generate a query plan and provider-specific search variants from `00_brief/` files.
- Add AI-only candidate screening labels, reasons, confidence values, and suggested actions to canonical candidate records.
- Check deterministic citation metadata against supplied local markdown.
- Extract structured paper evidence from local cleaned markdown and verified metadata.
- Build Stage 06 synthesis artifacts from Stage 05 evidence rows and paper summaries.
- Build Stage 07 gap-analysis artifacts from Stage 06 synthesis outputs.

AI must not invent papers, DOIs, URLs, abstracts, author names, citation counts, PDFs, source text, findings, gap claims, or screening decisions. Any AI-written relevance decision remains a suggestion until a human accepts it, and synthesis/gap-analysis outputs remain intermediate evidence organization and research positioning rather than manuscript prose.

## Repository Layout

```text
research_agent/
  README.md
  PROJECT_STATE.md
  agents/
    research_brief_agent.py
    prompts/
      00_research_brief_agent.md
      01_literature_search_agent.md
      02_source_collection_agent.md
      03_document_ingestion_agent.md
      04_citation_metadata_agent.md
      05_evidence_extraction_agent.md
      06_synthesis_matrix_agent.md
      07_gap_analysis_agent.md
      08_outline_agent.md
      09_intro_rrl_writer_agent.md
      10_results_interpreter_agent.md
      11_results_writer_agent.md
      12_discussion_writer_agent.md
      13_citation_audit_agent.md
      14_claim_audit_agent.md
      15_style_formatting_agent.md
      16_final_assembly_agent.md
      _prompt_qc_report.md
      _prompt_repair_log.md
      _prompt_qc_issues.csv
  projects/
    sample_project/
      input/
      00_brief/
  scripts/
    ai/
      client.py
      schemas.py
      prompts.py
      logging.py
    paper_discovery/
      run_discovery_pipeline.py
      generate_search_queries.py
      ai_query_generation.py
      ai_screen_candidates.py
      search.py
      candidate_schema.py
      build_download_queue_from_ai.py
      download_pdfs.py
      legacy/
      config.example.yaml
    synthesis/
      ai_build_synthesis.py
    gap_analysis/
      ai_gap_analysis.py
```

## Core Workflow

Run the workflow in order. Later agents assume that earlier folders and files exist.

| Stage | Agent Prompt | Main Purpose | Output Folder |
|---|---|---|---|
| 00 | `00_research_brief_agent.md` | Turn study notes into project planning files. | `00_brief/` |
| 01 | `01_literature_search_agent.md` | Create literature search plan, queries, candidate-paper template, and search log. | `01_literature_search/` |
| 02 | `02_source_collection_agent.md` | Organize source collection decisions and source queues. | `02_sources/` |
| 03 | `03_document_ingestion_agent.md` | Convert local documents to raw and cleaned markdown. | `03_markdown/` |
| 04 | `04_citation_metadata_agent.md` | Extract citation metadata, APA references, BibTeX, and citation keys. | `04_metadata/` |
| 05 | `05_evidence_extraction_agent.md` | Extract structured paper evidence and per-paper summaries. | `05_evidence_extraction/` |
| 06 | `06_synthesis_matrix_agent.md` | Organize extracted evidence by theme. | `06_synthesis/` |
| 07 | `07_gap_analysis_agent.md` | Define research gaps, contribution, and refined problem statement. | `07_gap_analysis/` |
| 08 | `08_outline_agent.md` | Create manuscript and section outlines. | `08_outline/` |
| 09 | `09_intro_rrl_writer_agent.md` | Draft Introduction and Review of Related Literature. | `09_drafts/introduction/`, `09_drafts/rrl/` |
| 10 | `10_results_interpreter_agent.md` | Interpret supplied statistical outputs and table needs. | `09_drafts/results/` |
| 11 | `11_results_writer_agent.md` | Draft verified Results prose and table notes. | `09_drafts/results/` |
| 12 | `12_discussion_writer_agent.md` | Draft Discussion and related notes. | `09_drafts/discussion/` |
| 13 | `13_citation_audit_agent.md` | Audit citation keys, references, and citation-source fit. | `10_audit/citations/` |
| 14 | `14_claim_audit_agent.md` | Audit whether claims are supported by local data and evidence. | `10_audit/claims/` |
| 15 | `15_style_formatting_agent.md` | Review tone, formatting, APA 7 style, and readiness. | `11_final/` |
| 16 | `16_final_assembly_agent.md` | Assemble an editable full manuscript draft. | `11_final/` |

## Standard Project File Contract

The prompts currently use `projects/sample_project/` as the project path.

```text
projects/sample_project/
  input/
    study_notes.md
    statistical_results.md
    raw_tables/

  00_brief/
    research_brief.md
    research_questions.md
    variables.md
    inclusion_exclusion_criteria.md
    search_keywords.md
    source_strategy.md
    writing_scope.md
    agent_instructions.md

  01_literature_search/
    literature_search_plan.md
    search_queries.md
    candidate_papers.csv
    search_log.md

  02_sources/
    source_collection_plan.md
    included_sources.csv
    excluded_sources.csv
    download_queue.csv
    source_notes.md
    pdf/
    html/
    other/

  03_markdown/
    raw_md/
    cleaned_md/
    ingestion_manifest.csv
    ingestion_log.md

  04_metadata/
    references.bib
    references_apa7.md
    metadata_table.csv
    citation_key_map.csv
    metadata_issues.md

  05_evidence_extraction/
    evidence_table.csv
    paper_summaries/
    extraction_log.md

  06_synthesis/
    synthesis_matrix.csv
    theme_matrix.md
    literature_map.md
    synthesis_notes.md

  07_gap_analysis/
    research_gap_analysis.md
    study_contribution.md
    problem_statement_refined.md

  08_outline/
    manuscript_outline.md
    introduction_outline.md
    rrl_outline.md
    methodology_outline.md
    results_outline.md
    discussion_outline.md

  09_drafts/
    introduction/
      introduction_draft.md
    rrl/
      rrl_draft.md
      rrl_citation_notes.md
    methodology/
      methodology_draft.md
    results/
      results_interpretation_notes.md
      results_table_notes.md
      missing_results_to_confirm.md
      results_draft.md
      results_tables_draft.md
      results_queries.md
    discussion/
      discussion_draft.md
      conclusion_recommendations_notes.md
      limitations_notes.md

  10_audit/
    citations/
      citation_audit.md
      unsupported_citations.csv
      missing_citations.csv
    claims/
      claim_audit.md
      claim_table.csv

  11_final/
    style_report.md
    formatting_checklist.md
    full_manuscript_draft.md
    final_revision_notes.md
```

## Using the Workflow

### 1. Prepare Study Notes

Edit:

```text
projects/sample_project/input/study_notes.md
```

This file is the controlling source for the first stage. It should include the working title, topic, background, objectives or research questions, population, design, variables, available data, desired manuscript sections, citation style, and constraints.

For the included sample project, the topic is:

```text
Academic Performance, Pre-Board Examination Results, and Radiologic Technologist Licensure Examination Success
```

### 2. Generate the Initial Research Brief Prompt

The helper script creates a single prompt file for the Research Brief Agent:

```powershell
python agents/research_brief_agent.py
```

It reads:

```text
projects/sample_project/input/study_notes.md
```

It writes:

```text
projects/sample_project/00_brief/_prompt_for_ai.md
```

The script does not call an LLM or parse an LLM response. It prints manual next steps:

1. Open `_prompt_for_ai.md`.
2. Paste it into ChatGPT, Codex, or another LLM environment.
3. Save the response as `_ai_response.md`.
4. Split or write the requested output files into `projects/sample_project/00_brief/`.

The repository already contains generated sample brief files under `projects/sample_project/00_brief/`.

### 3. Run Each Prompt Agent

For each subsequent stage, open the matching prompt in:

```text
agents/prompts/
```

Then run it in an LLM environment that has access to this repository. Each prompt says exactly:

- which local files to read;
- which local files or folders to create;
- what not to invent;
- how to handle missing data;
- what completion checklist to verify.

### 4. Add Sources Locally

Source collection and ingestion are local-file based. Place actual source files in:

```text
projects/sample_project/02_sources/pdf/
projects/sample_project/02_sources/html/
projects/sample_project/02_sources/other/
```

Then run the local PDF-to-markdown converter for text-bearing PDFs:

```powershell
python -m scripts.document_ingestion.pdf_to_markdown --project projects/sample_project
```

It writes raw and cleaned markdown plus an ingestion manifest/log under `03_markdown/`. Use the document ingestion prompt afterward only for manual cleanup, OCR needs, or difficult files.

## Optional API-Assisted Paper Discovery

The `scripts/paper_discovery/` tools add a controlled API layer before source collection. They do not replace human screening or the local evidence workflow. The main pipeline creates canonical candidate records from the multi-provider search layer. Legal OA PDF download is intentionally separate and explicit.

### APIs Used

- **OpenAlex Works API**: searches candidate papers through the provider layer. OpenAlex requires a free API key.
- **Crossref REST API**: searches and returns bibliographic metadata. Public Crossref access does not require a key, but a polite email is recommended; Crossref Metadata Plus users may provide an optional API token.
- **Unpaywall API**: supported by the provider layer and archived legacy queue script for legal open-access full-text locations. Unpaywall requires an email parameter.
- **Semantic Scholar Graph API**: searches papers and returns citation/reference counts, fields of study, external IDs, and open-access PDF links when available. `SEMANTIC_SCHOLAR_API_KEY` is optional and sent as `x-api-key`.
- **PubMed / NCBI E-utilities**: searches PubMed with ESearch and retrieves batched metadata with EFetch. `NCBI_API_KEY` is optional; `NCBI_TOOL` and `CONTACT_EMAIL` are supported.
- **Europe PMC REST API**: searches biomedical and open-access records. No API key is required.
- **arXiv API**: searches preprint metadata and links. No API key is required; the provider enforces a minimum 3-second request interval and does not mass-download PDFs.
- **CORE API**: searches repository/full-text records. `CORE_API_KEY` is optional and sent when present.
- **Direct PDF HTTP requests**: `download_pdfs.py` downloads only explicit legal OA `pdf_url` values already recorded in `download_queue.csv`, then saves files under `02_sources/pdf/`.

The API and ingestion scripts use `requests`, `pandas`, `PyYAML`, `python-slugify`, `tqdm`, and `pypdf` from `requirements.txt`. Discovery writes activity to `logs/paper_discovery_log.md`; queue building and PDF downloading write separate logs under `projects/sample_project/logs/`.

### How the Pipeline Works

### Canonical Candidate Schema

`candidate_papers.csv` now has one canonical schema used by the literature-search prompt, the multi-provider export path, and the recommended discovery pipeline:

```csv
candidate_id,title,authors,year,publication_date,journal_or_repository,publisher,source_type,database_or_source,source_providers,search_query,doi,pmid,pmcid,arxiv_id,semantic_scholar_id,openalex_id,core_id,url,pdf_url,is_open_access,oa_status,license,abstract,keywords,fields_of_study,publication_types,citation_count,reference_count,influential_citation_count,ranking_score,access_type,screening_status,screening_reason,human_decision,human_notes,metadata_warnings,date_added,date_updated
```

New rows default to `screening_status=unscreened`. `human_decision` and `human_notes` remain blank unless a human reviewer explicitly fills them. Discovery refreshes preserve existing human review fields.

Stable `candidate_id` values are generated from DOI first, then PMID, PMCID, arXiv ID, OpenAlex ID, Semantic Scholar ID, CORE ID, and finally normalized title/year. List-like fields such as `source_providers`, `keywords`, `fields_of_study`, and `publication_types` use semicolon-separated values.

1. Create or edit:

```text
projects/sample_project/01_literature_search/search_queries.md
```

Add one real search query per bullet or line. If this file is missing, the main discovery pipeline creates a small template and stops without inventing queries.

You can also generate a first-pass query set from the stage 00 brief files:

```powershell
python scripts\paper_discovery\generate_search_queries.py --project projects/sample_project --max-queries 24
```

This script reads `projects/sample_project/00_brief/_ai_response.md` and related brief files, then writes `01_literature_search/search_queries.md`. It does not call an AI API, search the web, create source records, or make screening decisions. By default it preserves existing queries; add `--replace` to rewrite the query file from generated queries only.

AI-assisted query planning is also available:

```powershell
python -m scripts.paper_discovery.ai_query_generation --project projects/sample_project --limit 40 --dry-run
python -m scripts.paper_discovery.ai_query_generation --project projects/sample_project --limit 40
python -m scripts.paper_discovery.ai_query_generation --project projects/sample_project --limit 40 --apply
```

This reads Stage 00 brief files and writes `01_literature_search/ai_query_plan.md`, `01_literature_search/ai_query_variants.csv`, `01_literature_search/search_queries_ai.md`, and `logs/ai_query_generation_log.md`. It does not search providers, create candidate paper records, or make screening decisions. Use `--apply` to append reviewed general query suggestions into `search_queries.md`, then run `run_discovery_pipeline.py`.

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy and edit the discovery config:

```powershell
Copy-Item scripts\paper_discovery\config.example.yaml scripts\paper_discovery\config.yaml
```

Set `openalex_api_key`, `unpaywall_email`, and your contact email fields in `config.yaml`:

```yaml
project_dir: projects/sample_project
max_results_per_query: 25
openalex_api_key: "your_openalex_api_key"
semantic_scholar_api_key: ""
ncbi_api_key: ""
ncbi_tool: "research_agent"
contact_email: "your_email@example.com"
openalex_email: "your_email@example.com"
unpaywall_email: "your_email@example.com"
crossref_email: "your_email@example.com"
crossref_plus_api_key: ""
core_api_key: ""
user_agent: "ResearchAgent/0.1 (mailto:your_email@example.com)"
request_delay_seconds: 1.0
```

`scripts/paper_discovery/config.yaml` is local-only and may contain API keys. It is intentionally ignored by git. Do not commit it. `.env`, `.env.local`, `*.key`, and `*.pem` files are also ignored.

You can also set secrets and contact details with environment variables:

```powershell
$env:OPENALEX_API_KEY="your_openalex_api_key"
$env:SEMANTIC_SCHOLAR_API_KEY="your_semantic_scholar_key"
$env:NCBI_API_KEY="your_ncbi_key"
$env:NCBI_TOOL="research_agent"
$env:CONTACT_EMAIL="your_email@example.com"
$env:UNPAYWALL_EMAIL="your_email@example.com"
$env:CROSSREF_EMAIL="your_email@example.com"
$env:CROSSREF_PLUS_API_KEY="your_crossref_plus_token"
$env:CORE_API_KEY="your_core_key"
```

`CROSSREF_PLUS_API_KEY` is optional and only applies if you subscribe to Crossref Metadata Plus.

Provider toggles are supported through:

```text
ENABLE_OPENALEX=true
ENABLE_CROSSREF=true
ENABLE_UNPAYWALL=true
ENABLE_SEMANTIC_SCHOLAR=true
ENABLE_PUBMED=true
ENABLE_EUROPE_PMC=true
ENABLE_ARXIV=true
ENABLE_CORE=true
```

### Multi-Provider Search CLI

There is one recommended discovery pipeline:

- `run_discovery_pipeline.py` runs the newer multi-provider search layer across enabled providers and writes canonical `candidate_papers.csv` rows.
- `python -m scripts.paper_discovery.search` runs one direct multi-provider search and can export canonical candidate rows.

The old OpenAlex-first scripts are archived under `scripts/paper_discovery/legacy/` for reference. The discovery/search layer itself is deterministic; AI screening is a separate explicit step.

Search all enabled providers:

```powershell
python -m scripts.paper_discovery.search "radiologic technologist licensure examination academic performance" --limit 20
```

Search selected providers and export normalized results:

```powershell
python -m scripts.paper_discovery.search "licensure exam predictors" --providers openalex,semantic_scholar,pubmed --year-from 2020 --year-to 2026 --export projects/sample_project/01_literature_search/provider_results.csv
```

By default, `--export` writes the canonical candidate schema. Use `--export-format provider` only when you need the older compact provider-result export.

The multi-provider search layer normalizes results into one `Paper` schema, deduplicates by DOI, PMID, PMCID, arXiv ID, normalized title/year, and high-confidence fuzzy title match, then ranks candidates using query relevance, citation counts, recency, full-text availability, and a biomedical-source boost for PubMed and Europe PMC.

Provider outages and timeouts are expected occasionally. If one provider fails, the run continues with partial results from the other providers and logs a concise warning.

Rate-limit behavior:

- PubMed uses about 3 requests/second without `NCBI_API_KEY` and 10 requests/second with one.
- arXiv is limited to one request every 3 seconds.
- HTTP calls use timeouts and retry 429/5xx responses with exponential backoff.
- Metadata links are safe to store, but PDFs should only be downloaded when license or open-access status allows it.

4. Run the recommended multi-provider discovery pipeline:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50 --skip-download
```

To restrict providers:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --providers openalex,crossref,semantic_scholar,pubmed,europe_pmc,arxiv,core --max-results 50 --skip-download
```

The main pipeline reads `search_queries.md`, searches the newer multi-provider layer, normalizes results into the canonical candidate schema, merges them into `candidate_papers.csv`, and preserves existing human review fields. It does not download PDFs automatically. The retained downloader only downloads explicit legal OA URLs from `download_queue.csv`.

5. Review the generated files:

```text
projects/sample_project/01_literature_search/candidate_papers.csv
projects/sample_project/logs/paper_discovery_log.md
```

Optional legal OA download files, when separately prepared and explicitly downloaded:

```text
projects/sample_project/02_sources/download_queue.csv
projects/sample_project/02_sources/pdf/
```

Candidate papers remain `unscreened` until a human reviews them. Inclusion and exclusion decisions still belong in the normal source collection files.

### AI-Assisted Candidate Screening

After `candidate_papers.csv` exists, you can ask OpenAI to add AI screening suggestions. This is optional and does not make final human decisions.

The script reads:

```text
projects/sample_project/00_brief/research_brief.md
projects/sample_project/01_literature_search/candidate_papers.csv
```

It writes AI-only columns back to `candidate_papers.csv`:

```text
ai_relevance_label
ai_confidence
ai_reason
ai_suggested_action
ai_key_terms
ai_metadata_warnings
ai_screened_at
ai_model
```

It does not overwrite `screening_status`, `screening_reason`, `human_decision`, or `human_notes`.

API key setup:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Or place it in a local `.env` file, which is ignored by git:

```text
OPENAI_API_KEY=your_api_key_here
AI_SCREENING_MODEL=gpt-5-nano
AI_METADATA_MODEL=gpt-5-nano
AI_EVIDENCE_MODEL=gpt-5-mini
AI_SYNTHESIS_MODEL=gpt-5-mini
AI_DISCOVERY_MODEL=gpt-5-mini
```

Default model:

```text
gpt-5-nano
```

This is the default because OpenAI describes GPT-5 nano as its fastest, cheapest GPT-5 model and suitable for classification tasks. Use `--model gpt-5-mini` if you want a stronger but more expensive reviewer for borderline records.

Dry run:

```powershell
python scripts\paper_discovery\ai_screen_candidates.py --project projects/sample_project --limit 50 --dry-run
```

Screen a small first batch:

```powershell
python scripts\paper_discovery\ai_screen_candidates.py --project projects/sample_project --limit 50 --batch-size 10
```

Screen remaining unscreened-by-AI rows:

```powershell
python scripts\paper_discovery\ai_screen_candidates.py --project projects/sample_project --batch-size 20
```

The script creates a timestamped backup of `candidate_papers.csv` before writing unless `--no-backup` is supplied.

### Legal OA Download Queue From AI Tags

After AI screening, build a controlled download queue directly from the AI columns in `candidate_papers.csv`. Do not use a separate AI suggestions CSV as the main input. AI labels are not final inclusion decisions; they only help prioritize manual full-text screening.

Recommended workflow:

```powershell
python -m scripts.paper_discovery.run_discovery_pipeline --project projects/sample_project --max-results 50 --skip-download
python -m scripts.paper_discovery.ai_screen_candidates --project projects/sample_project --limit 50 --batch-size 10
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant --overwrite
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant,possibly_relevant --overwrite
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant,possibly_relevant,background_only --actions screen_full_text,keep_for_background --overwrite
python -m scripts.paper_discovery.build_download_queue_from_ai --project projects/sample_project --tags highly_relevant,possibly_relevant --overwrite
python -m scripts.paper_discovery.download_pdfs --project projects/sample_project
```

The queue builder reads `projects/sample_project/01_literature_search/candidate_papers.csv` and writes:

```text
projects/sample_project/02_sources/download_queue.csv
projects/sample_project/02_sources/download_queue_by_tag/highly_relevant.csv
projects/sample_project/02_sources/download_queue_by_tag/possibly_relevant.csv
projects/sample_project/02_sources/download_queue_by_tag/background_only.csv
projects/sample_project/02_sources/download_queue_excluded.csv
projects/sample_project/logs/download_queue_log.md
```

By default it queues only `highly_relevant` rows with `ai_suggested_action=screen_full_text` and checks DOI-only rows through Unpaywall. Use `--tags`, `--actions`, and `--min-confidence` to broaden or narrow the queue. Use `--no-unpaywall` to skip OA lookup; DOI-only rows are then excluded with `needs_oa_lookup`. Unpaywall requires `UNPAYWALL_EMAIL` or `unpaywall_email` in `config.yaml`.

The downloader reads `download_queue.csv`, downloads only rows with `download_status=queued` and non-empty `pdf_url`, saves files under `02_sources/pdf/`, and writes:

```text
projects/sample_project/02_sources/download_results/success.csv
projects/sample_project/02_sources/download_results/failed.csv
projects/sample_project/logs/pdf_download_log.md
```

`download_queue.csv` is only a queue. `success.csv` and `failed.csv` support manual ingestion and review. Failed reasons such as `missing_pdf_url`, `not_pdf_response`, and `request_failed` help decide whether to manually retrieve a legal copy, exclude the record, or fix metadata. The queue builder and downloader do not modify `candidate_papers.csv`.

No illegal downloads are allowed. The scripts do not bypass paywalls, do not use Sci-Hub, do not fabricate PDF URLs, and do not mark a paper downloaded unless the local file exists.

### 5. Add Statistical Results Locally

Results interpretation and results writing depend on:

```text
projects/sample_project/input/statistical_results.md
projects/sample_project/input/raw_tables/
```

If these are empty or missing, the results agents create placeholders and mark the results as `To be confirmed.` They do not invent statistics.

## Agent Details

### Research Brief Agent

Creates the project foundation from `input/study_notes.md`.

Outputs:

- `research_brief.md`
- `research_questions.md`
- `variables.md`
- `inclusion_exclusion_criteria.md`
- `search_keywords.md`
- `source_strategy.md`
- `writing_scope.md`
- `agent_instructions.md`

Use this stage to define the scope before any searching or writing begins.

### Literature Search Agent

Creates reproducible search planning files without pretending to have searched.

Outputs:

- `literature_search_plan.md`
- `search_queries.md`
- `candidate_papers.csv`
- `search_log.md`

It can prepare searches for PubMed, PubMed Central, ERIC, DOAJ, OpenAlex, Crossref, CORE, Semantic Scholar, Google Scholar, institutional repositories, Philippine repositories, and regulator sites where relevant.

### Source Collection Agent

Turns candidate records and available files into organized source tracking.

Outputs:

- `source_collection_plan.md`
- `included_sources.csv`
- `excluded_sources.csv`
- `download_queue.csv`
- `source_notes.md`
- source folders for PDFs, HTML files, and other formats.

It only includes sources that are locally present, manually supplied, or already listed in candidate files.

### Document Ingestion Agent

Defines the prompt-guided process for checking and cleaning converted source documents for downstream agents. A local PDF converter is available:

```powershell
python -m scripts.document_ingestion.pdf_to_markdown --project projects/sample_project
```

The script reads `02_sources/pdf/`, writes `03_markdown/raw_md/`, `03_markdown/cleaned_md/`, `03_markdown/ingestion_manifest.csv`, and `03_markdown/ingestion_log.md`. It uses `pypdf` text extraction with page markers. It does not OCR scanned PDFs, summarize papers, extract evidence, or invent missing text.

### Deterministic Citation Metadata

After markdown conversion, create first-pass citation metadata without AI:

```powershell
python -m scripts.citation_metadata.extract_metadata --project projects/sample_project --overwrite
```

The script reads `candidate_papers.csv`, `download_queue.csv`, `download_results/success.csv`, `03_markdown/cleaned_md/`, and `03_markdown/ingestion_manifest.csv`. It writes:

```text
projects/sample_project/04_metadata/metadata_table.csv
projects/sample_project/04_metadata/citation_key_map.csv
projects/sample_project/04_metadata/references_apa7.md
projects/sample_project/04_metadata/references.bib
projects/sample_project/04_metadata/metadata_issues.md
```

This is conservative deterministic extraction. It matches local markdown back to candidate/download metadata where possible, scans markdown for DOI/year/volume/issue/page clues, and marks unresolved fields as `To be confirmed.` It does not use OpenAI, run web searches, or invent missing citation details.

Optionally, run an AI metadata check after the deterministic first pass:

```powershell
python -m scripts.citation_metadata.ai_check_metadata --project projects/sample_project --limit 19
```

This requires `OPENAI_API_KEY` in the shell or ignored `.env` file. It sends each current metadata row and its local cleaned markdown to OpenAI with instructions to use only the supplied evidence. It writes:

```text
projects/sample_project/04_metadata/metadata_table_ai_checked.csv
projects/sample_project/04_metadata/metadata_ai_check_report.csv
projects/sample_project/04_metadata/citation_key_map_ai_checked.csv
projects/sample_project/04_metadata/references_apa7_ai_checked.md
projects/sample_project/04_metadata/references_ai_checked.bib
projects/sample_project/04_metadata/metadata_ai_check_log.md
```

Use `--apply` only after inspecting the checked outputs; it backs up and replaces `metadata_table.csv`. AI metadata checks must leave unresolved fields as `To be confirmed.` and must not use web knowledge or invent citation details.

### Citation and Metadata Agent

Extracts bibliographic metadata from local sources and converted markdown.

Outputs:

- `references.bib`
- `references_apa7.md`
- `metadata_table.csv`
- `citation_key_map.csv`
- `metadata_issues.md`

Citation keys follow the pattern:

```text
FirstAuthorYearShortTitle
```

Example:

```text
Santos2021BoardPerformance
```

Incomplete metadata must be marked `To be confirmed.` and should not be treated as final-ready.

### Evidence Extraction Agent

Extracts structured evidence from cleaned markdown sources. A local OpenAI-backed script is available:

```powershell
python -m scripts.evidence_extraction.ai_extract_evidence --project projects/sample_project --limit 19 --overwrite
```

The script prefers `04_metadata/metadata_table_ai_checked.csv` when present, otherwise it uses `04_metadata/metadata_table.csv`. It reads the Stage 00 brief files, metadata, and each paper's `local_markdown_file`, then writes:

Outputs:

- `evidence_table.csv`
- one summary file per paper in `paper_summaries/`
- `extraction_log.md`

Each paper summary includes purpose, design, sample, setting, variables, measures, statistical methods, key findings, limitations, relevance, source location, and confidence rating.

This requires `OPENAI_API_KEY`. The default model is `AI_EVIDENCE_MODEL=gpt-5-mini` because this step reads longer paper text and extracts findings, methods, variables, and limitations. The script instructs the model to use only supplied local text and to mark unverifiable details as `To be confirmed.`

### Synthesis Matrix Agent

A bounded OpenAI-backed Stage 06 script can organize already-extracted Stage 05 evidence into structured synthesis artifacts:

```powershell
python -m scripts.synthesis.ai_build_synthesis --project projects/sample_project --dry-run
python -m scripts.synthesis.ai_build_synthesis --project projects/sample_project --overwrite
```

It reads `05_evidence_extraction/evidence_table.csv` and available files under `05_evidence_extraction/paper_summaries/`, plus brief and metadata context when present. It writes:

Outputs:

- `synthesis_matrix.csv`
- `theme_matrix.md`
- `literature_map.md`
- `synthesis_notes.md`

It separates direct evidence, indirect support, mixed findings, contradictions, methodological patterns, contextual gaps, and likely uses for Introduction, RRL, Methods, and Discussion. It does not reread raw PDFs by default and does not write the RRL or manuscript directly.

This requires `OPENAI_API_KEY` unless `--dry-run` is used. The default model is `AI_SYNTHESIS_MODEL=gpt-5-mini`. The implementation validates returned citation keys and paper IDs against the supplied Stage 05/metadata inputs, coerces unsupported classifications to `to_be_confirmed`, writes blocked notes if Stage 05 evidence is missing, and refuses to overwrite existing Stage 06 outputs unless `--overwrite` is supplied.

### Gap Analysis Agent

A bounded OpenAI-backed Stage 07 script can turn reviewed Stage 06 synthesis outputs into structured research-positioning artifacts:

```powershell
python -m scripts.gap_analysis.ai_gap_analysis --project projects/sample_project --dry-run
python -m scripts.gap_analysis.ai_gap_analysis --project projects/sample_project --overwrite
```

It reads `06_synthesis/synthesis_matrix.csv`, `theme_matrix.md`, `literature_map.md`, and `synthesis_notes.md`, plus Stage 00 brief context and available evidence/metadata context. It writes:

Outputs:

- `research_gap_analysis.md`
- `study_contribution.md`
- `problem_statement_refined.md`
- `gap_matrix.csv`

This stage prepares safe research positioning for outline and writing stages. It does not draft the Introduction, Review of Related Literature, Discussion, or full manuscript. Gap claims must trace to the supplied Stage 06 synthesis or be marked `To be confirmed.`, and the script refuses to overwrite existing Stage 07 outputs unless `--overwrite` is supplied.

This stage clarifies what is known, what remains unknown, population or context gaps, methodological gaps, local or Philippine gaps, and variable or measurement gaps.

### Outline Agent

Creates manuscript-level and section-level outlines.

Outputs:

- `manuscript_outline.md`
- `introduction_outline.md`
- `rrl_outline.md`
- `methodology_outline.md`
- `results_outline.md`
- `discussion_outline.md`

The workflow plans a Methodology section, but methodology prose is currently expected to be supplied manually at:

```text
projects/sample_project/09_drafts/methodology/methodology_draft.md
```

### Introduction and RRL Writer Agent

Drafts only the Introduction and Review of Related Literature.

Outputs:

- `introduction_draft.md`
- `rrl_draft.md`
- `rrl_citation_notes.md`

It uses temporary citation markers in this format:

```text
[@CitationKey]
```

It should use only verified or final-ready citation keys from local metadata.

### Results Interpreter Agent

Reads user-supplied statistical outputs and maps them to research questions.

Outputs:

- `results_interpretation_notes.md`
- `results_table_notes.md`
- `missing_results_to_confirm.md`

It does not run new analyses by default and does not write polished Results prose.

### Results Writer Agent

Drafts concise Results prose from verified statistical outputs.

Outputs:

- `results_draft.md`
- `results_tables_draft.md`
- `results_queries.md`

It reports findings without Discussion-style interpretation.

### Discussion Writer Agent

Drafts Discussion and related conclusion, recommendation, and limitation notes.

Outputs:

- `discussion_draft.md`
- `conclusion_recommendations_notes.md`
- `limitations_notes.md`

It interprets only verified results in relation to local synthesis and verified citations.

### Citation Audit Agent

Checks citation consistency and source fit.

Outputs:

- `citation_audit.md`
- `unsupported_citations.csv`
- `missing_citations.csv`

It verifies that citation keys used in drafts exist in metadata, that APA references match cited keys, and that cited sources plausibly support the claim based on local evidence.

### Claim Audit Agent

Checks whether manuscript claims are supported.

Outputs:

- `claim_audit.md`
- `claim_table.csv`

It classifies claims as supported by user data, supported by literature, partially supported, unsupported, too strong, needing citation, or needing revision.

### Style and Formatting Agent

Reviews manuscript readiness from a style and formatting perspective.

Outputs:

- `style_report.md`
- `formatting_checklist.md`

It checks academic tone, IMRaD organization, APA 7 style, headings, redundancy, tense, table and figure callouts, overclaiming, terminology consistency, and unresolved audit issues.

### Final Assembly Agent

Assembles an editable markdown manuscript.

Outputs:

- `full_manuscript_draft.md`
- `final_revision_notes.md`

It includes only available draft sections and final-ready references. Missing sections remain visible as `To be confirmed.` placeholders.

## Research Integrity Rules

These rules appear throughout the prompts and are central to the workflow:

- Keep all work local and file-based.
- Use APA 7th edition unless the project specifies another style.
- Do not invent sources, citations, authors, years, journals, DOIs, URLs, statistics, findings, sample sizes, p-values, coefficients, tables, figures, or conclusions.
- Do not claim statistical significance unless supplied local results verify it.
- Do not claim that a paper was downloaded unless the file exists locally.
- Do not cite a source unless it appears in local metadata, evidence, or synthesis files.
- Do not treat expected findings as actual findings.
- Do not make causal claims from retrospective, correlational, or predictive designs unless the design and evidence support them.
- Mark missing, uncertain, incomplete, or unsupported details as `To be confirmed.`
- Preserve distinction between actual extracted evidence and interpretation.
- Use allied health evidence only as supporting context when direct Radiologic Technology evidence is limited.

## Current Sample Project Status

The sample project currently contains:

- `input/study_notes.md`
- `input/statistical_results.md`, currently empty
- generated brief files in `00_brief/`
- `_prompt_for_ai.md` and `_ai_response.md` artifacts from the initial research brief run

The sample project brief is already aligned to the current predictive-validation positioning:

- academic performance;
- professional course grades and course-cluster grades;
- internship or clinical performance;
- pre-board examination results;
- terminal competency or comprehensive examination results, if available;
- Radiologic Technologist Licensure Examination rating;
- pass/fail licensure outcome;
- subject-area licensure performance, if available.

The sample project has also been manually reviewed after local PDF/markdown placement to repair citation-key propagation. Stable local paper IDs were assigned for no-DOI local sources, exact synthesis citation keys were restored where DOI paper IDs were already present, stale local path prefixes were corrected, and affected Stage 05 summary filenames were renamed away from `to-be-confirmed_*`. The repair log is:

```text
projects/sample_project/logs/citation_key_repair_log.md
```

The latest manual consistency check found no exact `To be confirmed.` values in `paper_id`, `citation_key`, or `supporting_synthesis_source` fields across metadata, evidence, synthesis, and gap-matrix CSVs.

Downstream literature search, source collection, drafting, audit, and final assembly folders may need to be created by running the matching prompt agents. Ingestion, metadata extraction/checking, evidence extraction, synthesis, and gap analysis also have local scripts and can be run before returning to the prompt-guided stages.

The optional paper discovery scripts are present under `scripts/paper_discovery/`. The main pipeline can populate `01_literature_search/candidate_papers.csv` and `logs/paper_discovery_log.md` after you supply search queries and any needed provider credentials. AI-assisted query generation, candidate screening, metadata checking, evidence extraction, synthesis, and gap analysis are implemented as bounded explicit scripts. Legal OA download remains a separate explicit step using `build_download_queue_from_ai.py` and `download_pdfs.py`.

## Prompt Quality Notes

The repository includes prompt maintenance files:

- `_prompt_qc_report.md`
- `_prompt_repair_log.md`
- `_prompt_qc_issues.csv`

The repair log notes that several prompt consistency issues were already addressed, including:

- final assembly handling for incomplete references;
- blocked/template behavior when audits are run before drafts exist;
- missing style-report behavior during final assembly;
- CSV escaping rules in CSV-producing prompts;
- citation-key readiness checks in writer prompts;
- clarification that citation audit checks citation-source fit while claim audit is authoritative for claim support classification.

One known convention remains: prompts are hard-coded to `projects/sample_project/`. To reuse the workflow across multiple projects, update all prompts consistently or introduce a project-directory variable convention such as `{PROJECT_DIR}`.

## Recommended End-to-End Run Order

1. Edit `projects/sample_project/input/study_notes.md`.
2. Run `python agents/research_brief_agent.py` or use `00_research_brief_agent.md` directly.
3. Confirm all files in `00_brief/`.
4. Run the Literature Search Agent.
5. Populate `candidate_papers.csv` by manually executing searches, running the optional paper discovery pipeline, or providing sources locally.
6. Run the Source Collection Agent.
7. Add actual PDFs, HTML captures, or other source files.
8. Run `python -m scripts.document_ingestion.pdf_to_markdown --project projects/sample_project`, then use the Document Ingestion Agent prompt only for manual cleanup or difficult files.
9. Run `python -m scripts.citation_metadata.extract_metadata --project projects/sample_project --overwrite`, then use the Citation and Metadata Agent prompt for manual verification or cleanup.
10. Run `python -m scripts.evidence_extraction.ai_extract_evidence --project projects/sample_project --limit 19 --overwrite`, then review the Stage 05 outputs or use the Evidence Extraction Agent prompt for manual extraction/cleanup.
11. Run `python -m scripts.synthesis.ai_build_synthesis --project projects/sample_project --overwrite`, then review the Stage 06 outputs or use the Synthesis Matrix Agent prompt for manual cleanup.
12. Run `python -m scripts.gap_analysis.ai_gap_analysis --project projects/sample_project --overwrite`, then review Stage 07 research positioning outputs or use the Gap Analysis Agent prompt for manual cleanup.
13. Run the Outline Agent.
14. Draft or supply `09_drafts/methodology/methodology_draft.md` if a Methodology section is needed.
15. Run the Introduction and RRL Writer Agent.
16. Add verified statistical outputs to `input/statistical_results.md` and/or `input/raw_tables/`.
17. Run the Results Interpreter Agent.
18. Run the Results Writer Agent.
19. Run the Discussion Writer Agent.
20. Run the Citation Audit Agent.
21. Run the Claim Audit Agent.
22. Run the Style and Formatting Agent.
23. Run the Final Assembly Agent.
24. Review `11_final/full_manuscript_draft.md` and `11_final/final_revision_notes.md`.

## Reusing for Another Project

To adapt the workflow:

1. Create a new folder under `projects/`.
2. Copy the expected input structure.
3. Replace `input/study_notes.md` with the new study details.
4. Update prompt paths from `projects/sample_project/` to the new project path.
5. Run the agents in order.

For repeated use across projects, consider refactoring prompts to use a project variable such as:

```text
{PROJECT_DIR}
```

with `projects/sample_project/` as the default example.

## Practical Notes

- CSV files should quote fields containing commas, quotation marks, or line breaks, and escape internal quotation marks by doubling them.
- Draft citations use `[@CitationKey]` markers until final formatting.
- References under `## Metadata To Confirm` in `references_apa7.md` should not be included as final-ready manuscript references.
- Manually added PDFs may produce provisional local IDs when no DOI is available. Keep those IDs stable across `04_metadata/`, `05_evidence_extraction/`, `06_synthesis/`, and `07_gap_analysis/` instead of leaving `paper_id` as `To be confirmed.`.
- If local source folders move, verify `local_source_file` and `local_markdown_file` paths in metadata tables before rerunning AI extraction or synthesis.
- Manual downstream repairs should leave a log under `projects/<project>/logs/` and backups beside edited files, as in `.citation_repair.bak` and `.path_repair.bak`.
- If an agent runs before prerequisites exist, it should create templates or blocked-status notes instead of fabricating content.
- Final assembly is provisional unless citation audit, claim audit, and style review are complete and do not identify unresolved major blockers.
