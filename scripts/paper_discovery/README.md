# Paper Discovery Scripts

These scripts add an API-based discovery layer to the local Research Agent workflow. They search for candidate papers, enrich metadata, identify legal open-access locations, and optionally download legal OA PDFs into the project source folder.

## APIs Used

- OpenAlex Works API for paper discovery.
- Crossref REST API for DOI and bibliographic metadata enrichment.
- Unpaywall API for legal open-access full-text and PDF locations.

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

Edit `scripts/paper_discovery/config.yaml` and add your email addresses. Unpaywall requires an email. You can also set it with an environment variable:

```powershell
$env:UNPAYWALL_EMAIL="your_email@example.com"
```

## Inputs

OpenAlex search queries are read from:

```text
projects/sample_project/01_literature_search/search_queries.md
```

If this file is missing, the scripts create a small template and stop without inventing queries.

## Run the Pipeline

From the repository root:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50
```

To identify OA records without downloading PDFs:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50 --skip-download
```

To re-download existing PDFs:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --force
```

## Outputs

- Candidate papers: `projects/sample_project/01_literature_search/candidate_papers.csv`
- OA download queue: `projects/sample_project/02_sources/download_queue.csv`
- Downloaded PDFs: `projects/sample_project/02_sources/pdf/`
- Log file: `projects/sample_project/logs/paper_discovery_log.md`

Candidate results still require human screening. The scripts mark discovered candidates as `unscreened`; inclusion and exclusion decisions should be made manually in the project CSV files.
