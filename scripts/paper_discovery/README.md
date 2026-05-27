# Paper Discovery Scripts

These scripts add an API-based discovery layer to the local Research Agent workflow. The main pipeline searches multiple scholarly providers, normalizes metadata, deduplicates/ranks results, and writes canonical candidate records. Legal OA PDF download is separate and explicit.

## APIs Used

- OpenAlex Works API for paper discovery. OpenAlex requires a free API key.
- Crossref REST API for DOI and bibliographic metadata enrichment. Public access does not require a key, but a polite email is recommended. Crossref Plus users may provide an optional API token.
- Unpaywall API for legal open-access full-text and PDF locations. Unpaywall requires an email parameter.
- Semantic Scholar Graph API for relevance-ranked paper search and citation metadata. `SEMANTIC_SCHOLAR_API_KEY` is optional and sent as `x-api-key` when present.
- PubMed / NCBI E-utilities for biomedical literature discovery. `NCBI_API_KEY` is optional; `NCBI_TOOL` and `CONTACT_EMAIL` are supported.
- Europe PMC REST API for biomedical and open-access metadata. No API key is required.
- arXiv API for preprint metadata. No API key is required; the provider enforces a minimum 3-second request interval.
- CORE API for repository and full-text discovery. `CORE_API_KEY` is optional and sent when present.

The scripts do not use Sci-Hub or illegal sources.

## Setup

Install dependencies from the repository root:

```powershell
pip install -r requirements.txt
```

Copy the example config:

```powershell
Copy-Item scripts\paper_discovery\config.example.yaml scripts\paper_discovery\config.yaml
```

Edit `scripts/paper_discovery/config.yaml` and add your API keys and email addresses:

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

`config.yaml` is local-only and may contain API keys. It is intentionally ignored by git. Do not commit it.

You can also set secrets with environment variables instead of storing them in `config.yaml`:

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

Provider toggles are supported through `ENABLE_OPENALEX`, `ENABLE_CROSSREF`, `ENABLE_UNPAYWALL`, `ENABLE_SEMANTIC_SCHOLAR`, `ENABLE_PUBMED`, `ENABLE_EUROPE_PMC`, `ENABLE_ARXIV`, and `ENABLE_CORE`.

## Multi-Provider Search

Search all enabled providers:

```powershell
python -m scripts.paper_discovery.search "radiologic technologist licensure examination academic performance" --limit 20
```

Search selected providers:

```powershell
python -m scripts.paper_discovery.search "licensure exam predictors" --providers openalex,semantic_scholar,pubmed --year-from 2020 --year-to 2026 --export projects/sample_project/01_literature_search/provider_results.csv
```

By default, `--export` writes the canonical `candidate_papers.csv` schema. Use `--export-format provider` for the older compact provider-result export.

The multi-provider layer normalizes records into a shared `Paper` model, deduplicates by DOI, PMID, PMCID, arXiv ID, normalized title/year, and high-confidence fuzzy title match, then ranks results using query relevance, citation counts, recency, full-text availability, and biomedical-source boosts.

Provider outages and timeouts are handled conservatively. If one provider fails, the search continues with results from the remaining providers and logs a concise warning instead of stopping the run.

## Canonical Candidate Schema

The discovery foundation now uses one canonical candidate schema:

```csv
candidate_id,title,authors,year,publication_date,journal_or_repository,publisher,source_type,database_or_source,source_providers,search_query,doi,pmid,pmcid,arxiv_id,semantic_scholar_id,openalex_id,core_id,url,pdf_url,is_open_access,oa_status,license,abstract,keywords,fields_of_study,publication_types,citation_count,reference_count,influential_citation_count,ranking_score,access_type,screening_status,screening_reason,human_decision,human_notes,metadata_warnings,date_added,date_updated
```

New records are `unscreened`. Human review fields are blank by default and preserved on refresh.

## Rate Limits and Access Notes

- PubMed uses about 3 requests/second without `NCBI_API_KEY` and 10 requests/second with one.
- arXiv is limited to one request every 3 seconds.
- All HTTP calls use timeouts and retry 429/5xx responses with exponential backoff.
- Metadata links are safe to store, but PDFs should be downloaded only when license or open-access status allows it.
- The scripts do not mass-download PDFs from arXiv or CORE. PDF downloading remains limited to explicit OA URLs in the downstream download queue.

## Inputs

Search queries are read from:

```text
projects/sample_project/01_literature_search/search_queries.md
```

If this file is missing, the scripts create a small template and stop without inventing queries.

To generate a first-pass query file from stage 00 brief outputs:

```powershell
python scripts\paper_discovery\generate_search_queries.py --project projects/sample_project --max-queries 24
```

The query generator reads `00_brief/_ai_response.md` and related brief files. It is deterministic local code: it does not call an AI API, search the web, create source records, or make screening decisions. Existing queries are preserved unless `--replace` is supplied.

## Run the Pipeline

From the repository root:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50 --skip-download
```

The main pipeline uses the newer multi-provider layer and writes canonical candidate rows. It does not download PDFs automatically.

To restrict providers:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --providers openalex,crossref,semantic_scholar,pubmed,europe_pmc,arxiv,core --max-results 50 --skip-download
```

The older OpenAlex-first scripts are archived in `scripts/paper_discovery/legacy/` for reference only.

To download existing legal OA PDF URLs from `download_queue.csv`, run the downloader explicitly:

```powershell
python scripts\paper_discovery\download_pdfs.py --project projects/sample_project
```

## Outputs

- Candidate papers: `projects/sample_project/01_literature_search/candidate_papers.csv`
- OA download queue, when separately prepared: `projects/sample_project/02_sources/download_queue.csv`
- Downloaded PDFs, when explicitly downloaded: `projects/sample_project/02_sources/pdf/`
- Log file: `projects/sample_project/logs/paper_discovery_log.md`

Candidate results still require human screening. The scripts mark discovered candidates as `unscreened`; inclusion and exclusion decisions should be made manually in the project CSV files.
