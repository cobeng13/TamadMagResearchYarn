from __future__ import annotations

import argparse
import hashlib
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


SUCCESS_COLUMNS = [
    "candidate_id",
    "title",
    "doi",
    "pdf_url",
    "saved_path",
    "filename",
    "ai_relevance_label",
    "ai_confidence",
    "downloaded_at",
    "file_size_bytes",
    "sha256",
    "status",
    "reason",
]

FAILED_COLUMNS = [
    "candidate_id",
    "title",
    "doi",
    "pdf_url",
    "ai_relevance_label",
    "ai_confidence",
    "status",
    "reason",
    "error_message",
    "attempted_at",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def parse_tags(value: str | None) -> list[str]:
    if value is None or not str(value).strip():
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return " ".join(str(value).strip().split())


def slugify(value: str, max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", safe_text(value).lower()).strip("-")
    return slug[:max_length].rstrip("-")


def safe_filename(row: pd.Series) -> str:
    candidate = slugify(row.get("candidate_id", ""), 40)
    year = slugify(row.get("year", ""), 10)
    title = slugify(row.get("title", ""), 70)
    parts = [part for part in [candidate, year, title] if part]
    return f"{'_'.join(parts) or hashlib.sha1(safe_text(row.get('pdf_url', '')).encode('utf-8')).hexdigest()[:12]}.pdf"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_pdf_response(response: requests.Response, first_chunk: bytes) -> bool:
    content_type = response.headers.get("Content-Type", "").lower()
    if "pdf" in content_type:
        return True
    return first_chunk.lstrip().startswith(b"%PDF")


def queue_path(project_dir: Path) -> Path:
    return project_dir / "02_sources" / "download_queue.csv"


def result_paths(project_dir: Path) -> dict[str, Path]:
    results = project_dir / "02_sources" / "download_results"
    return {
        "pdf_dir": project_dir / "02_sources" / "pdf",
        "success": results / "success.csv",
        "failed": results / "failed.csv",
        "log": project_dir / "logs" / "pdf_download_log.md",
    }


def success_row(row: pd.Series, path: Path, reason: str) -> dict[str, str]:
    return {
        "candidate_id": safe_text(row.get("candidate_id", "")),
        "title": safe_text(row.get("title", "")),
        "doi": safe_text(row.get("doi", "")),
        "pdf_url": safe_text(row.get("pdf_url", "")),
        "saved_path": str(path),
        "filename": path.name,
        "ai_relevance_label": safe_text(row.get("ai_relevance_label", "")),
        "ai_confidence": safe_text(row.get("ai_confidence", "")),
        "downloaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "file_size_bytes": str(path.stat().st_size),
        "sha256": sha256_file(path),
        "status": "success",
        "reason": reason,
    }


def failed_row(row: pd.Series, reason: str, error_message: str = "") -> dict[str, str]:
    return {
        "candidate_id": safe_text(row.get("candidate_id", "")),
        "title": safe_text(row.get("title", "")),
        "doi": safe_text(row.get("doi", "")),
        "pdf_url": safe_text(row.get("pdf_url", "")),
        "ai_relevance_label": safe_text(row.get("ai_relevance_label", "")),
        "ai_confidence": safe_text(row.get("ai_confidence", "")),
        "status": "failed",
        "reason": reason,
        "error_message": safe_text(error_message),
        "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def download_one(row: pd.Series, destination: Path, timeout: int, retries: int) -> tuple[bool, str]:
    url = safe_text(row.get("pdf_url", ""))
    headers = {"User-Agent": "ResearchAgent/0.1"}
    last_error = ""
    for attempt in range(retries + 1):
        try:
            with requests.get(url, headers=headers, timeout=timeout, stream=True, allow_redirects=True) as response:
                response.raise_for_status()
                iterator = response.iter_content(chunk_size=1024 * 128)
                first_chunk = next(iterator, b"")
                if not is_pdf_response(response, first_chunk):
                    return False, "not_pdf_response"
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("wb") as handle:
                    if first_chunk:
                        handle.write(first_chunk)
                    for chunk in iterator:
                        if chunk:
                            handle.write(chunk)
            if not destination.exists() or destination.stat().st_size == 0:
                destination.unlink(missing_ok=True)
                return False, "not_pdf_response"
            return True, ""
        except Exception as exc:
            last_error = safe_text(exc)
            if attempt < retries:
                time.sleep(min(2**attempt, 5))
                continue
    destination.unlink(missing_ok=True)
    return False, last_error or "request_failed"


def download_pdfs(
    project_dir: Path,
    tags: list[str] | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    timeout: int = 30,
    retries: int = 3,
) -> dict[str, Any]:
    path = queue_path(project_dir)
    if not path.exists():
        raise FileNotFoundError(f"Missing download queue: {path}")
    queue = pd.read_csv(path, dtype=str).fillna("")
    selected_tags = tags or []
    rows = queue[queue.get("download_status", "") == "queued"] if "download_status" in queue.columns else queue.iloc[0:0]
    if selected_tags:
        rows = rows[rows.get("ai_relevance_label", "").isin(selected_tags)]
    if limit is not None:
        rows = rows.head(limit)

    paths = result_paths(project_dir)
    successes: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []

    for _, row in rows.iterrows():
        pdf_url = safe_text(row.get("pdf_url", ""))
        destination = paths["pdf_dir"] / (safe_text(row.get("target_filename", "")) or safe_filename(row))
        if not pdf_url:
            failures.append(failed_row(row, "missing_pdf_url"))
            continue
        if destination.exists() and not overwrite:
            successes.append(success_row(row, destination, "file_already_exists"))
            continue
        if dry_run:
            continue
        ok, detail = download_one(row, destination, timeout=timeout, retries=retries)
        if ok and destination.exists():
            successes.append(success_row(row, destination, "downloaded"))
        elif detail == "not_pdf_response":
            failures.append(failed_row(row, "not_pdf_response"))
        else:
            failures.append(failed_row(row, "request_failed", detail))

    success_df = pd.DataFrame(successes, columns=SUCCESS_COLUMNS).fillna("")
    failed_df = pd.DataFrame(failures, columns=FAILED_COLUMNS).fillna("")
    if not dry_run:
        paths["success"].parent.mkdir(parents=True, exist_ok=True)
        success_df.to_csv(paths["success"], index=False, encoding="utf-8")
        failed_df.to_csv(paths["failed"], index=False, encoding="utf-8")
        write_log(paths["log"], selected_tags, len(rows), len(success_df), len(failed_df), paths)

    return {
        "selected_count": len(rows),
        "success_count": len(success_df),
        "failed_count": len(failed_df),
        "success": success_df,
        "failed": failed_df,
        "paths": paths,
    }


def write_log(log_path: Path, tags: list[str], selected_count: int, success_count: int, failed_count: int, paths: dict[str, Path]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {stamp} PDF download\n")
        handle.write(f"- selected tags: {', '.join(tags) if tags else '(all)'}\n")
        handle.write(f"- candidates read: {selected_count}\n")
        handle.write(f"- success count: {success_count}\n")
        handle.write(f"- failed count: {failed_count}\n")
        handle.write(f"- output paths: {paths['pdf_dir']}; {paths['success']}; {paths['failed']}\n\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download legal PDFs from download_queue.csv.")
    parser.add_argument("--project", default="projects/sample_project", help="Project directory")
    parser.add_argument("--tags", help="Comma-separated AI relevance labels")
    parser.add_argument("--limit", type=int, default=50, help="Maximum queue rows to process")
    parser.add_argument("--dry-run", action="store_true", help="Do not download PDFs or write result files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing local PDFs")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Retry count for request failures")
    args = parser.parse_args()

    summary = download_pdfs(
        project_dir=resolve_project(args.project),
        tags=parse_tags(args.tags),
        limit=args.limit,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        timeout=args.timeout,
        retries=args.retries,
    )
    print(f"selected={summary['selected_count']} success={summary['success_count']} failed={summary['failed_count']}")
    if not args.dry_run:
        print(f"success_path={summary['paths']['success']}")
        print(f"failed_path={summary['paths']['failed']}")


if __name__ == "__main__":
    main()
