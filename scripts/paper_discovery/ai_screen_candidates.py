from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-nano"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

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

RELEVANCE_LABELS = [
    "highly_relevant",
    "possibly_relevant",
    "background_only",
    "out_of_scope",
    "insufficient_metadata",
]

SUGGESTED_ACTIONS = [
    "screen_full_text",
    "keep_for_background",
    "exclude_after_human_review",
    "needs_metadata_check",
    "needs_query_followup",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def get_api_key(dotenv_path: Path | None = None) -> str:
    if dotenv_path:
        load_dotenv(dotenv_path)
    else:
        load_dotenv(repo_root() / ".env")
    return os.getenv("OPENAI_API_KEY", "").strip()


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
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "screenings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "row_index": {"type": "integer"},
                        "candidate_id": {"type": "string"},
                        "ai_relevance_label": {"type": "string", "enum": RELEVANCE_LABELS},
                        "ai_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "ai_reason": {"type": "string"},
                        "ai_suggested_action": {"type": "string", "enum": SUGGESTED_ACTIONS},
                        "ai_key_terms": {"type": "array", "items": {"type": "string"}},
                        "ai_metadata_warnings": {"type": "string"},
                    },
                    "required": [
                        "row_index",
                        "candidate_id",
                        "ai_relevance_label",
                        "ai_confidence",
                        "ai_reason",
                        "ai_suggested_action",
                        "ai_key_terms",
                        "ai_metadata_warnings",
                    ],
                },
            }
        },
        "required": ["screenings"],
    }


def build_request_payload(model: str, research_brief: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
    instructions = (
        "You are screening candidate academic papers for a conservative research workflow. "
        "Use only the supplied research brief and candidate metadata. Do not invent papers, findings, URLs, DOIs, or full-text availability. "
        "Do not make final human decisions. Return screening suggestions only. "
        "Prioritize direct Radiologic Technology or radiography licensure evidence, especially Philippine studies. "
        "Allied health licensure prediction studies can be relevant as supporting/background evidence. "
        "Exclude clinical imaging technique papers, unrelated radiology clinical papers, and papers with no education/licensure/predictor angle."
    )
    return {
        "model": model,
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(
                            {
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
                            ensure_ascii=False,
                        ),
                    }
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "candidate_screening_batch",
                "schema": screening_schema(),
                "strict": True,
            }
        },
    }


def extract_output_text(response_json: dict[str, Any]) -> str:
    if response_json.get("output_text"):
        return str(response_json["output_text"])
    parts: list[str] = []
    for item in response_json.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                parts.append(str(content["text"]))
    return "\n".join(parts)


def call_openai_screening(
    api_key: str,
    model: str,
    research_brief: str,
    candidates: list[dict[str, Any]],
    timeout: int = 90,
    retries: int = 2,
) -> list[dict[str, Any]]:
    payload = build_request_payload(model, research_brief, candidates)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = requests.post(OPENAI_RESPONSES_URL, headers=headers, json=payload, timeout=timeout)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(2**attempt)
                continue
            response.raise_for_status()
            data = response.json()
            parsed = json.loads(extract_output_text(data))
            return list(parsed.get("screenings", []))
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2**attempt)
                continue
    raise RuntimeError(f"OpenAI screening request failed: {last_error}")


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
    return {"selected": len(selected), "updated": updated, "csv_path": str(csv_path), "backup_path": backup_path}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to add AI screening suggestions to candidate_papers.csv.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=os.getenv("AI_SCREENING_MODEL", DEFAULT_MODEL), help="OpenAI model for screening")
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

