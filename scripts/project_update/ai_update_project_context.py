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
from scripts.ai.prompts import build_project_context_update_prompt
from scripts.ai.schemas import (
    PROJECT_CONTEXT_CAUTION_LEVELS,
    PROJECT_CONTEXT_CHANGE_COLUMNS,
    PROJECT_CONTEXT_CHANGE_TYPES,
    project_context_update_schema,
)


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-mini"
TO_CONFIRM = "To be confirmed."
PROMPT_VERSION = "project_context_update_v1"

STAGE00_FILES = [
    "research_brief.md",
    "research_questions.md",
    "variables.md",
    "inclusion_exclusion_criteria.md",
    "search_keywords.md",
    "source_strategy.md",
    "writing_scope.md",
    "agent_instructions.md",
]

STAGE06_FILES = [
    "synthesis_matrix.csv",
    "theme_matrix.md",
    "literature_map.md",
    "synthesis_notes.md",
]

STAGE07_FILES = [
    "research_gap_analysis.md",
    "study_contribution.md",
    "problem_statement_refined.md",
    "gap_matrix.csv",
]

ORIGINAL_APPLY_TARGETS = [
    "research_brief.md",
    "research_questions.md",
    "writing_scope.md",
    "agent_instructions.md",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return (
        os.getenv("AI_PROJECT_UPDATE_MODEL", "").strip()
        or os.getenv("AI_GAP_MODEL", "").strip()
        or os.getenv("AI_SYNTHESIS_MODEL", "").strip()
        or DEFAULT_MODEL
    )


def paths(project_dir: Path) -> dict[str, Path]:
    brief = project_dir / "00_brief"
    outline = project_dir / "08_outline"
    drafts = project_dir / "09_drafts"
    return {
        "brief_dir": brief,
        "stage06_dir": project_dir / "06_synthesis",
        "stage07_dir": project_dir / "07_gap_analysis",
        "outline_dir": outline,
        "drafts_dir": drafts,
        "metadata_ai": project_dir / "04_metadata" / "metadata_table_ai_checked.csv",
        "metadata": project_dir / "04_metadata" / "metadata_table.csv",
        "evidence": project_dir / "05_evidence_extraction" / "evidence_table.csv",
        "research_brief_refined": brief / "research_brief_refined.md",
        "research_questions_refined": brief / "research_questions_refined.md",
        "writing_scope_refined": brief / "writing_scope_refined.md",
        "agent_instructions_refined": brief / "agent_instructions_refined.md",
        "outline_context": outline / "_context_for_outline.md",
        "writer_context": drafts / "_context_for_writers.md",
        "summary": brief / "project_context_update_summary.md",
        "blocked": brief / "project_context_update_blocked.md",
        "changes": brief / "project_context_changes.csv",
        "log": project_dir / "logs" / "ai_project_context_update_log.md",
    }


def output_files(p: dict[str, Path]) -> list[Path]:
    return [
        p["research_brief_refined"],
        p["research_questions_refined"],
        p["writing_scope_refined"],
        p["agent_instructions_refined"],
        p["outline_context"],
        p["writer_context"],
        p["summary"],
        p["changes"],
    ]


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


def read_text_file(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    return compact_text(path.read_text(encoding="utf-8", errors="replace").strip(), max_chars)


def read_named_context(base_dir: Path, filenames: list[str], label: str, max_chars: int | None = None) -> tuple[str, list[Path], list[str]]:
    chunks: list[str] = []
    used: list[Path] = []
    warnings: list[str] = []
    for name in filenames:
        path = base_dir / name
        text = read_text_file(path)
        if text:
            chunks.append(f"# {label}: {name}\n\n{text}")
            used.append(path)
        else:
            warnings.append(f"Missing or empty {label} input: {path}")
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


def backup_outputs(outputs: list[Path]) -> list[Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups: list[Path] = []
    for path in outputs:
        if path.exists():
            backup = path.with_suffix(f".{stamp}.bak{path.suffix}")
            backup.write_bytes(path.read_bytes())
            backups.append(backup)
    return backups


def markdown_bullets(values: Any, allowed_citations: set[str]) -> list[str]:
    if not isinstance(values, list) or not values:
        return [f"- {TO_CONFIRM}"]
    return [f"- {sanitize_citation_markers(safe_text(item) or TO_CONFIRM, allowed_citations)}" for item in values]


def sanitize_citation_markers(text: str, allowed_citations: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return match.group(0) if key in allowed_citations else "[@ToBeConfirmed]"

    return re.sub(r"\[@([A-Za-z0-9_.:-]+)\]", replace, text)


def list_value(result: dict[str, Any], key: str) -> list[str]:
    value = result.get(key, [])
    if not isinstance(value, list):
        return [safe_text(value) or TO_CONFIRM]
    return [safe_text(item) or TO_CONFIRM for item in value] or [TO_CONFIRM]


def dict_value(result: dict[str, Any], key: str) -> dict[str, Any]:
    value = result.get(key, {})
    return value if isinstance(value, dict) else {}


def existing_outputs(p: dict[str, Path]) -> list[Path]:
    return [path for path in output_files(p) if path.exists()]


def empty_result(status: str, message: str, warnings: list[str] | None = None) -> dict[str, Any]:
    warning_items = list(dict.fromkeys([message, *(warnings or [])]))
    return {
        "completion_status": status,
        "original_study_focus": TO_CONFIRM,
        "evidence_informed_study_focus": TO_CONFIRM,
        "refined_background": TO_CONFIRM,
        "defensible_research_gap": message,
        "refined_contribution": TO_CONFIRM,
        "current_study_positioning": TO_CONFIRM,
        "scope_boundaries": [TO_CONFIRM],
        "claims_to_avoid": ["Do not use project-context refinements until Stage 07 gap analysis is available."],
        "to_be_confirmed": warning_items,
        "refined_research_questions": {
            "original_research_questions": [TO_CONFIRM],
            "refinement_notes": warning_items,
            "main_research_question": TO_CONFIRM,
            "specific_research_questions": [TO_CONFIRM],
            "questions_to_remove_merge_or_reword": [TO_CONFIRM],
            "rationale_for_changes": warning_items,
            "to_be_confirmed": warning_items,
        },
        "refined_writing_scope": {
            "manuscript_positioning": TO_CONFIRM,
            "included_scope": [TO_CONFIRM],
            "excluded_scope": [TO_CONFIRM],
            "evidence_boundaries": warning_items,
            "literature_use_rules": ["Use original Stage 00 files until refined context is completed."],
            "local_context_framing": TO_CONFIRM,
            "terminology_preferences": [TO_CONFIRM],
            "claims_allowed": [TO_CONFIRM],
            "claims_not_allowed": ["Do not overclaim unsupported novelty, causality, or institutional findings."],
            "to_be_confirmed": warning_items,
        },
        "refined_agent_instructions": {
            "general_rules": ["Use supplied local files only.", "Preserve uncertainty as To be confirmed."],
            "stage_08_outline_instructions": ["Do not create a final outline until Stage 07B is completed."],
            "stage_09_writer_instructions": ["Do not draft from blocked Stage 07B context."],
            "results_and_discussion_instructions": ["To be confirmed."],
            "citation_and_claim_safety_rules": ["Do not invent citations or findings."],
            "gap_informed_positioning_rules": warning_items,
            "to_be_confirmed": warning_items,
        },
        "outline_context": {
            "refined_paper_positioning": TO_CONFIRM,
            "defensible_gap": message,
            "refined_research_questions": [TO_CONFIRM],
            "recommended_argument_flow": [TO_CONFIRM],
            "sections_needing_caution": warning_items,
            "required_inputs_before_final_outline": ["Completed Stage 07 gap-analysis outputs."],
        },
        "writer_context": {
            "core_framing": TO_CONFIRM,
            "safe_claims": [TO_CONFIRM],
            "claims_to_avoid": ["Do not write manuscript sections from blocked Stage 07B context."],
            "citation_use_rules": ["Use only citation keys from supplied local evidence, synthesis, gap analysis, or metadata."],
            "evidence_hierarchy": [TO_CONFIRM],
            "preferred_terms": [TO_CONFIRM],
            "gap_and_contribution_language": [TO_CONFIRM],
            "to_be_confirmed": warning_items,
        },
        "main_framing_changes": warning_items,
        "research_question_changes": warning_items,
        "scope_changes": warning_items,
        "downstream_cascade_notes": warning_items,
        "human_review_checklist": ["Confirm Stage 07 outputs are complete before using refined context."],
        "change_rows": [],
    }


def dry_run_result(warnings: list[str]) -> dict[str, Any]:
    return empty_result("partial", "Dry run only. No OpenAI request was made.", warnings)


def build_request_payload(
    model: str,
    original_brief_context: str,
    synthesis_context: str,
    gap_analysis_context: str,
    evidence_context: str = "",
    metadata_context: str = "",
    apply_to_originals: bool = False,
) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_project_context_update_prompt(
            original_brief_context,
            synthesis_context,
            gap_analysis_context,
            evidence_context,
            metadata_context,
            apply_to_originals,
        ),
        input_data={
            "original_brief_context": original_brief_context,
            "synthesis_context": synthesis_context,
            "gap_analysis_context": gap_analysis_context,
            "evidence_context": evidence_context,
            "metadata_context": metadata_context,
            "apply_to_originals": apply_to_originals,
        },
        schema=project_context_update_schema(),
        schema_name="stage07b_project_context_update",
    )


def call_openai_project_context_update(
    api_key: str,
    model: str,
    original_brief_context: str,
    synthesis_context: str,
    gap_analysis_context: str,
    evidence_context: str = "",
    metadata_context: str = "",
    apply_to_originals: bool = False,
    timeout: int = 180,
    retries: int = 2,
) -> dict[str, Any]:
    return AIClient(api_key=api_key, default_model=model).responses_json(
        instructions=build_project_context_update_prompt(
            original_brief_context,
            synthesis_context,
            gap_analysis_context,
            evidence_context,
            metadata_context,
            apply_to_originals,
        ),
        input_data={
            "original_brief_context": original_brief_context,
            "synthesis_context": synthesis_context,
            "gap_analysis_context": gap_analysis_context,
            "evidence_context": evidence_context,
            "metadata_context": metadata_context,
            "apply_to_originals": apply_to_originals,
        },
        schema=project_context_update_schema(),
        schema_name="stage07b_project_context_update",
        timeout=timeout,
        retries=retries,
    )


def normalize_change_rows(result: dict[str, Any], warnings: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, item in enumerate(result.get("change_rows", []), start=1):
        if not isinstance(item, dict):
            warnings.append(f"Change row {index} was not an object; skipped.")
            continue
        row = {column: safe_text(item.get(column, "")) for column in PROJECT_CONTEXT_CHANGE_COLUMNS if column != "change_id"}
        row["change_id"] = f"CTX-{len(rows) + 1:04d}"
        for required in ["file_target", "change_type", "original_point", "refined_point", "rationale"]:
            if not row.get(required):
                warnings.append(f"{row['change_id']} missing {required}; filled with To be confirmed.")
                row[required] = TO_CONFIRM
        if row["change_type"] not in PROJECT_CONTEXT_CHANGE_TYPES:
            warnings.append(f"Invalid change_type for {row['change_id']}; coerced to to_be_confirmed.")
            row["change_type"] = "to_be_confirmed"
        if row["caution_level"] not in PROJECT_CONTEXT_CAUTION_LEVELS:
            warnings.append(f"Invalid caution_level for {row['change_id']}; coerced to to_be_confirmed.")
            row["caution_level"] = "to_be_confirmed"
        if row["human_review_needed"] not in {"yes", "no"}:
            warnings.append(f"Invalid human_review_needed for {row['change_id']}; coerced to yes.")
            row["human_review_needed"] = "yes"
        for column in PROJECT_CONTEXT_CHANGE_COLUMNS:
            row[column] = row.get(column) or TO_CONFIRM
        rows.append({column: row[column] for column in PROJECT_CONTEXT_CHANGE_COLUMNS})
    return rows


def normalize_result(result: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    warnings = [safe_text(item) for item in result.get("to_be_confirmed", []) if safe_text(item)]
    if result.get("completion_status") not in {"completed", "partial", "blocked"}:
        warnings.append("Invalid completion_status; coerced to partial.")
        result["completion_status"] = "partial"
    for key in [
        "original_study_focus",
        "evidence_informed_study_focus",
        "refined_background",
        "defensible_research_gap",
        "refined_contribution",
        "current_study_positioning",
    ]:
        if not safe_text(result.get(key, "")):
            warnings.append(f"Missing {key}; filled with To be confirmed.")
            result[key] = TO_CONFIRM
    for key in [
        "scope_boundaries",
        "claims_to_avoid",
        "main_framing_changes",
        "research_question_changes",
        "scope_changes",
        "downstream_cascade_notes",
        "human_review_checklist",
    ]:
        if not isinstance(result.get(key), list):
            warnings.append(f"Missing or invalid {key}; filled with To be confirmed.")
            result[key] = [TO_CONFIRM]
    for key in ["refined_research_questions", "refined_writing_scope", "refined_agent_instructions", "outline_context", "writer_context"]:
        if not isinstance(result.get(key), dict):
            warnings.append(f"Missing {key}; filled with blocked placeholder.")
            result[key] = dict_value(empty_result("partial", TO_CONFIRM), key)
    rows = normalize_change_rows(result, warnings)
    result["to_be_confirmed"] = list(dict.fromkeys([*warnings, *list_value(result, "to_be_confirmed")]))
    return result, rows, warnings


def write_research_brief(path: Path, result: dict[str, Any], model: str, input_paths: list[Path], allowed_citations: set[str]) -> None:
    lines = ["# Refined Research Brief", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    for heading, key in [
        ("Refinement Status", "completion_status"),
        ("Original Study Focus", "original_study_focus"),
        ("Evidence-Informed Study Focus", "evidence_informed_study_focus"),
        ("Refined Background", "refined_background"),
        ("Defensible Research Gap", "defensible_research_gap"),
        ("Refined Contribution", "refined_contribution"),
        ("Current Study Positioning", "current_study_positioning"),
    ]:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(result.get(key, "")) or TO_CONFIRM, allowed_citations), ""])
    for heading, key in [("Scope Boundaries", "scope_boundaries"), ("Claims to Avoid", "claims_to_avoid"), ("To Be Confirmed", "to_be_confirmed")]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(result.get(key, []), allowed_citations))
        lines.append("")
    lines.extend(["## Inputs Used", ""])
    lines.extend([f"- {path}" for path in input_paths] or ["- none"])
    lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_research_questions(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    rq = dict_value(result, "refined_research_questions")
    lines = ["# Refined Research Questions", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    for heading, key in [
        ("Original Research Questions", "original_research_questions"),
        ("Evidence-Informed Refinement Notes", "refinement_notes"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(rq.get(key, []), allowed_citations))
        lines.append("")
    lines.extend(["## Refined Main Research Question", "", sanitize_citation_markers(safe_text(rq.get("main_research_question", "")) or TO_CONFIRM, allowed_citations), ""])
    for heading, key in [
        ("Refined Specific Research Questions", "specific_research_questions"),
        ("Questions to Remove, Merge, or Reword", "questions_to_remove_merge_or_reword"),
        ("Rationale for Changes", "rationale_for_changes"),
        ("To Be Confirmed", "to_be_confirmed"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(rq.get(key, []), allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_writing_scope(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    scope = dict_value(result, "refined_writing_scope")
    lines = ["# Refined Writing Scope", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    lines.extend(["## Manuscript Positioning", "", sanitize_citation_markers(safe_text(scope.get("manuscript_positioning", "")) or TO_CONFIRM, allowed_citations), ""])
    for heading, key in [
        ("Included Scope", "included_scope"),
        ("Excluded Scope", "excluded_scope"),
        ("Evidence Boundaries", "evidence_boundaries"),
        ("Literature Use Rules", "literature_use_rules"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(scope.get(key, []), allowed_citations))
        lines.append("")
    lines.extend(["## Local Context Framing", "", sanitize_citation_markers(safe_text(scope.get("local_context_framing", "")) or TO_CONFIRM, allowed_citations), ""])
    for heading, key in [
        ("Terminology Preferences", "terminology_preferences"),
        ("Claims Allowed", "claims_allowed"),
        ("Claims Not Allowed", "claims_not_allowed"),
        ("To Be Confirmed", "to_be_confirmed"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(scope.get(key, []), allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_agent_instructions(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    inst = dict_value(result, "refined_agent_instructions")
    lines = ["# Refined Agent Instructions", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    lines.extend(["## General Rules for Downstream Agents", ""])
    lines.extend(markdown_bullets(inst.get("general_rules", []), allowed_citations))
    lines.extend([
        "",
        "## Preferred Refined Files",
        "",
        "When present, downstream agents should prefer:",
        "",
        "- 00_brief/research_brief_refined.md",
        "- 00_brief/research_questions_refined.md",
        "- 00_brief/writing_scope_refined.md",
        "- 00_brief/agent_instructions_refined.md",
        "",
        "over the original Stage 00 files.",
        "",
    ])
    for heading, key in [
        ("Instructions for Stage 08 Outline Agent", "stage_08_outline_instructions"),
        ("Instructions for Stage 09 Introduction/RRL Writer", "stage_09_writer_instructions"),
        ("Instructions for Results and Discussion Agents", "results_and_discussion_instructions"),
        ("Citation and Claim Safety Rules", "citation_and_claim_safety_rules"),
        ("Gap-Informed Positioning Rules", "gap_informed_positioning_rules"),
        ("To Be Confirmed", "to_be_confirmed"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(inst.get(key, []), allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_outline_context(path: Path, result: dict[str, Any], allowed_citations: set[str]) -> None:
    ctx = dict_value(result, "outline_context")
    lines = ["# Context for Outline Agent", ""]
    for heading, key in [
        ("Refined Paper Positioning", "refined_paper_positioning"),
        ("Defensible Gap", "defensible_gap"),
    ]:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(ctx.get(key, "")) or TO_CONFIRM, allowed_citations), ""])
    for heading, key in [
        ("Refined Research Questions", "refined_research_questions"),
        ("Recommended Manuscript Argument Flow", "recommended_argument_flow"),
        ("Sections That Need Caution", "sections_needing_caution"),
        ("Required Inputs Before Final Outline", "required_inputs_before_final_outline"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(ctx.get(key, []), allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_writer_context(path: Path, result: dict[str, Any], allowed_citations: set[str]) -> None:
    ctx = dict_value(result, "writer_context")
    lines = ["# Context for Writing Agents", "", "## Core Framing", "", sanitize_citation_markers(safe_text(ctx.get("core_framing", "")) or TO_CONFIRM, allowed_citations), ""]
    for heading, key in [
        ("Safe Claims", "safe_claims"),
        ("Claims to Avoid", "claims_to_avoid"),
        ("Citation Use Rules", "citation_use_rules"),
        ("Evidence Hierarchy", "evidence_hierarchy"),
        ("Preferred Terms", "preferred_terms"),
        ("Gap and Contribution Language", "gap_and_contribution_language"),
        ("To Be Confirmed", "to_be_confirmed"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(ctx.get(key, []), allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_summary(path: Path, result: dict[str, Any], rows: list[dict[str, str]], model: str, input_paths: list[Path], output_paths: list[Path], warnings: list[str]) -> None:
    lines = ["# Project Context Update Summary", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    lines.extend(["## Status", "", safe_text(result.get("completion_status", "")) or TO_CONFIRM, ""])
    lines.extend(["## Files Read", ""])
    lines.extend([f"- {path}" for path in input_paths] or ["- none"])
    lines.extend(["", "## Files Written", ""])
    lines.extend([f"- {path}" for path in output_paths] or ["- none"])
    for heading, key in [
        ("Main Framing Changes", "main_framing_changes"),
        ("Research Question Changes", "research_question_changes"),
        ("Scope Changes", "scope_changes"),
        ("Downstream Cascade Notes", "downstream_cascade_notes"),
        ("Human Review Checklist", "human_review_checklist"),
    ]:
        lines.extend(["", f"## {heading}", ""])
        lines.extend([f"- {safe_text(item) or TO_CONFIRM}" for item in result.get(key, [])] if isinstance(result.get(key), list) else [f"- {TO_CONFIRM}"])
    lines.extend(["", "## Change Rows", "", f"- Rows written: {len(rows)}", ""])
    if warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_blocked_status(path: Path, message: str, model: str, warnings: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Project Context Update Blocked",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Model: {model}",
        "",
        "## Status",
        "",
        message,
        "",
        "## To Be Confirmed",
        "",
    ]
    lines.extend(f"- {warning}" for warning in warnings or [TO_CONFIRM])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_outputs(project_dir: Path, result: dict[str, Any], rows: list[dict[str, str]], model: str, input_paths: list[Path], allowed_citations: set[str]) -> dict[str, Path]:
    p = paths(project_dir)
    for key in ["brief_dir", "outline_dir", "drafts_dir"]:
        p[key].mkdir(parents=True, exist_ok=True)
    write_research_brief(p["research_brief_refined"], result, model, input_paths, allowed_citations)
    write_research_questions(p["research_questions_refined"], result, model, allowed_citations)
    write_writing_scope(p["writing_scope_refined"], result, model, allowed_citations)
    write_agent_instructions(p["agent_instructions_refined"], result, model, allowed_citations)
    write_outline_context(p["outline_context"], result, allowed_citations)
    write_writer_context(p["writer_context"], result, allowed_citations)
    pd.DataFrame(rows, columns=PROJECT_CONTEXT_CHANGE_COLUMNS).fillna("").to_csv(p["changes"], index=False, encoding="utf-8")
    summary_outputs = output_files(p)
    write_summary(p["summary"], result, rows, model, input_paths, summary_outputs, list_value(result, "to_be_confirmed"))
    return p


def apply_refined_to_originals(project_dir: Path, no_backup: bool) -> list[Path]:
    p = paths(project_dir)
    mapping = {
        "research_brief.md": p["research_brief_refined"],
        "research_questions.md": p["research_questions_refined"],
        "writing_scope.md": p["writing_scope_refined"],
        "agent_instructions.md": p["agent_instructions_refined"],
    }
    originals = [p["brief_dir"] / name for name in ORIGINAL_APPLY_TARGETS if (p["brief_dir"] / name).exists()]
    backups = [] if no_backup else backup_outputs(originals)
    for name, source in mapping.items():
        target = p["brief_dir"] / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return backups


def write_log(
    log_path: Path,
    model: str,
    project_dir: Path,
    input_paths: list[Path],
    output_paths: list[Path],
    change_rows_written: int,
    dry_run: bool,
    overwrite: bool,
    apply_to_originals: bool,
    strict: bool,
    warnings: list[str],
) -> None:
    write_ai_run_log(
        log_path,
        task_name="stage07b_project_context_update",
        model=model,
        input_paths=input_paths,
        output_paths=output_paths,
        counts={
            "project_path": project_dir,
            "change_rows_written": change_rows_written,
            "dry_run": str(dry_run).lower(),
            "overwrite": str(overwrite).lower(),
            "apply_to_originals": str(apply_to_originals).lower(),
            "strict": str(strict).lower(),
        },
        errors=warnings,
        prompt_version=PROMPT_VERSION,
    )


def run_ai_project_context_update(
    project_dir: Path,
    model: str,
    dry_run: bool,
    overwrite: bool,
    no_backup: bool,
    strict: bool,
    apply_to_originals: bool,
    max_input_chars: int | None,
) -> dict[str, Any]:
    if apply_to_originals and not overwrite:
        raise ValueError("--apply-to-originals requires --overwrite.")

    p = paths(project_dir)
    p["brief_dir"].mkdir(parents=True, exist_ok=True)
    p["stage07_dir"].mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    original_context, original_paths, original_warnings = read_named_context(p["brief_dir"], STAGE00_FILES, "Stage 00", max_input_chars)
    synthesis_context, synthesis_paths, synthesis_warnings = read_named_context(p["stage06_dir"], STAGE06_FILES, "Stage 06", max_input_chars)
    gap_context, gap_paths, gap_warnings = read_named_context(p["stage07_dir"], STAGE07_FILES, "Stage 07", max_input_chars)
    warnings.extend(synthesis_warnings)
    warnings.extend(gap_warnings)
    warnings.extend(original_warnings)

    existing = existing_outputs(p)
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing Stage 07B outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup or not existing else backup_outputs(existing)

    input_paths = [*original_paths, *synthesis_paths, *gap_paths]
    if not gap_context:
        message = "Stage 07 gap-analysis outputs must be completed before Stage 07B project context update."
        if strict:
            raise FileNotFoundError(message)
        result = empty_result("blocked", message, warnings)
        write_blocked_status(p["blocked"], message, model, warnings)
        write_summary(p["summary"], result, [], model, input_paths, [p["blocked"], p["summary"], p["log"]], warnings)
        write_log(p["log"], model, project_dir, input_paths, [p["blocked"], p["summary"], p["log"]], 0, dry_run, overwrite, apply_to_originals, strict, warnings)
        return {"status": "blocked", "rows_written": 0, "paths": p, "warnings": warnings, "backups": backups}

    evidence_context, evidence_path, evidence_citations = read_csv_context(p["evidence"])
    metadata_context, metadata_path, metadata_citations = read_metadata_context(project_dir)
    if evidence_path:
        input_paths.append(evidence_path)
    if metadata_path:
        input_paths.append(metadata_path)

    allowed_citations = {
        key
        for key in [
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", original_context),
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", synthesis_context),
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", gap_context),
            *evidence_citations,
            *metadata_citations,
        ]
        if key and key != "ToBeConfirmed"
    }

    if dry_run:
        result = dry_run_result(warnings)
        result, rows, validation_warnings = normalize_result(result)
        warnings = list(dict.fromkeys([*warnings, *validation_warnings]))
        write_summary(p["summary"], result, rows, model, input_paths, [p["summary"], p["log"]], warnings)
        write_log(p["log"], model, project_dir, input_paths, [p["summary"], p["log"]], len(rows), dry_run, overwrite, apply_to_originals, strict, warnings)
        return {"status": "partial", "rows_written": len(rows), "paths": p, "warnings": warnings, "backups": backups}

    load_dotenv(repo_root() / ".env")
    api_key = require_api_key(dry_run=False)
    result = call_openai_project_context_update(
        api_key or "",
        model,
        original_context,
        synthesis_context,
        gap_context,
        evidence_context,
        metadata_context,
        apply_to_originals,
    )
    result, rows, validation_warnings = normalize_result(result)
    warnings = list(dict.fromkeys([*warnings, *validation_warnings]))
    result["to_be_confirmed"] = list(dict.fromkeys([*list_value(result, "to_be_confirmed"), *warnings]))
    write_outputs(project_dir, result, rows, model, input_paths, allowed_citations)
    output_paths = output_files(p) + [p["log"]]
    original_backups: list[Path] = []
    if apply_to_originals:
        original_backups = apply_refined_to_originals(project_dir, no_backup=no_backup)
        output_paths.extend(p["brief_dir"] / name for name in ORIGINAL_APPLY_TARGETS)
        output_paths.extend(original_backups)
        warnings.append("Original Stage 00 files were replaced from refined outputs after backup.")
    write_log(p["log"], model, project_dir, input_paths, output_paths, len(rows), dry_run, overwrite, apply_to_originals, strict, warnings)
    return {
        "status": result.get("completion_status", "completed"),
        "rows_written": len(rows),
        "paths": p,
        "warnings": warnings,
        "backups": [*backups, *original_backups],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to create Stage 07B refined project-context files after gap analysis.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=default_model(), help="OpenAI model for project context update")
    parser.add_argument("--dry-run", action="store_true", help="Write status outputs without calling OpenAI")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing existing refined outputs")
    parser.add_argument("--no-backup", action="store_true", help="Skip timestamped backups when overwriting")
    parser.add_argument("--strict", action="store_true", help="Fail if Stage 07 gap-analysis outputs are missing")
    parser.add_argument("--apply-to-originals", action="store_true", help="Replace selected original Stage 00 files after backing them up")
    parser.add_argument("--max-input-chars", type=int, help="Maximum combined context characters per stage group")
    args = parser.parse_args()

    summary = run_ai_project_context_update(
        project_dir=resolve_project(args.project),
        model=args.model,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        no_backup=args.no_backup,
        strict=args.strict,
        apply_to_originals=args.apply_to_originals,
        max_input_chars=args.max_input_chars,
    )
    print(f"status={summary['status']} change_rows={summary['rows_written']}")
    print(f"research_brief_refined={summary['paths']['research_brief_refined']}")
    print(f"research_questions_refined={summary['paths']['research_questions_refined']}")
    print(f"writing_scope_refined={summary['paths']['writing_scope_refined']}")
    print(f"agent_instructions_refined={summary['paths']['agent_instructions_refined']}")


if __name__ == "__main__":
    main()
