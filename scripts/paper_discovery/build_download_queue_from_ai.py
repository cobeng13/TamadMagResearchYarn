from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.paper_discovery.config import load_config


QUEUE_COLUMNS = [
    "candidate_id",
    "title",
    "authors",
    "year",
    "doi",
    "url",
    "pdf_url",
    "journal_or_repository",
    "source_providers",
    "ai_relevance_label",
    "ai_confidence",
    "ai_reason",
    "ai_suggested_action",
    "ai_key_terms",
    "ai_metadata_warnings",
    "access_type",
    "oa_status",
    "license",
    "download_status",
    "download_reason",
    "target_filename",
    "source_candidate_file",
]

TAG_FILES = ["highly_relevant", "possibly_relevant", "background_only"]
DEFAULT_TAGS = ["highly_relevant"]
DEFAULT_ACTIONS = ["screen_full_text"]
UNPAYWALL_URL = "https://api.unpaywall.org/v2/{doi}"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def parse_csv_option(value: str | None, default: list[str]) -> list[str]:
    if value is None or str(value).strip() == "":
        return list(default)
    return [part.strip() for part in str(value).split(",") if part.strip()]


def candidate_path(project_dir: Path) -> Path:
    return project_dir / "01_literature_search" / "candidate_papers.csv"


def output_paths(project_dir: Path) -> dict[str, Path]:
    sources = project_dir / "02_sources"
    by_tag = sources / "download_queue_by_tag"
    return {
        "queue": sources / "download_queue.csv",
        "excluded": sources / "download_queue_excluded.csv",
        "by_tag": by_tag,
        "log": project_dir / "logs" / "download_queue_log.md",
    }


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return " ".join(str(value).strip().split())


def confidence(value: Any) -> float:
    try:
        return float(safe_text(value))
    except ValueError:
        return 0.0


def slugify(value: str, max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", safe_text(value).lower()).strip("-")
    return slug[:max_length].rstrip("-")


def target_filename(row: pd.Series) -> str:
    candidate = slugify(row.get("candidate_id", ""), 40)
    year = slugify(row.get("year", ""), 10)
    title = slugify(row.get("title", ""), 70)
    parts = [part for part in [candidate, year, title] if part]
    return f"{'_'.join(parts) or 'paper'}.pdf"


def empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=QUEUE_COLUMNS)


def queue_row(row: pd.Series, reason: str, source_file: Path, pdf_url: str | None = None, extra: dict[str, str] | None = None) -> dict[str, str]:
    data = {column: safe_text(row.get(column, "")) for column in QUEUE_COLUMNS}
    data["pdf_url"] = safe_text(pdf_url) if pdf_url is not None else safe_text(row.get("pdf_url", ""))
    data["download_status"] = "queued"
    data["download_reason"] = reason
    data["target_filename"] = target_filename(row)
    data["source_candidate_file"] = str(source_file)
    if extra:
        data.update(extra)
    return data


def excluded_row(row: pd.Series, reason: str, source_file: Path) -> dict[str, str]:
    data = queue_row(row, reason, source_file)
    data["download_status"] = "excluded"
    data["download_reason"] = reason
    return data


def unpaywall_email(config: dict[str, Any]) -> str:
    return os.getenv("UNPAYWALL_EMAIL", "").strip() or safe_text(config.get("unpaywall_email", ""))


def lookup_unpaywall_pdf(doi: str, email: str, timeout: int = 30) -> dict[str, str] | None:
    try:
        response = requests.get(UNPAYWALL_URL.format(doi=doi), params={"email": email}, timeout=timeout)
        if response.status_code == 404:
            return None
        response.raise_for_status()
    except requests.RequestException:
        return None
    data = response.json()
    locations: list[dict[str, Any]] = []
    if isinstance(data.get("best_oa_location"), dict):
        locations.append(data["best_oa_location"])
    locations.extend(location for location in data.get("oa_locations", []) if isinstance(location, dict))
    for location in locations:
        pdf_url = safe_text(location.get("url_for_pdf", ""))
        if pdf_url:
            return {
                "pdf_url": pdf_url,
                "url": safe_text(location.get("url") or location.get("url_for_landing_page") or data.get("doi_url", "")),
                "oa_status": safe_text(data.get("oa_status", "")),
                "license": safe_text(location.get("license", "")),
                "access_type": safe_text(data.get("oa_status", "")),
            }
    return None


def build_download_queue(
    project_dir: Path,
    tags: list[str] | None = None,
    min_confidence: float = 0.0,
    actions: list[str] | None = None,
    dry_run: bool = False,
    overwrite: bool = False,
    limit: int | None = None,
    include_existing_pdf_url: bool = False,
    use_unpaywall: bool = False,
    config_path: Path | None = None,
) -> dict[str, Any]:
    del include_existing_pdf_url  # Existing legal PDF URLs in candidate metadata are always honored.
    selected_tags = tags or list(DEFAULT_TAGS)
    selected_actions = actions or list(DEFAULT_ACTIONS)
    csv_path = candidate_path(project_dir)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing candidate CSV: {csv_path}")

    paths = output_paths(project_dir)
    if not dry_run and paths["queue"].exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing queue without --overwrite: {paths['queue']}")

    df = pd.read_csv(csv_path, dtype=str).fillna("")
    config = load_config(config_path)
    email = unpaywall_email(config)
    if use_unpaywall and not email:
        raise RuntimeError("Unpaywall lookup requires UNPAYWALL_EMAIL or config.yaml unpaywall_email.")

    queued: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    considered = 0

    for _, row in df.iterrows():
        label = safe_text(row.get("ai_relevance_label", ""))
        action = safe_text(row.get("ai_suggested_action", ""))
        row_confidence = confidence(row.get("ai_confidence", ""))
        doi = safe_text(row.get("doi", ""))
        pdf_url = safe_text(row.get("pdf_url", ""))

        if label not in selected_tags:
            excluded.append(excluded_row(row, "skipped_tag_not_selected", csv_path))
            continue
        if row_confidence < min_confidence:
            excluded.append(excluded_row(row, "skipped_low_confidence", csv_path))
            continue
        if "ai_suggested_action" in df.columns and action not in selected_actions:
            excluded.append(excluded_row(row, "skipped_action_not_selected", csv_path))
            continue
        if not doi and not pdf_url:
            excluded.append(excluded_row(row, "skipped_no_doi_or_pdf_url", csv_path))
            continue

        considered += 1
        if pdf_url:
            queued.append(queue_row(row, "queued_existing_pdf_url", csv_path))
        elif doi and use_unpaywall:
            found = lookup_unpaywall_pdf(doi, email)
            if found:
                queued.append(queue_row(row, "queued_unpaywall_oa_pdf", csv_path, pdf_url=found["pdf_url"], extra=found))
            else:
                excluded.append(excluded_row(row, "no_legal_oa_pdf_found", csv_path))
        else:
            excluded.append(excluded_row(row, "needs_oa_lookup", csv_path))

        if limit is not None and len(queued) >= limit:
            break

    queue_df = pd.DataFrame(queued, columns=QUEUE_COLUMNS).fillna("")
    excluded_df = pd.DataFrame(excluded, columns=QUEUE_COLUMNS).fillna("")

    if not dry_run:
        paths["queue"].parent.mkdir(parents=True, exist_ok=True)
        paths["by_tag"].mkdir(parents=True, exist_ok=True)
        queue_df.to_csv(paths["queue"], index=False, encoding="utf-8")
        excluded_df.to_csv(paths["excluded"], index=False, encoding="utf-8")
        for tag in TAG_FILES:
            tag_df = queue_df[queue_df["ai_relevance_label"] == tag] if not queue_df.empty else empty_frame()
            tag_df.to_csv(paths["by_tag"] / f"{tag}.csv", index=False, encoding="utf-8")
        write_log(paths["log"], selected_tags, selected_actions, min_confidence, len(df), len(queue_df), len(excluded_df), paths)

    return {
        "candidates_read": len(df),
        "considered": considered,
        "queued_count": len(queue_df),
        "excluded_count": len(excluded_df),
        "queue": queue_df,
        "excluded": excluded_df,
        "paths": paths,
    }


def write_log(
    log_path: Path,
    tags: list[str],
    actions: list[str],
    min_confidence: float,
    candidates_read: int,
    queued_count: int,
    excluded_count: int,
    paths: dict[str, Path],
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {stamp} download queue\n")
        handle.write(f"- selected tags: {', '.join(tags)}\n")
        handle.write(f"- selected actions: {', '.join(actions)}\n")
        handle.write(f"- min confidence: {min_confidence}\n")
        handle.write(f"- candidates read: {candidates_read}\n")
        handle.write(f"- queued count: {queued_count}\n")
        handle.write(f"- excluded count: {excluded_count}\n")
        handle.write(f"- output paths: {paths['queue']}; {paths['excluded']}; {paths['by_tag']}\n\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a legal OA PDF download queue from AI tags in candidate_papers.csv.")
    parser.add_argument("--project", default="projects/sample_project", help="Project directory")
    parser.add_argument("--tags", default=",".join(DEFAULT_TAGS), help="Comma-separated AI relevance labels")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Minimum AI confidence")
    parser.add_argument("--actions", default=",".join(DEFAULT_ACTIONS), help="Comma-separated AI suggested actions")
    parser.add_argument("--dry-run", action="store_true", help="Compute counts without writing files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing download_queue.csv")
    parser.add_argument("--limit", type=int, help="Maximum queued rows")
    parser.add_argument("--include-existing-pdf-url", action="store_true", help="Honor existing candidate pdf_url values")
    parser.add_argument("--unpaywall", dest="use_unpaywall", action="store_true", help="Look up legal OA PDFs with Unpaywall")
    parser.add_argument("--no-unpaywall", dest="use_unpaywall", action="store_false", help="Disable Unpaywall lookup")
    parser.set_defaults(use_unpaywall=True)
    parser.add_argument("--config", type=Path, help="Optional config.yaml path")
    args = parser.parse_args()

    summary = build_download_queue(
        project_dir=resolve_project(args.project),
        tags=parse_csv_option(args.tags, DEFAULT_TAGS),
        min_confidence=args.min_confidence,
        actions=parse_csv_option(args.actions, DEFAULT_ACTIONS),
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        limit=args.limit,
        include_existing_pdf_url=args.include_existing_pdf_url,
        use_unpaywall=args.use_unpaywall,
        config_path=args.config,
    )
    print(f"candidates_read={summary['candidates_read']} queued={summary['queued_count']} excluded={summary['excluded_count']}")
    if not args.dry_run:
        print(f"queue_path={summary['paths']['queue']}")


if __name__ == "__main__":
    main()
