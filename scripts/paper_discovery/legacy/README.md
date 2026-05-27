# Legacy Paper Discovery Scripts

These scripts are retained for reference only. The recommended discovery entry point is now:

```powershell
python scripts\paper_discovery\run_discovery_pipeline.py --project projects/sample_project --max-results 50 --skip-download
```

Archived scripts:

- `run_discovery_pipeline_legacy.py`: old sequential OpenAlex-first pipeline.
- `search_openalex.py`: legacy OpenAlex-only candidate search.
- `enrich_crossref.py`: legacy Crossref enrichment step.
- `find_oa_pdfs.py`: legacy Unpaywall queue-generation step.

Do not use these scripts for the main workflow unless you are deliberately comparing old behavior. They may not use the canonical candidate schema without adapters.

Legal PDF downloading remains conservative. The active downloader is still:

```text
scripts/paper_discovery/download_pdfs.py
```

It should only be used with explicit legal OA `pdf_url` values.

