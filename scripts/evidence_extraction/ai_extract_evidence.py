from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ai.client import AIClient, get_env_model
from scripts.ai.logging import write_ai_run_log
from scripts.ai.prompts import build_evidence_extraction_prompt
from scripts.ai.schemas import EVIDENCE_COLUMNS, SUMMARY_SECTIONS, evidence_extraction_schema
from scripts.paper_discovery.ai_screen_candidates import get_api_key


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-mini"
TO_CONFIRM = "To be confirmed."


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def paths(project_dir: Path) -> dict[str, Path]:
    base = project_dir / "05_evidence_extraction"
    return {
        "metadata_ai": project_dir / "04_metadata" / "metadata_table_ai_checked.csv",
        "metadata": project_dir / "04_metadata" / "metadata_table.csv",
        "brief_dir": project_dir / "00_brief",
        "output_dir": base,
        "summaries": base / "paper_summaries",
        "evidence": base / "evidence_table.csv",
        "log": base / "extraction_log.md",
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


def slugify(value: str, max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", safe_text(value).lower()).strip("-")
    return slug[:max_length].rstrip("-") or "paper"


def load_research_context(project_dir: Path, max_chars: int = 20000) -> str:
    brief_dir = paths(project_dir)["brief_dir"]
    if not brief_dir.exists():
        return ""
    names = [
        "research_brief.md",
        "research_questions.md",
        "variables.md",
        "inclusion_exclusion_criteria.md",
        "source_strategy.md",
        "writing_scope.md",
    ]
    chunks: list[str] = []
    for name in names:
        path = brief_dir / name
        if path.exists():
            chunks.append(f"# {name}\n\n{path.read_text(encoding='utf-8', errors='replace')}")
    return compact_text("\n\n".join(chunks), max_chars)


def load_metadata(project_dir: Path) -> tuple[pd.DataFrame, Path]:
    p = paths(project_dir)
    source = p["metadata_ai"] if p["metadata_ai"].exists() else p["metadata"]
    if not source.exists():
        raise FileNotFoundError(f"Missing metadata table: {source}")
    return pd.read_csv(source, dtype=str).fillna(""), source


def rows_to_extract(df: pd.DataFrame, limit: int | None = None, offset: int = 0) -> list[int]:
    indexes: list[int] = []
    for idx, row in df.iterrows():
        if idx < offset:
            continue
        markdown = Path(safe_text(row.get("local_markdown_file", "")))
        if not markdown.exists():
            continue
        indexes.append(idx)
        if limit is not None and len(indexes) >= limit:
            break
    return indexes


def full_citation(row: pd.Series) -> str:
    authors = safe_text(row.get("authors", "")) or TO_CONFIRM
    year = safe_text(row.get("year", "")) or TO_CONFIRM
    title = safe_text(row.get("title", "")) or TO_CONFIRM
    source = safe_text(row.get("journal_or_repository", "")) or TO_CONFIRM
    doi = safe_text(row.get("doi", ""))
    suffix = f" https://doi.org/{doi}" if doi and doi != TO_CONFIRM else ""
    return f"{authors} ({year}). {title}. {source}.{suffix}".strip()


def paper_payload(row_index: int, row: pd.Series, markdown: str) -> dict[str, Any]:
    metadata = {str(key): safe_text(value) for key, value in row.items()}
    return {
        "row_index": row_index,
        "paper_id": safe_text(row.get("paper_id", "")) or safe_text(row.get("citation_key", "")) or f"row_{row_index}",
        "citation_key": safe_text(row.get("citation_key", "")),
        "full_citation": full_citation(row),
        "metadata": metadata,
        "markdown": markdown,
    }


def evidence_schema() -> dict[str, Any]:
    return evidence_extraction_schema()


def build_request_payload(model: str, research_context: str, paper: dict[str, Any]) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_evidence_extraction_prompt(TO_CONFIRM),
        input_data={"research_context": research_context, "paper": paper},
        schema=evidence_schema(),
        schema_name="paper_evidence_extraction",
    )


def call_openai_evidence_extraction(
    api_key: str,
    model: str,
    research_context: str,
    paper: dict[str, Any],
    timeout: int = 180,
    retries: int = 2,
) -> dict[str, Any]:
    try:
        return AIClient(api_key=api_key, default_model=model).responses_json(
            instructions=build_evidence_extraction_prompt(TO_CONFIRM),
            input_data={"research_context": research_context, "paper": paper},
            schema=evidence_schema(),
            schema_name="paper_evidence_extraction",
            timeout=timeout,
            retries=retries,
        )
    except Exception as exc:
        raise RuntimeError(f"OpenAI evidence extraction failed: {exc}") from exc


def summary_filename(result: dict[str, Any]) -> str:
    paper_id = safe_text(result.get("paper_id", "")) or "paper"
    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    title = safe_text(summary.get("full_citation", "")) or paper_id
    return f"{slugify(paper_id, 40)}_{slugify(title, 70)}.md"


def markdown_summary(result: dict[str, Any]) -> str:
    summary = result.get("summary", {}) if isinstance(result.get("summary"), dict) else {}
    paper_id = safe_text(result.get("paper_id", "")) or safe_text(summary.get("paper_id", "")) or TO_CONFIRM
    labels = {
        "paper_id": "Paper ID",
        "full_citation": "Full Citation",
        "research_purpose": "Research Purpose",
        "study_design": "Study Design",
        "population_sample": "Population/Sample",
        "setting_context": "Setting/Context",
        "variables": "Variables",
        "instruments_measures": "Instruments/Measures",
        "statistical_methods": "Statistical Methods",
        "key_findings": "Key Findings",
        "limitations": "Limitations",
        "relevance_to_current_study": "Relevance to Current Study",
        "useful_concepts_for_introduction": "Useful Concepts for Introduction",
        "useful_concepts_for_rrl": "Useful Concepts for RRL",
        "useful_concepts_for_discussion": "Useful Concepts for Discussion",
        "exact_source_location_if_available": "Exact Source Location if Available",
        "confidence_rating": "Confidence Rating",
    }
    lines = [f"# Paper Summary: {paper_id}", ""]
    for key in SUMMARY_SECTIONS:
        lines.append(f"## {labels[key]}")
        lines.append("")
        lines.append(safe_text(summary.get(key, "")) or TO_CONFIRM)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def normalize_evidence_rows(result: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in result.get("evidence_rows", []):
        if not isinstance(item, dict):
            continue
        row = {column: safe_text(item.get(column, "")) or TO_CONFIRM for column in EVIDENCE_COLUMNS}
        row["paper_id"] = row["paper_id"] or safe_text(result.get("paper_id", "")) or TO_CONFIRM
        row["citation_key"] = row["citation_key"] or safe_text(result.get("citation_key", ""))
        rows.append(row)
    return rows


def write_outputs(project_dir: Path, results: list[dict[str, Any]], skipped: list[str], model: str, metadata_source: Path, overwrite: bool) -> dict[str, Path]:
    p = paths(project_dir)
    if p["evidence"].exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing evidence table without --overwrite: {p['evidence']}")
    p["output_dir"].mkdir(parents=True, exist_ok=True)
    p["summaries"].mkdir(parents=True, exist_ok=True)

    evidence_rows: list[dict[str, str]] = []
    for result in results:
        (p["summaries"] / summary_filename(result)).write_text(markdown_summary(result), encoding="utf-8")
        evidence_rows.extend(normalize_evidence_rows(result))

    pd.DataFrame(evidence_rows, columns=EVIDENCE_COLUMNS).fillna("").to_csv(p["evidence"], index=False, encoding="utf-8")
    write_log(p["log"], results, skipped, model, metadata_source)
    return p


def write_log(path: Path, results: list[dict[str, Any]], skipped: list[str], model: str, metadata_source: Path) -> None:
    lines = [
        "# Evidence Extraction Log",
        "",
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Model: {model}",
        f"Metadata source: {metadata_source}",
        f"Papers processed: {len(results)}",
        f"Papers skipped: {len(skipped)}",
        "",
    ]
    if skipped:
        lines.append("## Skipped")
        lines.extend(f"- {item}" for item in skipped)
        lines.append("")
    lines.append("## Processed")
    for result in results:
        paper_id = safe_text(result.get("paper_id", "")) or TO_CONFIRM
        issues = [safe_text(issue) for issue in result.get("extraction_issues", []) if safe_text(issue)]
        lines.append(f"- `{paper_id}`: {'; '.join(issues) if issues else 'No extraction issues reported.'}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    write_ai_run_log(
        path.with_name("ai_run_log.md"),
        task_name="evidence_extraction",
        model=model,
        input_paths=[metadata_source],
        output_paths=[path.parent / "evidence_table.csv", path.parent / "paper_summaries"],
        counts={"attempted": len(results), "succeeded": len(results), "failed": len(skipped), "skipped": len(skipped)},
        prompt_version="evidence_extraction_v1",
    )


def run_evidence_extraction(
    project_dir: Path,
    model: str,
    limit: int | None,
    offset: int,
    max_md_chars: int,
    dry_run: bool,
    overwrite: bool,
    dotenv_path: Path | None = None,
) -> dict[str, Any]:
    metadata, metadata_source = load_metadata(project_dir)
    selected = rows_to_extract(metadata, limit=limit, offset=offset)
    skipped = [
        f"row {idx}: missing local markdown file"
        for idx, row in metadata.iterrows()
        if idx >= offset and idx not in selected and not Path(safe_text(row.get("local_markdown_file", ""))).exists()
    ]
    if dry_run:
        return {"selected": len(selected), "processed": 0, "evidence_rows": 0, "skipped": len(skipped), "paths": paths(project_dir)}

    api_key = get_api_key(dotenv_path)
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY. Set it in the shell or in a local ignored .env file.")

    research_context = load_research_context(project_dir)
    results: list[dict[str, Any]] = []
    for idx in selected:
        row = metadata.loc[idx]
        markdown_path = Path(safe_text(row.get("local_markdown_file", "")))
        markdown = compact_text(markdown_path.read_text(encoding="utf-8", errors="replace"), max_md_chars)
        paper = paper_payload(idx, row, markdown)
        result = call_openai_evidence_extraction(api_key, model, research_context, paper)
        results.append(result)

    out_paths = write_outputs(project_dir, results, skipped, model=model, metadata_source=metadata_source, overwrite=overwrite)
    evidence_rows = sum(len(normalize_evidence_rows(result)) for result in results)
    return {"selected": len(selected), "processed": len(results), "evidence_rows": evidence_rows, "skipped": len(skipped), "paths": out_paths}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to extract structured evidence from cleaned markdown papers.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=get_env_model("AI_EVIDENCE_MODEL", DEFAULT_MODEL), help="OpenAI model for evidence extraction")
    parser.add_argument("--limit", type=int, help="Maximum papers to process")
    parser.add_argument("--offset", type=int, default=0, help="Start at this metadata row offset")
    parser.add_argument("--max-md-chars", type=int, default=90000, help="Maximum markdown characters sent per paper")
    parser.add_argument("--dry-run", action="store_true", help="Count papers without calling OpenAI")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing evidence outputs")
    parser.add_argument("--dotenv", type=Path, help="Optional path to an ignored .env file")
    args = parser.parse_args()

    summary = run_evidence_extraction(
        project_dir=resolve_project(args.project),
        model=args.model,
        limit=args.limit,
        offset=args.offset,
        max_md_chars=args.max_md_chars,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        dotenv_path=args.dotenv,
    )
    print(f"selected={summary['selected']} processed={summary['processed']} evidence_rows={summary['evidence_rows']} skipped={summary['skipped']}")
    if not args.dry_run:
        print(f"evidence_table={summary['paths']['evidence']}")
        print(f"summaries={summary['paths']['summaries']}")


if __name__ == "__main__":
    main()
