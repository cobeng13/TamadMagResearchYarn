from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ai.client import AIClient, extract_output_text, get_env_model, load_dotenv, require_api_key
from scripts.ai.logging import write_ai_run_log
from scripts.ai.prompts import build_candidate_screening_prompt
from scripts.ai.schemas import SCREENING_ACTIONS, SCREENING_LABELS, candidate_screening_schema


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-nano"

AI_COLUMNS = [
    "ai_relevance_label",
    "ai_confidence",
    "ai_reason",
    "ai_suggested_action",
    "ai_key_terms",
    "ai_metadata_warnings",
    "ai_screened_at",
    "ai_model",
]

RELEVANCE_LABELS = SCREENING_LABELS
SUGGESTED_ACTIONS = SCREENING_ACTIONS


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def get_api_key(dotenv_path: Path | None = None) -> str:
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv(repo_root() / ".env")
    return require_api_key(dry_run=True) or ""


def ensure_ai_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in AI_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df.fillna("")


def candidate_path(project_dir: Path) -> Path:
    return project_dir / "01_literature_search" / "candidate_papers.csv"


def brief_path(project_dir: Path) -> Path:
    return project_dir / "00_brief" / "research_brief.md"


def compact_text(value: Any, max_chars: int = 1800) -> str:
    text = " ".join(str(value or "").split())
    return text[:max_chars]


def candidate_payload(row_index: int, row: pd.Series) -> dict[str, Any]:
    return {
        "row_index": row_index,
        "candidate_id": compact_text(row.get("candidate_id", ""), 300),
        "title": compact_text(row.get("title", ""), 500),
        "authors": compact_text(row.get("authors", ""), 500),
        "year": compact_text(row.get("year", ""), 20),
        "journal_or_repository": compact_text(row.get("journal_or_repository", ""), 300),
        "source_providers": compact_text(row.get("source_providers", ""), 300),
        "search_query": compact_text(row.get("search_query", ""), 500),
        "doi": compact_text(row.get("doi", ""), 200),
        "is_open_access": compact_text(row.get("is_open_access", ""), 20),
        "oa_status": compact_text(row.get("oa_status", ""), 50),
        "abstract": compact_text(row.get("abstract", ""), 1800),
        "keywords": compact_text(row.get("keywords", ""), 600),
        "fields_of_study": compact_text(row.get("fields_of_study", ""), 600),
        "publication_types": compact_text(row.get("publication_types", ""), 300),
        "ranking_score": compact_text(row.get("ranking_score", ""), 50),
    }


def rows_to_screen(
    df: pd.DataFrame,
    limit: int | None = None,
    offset: int = 0,
    force: bool = False,
    include_human_reviewed: bool = False,
) -> list[int]:
    indexes: list[int] = []
    for idx, row in df.iterrows():
        if idx < offset:
            continue
        if not force and str(row.get("ai_screened_at", "")).strip():
            continue
        if not include_human_reviewed and (
            str(row.get("human_decision", "")).strip() or str(row.get("screening_status", "")).strip() not in {"", "unscreened"}
        ):
            continue
        if not str(row.get("title", "")).strip() and not str(row.get("abstract", "")).strip():
            continue
        indexes.append(idx)
        if limit is not None and len(indexes) >= limit:
            break
    return indexes


def screening_schema() -> dict[str, Any]:
    return candidate_screening_schema()


def build_request_payload(model: str, research_brief: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_candidate_screening_prompt(),
        input_data={
            "research_brief": research_brief,
            "label_definitions": {
                "highly_relevant": "Directly about Radiologic Technology/radiography licensure, board performance, academic predictors, pre-board/mock board, clinical/internship, or predictive validity.",
                "possibly_relevant": "Likely useful but indirect, incomplete, or not Radiologic Technology-specific.",
                "background_only": "Useful context for licensure, health professions education, policy, or methods but not central evidence.",
                "out_of_scope": "Unrelated to licensure/board performance, education predictors, or health professions assessment.",
                "insufficient_metadata": "Not enough title/abstract/metadata to judge.",
            },
            "candidates": candidates,
        },
        schema=screening_schema(),
        schema_name="candidate_screening_batch",
    )


def call_openai_screening(
    api_key: str,
    model: str,
    research_brief: str,
    candidates: list[dict[str, Any]],
    timeout: int = 90,
    retries: int = 2,
) -> list[dict[str, Any]]:
    try:
        parsed = AIClient(api_key=api_key, default_model=model).responses_json(
            instructions=build_candidate_screening_prompt(),
            input_data={
                "research_brief": research_brief,
                "label_definitions": {
                    "highly_relevant": "Directly about Radiologic Technology/radiography licensure, board performance, academic predictors, pre-board/mock board, clinical/internship, or predictive validity.",
                    "possibly_relevant": "Likely useful but indirect, incomplete, or not Radiologic Technology-specific.",
                    "background_only": "Useful context for licensure, health professions education, policy, or methods but not central evidence.",
                    "out_of_scope": "Unrelated to licensure/board performance, education predictors, or health professions assessment.",
                    "insufficient_metadata": "Not enough title/abstract/metadata to judge.",
                },
                "candidates": candidates,
            },
            schema=screening_schema(),
            schema_name="candidate_screening_batch",
            timeout=timeout,
            retries=retries,
        )
        return list(parsed.get("screenings", []))
    except Exception as exc:
        raise RuntimeError(f"OpenAI screening request failed: {exc}") from exc


def apply_screenings(df: pd.DataFrame, screenings: list[dict[str, Any]], model: str, screened_at: str) -> int:
    updated = 0
    for item in screenings:
        idx = int(item.get("row_index", -1))
        if idx not in df.index:
            continue
        df.at[idx, "ai_relevance_label"] = str(item.get("ai_relevance_label", ""))
        df.at[idx, "ai_confidence"] = str(item.get("ai_confidence", ""))
        df.at[idx, "ai_reason"] = compact_text(item.get("ai_reason", ""), 800)
        df.at[idx, "ai_suggested_action"] = str(item.get("ai_suggested_action", ""))
        df.at[idx, "ai_key_terms"] = "; ".join(str(term) for term in item.get("ai_key_terms", []) if str(term).strip())
        df.at[idx, "ai_metadata_warnings"] = compact_text(item.get("ai_metadata_warnings", ""), 500)
        df.at[idx, "ai_screened_at"] = screened_at
        df.at[idx, "ai_model"] = model
        updated += 1
    return updated


def backup_csv(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(f".{stamp}.bak.csv")
    backup.write_bytes(path.read_bytes())
    return backup


def run_screening(
    project_dir: Path,
    model: str,
    batch_size: int,
    limit: int | None,
    offset: int,
    force: bool,
    include_human_reviewed: bool,
    dry_run: bool,
    no_backup: bool,
    dotenv_path: Path | None = None,
) -> dict[str, Any]:
    csv_path = candidate_path(project_dir)
    brief_file = brief_path(project_dir)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing candidate CSV: {csv_path}")
    if not brief_file.exists():
        raise FileNotFoundError(f"Missing research brief: {brief_file}")

    df = ensure_ai_columns(pd.read_csv(csv_path, dtype=str).fillna(""))
    selected = rows_to_screen(df, limit=limit, offset=offset, force=force, include_human_reviewed=include_human_reviewed)
    if dry_run:
        return {"selected": len(selected), "updated": 0, "csv_path": str(csv_path), "backup_path": ""}

    api_key = get_api_key(dotenv_path)
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in the shell or in a local ignored .env file.")

    backup_path = "" if no_backup else str(backup_csv(csv_path))
    research_brief = brief_file.read_text(encoding="utf-8")
    updated = 0
    screened_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for start in range(0, len(selected), batch_size):
        batch_indexes = selected[start : start + batch_size]
        payload_rows = [candidate_payload(idx, df.loc[idx]) for idx in batch_indexes]
        screenings = call_openai_screening(api_key, model, research_brief, payload_rows)
        updated += apply_screenings(df, screenings, model=model, screened_at=screened_at)
        df.to_csv(csv_path, index=False, encoding="utf-8")
    write_ai_run_log(
        project_dir / "01_literature_search" / "ai_screening_log.md",
        task_name="candidate_screening",
        model=model,
        input_paths=[brief_file, csv_path],
        output_paths=[csv_path],
        counts={"attempted": len(selected), "succeeded": updated, "failed": max(len(selected) - updated, 0)},
        prompt_version="candidate_screening_v1",
    )
    return {"selected": len(selected), "updated": updated, "csv_path": str(csv_path), "backup_path": backup_path}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to add AI screening suggestions to candidate_papers.csv.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=get_env_model("AI_SCREENING_MODEL", DEFAULT_MODEL), help="OpenAI model for screening")
    parser.add_argument("--batch-size", type=int, default=20, help="Candidate rows per API request")
    parser.add_argument("--limit", type=int, help="Maximum rows to screen this run")
    parser.add_argument("--offset", type=int, default=0, help="Start at this CSV row offset")
    parser.add_argument("--force", action="store_true", help="Rescreen rows that already have ai_screened_at")
    parser.add_argument("--include-human-reviewed", action="store_true", help="Allow AI suggestions on rows already reviewed by a human")
    parser.add_argument("--dry-run", action="store_true", help="Count rows that would be screened without calling the API")
    parser.add_argument("--no-backup", action="store_true", help="Do not create a timestamped CSV backup before writing")
    parser.add_argument("--dotenv", type=Path, help="Optional path to an ignored .env file")
    args = parser.parse_args()

    summary = run_screening(
        project_dir=resolve_project(args.project),
        model=args.model,
        batch_size=args.batch_size,
        limit=args.limit,
        offset=args.offset,
        force=args.force,
        include_human_reviewed=args.include_human_reviewed,
        dry_run=args.dry_run,
        no_backup=args.no_backup,
        dotenv_path=args.dotenv,
    )
    print(f"selected={summary['selected']} updated={summary['updated']}")
    print(f"csv_path={summary['csv_path']}")
    if summary["backup_path"]:
        print(f"backup_path={summary['backup_path']}")


if __name__ == "__main__":
    main()
