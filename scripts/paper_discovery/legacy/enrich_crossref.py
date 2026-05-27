from __future__ import annotations

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml


BASE_COLUMNS = [
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
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(config_path: Path | None) -> dict[str, Any]:
    path = config_path or Path(__file__).with_name("config.yaml")
    return (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.exists() else {}


def resolve_project(project_arg: str | None, config: dict[str, Any]) -> Path:
    project = project_arg or config.get("project_dir") or "projects/sample_project"
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def log(project_dir: Path, message: str) -> None:
    path = project_dir / "logs" / "paper_discovery_log.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {stamp} enrich_crossref: {message}\n")


def normalize_doi(value: Any) -> str:
    if pd.isna(value) or not str(value).strip():
        return ""
    doi = str(value).strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.lower()


def title_similarity(left: str, right: str) -> float:
    left_tokens = set(re.sub(r"\W+", " ", left.lower()).split())
    right_tokens = set(re.sub(r"\W+", " ", right.lower()).split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def ensure_candidate_file(path: Path) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    df = pd.DataFrame(columns=BASE_COLUMNS + ["metadata_source", "crossref_status"])
    df.to_csv(path, index=False, encoding="utf-8")
    return df


def crossref_headers(config: dict[str, Any]) -> dict[str, str]:
    headers = {"User-Agent": config.get("user_agent") or "ResearchAgent/0.1"}
    plus_key = os.getenv("CROSSREF_PLUS_API_KEY") or config.get("crossref_plus_api_key") or ""
    if plus_key:
        headers["Crossref-Plus-API-Token"] = f"Bearer {plus_key}"
    return headers


def crossref_params(config: dict[str, Any], extra: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(extra or {})
    email = os.getenv("CROSSREF_EMAIL") or os.getenv("CONTACT_EMAIL") or config.get("crossref_email") or config.get("contact_email") or ""
    if email:
        params["mailto"] = email
    return params


def parse_crossref_item(item: dict[str, Any]) -> dict[str, str]:
    authors = "; ".join(
        " ".join(part for part in [a.get("given", ""), a.get("family", "")] if part).strip()
        for a in item.get("author", [])[:20]
    )
    year_parts = (item.get("published-print") or item.get("published-online") or item.get("issued") or {}).get("date-parts") or []
    year = str(year_parts[0][0]) if year_parts and year_parts[0] else ""
    return {
        "title": (item.get("title") or [""])[0],
        "authors": authors,
        "year": year,
        "source": (item.get("container-title") or [""])[0],
        "doi": normalize_doi(item.get("DOI") or ""),
        "url": item.get("URL") or "",
    }


def fetch_by_doi(doi: str, config: dict[str, Any]) -> dict[str, str] | None:
    response = requests.get(
        f"https://api.crossref.org/works/{doi}",
        params=crossref_params(config),
        headers=crossref_headers(config),
        timeout=30,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return parse_crossref_item(response.json().get("message", {}))


def fetch_by_title(title: str, config: dict[str, Any]) -> dict[str, str] | None:
    response = requests.get(
        "https://api.crossref.org/works",
        params=crossref_params(config, {"query.bibliographic": title, "rows": 1}),
        headers=crossref_headers(config),
        timeout=30,
    )
    response.raise_for_status()
    items = response.json().get("message", {}).get("items", [])
    if not items:
        return None
    parsed = parse_crossref_item(items[0])
    if title_similarity(title, parsed.get("title", "")) < 0.65:
        return None
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich candidate papers with Crossref metadata.")
    parser.add_argument("--project", help="Project directory")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    project_dir = resolve_project(args.project, config)
    path = project_dir / "01_literature_search" / "candidate_papers.csv"
    df = ensure_candidate_file(path)
    for column in BASE_COLUMNS + ["metadata_source", "crossref_status"]:
        if column not in df.columns:
            df[column] = ""

    delay = float(config.get("request_delay_seconds") or 1.0)
    updated = 0
    failures = 0
    for idx, row in df.iterrows():
        try:
            doi = normalize_doi(row.get("doi", ""))
            metadata = fetch_by_doi(doi, config) if doi else fetch_by_title(str(row.get("title", "")), config)
            if not metadata:
                df.at[idx, "crossref_status"] = "not_found"
                time.sleep(delay)
                continue
            changed = False
            for column in ["doi", "title", "authors", "year", "source", "url"]:
                if not str(row.get(column, "")).strip() and metadata.get(column):
                    df.at[idx, column] = metadata[column]
                    changed = True
            df.at[idx, "crossref_status"] = "matched"
            if changed:
                df.at[idx, "metadata_source"] = "Crossref"
                updated += 1
        except Exception as exc:
            failures += 1
            df.at[idx, "crossref_status"] = "error"
            log(project_dir, f"Failed row {idx}: {exc}")
        time.sleep(delay)

    df.to_csv(path, index=False, encoding="utf-8")
    log(project_dir, f"Updated {updated} candidate rows with Crossref; failures={failures}.")
    print(f"crossref_updated={updated} failures={failures}")


if __name__ == "__main__":
    main()
