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
from scripts.ai.prompts import build_gap_analysis_prompt
from scripts.ai.schemas import (
    CONTRIBUTION_TYPES,
    GAP_CAUTION_LEVELS,
    GAP_MATRIX_COLUMNS,
    GAP_RECOMMENDED_USES,
    GAP_STRENGTHS,
    GAP_TYPES,
    gap_analysis_schema,
)


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-mini"
TO_CONFIRM = "To be confirmed."
PROMPT_VERSION = "gap_analysis_v1"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return (
        os.getenv("AI_GAP_MODEL", "").strip()
        or os.getenv("AI_SYNTHESIS_MODEL", "").strip()
        or os.getenv("AI_DISCOVERY_MODEL", "").strip()
        or DEFAULT_MODEL
    )


def paths(project_dir: Path) -> dict[str, Path]:
    stage06 = project_dir / "06_synthesis"
    stage07 = project_dir / "07_gap_analysis"
    return {
        "brief_dir": project_dir / "00_brief",
        "evidence": project_dir / "05_evidence_extraction" / "evidence_table.csv",
        "metadata_ai": project_dir / "04_metadata" / "metadata_table_ai_checked.csv",
        "metadata": project_dir / "04_metadata" / "metadata_table.csv",
        "synthesis_matrix": stage06 / "synthesis_matrix.csv",
        "theme_matrix": stage06 / "theme_matrix.md",
        "literature_map": stage06 / "literature_map.md",
        "synthesis_notes": stage06 / "synthesis_notes.md",
        "output_dir": stage07,
        "gap_analysis": stage07 / "research_gap_analysis.md",
        "contribution": stage07 / "study_contribution.md",
        "problem_statement": stage07 / "problem_statement_refined.md",
        "gap_matrix": stage07 / "gap_matrix.csv",
        "log": project_dir / "logs" / "ai_gap_analysis_log.md",
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


def compact_text(value: str, max_chars: int | None) -> str:
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    return text if max_chars is None else text[:max_chars]


def parse_theme_filters(values: list[str] | None) -> list[str]:
    filters: list[str] = []
    for value in values or []:
        for item in value.split(","):
            theme = safe_text(item)
            if theme and theme not in filters:
                filters.append(theme)
    return filters


def read_text_file(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    return compact_text(path.read_text(encoding="utf-8", errors="replace").strip(), max_chars)


def read_brief_context(project_dir: Path, max_chars: int = 20000) -> tuple[str, str, list[Path]]:
    brief_dir = paths(project_dir)["brief_dir"]
    brief_names = ["research_brief.md", "variables.md", "inclusion_exclusion_criteria.md", "writing_scope.md"]
    chunks: list[str] = []
    used: list[Path] = []
    for name in brief_names:
        path = brief_dir / name
        text = read_text_file(path)
        if text:
            chunks.append(f"# {name}\n\n{text}")
            used.append(path)
    rq_path = brief_dir / "research_questions.md"
    research_questions = read_text_file(rq_path, max_chars // 2)
    if research_questions:
        used.append(rq_path)
    return compact_text("\n\n".join(chunks), max_chars), research_questions, used


def read_synthesis_context(project_dir: Path, max_chars: int | None = None) -> tuple[str, list[Path], list[str]]:
    p = paths(project_dir)
    stage06_files = [p["synthesis_matrix"], p["theme_matrix"], p["literature_map"], p["synthesis_notes"]]
    chunks: list[str] = []
    used: list[Path] = []
    warnings: list[str] = []
    for path in stage06_files:
        text = read_text_file(path)
        if text:
            chunks.append(f"# {path.name}\n\n{text}")
            used.append(path)
        else:
            warnings.append(f"Missing or empty Stage 06 input: {path}")
    return compact_text("\n\n".join(chunks), max_chars), used, warnings


def read_csv_context(path: Path, max_chars: int = 30000) -> tuple[str, Path | None, set[str]]:
    if not path.exists():
        return "", None, set()
    df = pd.read_csv(path, dtype=str).fillna("")
    citations = {safe_text(value) for value in df.get("citation_key", pd.Series(dtype=str)).tolist() if safe_text(value)}
    return compact_text(df.to_csv(index=False), max_chars), path, citations


def read_metadata_context(project_dir: Path, max_chars: int = 20000) -> tuple[str, Path | None, set[str]]:
    p = paths(project_dir)
    source = p["metadata_ai"] if p["metadata_ai"].exists() else p["metadata"]
    if not source.exists():
        return "", None, set()
    df = pd.read_csv(source, dtype=str).fillna("")
    columns = [
        column
        for column in ["paper_id", "citation_key", "title", "authors", "year", "journal_or_repository", "metadata_status"]
        if column in df.columns
    ]
    citations = {safe_text(value) for value in df.get("citation_key", pd.Series(dtype=str)).tolist() if safe_text(value)}
    return compact_text(df[columns].to_csv(index=False), max_chars), source, citations


def output_files(p: dict[str, Path]) -> list[Path]:
    return [p["gap_analysis"], p["contribution"], p["problem_statement"], p["gap_matrix"]]


def existing_outputs(p: dict[str, Path]) -> list[Path]:
    return [path for path in output_files(p) if path.exists()]


def backup_outputs(outputs: list[Path]) -> list[Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups: list[Path] = []
    for path in outputs:
        backup = path.with_suffix(f".{stamp}.bak{path.suffix}")
        backup.write_bytes(path.read_bytes())
        backups.append(backup)
    return backups


def empty_contribution() -> dict[str, Any]:
    return {
        "proposed_contribution_statement": TO_CONFIRM,
        "contribution_types": ["to_be_confirmed"],
        "contribution_rationale": TO_CONFIRM,
        "safe_claims": [TO_CONFIRM],
        "claims_to_avoid": ["Do not claim novelty, causality, or effectiveness beyond supplied evidence."],
        "likely_stakeholders": [TO_CONFIRM],
        "manuscript_ready_contribution_statement": TO_CONFIRM,
    }


def empty_problem_statement() -> dict[str, Any]:
    return {
        "working_problem_statement": TO_CONFIRM,
        "research_problem_context": TO_CONFIRM,
        "evidence_based_rationale": TO_CONFIRM,
        "local_or_institutional_relevance": TO_CONFIRM,
        "variables_and_outcome_focus": TO_CONFIRM,
        "research_questions_alignment": TO_CONFIRM,
        "final_refined_problem_statement_draft": TO_CONFIRM,
        "assumptions_and_items_to_confirm": [TO_CONFIRM],
    }


def blocked_result(message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    warning_items = [message, *(warnings or [])]
    return {
        "completion_status": "blocked",
        "current_study_focus": TO_CONFIRM,
        "what_is_known": [TO_CONFIRM],
        "what_remains_unknown": warning_items,
        "population_or_context_gaps": [TO_CONFIRM],
        "local_or_philippine_gaps": [TO_CONFIRM],
        "methodological_gaps": [TO_CONFIRM],
        "variable_or_measurement_gaps": [TO_CONFIRM],
        "evidence_limitations": warning_items,
        "direct_vs_indirect_evidence_balance": TO_CONFIRM,
        "safe_gap_statement": message,
        "gap_claims_requiring_caution": ["No gap claims should be used until Stage 06 synthesis is available."],
        "to_be_confirmed": warning_items,
        "contribution": empty_contribution(),
        "problem_statement": empty_problem_statement(),
        "gap_rows": [],
        "recommended_next_step": "Complete Stage 06 synthesis before running Stage 07 gap analysis.",
    }


def dry_run_result(theme_filters: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "completion_status": "partial",
        "current_study_focus": "Dry run only. To be confirmed.",
        "what_is_known": ["Dry run only. Stage 06 inputs were inspected but no AI request was made."],
        "what_remains_unknown": ["Gap analysis content is not complete."],
        "population_or_context_gaps": [TO_CONFIRM],
        "local_or_philippine_gaps": [TO_CONFIRM],
        "methodological_gaps": [TO_CONFIRM],
        "variable_or_measurement_gaps": [TO_CONFIRM],
        "evidence_limitations": warnings or [TO_CONFIRM],
        "direct_vs_indirect_evidence_balance": "Dry run only. To be confirmed.",
        "safe_gap_statement": "Dry run only. Do not use as completed gap analysis.",
        "gap_claims_requiring_caution": ["Dry-run outputs are status notes only."],
        "to_be_confirmed": warnings or ["Run without --dry-run to generate AI-assisted Stage 07 outputs."],
        "contribution": empty_contribution(),
        "problem_statement": empty_problem_statement(),
        "gap_rows": [],
        "recommended_next_step": f"Review Stage 06 inputs and run without --dry-run. Theme filters: {', '.join(theme_filters) or 'none'}.",
    }


def build_request_payload(
    model: str,
    brief_context: str,
    research_questions: str,
    synthesis_context: str,
    evidence_context: str,
    metadata_context: str,
    theme_filters: list[str] | None = None,
    include_weak_evidence: bool = False,
) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_gap_analysis_prompt(
            brief_context,
            research_questions,
            synthesis_context,
            evidence_context,
            metadata_context,
            theme_filters,
            include_weak_evidence,
        ),
        input_data={
            "brief_context": brief_context,
            "research_questions": research_questions,
            "synthesis_context": synthesis_context,
            "evidence_context": evidence_context,
            "metadata_context": metadata_context,
            "theme_filters": theme_filters or [],
            "include_weak_evidence": include_weak_evidence,
        },
        schema=gap_analysis_schema(),
        schema_name="stage07_gap_analysis",
    )


def call_openai_gap_analysis(
    api_key: str,
    model: str,
    brief_context: str,
    research_questions: str,
    synthesis_context: str,
    evidence_context: str,
    metadata_context: str,
    theme_filters: list[str] | None = None,
    include_weak_evidence: bool = False,
    timeout: int = 180,
    retries: int = 2,
) -> dict[str, Any]:
    return AIClient(api_key=api_key, default_model=model).responses_json(
        instructions=build_gap_analysis_prompt(
            brief_context,
            research_questions,
            synthesis_context,
            evidence_context,
            metadata_context,
            theme_filters,
            include_weak_evidence,
        ),
        input_data={
            "brief_context": brief_context,
            "research_questions": research_questions,
            "synthesis_context": synthesis_context,
            "evidence_context": evidence_context,
            "metadata_context": metadata_context,
            "theme_filters": theme_filters or [],
            "include_weak_evidence": include_weak_evidence,
        },
        schema=gap_analysis_schema(),
        schema_name="stage07_gap_analysis",
        timeout=timeout,
        retries=retries,
    )


def markdown_bullets(values: Any, allowed_citations: set[str]) -> list[str]:
    if not isinstance(values, list) or not values:
        return [f"- {TO_CONFIRM}"]
    return [f"- {sanitize_citation_markers(safe_text(item) or TO_CONFIRM, allowed_citations)}" for item in values]


def sanitize_citation_markers(text: str, allowed_citations: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return match.group(0) if key in allowed_citations else "[@ToBeConfirmed]"

    return re.sub(r"\[@([A-Za-z0-9_.:-]+)\]", replace, text)


def normalize_contribution_types(result: dict[str, Any], warnings: list[str]) -> None:
    contribution = result.get("contribution", {})
    if not isinstance(contribution, dict):
        result["contribution"] = empty_contribution()
        warnings.append("Missing contribution object; set to To be confirmed.")
        return
    types = contribution.get("contribution_types", [])
    normalized: list[str] = []
    if isinstance(types, list):
        for value in types:
            item = safe_text(value)
            if item in CONTRIBUTION_TYPES:
                normalized.append(item)
            else:
                warnings.append(f"Invalid contribution_type '{item}'; coerced to to_be_confirmed.")
                normalized.append("to_be_confirmed")
    if not normalized:
        normalized = ["to_be_confirmed"]
    contribution["contribution_types"] = list(dict.fromkeys(normalized))
    for key, value in empty_contribution().items():
        contribution.setdefault(key, value)


def weak_or_unclear(row: dict[str, str]) -> bool:
    text = f"{row.get('evidence_basis', '')} {row.get('notes', '')} {row.get('supporting_synthesis_source', '')}".lower()
    return row.get("strength_of_gap") in {"weak", "limited", "to_be_confirmed"} or any(term in text for term in ["weak", "unclear", "limited", "to be confirmed", "unsupported"])


def normalize_result(result: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    warnings = [safe_text(item) for item in result.get("to_be_confirmed", []) if safe_text(item)]
    if result.get("completion_status") not in {"completed", "partial", "blocked"}:
        warnings.append("Invalid completion_status; coerced to partial.")
        result["completion_status"] = "partial"

    normalize_contribution_types(result, warnings)
    if not isinstance(result.get("problem_statement"), dict):
        result["problem_statement"] = empty_problem_statement()
        warnings.append("Missing problem_statement object; set to To be confirmed.")

    rows: list[dict[str, str]] = []
    for index, item in enumerate(result.get("gap_rows", []), start=1):
        if not isinstance(item, dict):
            warnings.append(f"Gap row {index} was not an object; skipped.")
            continue
        row = {column: safe_text(item.get(column, "")) for column in GAP_MATRIX_COLUMNS if column != "gap_id"}
        if not row["gap_statement"]:
            warnings.append(f"Gap row {index} missing gap_statement; skipped.")
            continue
        row["gap_id"] = f"GAP-{len(rows) + 1:04d}"
        if row["gap_type"] not in GAP_TYPES:
            warnings.append(f"Invalid gap_type for {row['gap_id']}; coerced to to_be_confirmed.")
            row["gap_type"] = "to_be_confirmed"
        if row["strength_of_gap"] not in GAP_STRENGTHS:
            warnings.append(f"Invalid strength_of_gap for {row['gap_id']}; coerced to to_be_confirmed.")
            row["strength_of_gap"] = "to_be_confirmed"
        if row["caution_level"] not in GAP_CAUTION_LEVELS:
            warnings.append(f"Invalid caution_level for {row['gap_id']}; coerced to to_be_confirmed.")
            row["caution_level"] = "to_be_confirmed"
        if row["recommended_use"] not in GAP_RECOMMENDED_USES:
            warnings.append(f"Invalid recommended_use for {row['gap_id']}; coerced to to_be_confirmed.")
            row["recommended_use"] = "to_be_confirmed"
        if weak_or_unclear(row) and row["caution_level"] == "low":
            warnings.append(f"{row['gap_id']} had weak or unclear support with low caution; caution_level set to moderate.")
            row["caution_level"] = "moderate"
        if not row["supporting_synthesis_source"] or "to be confirmed" in row["supporting_synthesis_source"].lower():
            if row["strength_of_gap"] not in {"to_be_confirmed", "weak"}:
                warnings.append(f"{row['gap_id']} lacks clear synthesis support; strength_of_gap set to to_be_confirmed.")
                row["strength_of_gap"] = "to_be_confirmed"
            if row["caution_level"] == "low":
                warnings.append(f"{row['gap_id']} lacks clear synthesis support; caution_level set to high.")
                row["caution_level"] = "high"
        for column in GAP_MATRIX_COLUMNS:
            row[column] = row.get(column) or TO_CONFIRM
        rows.append({column: row[column] for column in GAP_MATRIX_COLUMNS})

    result["to_be_confirmed"] = list(dict.fromkeys(warnings)) or result.get("to_be_confirmed", [])
    return result, rows, warnings


def write_outputs(project_dir: Path, result: dict[str, Any], rows: list[dict[str, str]], model: str, allowed_citations: set[str]) -> dict[str, Path]:
    p = paths(project_dir)
    p["output_dir"].mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=GAP_MATRIX_COLUMNS).fillna("").to_csv(p["gap_matrix"], index=False, encoding="utf-8")
    write_research_gap_analysis(p["gap_analysis"], result, model, allowed_citations)
    write_study_contribution(p["contribution"], result, model, allowed_citations)
    write_problem_statement(p["problem_statement"], result, model, allowed_citations)
    return p


def write_research_gap_analysis(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    lines = ["# Research Gap Analysis", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    scalar_sections = [
        ("Completion Status", result.get("completion_status", "")),
        ("Current Study Focus", result.get("current_study_focus", "")),
    ]
    list_sections = [
        ("What Is Already Known", "what_is_known"),
        ("What Remains Unknown", "what_remains_unknown"),
        ("Population or Context Gaps", "population_or_context_gaps"),
        ("Local / Philippine Context Gaps", "local_or_philippine_gaps"),
        ("Methodological Gaps", "methodological_gaps"),
        ("Variable or Measurement Gaps", "variable_or_measurement_gaps"),
        ("Evidence Limitations", "evidence_limitations"),
    ]
    for heading, value in scalar_sections:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(value) or TO_CONFIRM, allowed_citations), ""])
    lines.extend(["## Inputs Used", "", "See `projects/<project>/logs/ai_gap_analysis_log.md` for the input file list.", ""])
    for heading, key in list_sections:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(result.get(key, []), allowed_citations))
        lines.append("")
    for heading, key in [
        ("Direct vs Indirect Evidence Balance", "direct_vs_indirect_evidence_balance"),
        ("Safe Gap Statement", "safe_gap_statement"),
    ]:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(result.get(key, "")) or TO_CONFIRM, allowed_citations), ""])
    for heading, key in [("Gap Claims Requiring Caution", "gap_claims_requiring_caution"), ("To Be Confirmed", "to_be_confirmed")]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(result.get(key, []), allowed_citations))
        lines.append("")
    lines.extend(["## Recommended Next Step", "", sanitize_citation_markers(safe_text(result.get("recommended_next_step", "")) or TO_CONFIRM, allowed_citations), ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_study_contribution(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    contribution = result.get("contribution", {}) if isinstance(result.get("contribution"), dict) else empty_contribution()
    lines = ["# Study Contribution", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    for heading, key in [
        ("Proposed Contribution Statement", "proposed_contribution_statement"),
        ("Contribution Rationale", "contribution_rationale"),
    ]:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(contribution.get(key, "")) or TO_CONFIRM, allowed_citations), ""])
    lines.extend(["## Contribution Type", ""])
    lines.extend(markdown_bullets(contribution.get("contribution_types", []), allowed_citations))
    lines.append("")
    for heading, key in [
        ("What This Study Can Safely Claim", "safe_claims"),
        ("What This Study Should Not Claim", "claims_to_avoid"),
        ("Likely Readers or Stakeholders", "likely_stakeholders"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(contribution.get(key, []), allowed_citations))
        lines.append("")
    lines.extend([
        "## Contribution Statement for Later Manuscript Use",
        "",
        sanitize_citation_markers(safe_text(contribution.get("manuscript_ready_contribution_statement", "")) or TO_CONFIRM, allowed_citations),
        "",
    ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_problem_statement(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    problem = result.get("problem_statement", {}) if isinstance(result.get("problem_statement"), dict) else empty_problem_statement()
    lines = ["# Refined Problem Statement", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    for heading, key in [
        ("Working Problem Statement", "working_problem_statement"),
        ("Research Problem Context", "research_problem_context"),
        ("Evidence-Based Rationale", "evidence_based_rationale"),
        ("Local or Institutional Relevance", "local_or_institutional_relevance"),
        ("Variables and Outcome Focus", "variables_and_outcome_focus"),
        ("Refined Research Questions Alignment", "research_questions_alignment"),
        ("Final Refined Problem Statement Draft", "final_refined_problem_statement_draft"),
    ]:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(problem.get(key, "")) or TO_CONFIRM, allowed_citations), ""])
    lines.extend(["## Assumptions and Items To Be Confirmed", ""])
    lines.extend(markdown_bullets(problem.get("assumptions_and_items_to_confirm", []), allowed_citations))
    lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_log(
    log_path: Path,
    model: str,
    project_dir: Path,
    input_paths: list[Path],
    output_paths: list[Path],
    gap_rows_written: int,
    dry_run: bool,
    overwrite: bool,
    strict: bool,
    warnings: list[str],
) -> None:
    write_ai_run_log(
        log_path,
        task_name="stage07_gap_analysis",
        model=model,
        input_paths=input_paths,
        output_paths=output_paths,
        counts={
            "project_path": project_dir,
            "gap_rows_written": gap_rows_written,
            "dry_run": str(dry_run).lower(),
            "overwrite": str(overwrite).lower(),
            "strict": str(strict).lower(),
        },
        errors=warnings,
        prompt_version=PROMPT_VERSION,
    )


def run_ai_gap_analysis(
    project_dir: Path,
    model: str,
    dry_run: bool,
    overwrite: bool,
    no_backup: bool,
    strict: bool,
    theme_filters: list[str] | None,
    include_weak_evidence: bool,
    max_input_chars: int | None,
) -> dict[str, Any]:
    p = paths(project_dir)
    p["output_dir"].mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    existing = existing_outputs(p)
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing Stage 07 outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup or not existing else backup_outputs(existing)

    synthesis_context, synthesis_paths, synthesis_warnings = read_synthesis_context(project_dir, max_chars=max_input_chars)
    warnings.extend(synthesis_warnings)
    if not synthesis_context:
        message = "Stage 06 synthesis must be completed before Stage 07 gap analysis."
        if strict:
            raise FileNotFoundError(message)
        result = blocked_result(message, warnings)
        result, rows, validation_warnings = normalize_result(result)
        warnings = list(dict.fromkeys([*warnings, *validation_warnings]))
        write_outputs(project_dir, result, rows, model, set())
        output_paths = output_files(p) + [p["log"]]
        write_log(p["log"], model, project_dir, [], output_paths, len(rows), dry_run, overwrite, strict, warnings)
        return {"status": "blocked", "rows_written": len(rows), "paths": p, "warnings": warnings, "backups": backups}

    brief_context, research_questions, brief_paths = read_brief_context(project_dir)
    evidence_context, evidence_path, evidence_citations = read_csv_context(p["evidence"])
    metadata_context, metadata_path, metadata_citations = read_metadata_context(project_dir)
    input_paths = [*synthesis_paths, *brief_paths]
    if evidence_path:
        input_paths.append(evidence_path)
    if metadata_path:
        input_paths.append(metadata_path)

    synthesis_citations = set(re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", synthesis_context))
    allowed_citations = {key for key in [*synthesis_citations, *evidence_citations, *metadata_citations] if key and key != "ToBeConfirmed"}

    if dry_run:
        result = dry_run_result(theme_filters or [], warnings)
    else:
        load_dotenv(repo_root() / ".env")
        api_key = require_api_key(dry_run=False)
        result = call_openai_gap_analysis(
            api_key or "",
            model,
            brief_context,
            research_questions,
            synthesis_context,
            evidence_context,
            metadata_context,
            theme_filters,
            include_weak_evidence,
        )

    result, rows, validation_warnings = normalize_result(result)
    warnings = list(dict.fromkeys([*warnings, *validation_warnings]))
    result["to_be_confirmed"] = list(dict.fromkeys([*result.get("to_be_confirmed", []), *warnings]))
    write_outputs(project_dir, result, rows, model, allowed_citations)
    output_paths = output_files(p) + [p["log"]]
    write_log(p["log"], model, project_dir, input_paths, output_paths, len(rows), dry_run, overwrite, strict, warnings)
    return {"status": result.get("completion_status", "completed"), "rows_written": len(rows), "paths": p, "warnings": warnings, "backups": backups}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to build Stage 07 gap-analysis artifacts from Stage 06 synthesis outputs.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=default_model(), help="OpenAI model for gap analysis")
    parser.add_argument("--dry-run", action="store_true", help="Write status outputs without calling OpenAI")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing existing Stage 07 outputs")
    parser.add_argument("--no-backup", action="store_true", help="Skip backups when overwriting")
    parser.add_argument("--strict", action="store_true", help="Fail if required Stage 06 files are missing")
    parser.add_argument("--theme", action="append", help="Optional repeatable or comma-separated theme focus filter")
    parser.add_argument("--include-weak-evidence", action="store_true", help="Include weak/limited evidence with caution labels")
    parser.add_argument("--max-input-chars", type=int, help="Maximum combined Stage 06 synthesis characters to send")
    args = parser.parse_args()

    summary = run_ai_gap_analysis(
        project_dir=resolve_project(args.project),
        model=args.model,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        no_backup=args.no_backup,
        strict=args.strict,
        theme_filters=parse_theme_filters(args.theme),
        include_weak_evidence=args.include_weak_evidence,
        max_input_chars=args.max_input_chars,
    )
    print(f"status={summary['status']} gap_rows={summary['rows_written']}")
    print(f"research_gap_analysis={summary['paths']['gap_analysis']}")
    print(f"study_contribution={summary['paths']['contribution']}")
    print(f"problem_statement_refined={summary['paths']['problem_statement']}")
    print(f"gap_matrix={summary['paths']['gap_matrix']}")


if __name__ == "__main__":
    main()
