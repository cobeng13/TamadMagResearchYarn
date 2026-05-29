from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import requests

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.citation_metadata.extract_metadata import (
    KEY_MAP_COLUMNS,
    METADATA_COLUMNS,
    TO_CONFIRM,
    apa_reference,
    bibtex_entry,
    in_text_citation,
    make_key,
)
from scripts.paper_discovery.ai_screen_candidates import extract_output_text, get_api_key


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-nano"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

REVIEW_COLUMNS = [
    "paper_id",
    "citation_key",
    "row_index",
    "ai_metadata_status",
    "ai_change_summary",
    "ai_evidence_snippets",
    "ai_unresolved_fields",
    "ai_checked_at",
    "ai_model",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def paths(project_dir: Path) -> dict[str, Path]:
    metadata = project_dir / "04_metadata"
    return {
        "metadata": metadata / "metadata_table.csv",
        "checked_metadata": metadata / "metadata_table_ai_checked.csv",
        "review": metadata / "metadata_ai_check_report.csv",
        "key_map": metadata / "citation_key_map_ai_checked.csv",
        "apa": metadata / "references_apa7_ai_checked.md",
        "bib": metadata / "references_ai_checked.bib",
        "log": metadata / "metadata_ai_check_log.md",
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


def compact_text(value: Any, max_chars: int) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    return text[:max_chars]


def load_markdown(row: pd.Series, max_chars: int) -> str:
    path = Path(safe_text(row.get("local_markdown_file", "")))
    if not path.exists():
        return ""
    return compact_text(path.read_text(encoding="utf-8", errors="replace"), max_chars)


def ensure_metadata_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in METADATA_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[METADATA_COLUMNS].fillna("")


def rows_to_check(df: pd.DataFrame, limit: int | None = None, offset: int = 0) -> list[int]:
    indexes: list[int] = []
    for idx, row in df.iterrows():
        if idx < offset:
            continue
        if not safe_text(row.get("local_markdown_file", "")):
            continue
        indexes.append(idx)
        if limit is not None and len(indexes) >= limit:
            break
    return indexes


def metadata_payload(row_index: int, row: pd.Series, markdown: str) -> dict[str, Any]:
    current = {column: safe_text(row.get(column, "")) for column in METADATA_COLUMNS}
    return {
        "row_index": row_index,
        "current_metadata": current,
        "markdown": markdown,
    }


def checked_schema() -> dict[str, Any]:
    field_properties = {column: {"type": "string"} for column in METADATA_COLUMNS if column != "citation_key"}
    field_properties["row_index"] = {"type": "integer"}
    field_properties["citation_key"] = {"type": "string"}
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        **field_properties,
                        "ai_metadata_status": {"type": "string", "enum": ["complete", "needs_review"]},
                        "ai_change_summary": {"type": "string"},
                        "ai_evidence_snippets": {"type": "array", "items": {"type": "string"}},
                        "ai_unresolved_fields": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": [
                        "row_index",
                        *METADATA_COLUMNS,
                        "ai_metadata_status",
                        "ai_change_summary",
                        "ai_evidence_snippets",
                        "ai_unresolved_fields",
                    ],
                },
            }
        },
        "required": ["records"],
    }


def build_request_payload(model: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    instructions = (
        "You are checking citation metadata for an academic research workflow. "
        "Use only the supplied markdown text and current metadata. Do not use outside knowledge, web memory, or guesses. "
        "Revise fields only when the markdown provides evidence or when the current value is plainly contradicted by the markdown. "
        f"Use '{TO_CONFIRM}' for unresolved fields. Preserve local_source_file and local_markdown_file. "
        "Return concise evidence snippets copied from the markdown for material changes. "
        "Do not fabricate authors, dates, volume, issue, pages, DOI, publisher, URL, journal, or country context."
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
                        "text": json.dumps({"records": records}, ensure_ascii=False),
                    }
                ],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "metadata_check_batch",
                "schema": checked_schema(),
                "strict": True,
            }
        },
    }


def call_openai_metadata_check(
    api_key: str,
    model: str,
    records: list[dict[str, Any]],
    timeout: int = 120,
    retries: int = 2,
) -> list[dict[str, Any]]:
    payload = build_request_payload(model, records)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            response = requests.post(OPENAI_RESPONSES_URL, headers=headers, json=payload, timeout=timeout)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(2**attempt)
                continue
            response.raise_for_status()
            parsed = json.loads(extract_output_text(response.json()))
            return list(parsed.get("records", []))
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2**attempt)
                continue
    raise RuntimeError(f"OpenAI metadata check failed: {last_error}")


def normalize_checked_record(item: dict[str, Any], original: pd.Series) -> tuple[dict[str, str], dict[str, str]]:
    revised: dict[str, str] = {}
    for column in METADATA_COLUMNS:
        value = safe_text(item.get(column, ""))
        revised[column] = value or safe_text(original.get(column, "")) or TO_CONFIRM
    revised["local_source_file"] = safe_text(original.get("local_source_file", ""))
    revised["local_markdown_file"] = safe_text(original.get("local_markdown_file", ""))
    status = safe_text(item.get("ai_metadata_status", "")) or ("needs_review" if revised.get("notes") else "complete")
    revised["metadata_status"] = status
    revised["notes"] = safe_text(item.get("notes", "")) or safe_text(original.get("notes", ""))

    review = {
        "paper_id": revised["paper_id"],
        "citation_key": revised["citation_key"],
        "row_index": str(item.get("row_index", "")),
        "ai_metadata_status": status,
        "ai_change_summary": safe_text(item.get("ai_change_summary", "")),
        "ai_evidence_snippets": " | ".join(safe_text(value) for value in item.get("ai_evidence_snippets", []) if safe_text(value)),
        "ai_unresolved_fields": "; ".join(safe_text(value) for value in item.get("ai_unresolved_fields", []) if safe_text(value)),
        "ai_checked_at": "",
        "ai_model": "",
    }
    return revised, review


def apply_checked_records(df: pd.DataFrame, checked: list[dict[str, Any]], model: str, checked_at: str) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    revised = df.copy()
    reviews: list[dict[str, str]] = []
    updated = 0
    for item in checked:
        idx = int(item.get("row_index", -1))
        if idx not in revised.index:
            continue
        row, review = normalize_checked_record(item, revised.loc[idx])
        for column, value in row.items():
            revised.at[idx, column] = value
        review["ai_checked_at"] = checked_at
        review["ai_model"] = model
        reviews.append(review)
        updated += 1
    return revised, pd.DataFrame(reviews, columns=REVIEW_COLUMNS).fillna(""), updated


def refresh_citation_keys(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    used: Counter[str] = Counter()
    refreshed: list[dict[str, str]] = []
    for row in rows:
        current = dict(row)
        current["citation_key"] = make_key(current, used)  # type: ignore[arg-type]
        refreshed.append(current)
    return refreshed


def write_checked_outputs(project_dir: Path, metadata: pd.DataFrame, review: pd.DataFrame, apply: bool = False) -> dict[str, Path]:
    p = paths(project_dir)
    metadata_dir = p["metadata"].parent
    metadata_dir.mkdir(parents=True, exist_ok=True)
    rows = refresh_citation_keys(metadata[METADATA_COLUMNS].fillna("").to_dict("records"))
    metadata = pd.DataFrame(rows, columns=METADATA_COLUMNS).fillna("")

    metadata.to_csv(p["checked_metadata"], index=False, encoding="utf-8")
    review.to_csv(p["review"], index=False, encoding="utf-8")
    key_rows = [
        {
            "paper_id": row["paper_id"],
            "citation_key": row["citation_key"],
            "short_in_text_citation": in_text_citation(row),
            "full_apa_reference": apa_reference(row),
            "metadata_status": row["metadata_status"],
            "notes": row["notes"],
        }
        for row in rows
    ]
    pd.DataFrame(key_rows, columns=KEY_MAP_COLUMNS).to_csv(p["key_map"], index=False, encoding="utf-8")
    write_apa(p["apa"], rows)
    write_bib(p["bib"], rows)
    write_log(p["log"], len(rows), len(review), apply)
    if apply:
        backup = p["metadata"].with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak.csv")
        backup.write_bytes(p["metadata"].read_bytes())
        metadata.to_csv(p["metadata"], index=False, encoding="utf-8")
    return p


def write_apa(path: Path, rows: list[dict[str, str]]) -> None:
    lines = ["# APA 7 References - AI Checked", ""]
    for row in sorted(rows, key=lambda item: item["citation_key"]):
        prefix = "- " if row["metadata_status"] == "complete" else "- Not final-ready: "
        lines.append(f"{prefix}{apa_reference(row)}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_bib(path: Path, rows: list[dict[str, str]]) -> None:
    useful = [row for row in rows if row["title"] != TO_CONFIRM and (row["authors"] != TO_CONFIRM or row["doi"] != TO_CONFIRM or row["url"] != TO_CONFIRM)]
    path.write_text("\n\n".join(bibtex_entry(row) for row in useful).rstrip() + ("\n" if useful else ""), encoding="utf-8")


def write_log(path: Path, records: int, checked: int, apply: bool) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path.write_text(
        "\n".join(
            [
                "# AI Metadata Check Log",
                "",
                f"Timestamp: {stamp}",
                f"Records in output: {records}",
                f"Records AI-checked this run: {checked}",
                f"Applied to canonical metadata_table.csv: {'yes' if apply else 'no'}",
                "",
                "AI was instructed to use only local markdown and existing metadata, with unresolved fields left as To be confirmed.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def run_ai_metadata_check(
    project_dir: Path,
    model: str,
    batch_size: int,
    limit: int | None,
    offset: int,
    max_md_chars: int,
    dry_run: bool,
    apply: bool,
    dotenv_path: Path | None = None,
) -> dict[str, Any]:
    p = paths(project_dir)
    if not p["metadata"].exists():
        raise FileNotFoundError(f"Missing metadata table: {p['metadata']}")
    df = ensure_metadata_columns(pd.read_csv(p["metadata"], dtype=str).fillna(""))
    selected = rows_to_check(df, limit=limit, offset=offset)
    if dry_run:
        return {"selected": len(selected), "updated": 0, "paths": p}

    api_key = get_api_key(dotenv_path)
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in the shell or in a local ignored .env file.")

    checked_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_reviews: list[pd.DataFrame] = []
    updated = 0
    revised = df.copy()
    for start in range(0, len(selected), batch_size):
        batch_indexes = selected[start : start + batch_size]
        records = [metadata_payload(idx, revised.loc[idx], load_markdown(revised.loc[idx], max_md_chars)) for idx in batch_indexes]
        checked = call_openai_metadata_check(api_key, model, records)
        revised, review, count = apply_checked_records(revised, checked, model=model, checked_at=checked_at)
        all_reviews.append(review)
        updated += count

    review_df = pd.concat(all_reviews, ignore_index=True) if all_reviews else pd.DataFrame(columns=REVIEW_COLUMNS)
    out_paths = write_checked_outputs(project_dir, revised, review_df, apply=apply)
    return {"selected": len(selected), "updated": updated, "paths": out_paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to check deterministic citation metadata against local markdown.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=os.getenv("AI_METADATA_MODEL", DEFAULT_MODEL), help="OpenAI model for metadata checking")
    parser.add_argument("--batch-size", type=int, default=1, help="Metadata records per API request")
    parser.add_argument("--limit", type=int, help="Maximum records to check")
    parser.add_argument("--offset", type=int, default=0, help="Start at this metadata row offset")
    parser.add_argument("--max-md-chars", type=int, default=60000, help="Maximum markdown characters sent per record")
    parser.add_argument("--dry-run", action="store_true", help="Count rows without calling the API")
    parser.add_argument("--apply", action="store_true", help="Also replace canonical metadata_table.csv after writing checked outputs")
    parser.add_argument("--dotenv", type=Path, help="Optional path to an ignored .env file")
    args = parser.parse_args()

    summary = run_ai_metadata_check(
        project_dir=resolve_project(args.project),
        model=args.model,
        batch_size=args.batch_size,
        limit=args.limit,
        offset=args.offset,
        max_md_chars=args.max_md_chars,
        dry_run=args.dry_run,
        apply=args.apply,
        dotenv_path=args.dotenv,
    )
    print(f"selected={summary['selected']} updated={summary['updated']}")
    if not args.dry_run:
        print(f"checked_metadata={summary['paths']['checked_metadata']}")
        print(f"review_report={summary['paths']['review']}")


if __name__ == "__main__":
    main()
