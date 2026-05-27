from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from scripts.paper_discovery.candidate_schema import (
    CANONICAL_CANDIDATE_COLUMNS,
    merge_candidate_dataframes,
    papers_to_candidate_dataframe,
)
from scripts.paper_discovery.config import load_config
from scripts.paper_discovery.discovery.search import search_all


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project_arg: str | None, config: dict) -> Path:
    project = project_arg or config.get("project_dir") or "projects/sample_project"
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def log(project_dir: Path, message: str) -> None:
    log_path = project_dir / "logs" / "paper_discovery_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {stamp} run_discovery_pipeline: {message}\n")


def ensure_query_file(project_dir: Path) -> tuple[Path, bool]:
    path = project_dir / "01_literature_search" / "search_queries.md"
    if path.exists():
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Search Queries\n\n"
        "Add one real search query per bullet or line. The discovery pipeline will not invent queries.\n\n"
        "# Example only:\n"
        "# - radiologic technologist licensure examination academic performance\n",
        encoding="utf-8",
    )
    return path, True


def read_queries(path: Path) -> list[str]:
    queries: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*]\s+", "", line).strip()
        if line and not line.lower().startswith("add one real search query"):
            queries.append(line)
    return list(dict.fromkeys(queries))


def load_existing_candidates(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    path.parent.mkdir(parents=True, exist_ok=True)
    return pd.DataFrame(columns=CANONICAL_CANDIDATE_COLUMNS)


def write_candidate_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        pd.DataFrame(columns=CANONICAL_CANDIDATE_COLUMNS).to_csv(path, index=False, encoding="utf-8")


def parse_providers(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def run_pipeline(
    project_dir: Path,
    max_results: int,
    providers: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    config: dict | None = None,
) -> dict[str, int]:
    config = config or {}
    query_file, created = ensure_query_file(project_dir)
    candidate_path = project_dir / "01_literature_search" / "candidate_papers.csv"
    if created:
        write_candidate_template(candidate_path)
        log(project_dir, f"Created query template at {query_file}; no searches run.")
        return {"queries": 0, "incoming_rows": 0, "candidate_rows": 0, "failures": 0}

    queries = read_queries(query_file)
    if not queries:
        write_candidate_template(candidate_path)
        log(project_dir, "No search queries found; candidate template created or preserved.")
        return {"queries": 0, "incoming_rows": 0, "candidate_rows": len(load_existing_candidates(candidate_path)), "failures": 0}

    incoming_frames: list[pd.DataFrame] = []
    failures = 0
    incoming_rows = 0
    for query in queries:
        try:
            papers = search_all(
                query,
                limit_per_provider=max_results,
                year_from=year_from,
                year_to=year_to,
                providers=providers,
                config=config,
            )
            frame = papers_to_candidate_dataframe(papers, search_query=query)
            incoming_rows += len(frame)
            incoming_frames.append(frame)
            log(project_dir, f"Searched query '{query}' and normalized {len(frame)} candidate rows.")
        except Exception as exc:
            failures += 1
            log(project_dir, f"Failed query '{query}': {exc}")

    existing = load_existing_candidates(candidate_path)
    incoming = pd.concat(incoming_frames, ignore_index=True) if incoming_frames else pd.DataFrame(columns=CANONICAL_CANDIDATE_COLUMNS)
    merged = merge_candidate_dataframes(existing, incoming)
    merged.to_csv(candidate_path, index=False, encoding="utf-8")
    log(project_dir, f"Saved {len(merged)} canonical candidate rows; incoming_rows={incoming_rows}; failures={failures}.")
    return {"queries": len(queries), "incoming_rows": incoming_rows, "candidate_rows": len(merged), "failures": failures}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-provider discovery into canonical candidate_papers.csv.")
    parser.add_argument("--project", default="projects/sample_project", help="Project directory")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum results per provider per query")
    parser.add_argument("--providers", help="Comma-separated providers: openalex,crossref,semantic_scholar,pubmed,europe_pmc,arxiv,core")
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    parser.add_argument("--skip-download", action="store_true", help="Accepted for compatibility; the main pipeline does not download PDFs automatically.")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    project_dir = resolve_project(args.project, config)
    summary = run_pipeline(
        project_dir=project_dir,
        max_results=args.max_results,
        providers=parse_providers(args.providers),
        year_from=args.year_from,
        year_to=args.year_to,
        config=config,
    )
    if args.skip_download:
        log(project_dir, "--skip-download supplied; the main pipeline does not download PDFs automatically.")
    else:
        log(project_dir, "PDF download not run. Use the existing OA queue and downloader explicitly after review.")
    print("Summary")
    print(f"queries: {summary['queries']}")
    print(f"incoming candidate rows: {summary['incoming_rows']}")
    print(f"candidate papers saved: {summary['candidate_rows']}")
    print(f"failures: {summary['failures']}")


if __name__ == "__main__":
    main()
