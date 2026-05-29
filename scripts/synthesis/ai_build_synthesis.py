from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ai.client import AIClient, load_dotenv, require_api_key
from scripts.ai.logging import write_ai_run_log
from scripts.ai.prompts import build_synthesis_prompt
from scripts.ai.schemas import (
    SYNTHESIS_EVIDENCE_ROLES,
    SYNTHESIS_MANUSCRIPT_USES,
    SYNTHESIS_MATRIX_COLUMNS,
    SYNTHESIS_STRENGTHS,
    synthesis_schema,
)


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-mini"
TO_CONFIRM = "To be confirmed."


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return os.getenv("AI_SYNTHESIS_MODEL", "").strip() or os.getenv("AI_DISCOVERY_MODEL", "").strip() or DEFAULT_MODEL


def paths(project_dir: Path) -> dict[str, Path]:
    stage05 = project_dir / "05_evidence_extraction"
    stage06 = project_dir / "06_synthesis"
    return {
        "evidence": stage05 / "evidence_table.csv",
        "summaries": stage05 / "paper_summaries",
        "brief_dir": project_dir / "00_brief",
        "metadata_ai": project_dir / "04_metadata" / "metadata_table_ai_checked.csv",
        "metadata": project_dir / "04_metadata" / "metadata_table.csv",
        "output_dir": stage06,
        "matrix": stage06 / "synthesis_matrix.csv",
        "theme": stage06 / "theme_matrix.md",
        "map": stage06 / "literature_map.md",
        "notes": stage06 / "synthesis_notes.md",
        "log": project_dir / "logs" / "ai_synthesis_log.md",
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


def compact_text(value: str, max_chars: int) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")[:max_chars]


def parse_theme_hints(values: list[str] | None) -> list[str]:
    hints: list[str] = []
    for value in values or []:
        for item in value.split(","):
            hint = safe_text(item)
            if hint and hint not in hints:
                hints.append(hint)
    return hints


def read_brief_context(project_dir: Path, max_chars: int = 20000) -> tuple[str, str, list[Path]]:
    brief_dir = paths(project_dir)["brief_dir"]
    brief_names = ["research_brief.md", "variables.md", "inclusion_exclusion_criteria.md", "writing_scope.md"]
    chunks: list[str] = []
    used: list[Path] = []
    for name in brief_names:
        path = brief_dir / name
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if text:
                chunks.append(f"# {name}\n\n{text}")
                used.append(path)
    rq_path = brief_dir / "research_questions.md"
    research_questions = ""
    if rq_path.exists():
        research_questions = rq_path.read_text(encoding="utf-8", errors="replace").strip()
        if research_questions:
            used.append(rq_path)
    return compact_text("\n\n".join(chunks), max_chars), compact_text(research_questions, max_chars // 2), used


def load_evidence(path: Path, limit: int | None, include_background: bool, min_confidence: str | None) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    if not include_background:
        for column in ["ai_relevance_label", "evidence_role"]:
            if column in df.columns:
                df = df[df[column].str.lower() != "background_only"]
    if min_confidence and "confidence_rating" in df.columns:
        df = filter_by_confidence(df, min_confidence)
    if limit is not None:
        df = df.head(limit)
    return df.fillna("")


def filter_by_confidence(df: pd.DataFrame, minimum: str) -> pd.DataFrame:
    order = {"low": 1, "medium": 2, "moderate": 2, "high": 3}
    min_value = order.get(minimum.strip().lower())
    if not min_value:
        return df
    return df[df["confidence_rating"].map(lambda value: order.get(str(value).strip().lower(), 0) >= min_value)]


def read_paper_summaries(summary_dir: Path, limit: int | None, max_chars: int = 40000) -> tuple[str, int, list[Path], list[str]]:
    warnings: list[str] = []
    if not summary_dir.exists():
        return "", 0, [], [f"Missing paper_summaries folder: {summary_dir}"]
    files = sorted(summary_dir.glob("*.md"))
    if limit is not None:
        files = files[:limit]
    chunks: list[str] = []
    used: list[Path] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            chunks.append(f"# {path.name}\n\n{text}")
            used.append(path)
    return compact_text("\n\n".join(chunks), max_chars), len(used), used, warnings


def read_metadata_context(project_dir: Path, max_chars: int = 20000) -> tuple[str, Path | None]:
    p = paths(project_dir)
    source = p["metadata_ai"] if p["metadata_ai"].exists() else p["metadata"]
    if not source.exists():
        return "", None
    df = pd.read_csv(source, dtype=str).fillna("")
    columns = [column for column in ["paper_id", "citation_key", "title", "authors", "year", "journal_or_repository", "metadata_status"] if column in df.columns]
    return compact_text(df[columns].to_csv(index=False), max_chars), source


def evidence_table_text(df: pd.DataFrame, max_chars: int = 60000) -> str:
    return compact_text(df.to_csv(index=False), max_chars)


def existing_outputs(p: dict[str, Path]) -> list[Path]:
    return [path for path in [p["matrix"], p["theme"], p["map"], p["notes"]] if path.exists()]


def backup_outputs(outputs: list[Path]) -> list[Path]:
    backups: list[Path] = []
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for path in outputs:
        backup = path.with_suffix(f".{stamp}.bak{path.suffix}")
        backup.write_bytes(path.read_bytes())
        backups.append(backup)
    return backups


def blocked_result(message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    return {
        "completion_status": "blocked",
        "themes": [],
        "synthesis_rows": [],
        "literature_map": {
            "current_study_focus": TO_CONFIRM,
            "evidence_clusters": [],
            "directly_relevant_studies": [],
            "adjacent_evidence": [],
            "methodological_evidence": [],
            "gaps_identified": [],
            "contradictions_or_mixed_findings": [],
            "next_stage_support": message,
        },
        "claims_safe_to_use_later": [],
        "claims_requiring_caution": [],
        "missing_evidence": [message, *(warnings or [])],
        "recommended_next_step": "Complete Stage 05 evidence extraction before running Stage 06 synthesis.",
    }


def dry_run_result(evidence_rows: int, summary_count: int, theme_hints: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "completion_status": "partial",
        "themes": [
            {
                "theme": "Dry-run synthesis preview",
                "subthemes": theme_hints or [TO_CONFIRM],
                "summary": "Dry run only. No OpenAI request was made.",
                "direct_evidence": [],
                "indirect_evidence": [],
                "mixed_or_conflicting_findings": [],
                "methodological_notes": [f"Evidence rows available: {evidence_rows}", f"Paper summaries available: {summary_count}"],
                "limitations_or_cautions": ["This is not completed synthesis."],
                "use_in_manuscript": ["Do not use as manuscript prose."],
            }
        ],
        "synthesis_rows": [],
        "literature_map": {
            "current_study_focus": "Dry run only. To be confirmed.",
            "evidence_clusters": theme_hints,
            "directly_relevant_studies": [],
            "adjacent_evidence": [],
            "methodological_evidence": [],
            "gaps_identified": [],
            "contradictions_or_mixed_findings": [],
            "next_stage_support": "Run without --dry-run to build AI-assisted Stage 06 synthesis.",
        },
        "claims_safe_to_use_later": [],
        "claims_requiring_caution": ["Dry-run outputs are status notes only."],
        "missing_evidence": warnings,
        "recommended_next_step": "Run without --dry-run after reviewing Stage 05 evidence availability.",
    }


def build_request_payload(
    model: str,
    brief_context: str,
    research_questions: str,
    evidence_table_text_value: str,
    paper_summaries_text: str,
    metadata_context: str,
    theme_hints: list[str] | None = None,
) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_synthesis_prompt(brief_context, research_questions, evidence_table_text_value, paper_summaries_text, metadata_context, theme_hints),
        input_data={
            "brief_context": brief_context,
            "research_questions": research_questions,
            "evidence_table": evidence_table_text_value,
            "paper_summaries": paper_summaries_text,
            "metadata_context": metadata_context,
            "theme_hints": theme_hints or [],
        },
        schema=synthesis_schema(),
        schema_name="stage06_synthesis",
    )


def call_openai_synthesis(
    api_key: str,
    model: str,
    brief_context: str,
    research_questions: str,
    evidence_table_text_value: str,
    paper_summaries_text: str,
    metadata_context: str,
    theme_hints: list[str] | None = None,
    timeout: int = 180,
    retries: int = 2,
) -> dict[str, Any]:
    return AIClient(api_key=api_key, default_model=model).responses_json(
        instructions=build_synthesis_prompt(brief_context, research_questions, evidence_table_text_value, paper_summaries_text, metadata_context, theme_hints),
        input_data={
            "brief_context": brief_context,
            "research_questions": research_questions,
            "evidence_table": evidence_table_text_value,
            "paper_summaries": paper_summaries_text,
            "metadata_context": metadata_context,
            "theme_hints": theme_hints or [],
        },
        schema=synthesis_schema(),
        schema_name="stage06_synthesis",
        timeout=timeout,
        retries=retries,
    )


def normalize_result(result: dict[str, Any], allowed_ids: set[str], allowed_citations: set[str]) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    warnings = [safe_text(item) for item in result.get("missing_evidence", []) if safe_text(item)]
    rows: list[dict[str, str]] = []
    for index, item in enumerate(result.get("synthesis_rows", []), start=1):
        if not isinstance(item, dict):
            continue
        row = {column: safe_text(item.get(column, "")) for column in SYNTHESIS_MATRIX_COLUMNS if column != "synthesis_id"}
        row["synthesis_id"] = f"SYN-{index:04d}"
        if row["evidence_role"] not in SYNTHESIS_EVIDENCE_ROLES:
            warnings.append(f"Invalid evidence_role for {row['synthesis_id']}; coerced to to_be_confirmed.")
            row["evidence_role"] = "to_be_confirmed"
        if row["strength_of_evidence"] not in SYNTHESIS_STRENGTHS:
            warnings.append(f"Invalid strength_of_evidence for {row['synthesis_id']}; coerced to to_be_confirmed.")
            row["strength_of_evidence"] = "to_be_confirmed"
        if row["use_in_manuscript"] not in SYNTHESIS_MANUSCRIPT_USES:
            warnings.append(f"Invalid use_in_manuscript for {row['synthesis_id']}; coerced to to_be_confirmed.")
            row["use_in_manuscript"] = "to_be_confirmed"
        if not row["paper_id"] and not row["citation_key"]:
            warnings.append(f"{row['synthesis_id']} missing both paper_id and citation_key; set to To be confirmed.")
            row["paper_id"] = TO_CONFIRM
            row["citation_key"] = TO_CONFIRM
        if row["citation_key"] and row["citation_key"] not in allowed_citations and row["citation_key"] != TO_CONFIRM:
            warnings.append(f"{row['synthesis_id']} citation_key was not in supplied inputs; set to To be confirmed.")
            row["citation_key"] = TO_CONFIRM
        if row["paper_id"] and row["paper_id"] not in allowed_ids and row["paper_id"] != TO_CONFIRM:
            warnings.append(f"{row['synthesis_id']} paper_id was not in supplied inputs; set to To be confirmed.")
            row["paper_id"] = TO_CONFIRM
        for column in SYNTHESIS_MATRIX_COLUMNS:
            row[column] = row.get(column) or TO_CONFIRM
        rows.append({column: row[column] for column in SYNTHESIS_MATRIX_COLUMNS})
    result["missing_evidence"] = warnings
    return result, rows, warnings


def sanitize_citation_markers(text: str, allowed_citations: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return match.group(0) if key in allowed_citations else "[@ToBeConfirmed]"

    return re.sub(r"\[@([A-Za-z0-9_.:-]+)\]", replace, text)


def write_outputs(project_dir: Path, result: dict[str, Any], rows: list[dict[str, str]], model: str, allowed_citations: set[str]) -> dict[str, Path]:
    p = paths(project_dir)
    p["output_dir"].mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=SYNTHESIS_MATRIX_COLUMNS).fillna("").to_csv(p["matrix"], index=False, encoding="utf-8")
    write_theme_matrix(p["theme"], result, model, allowed_citations)
    write_literature_map(p["map"], result)
    write_synthesis_notes(p["notes"], result, project_dir)
    return p


def write_theme_matrix(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    lines = ["# Theme Matrix", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    themes = result.get("themes", [])
    if not themes:
        lines.extend(["## Theme 1: To be confirmed", "", "### Summary", "", "To be confirmed.", ""])
    for idx, theme in enumerate(themes, start=1):
        if not isinstance(theme, dict):
            continue
        summary = sanitize_citation_markers(safe_text(theme.get("summary", "")) or TO_CONFIRM, allowed_citations)
        lines.extend([f"## Theme {idx}: {safe_text(theme.get('theme', '')) or TO_CONFIRM}", "", "### Summary", "", summary, ""])
        for heading, key in [
            ("Direct evidence", "direct_evidence"),
            ("Indirect/background evidence", "indirect_evidence"),
            ("Mixed or conflicting findings", "mixed_or_conflicting_findings"),
            ("Methodological notes", "methodological_notes"),
            ("Limitations/cautions", "limitations_or_cautions"),
            ("Useful manuscript placement", "use_in_manuscript"),
        ]:
            lines.extend([f"### {heading}", ""])
            lines.extend(markdown_bullets(theme.get(key, []), allowed_citations))
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def markdown_bullets(values: Any, allowed_citations: set[str]) -> list[str]:
    if not isinstance(values, list) or not values:
        return [f"- {TO_CONFIRM}"]
    return [f"- {sanitize_citation_markers(safe_text(item) or TO_CONFIRM, allowed_citations)}" for item in values]


def write_literature_map(path: Path, result: dict[str, Any]) -> None:
    lit = result.get("literature_map", {}) if isinstance(result.get("literature_map", {}), dict) else {}
    sections = [
        ("Current Study Focus", lit.get("current_study_focus", "")),
        ("Evidence Clusters", lit.get("evidence_clusters", [])),
        ("Directly Relevant Studies", lit.get("directly_relevant_studies", [])),
        ("Adjacent Allied Health / Education Evidence", lit.get("adjacent_evidence", [])),
        ("Methodological Evidence", lit.get("methodological_evidence", [])),
        ("Gaps Identified From Literature", lit.get("gaps_identified", [])),
        ("Contradictions or Mixed Findings", lit.get("contradictions_or_mixed_findings", [])),
        ("How This Supports the Next Stage", lit.get("next_stage_support", "")),
    ]
    lines = ["# Literature Map", ""]
    for heading, value in sections:
        lines.extend([f"## {heading}", ""])
        if isinstance(value, list):
            lines.extend([f"- {safe_text(item)}" for item in value if safe_text(item)] or [f"- {TO_CONFIRM}"])
        else:
            lines.append(safe_text(value) or TO_CONFIRM)
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_synthesis_notes(path: Path, result: dict[str, Any], project_dir: Path) -> None:
    lines = [
        "# Synthesis Notes",
        "",
        "## Completion Status",
        "",
        safe_text(result.get("completion_status", "")) or "blocked",
        "",
        "## Inputs Used",
        "",
        f"- Project: {project_dir}",
        "- Stage 05 evidence table and available paper summaries.",
        "",
        "## Main Themes",
        "",
    ]
    themes = result.get("themes", [])
    lines.extend([f"- {safe_text(theme.get('theme', ''))}" for theme in themes if isinstance(theme, dict) and safe_text(theme.get("theme", ""))] or [f"- {TO_CONFIRM}"])
    for heading, key in [
        ("Strongest Evidence", "claims_safe_to_use_later"),
        ("Weakest or Most Uncertain Evidence", "missing_evidence"),
        ("Claims Safe to Use Later", "claims_safe_to_use_later"),
        ("Claims Requiring Caution", "claims_requiring_caution"),
        ("Missing Evidence / To be confirmed", "missing_evidence"),
    ]:
        lines.extend(["", f"## {heading}", ""])
        values = result.get(key, [])
        lines.extend([f"- {safe_text(item)}" for item in values if safe_text(item)] if isinstance(values, list) else [f"- {TO_CONFIRM}"])
        if isinstance(values, list) and not values:
            lines.append(f"- {TO_CONFIRM}")
    lines.extend(["", "## Recommended Next Step", "", safe_text(result.get("recommended_next_step", "")) or TO_CONFIRM, ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_log(
    log_path: Path,
    model: str,
    project_dir: Path,
    input_paths: list[Path],
    output_paths: list[Path],
    evidence_rows_read: int,
    summaries_read: int,
    synthesis_rows_written: int,
    dry_run: bool,
    overwrite: bool,
    warnings: list[str],
) -> None:
    write_ai_run_log(
        log_path,
        task_name="stage06_synthesis",
        model=model,
        input_paths=input_paths,
        output_paths=output_paths,
        counts={
            "project_path": project_dir,
            "evidence_rows_read": evidence_rows_read,
            "paper_summaries_read": summaries_read,
            "synthesis_rows_written": synthesis_rows_written,
            "dry_run": str(dry_run).lower(),
            "overwrite": str(overwrite).lower(),
        },
        errors=warnings,
        prompt_version="synthesis_v1",
    )


def run_ai_synthesis(
    project_dir: Path,
    model: str,
    dry_run: bool,
    overwrite: bool,
    no_backup: bool,
    limit: int | None,
    batch_size: int,
    theme_hints: list[str] | None,
    include_background: bool,
    min_confidence: str | None,
    strict: bool,
) -> dict[str, Any]:
    p = paths(project_dir)
    output_paths = [p["matrix"], p["theme"], p["map"], p["notes"], p["log"]]
    p["output_dir"].mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    if not p["evidence"].exists():
        message = f"Missing Stage 05 evidence table: {p['evidence']}"
        if strict:
            raise FileNotFoundError(message)
        result = blocked_result("Stage 05 evidence extraction must be completed first.", [message])
        write_outputs(project_dir, result, [], model, set())
        write_log(p["log"], model, project_dir, [], output_paths, 0, 0, 0, dry_run, overwrite, result["missing_evidence"])
        return {"status": "blocked", "rows_written": 0, "paths": p, "warnings": result["missing_evidence"], "backups": []}

    existing = existing_outputs(p)
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing Stage 06 outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup or not existing else backup_outputs(existing)

    evidence = load_evidence(p["evidence"], limit=limit, include_background=include_background, min_confidence=min_confidence)
    if evidence.empty:
        message = "Stage 05 evidence_table.csv is empty after filtering."
        if strict:
            raise ValueError(message)
        result = blocked_result("Stage 05 evidence extraction must include at least one usable evidence row.", [message])
        write_outputs(project_dir, result, [], model, set())
        write_log(p["log"], model, project_dir, [p["evidence"]], output_paths, 0, 0, 0, dry_run, overwrite, result["missing_evidence"])
        return {"status": "blocked", "rows_written": 0, "paths": p, "warnings": result["missing_evidence"], "backups": backups}

    brief_context, research_questions, brief_paths = read_brief_context(project_dir)
    summaries_text, summary_count, summary_paths, summary_warnings = read_paper_summaries(p["summaries"], limit=limit)
    warnings.extend(summary_warnings)
    metadata_context, metadata_path = read_metadata_context(project_dir)
    input_paths = [p["evidence"], *brief_paths, *summary_paths]
    if metadata_path:
        input_paths.append(metadata_path)

    if len(evidence) > batch_size:
        warnings.append(f"Evidence rows ({len(evidence)}) exceed batch-size ({batch_size}); using one bounded request with all selected rows.")

    allowed_ids = {safe_text(value) for value in evidence.get("paper_id", pd.Series(dtype=str)).tolist() if safe_text(value)}
    allowed_citations = {safe_text(value) for value in evidence.get("citation_key", pd.Series(dtype=str)).tolist() if safe_text(value)}
    if metadata_context and metadata_path:
        meta = pd.read_csv(metadata_path, dtype=str).fillna("")
        if "paper_id" in meta.columns:
            allowed_ids.update(safe_text(value) for value in meta["paper_id"].tolist() if safe_text(value))
        if "citation_key" in meta.columns:
            allowed_citations.update(safe_text(value) for value in meta["citation_key"].tolist() if safe_text(value))

    if dry_run:
        result = dry_run_result(len(evidence), summary_count, theme_hints or [], warnings)
    else:
        load_dotenv(repo_root() / ".env")
        api_key = require_api_key(dry_run=False)
        result = call_openai_synthesis(
            api_key or "",
            model,
            brief_context,
            research_questions,
            evidence_table_text(evidence),
            summaries_text,
            metadata_context,
            theme_hints,
        )

    result, rows, validation_warnings = normalize_result(result, allowed_ids, allowed_citations)
    warnings = list(dict.fromkeys([*warnings, *validation_warnings]))
    result["missing_evidence"] = warnings
    write_outputs(project_dir, result, rows, model, allowed_citations)
    write_log(p["log"], model, project_dir, input_paths, output_paths, len(evidence), summary_count, len(rows), dry_run, overwrite, warnings)
    return {"status": result.get("completion_status", "completed"), "rows_written": len(rows), "paths": p, "warnings": warnings, "backups": backups}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to build Stage 06 synthesis artifacts from Stage 05 evidence outputs.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=default_model(), help="OpenAI model for synthesis")
    parser.add_argument("--dry-run", action="store_true", help="Write status outputs without calling OpenAI")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing existing Stage 06 outputs")
    parser.add_argument("--no-backup", action="store_true", help="Skip backups when overwriting")
    parser.add_argument("--limit", type=int, help="Maximum evidence rows and paper summaries to include")
    parser.add_argument("--batch-size", type=int, default=20, help="Evidence rows per synthesis batch target")
    parser.add_argument("--theme-hint", action="append", help="Optional repeatable or comma-separated theme hints")
    parser.add_argument("--include-background", action="store_true", help="Include background_only evidence if such labels exist")
    parser.add_argument("--min-confidence", help="Optional minimum confidence filter if confidence_rating exists")
    parser.add_argument("--strict", action="store_true", help="Fail if required Stage 05 files are missing")
    args = parser.parse_args()

    summary = run_ai_synthesis(
        project_dir=resolve_project(args.project),
        model=args.model,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        no_backup=args.no_backup,
        limit=args.limit,
        batch_size=args.batch_size,
        theme_hints=parse_theme_hints(args.theme_hint),
        include_background=args.include_background,
        min_confidence=args.min_confidence,
        strict=args.strict,
    )
    print(f"status={summary['status']} synthesis_rows={summary['rows_written']}")
    print(f"synthesis_matrix={summary['paths']['matrix']}")
    print(f"theme_matrix={summary['paths']['theme']}")
    print(f"literature_map={summary['paths']['map']}")
    print(f"synthesis_notes={summary['paths']['notes']}")


if __name__ == "__main__":
    main()
