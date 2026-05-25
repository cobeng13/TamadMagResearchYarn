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


QUEUE_COLUMNS = [
    "paper_id",
    "title",
    "doi",
    "landing_page_url",
    "pdf_url",
    "oa_status",
    "license",
    "source",
    "download_status",
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
        handle.write(f"- {stamp} find_oa_pdfs: {message}\n")


def normalize_doi(value: Any) -> str:
    if pd.isna(value) or not str(value).strip():
        return ""
    doi = str(value).strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.I)
    doi = re.sub(r"^doi:\s*", "", doi, flags=re.I)
    return doi.lower()


def ensure_candidate_file(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=["paper_id", "title", "doi"]).to_csv(path, index=False, encoding="utf-8")
    return pd.DataFrame(columns=["paper_id", "title", "doi"])


def existing_queue(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    path.parent.mkdir(parents=True, exist_ok=True)
    return pd.DataFrame(columns=QUEUE_COLUMNS)


def best_location(data: dict[str, Any]) -> dict[str, Any] | None:
    locations = []
    if data.get("best_oa_location"):
        locations.append(data["best_oa_location"])
    locations.extend(data.get("oa_locations") or [])
    for location in locations:
        pdf_url = location.get("url_for_pdf") or ""
        landing = location.get("url") or location.get("url_for_landing_page") or ""
        if pdf_url or landing:
            return location
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Find legal OA PDFs with Unpaywall.")
    parser.add_argument("--project", help="Project directory")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    project_dir = resolve_project(args.project, config)
    email = os.getenv("UNPAYWALL_EMAIL") or config.get("unpaywall_email") or ""
    if not email:
        log(project_dir, "Missing UNPAYWALL_EMAIL or unpaywall_email in config.")
        raise SystemExit("Unpaywall requires an email. Set UNPAYWALL_EMAIL or config.yaml unpaywall_email.")

    candidate_path = project_dir / "01_literature_search" / "candidate_papers.csv"
    queue_path = project_dir / "02_sources" / "download_queue.csv"
    candidates = ensure_candidate_file(candidate_path)
    queue = existing_queue(queue_path)
    for column in QUEUE_COLUMNS:
        if column not in queue.columns:
            queue[column] = ""

    headers = {"User-Agent": config.get("user_agent") or "ResearchAgent/0.1"}
    delay = float(config.get("request_delay_seconds") or 1.0)
    rows: list[dict[str, str]] = []
    failures = 0
    for _, paper in candidates.iterrows():
        doi = normalize_doi(paper.get("doi", ""))
        if not doi:
            continue
        try:
            response = requests.get(f"https://api.unpaywall.org/v2/{doi}", params={"email": email}, headers=headers, timeout=30)
            if response.status_code == 404:
                time.sleep(delay)
                continue
            response.raise_for_status()
            data = response.json()
            location = best_location(data)
            if not location:
                time.sleep(delay)
                continue
            rows.append(
                {
                    "paper_id": str(paper.get("paper_id", "")),
                    "title": str(paper.get("title", "")),
                    "doi": doi,
                    "landing_page_url": location.get("url") or location.get("url_for_landing_page") or data.get("doi_url") or "",
                    "pdf_url": location.get("url_for_pdf") or "",
                    "oa_status": data.get("oa_status") or "",
                    "license": location.get("license") or "",
                    "source": "Unpaywall",
                    "download_status": "",
                    "notes": f"host_type={location.get('host_type') or ''}; repository={location.get('repository_institution') or ''}".strip(),
                }
            )
        except Exception as exc:
            failures += 1
            log(project_dir, f"Failed DOI {doi}: {exc}")
        time.sleep(delay)

    found = pd.DataFrame(rows, columns=QUEUE_COLUMNS)
    combined = pd.concat([queue, found], ignore_index=True).fillna("")
    combined["_doi_key"] = combined["doi"].map(normalize_doi)
    combined = combined.drop_duplicates(subset=["_doi_key"], keep="first")
    combined = combined.drop(columns=["_doi_key"])
    combined = combined[QUEUE_COLUMNS + [c for c in combined.columns if c not in QUEUE_COLUMNS]]
    combined.to_csv(queue_path, index=False, encoding="utf-8")
    log(project_dir, f"Saved {len(combined)} OA queue rows; failures={failures}.")
    print(f"oa_records={len(combined)} new_records={len(found)} failures={failures}")


if __name__ == "__main__":
    main()
