from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml
from slugify import slugify
from tqdm import tqdm


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
        handle.write(f"- {stamp} download_pdfs: {message}\n")


def ensure_queue(path: Path) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    df = pd.DataFrame(columns=QUEUE_COLUMNS)
    df.to_csv(path, index=False, encoding="utf-8")
    return df


def load_candidates(project_dir: Path) -> pd.DataFrame:
    path = project_dir / "01_literature_search" / "candidate_papers.csv"
    if path.exists():
        return pd.read_csv(path, dtype=str).fillna("")
    return pd.DataFrame()


def first_author(authors: str) -> str:
    first = (authors or "").split(";")[0].strip()
    if "," in first:
        return first.split(",", 1)[0].strip()
    parts = first.split()
    return parts[-1] if parts else ""


def safe_filename(row: pd.Series, candidates: pd.DataFrame) -> str:
    paper_id = str(row.get("paper_id", "")).strip()
    title = str(row.get("title", "")).strip()
    match = candidates[candidates.get("paper_id", pd.Series(dtype=str)) == paper_id] if not candidates.empty else pd.DataFrame()
    authors = str(match.iloc[0].get("authors", "")) if not match.empty else ""
    year = str(match.iloc[0].get("year", "")) if not match.empty else ""
    author = first_author(authors)
    short_title = slugify(title, max_length=60) or hashlib.sha1(title.encode("utf-8")).hexdigest()[:10]
    if paper_id and author and year:
        base = "_".join(filter(None, [paper_id, slugify(author, max_length=24), slugify(year), short_title]))
    else:
        key = title or str(row.get("doi", "")) or paper_id
        base = "_".join(filter(None, [paper_id, hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]]))
    return f"{base}.pdf"


def download_pdf(url: str, destination: Path, user_agent: str) -> None:
    headers = {"User-Agent": user_agent}
    with requests.get(url, headers=headers, timeout=60, stream=True, allow_redirects=True) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 128):
                if chunk:
                    handle.write(chunk)
    if destination.stat().st_size == 0:
        destination.unlink(missing_ok=True)
        raise ValueError("Downloaded file is empty.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download legal OA PDFs from the project queue.")
    parser.add_argument("--project", help="Project directory")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    parser.add_argument("--force", action="store_true", help="Re-download existing PDFs")
    args = parser.parse_args()

    config = load_config(args.config)
    project_dir = resolve_project(args.project, config)
    queue_path = project_dir / "02_sources" / "download_queue.csv"
    pdf_dir = project_dir / "02_sources" / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    queue = ensure_queue(queue_path)
    for column in QUEUE_COLUMNS + ["local_pdf_path"]:
        if column not in queue.columns:
            queue[column] = ""
    candidates = load_candidates(project_dir)
    user_agent = config.get("user_agent") or "ResearchAgent/0.1"

    downloaded = 0
    failures = 0
    skipped = 0
    for idx, row in tqdm(queue.iterrows(), total=len(queue), desc="PDFs"):
        pdf_url = str(row.get("pdf_url", "")).strip()
        if not pdf_url:
            queue.at[idx, "download_status"] = "skipped_no_pdf_url"
            skipped += 1
            continue
        destination = pdf_dir / safe_filename(row, candidates)
        queue.at[idx, "local_pdf_path"] = str(destination.relative_to(repo_root())) if destination.is_relative_to(repo_root()) else str(destination)
        if destination.exists() and not args.force:
            queue.at[idx, "download_status"] = "downloaded"
            skipped += 1
            continue
        try:
            download_pdf(pdf_url, destination, user_agent)
            queue.at[idx, "download_status"] = "downloaded"
            downloaded += 1
        except Exception as exc:
            failures += 1
            queue.at[idx, "download_status"] = "failed"
            queue.at[idx, "notes"] = (str(row.get("notes", "")).strip() + f"; download_error={exc}").strip("; ")
            log(project_dir, f"Failed download for row {idx} ({pdf_url}): {exc}")

    queue.to_csv(queue_path, index=False, encoding="utf-8")
    log(project_dir, f"Downloaded={downloaded}; skipped={skipped}; failures={failures}.")
    print(f"pdfs_downloaded={downloaded} skipped={skipped} failures={failures}")


if __name__ == "__main__":
    main()
