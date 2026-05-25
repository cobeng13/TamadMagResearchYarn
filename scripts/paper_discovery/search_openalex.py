from __future__ import annotations

import argparse
import hashlib
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml


CANDIDATE_COLUMNS = [
    "paper_id",
    "title",
    "authors",
    "year",
    "source",
    "database",
    "url",
    "doi",
    "access_type",
    "screening_status",
    "reason_for_decision",
    "notes",
    "abstract",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(config_path: Path | None) -> dict[str, Any]:
    default_path = Path(__file__).with_name("config.yaml")
    path = config_path or default_path
    if path.exists():
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {}


def resolve_project(project_arg: str | None, config: dict[str, Any]) -> Path:
    project = project_arg or config.get("project_dir") or "projects/sample_project"
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def log(project_dir: Path, message: str) -> None:
    log_path = project_dir / "logs" / "paper_discovery_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {stamp} search_openalex: {message}\n")


def ensure_query_file(project_dir: Path) -> Path:
    path = project_dir / "01_literature_search" / "search_queries.md"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# Search Queries\n\n"
            "Add one real search query per bullet or line.\n\n"
            "# Example only:\n"
            "# - radiologic technologist licensure examination academic performance\n",
            encoding="utf-8",
        )
        log(project_dir, f"Created query template at {path}")
    return path


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


def normalize_doi(value: Any) -> str:
    if pd.isna(value) or not str(value).strip():
        return ""
    doi = str(value).strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.lower()


def normalize_title(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\W+", " ", str(value).lower()).strip()


def paper_id_for(title: str, doi: str) -> str:
    key = doi or normalize_title(title)
    return "OA-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]


def abstract_from_index(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for position in positions:
            words.append((position, word))
    return " ".join(word for _, word in sorted(words))


def existing_candidates(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    path.parent.mkdir(parents=True, exist_ok=True)
    return pd.DataFrame(columns=CANDIDATE_COLUMNS)


def request_openalex(query: str, max_results: int, config: dict[str, Any]) -> list[dict[str, Any]]:
    params = {"search": query, "per-page": max_results}
    email = config.get("openalex_email")
    if email:
        params["mailto"] = email
    headers = {"User-Agent": config.get("user_agent") or "ResearchAgent/0.1"}
    response = requests.get("https://api.openalex.org/works", params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get("results", [])


def work_to_row(work: dict[str, Any]) -> dict[str, str]:
    title = work.get("title") or ""
    doi = normalize_doi(work.get("doi") or "")
    authorships = work.get("authorships") or []
    authors = "; ".join(
        a.get("author", {}).get("display_name", "")
        for a in authorships
        if a.get("author", {}).get("display_name")
    )
    primary_location = work.get("primary_location") or {}
    source = (primary_location.get("source") or {}).get("display_name", "")
    oa = work.get("open_access") or {}
    return {
        "paper_id": paper_id_for(title, doi),
        "title": title,
        "authors": authors,
        "year": str(work.get("publication_year") or ""),
        "source": source,
        "database": "OpenAlex",
        "url": work.get("doi") or work.get("id") or "",
        "doi": doi,
        "access_type": oa.get("oa_status") or "",
        "screening_status": "unscreened",
        "reason_for_decision": "",
        "notes": "",
        "abstract": abstract_from_index(work.get("abstract_inverted_index")),
    }


def merge_candidates(existing: pd.DataFrame, discovered: pd.DataFrame) -> pd.DataFrame:
    for column in CANDIDATE_COLUMNS:
        if column not in existing.columns:
            existing[column] = ""
        if column not in discovered.columns:
            discovered[column] = ""
    combined = pd.concat([existing, discovered], ignore_index=True).fillna("")
    combined["_doi_key"] = combined["doi"].map(normalize_doi)
    combined["_title_key"] = combined["title"].map(normalize_title)
    combined["_dedupe_key"] = combined.apply(
        lambda row: f"doi:{row['_doi_key']}" if row["_doi_key"] else f"title:{row['_title_key']}",
        axis=1,
    )
    merged_rows = []
    for _, group in combined.groupby("_dedupe_key", sort=False):
        base = group.iloc[0].copy()
        for _, candidate in group.iloc[1:].iterrows():
            for column in combined.columns:
                if column.startswith("_"):
                    continue
                if not str(base.get(column, "")).strip() and str(candidate.get(column, "")).strip():
                    base[column] = candidate[column]
        merged_rows.append(base)
    merged = pd.DataFrame(merged_rows).drop(columns=["_doi_key", "_title_key", "_dedupe_key"])
    ordered = CANDIDATE_COLUMNS + [c for c in merged.columns if c not in CANDIDATE_COLUMNS]
    return merged[ordered]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search OpenAlex for candidate papers.")
    parser.add_argument("--project", help="Project directory")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    parser.add_argument("--max-results", type=int, help="Maximum results per query")
    args = parser.parse_args()

    config = load_config(args.config)
    project_dir = resolve_project(args.project, config)
    query_file = ensure_query_file(project_dir)
    candidate_path = project_dir / "01_literature_search" / "candidate_papers.csv"
    queries = read_queries(query_file)
    if not queries:
        existing_candidates(candidate_path).to_csv(candidate_path, index=False, encoding="utf-8")
        log(project_dir, "No search queries found; wrote candidate paper template only.")
        print("No search queries found. Template created or preserved.")
        return

    max_results = args.max_results or int(config.get("max_results_per_query") or 25)
    delay = float(config.get("request_delay_seconds") or 1.0)
    rows: list[dict[str, str]] = []
    failures = 0
    for query in queries:
        try:
            for work in request_openalex(query, max_results, config):
                rows.append(work_to_row(work))
            log(project_dir, f"Searched query: {query}")
        except Exception as exc:
            failures += 1
            log(project_dir, f"Failed query '{query}': {exc}")
        time.sleep(delay)

    existing = existing_candidates(candidate_path)
    discovered = pd.DataFrame(rows, columns=CANDIDATE_COLUMNS)
    merged = merge_candidates(existing, discovered)
    merged.to_csv(candidate_path, index=False, encoding="utf-8")
    log(project_dir, f"Saved {len(merged)} candidate rows; query failures={failures}.")
    print(f"candidate_papers={len(merged)} discovered_rows={len(discovered)} failures={failures}")


if __name__ == "__main__":
    main()
