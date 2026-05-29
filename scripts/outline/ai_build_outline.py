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
from scripts.ai.prompts import build_outline_prompt
from scripts.ai.schemas import (
    MANUSCRIPT_SECTIONS,
    OUTLINE_MAP_COLUMNS,
    OUTLINE_READINESS_STATUSES,
    outline_schema,
)


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-mini"
TO_CONFIRM = "To be confirmed."
PROMPT_VERSION = "outline_v1"

REFINED_CONTEXT_FILES = [
    "research_brief_refined.md",
    "research_questions_refined.md",
    "writing_scope_refined.md",
    "agent_instructions_refined.md",
]

ORIGINAL_CONTEXT_FILES = [
    "research_brief.md",
    "research_questions.md",
    "variables.md",
    "inclusion_exclusion_criteria.md",
    "writing_scope.md",
    "agent_instructions.md",
]

STAGE06_FILES = ["synthesis_matrix.csv", "theme_matrix.md", "literature_map.md", "synthesis_notes.md"]
STAGE07_FILES = ["research_gap_analysis.md", "study_contribution.md", "problem_statement_refined.md", "gap_matrix.csv"]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return (
        os.getenv("AI_OUTLINE_MODEL", "").strip()
        or os.getenv("AI_PROJECT_UPDATE_MODEL", "").strip()
        or os.getenv("AI_GAP_MODEL", "").strip()
        or DEFAULT_MODEL
    )


def paths(project_dir: Path) -> dict[str, Path]:
    outline = project_dir / "08_outline"
    return {
        "brief_dir": project_dir / "00_brief",
        "stage06_dir": project_dir / "06_synthesis",
        "stage07_dir": project_dir / "07_gap_analysis",
        "input_dir": project_dir / "input",
        "raw_tables_dir": project_dir / "input" / "raw_tables",
        "outline_dir": outline,
        "outline_context": outline / "_context_for_outline.md",
        "study_notes": project_dir / "input" / "study_notes.md",
        "statistical_results": project_dir / "input" / "statistical_results.md",
        "metadata_ai": project_dir / "04_metadata" / "metadata_table_ai_checked.csv",
        "metadata": project_dir / "04_metadata" / "metadata_table.csv",
        "evidence": project_dir / "05_evidence_extraction" / "evidence_table.csv",
        "manuscript": outline / "manuscript_outline.md",
        "introduction": outline / "introduction_outline.md",
        "rrl": outline / "rrl_outline.md",
        "methodology": outline / "methodology_outline.md",
        "results": outline / "results_outline.md",
        "discussion": outline / "discussion_outline.md",
        "map": outline / "outline_map.csv",
        "checklist": outline / "outline_readiness_checklist.md",
        "log": project_dir / "logs" / "ai_outline_log.md",
    }


def output_files(p: dict[str, Path]) -> list[Path]:
    return [p["manuscript"], p["introduction"], p["rrl"], p["methodology"], p["results"], p["discussion"], p["map"], p["checklist"]]


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


def read_named_context(base_dir: Path, filenames: list[str], label: str, max_chars: int | None = None, warn_missing: bool = True) -> tuple[str, list[Path], list[str]]:
    chunks: list[str] = []
    used: list[Path] = []
    warnings: list[str] = []
    for name in filenames:
        path = base_dir / name
        text = read_text_file(path)
        if text:
            chunks.append(f"# {label}: {name}\n\n{text}")
            used.append(path)
        elif warn_missing:
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


def read_results_context(project_dir: Path, include_results_outline: bool, max_chars: int | None = None) -> tuple[str, list[Path], list[str], bool]:
    if not include_results_outline:
        return "", [], ["Results outline disabled by --include-results-outline false."], False
    p = paths(project_dir)
    chunks: list[str] = []
    used: list[Path] = []
    warnings: list[str] = []
    stats = read_text_file(p["statistical_results"])
    if stats:
        chunks.append(f"# statistical_results.md\n\n{stats}")
        used.append(p["statistical_results"])
    elif p["statistical_results"].exists():
        warnings.append(f"Empty statistical results input: {p['statistical_results']}")
    else:
        warnings.append(f"Missing statistical results input: {p['statistical_results']}")
    if p["raw_tables_dir"].exists():
        for path in sorted(p["raw_tables_dir"].glob("*")):
            if path.is_file():
                text = read_text_file(path, 8000)
                if text:
                    chunks.append(f"# raw_tables/{path.name}\n\n{text}")
                    used.append(path)
    else:
        warnings.append(f"Missing raw tables folder: {p['raw_tables_dir']}")
    context = compact_text("\n\n".join(chunks), max_chars)
    return context, used, warnings, bool(context)


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


def sanitize_citation_markers(text: str, allowed_citations: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return match.group(0) if key in allowed_citations else "[@ToBeConfirmed]"

    return re.sub(r"\[@([A-Za-z0-9_.:-]+)\]", replace, text)


def markdown_bullets(values: Any, allowed_citations: set[str]) -> list[str]:
    if not isinstance(values, list) or not values:
        return [f"- {TO_CONFIRM}"]
    return [f"- {sanitize_citation_markers(safe_text(item) or TO_CONFIRM, allowed_citations)}" for item in values]


def dict_value(result: dict[str, Any], key: str) -> dict[str, Any]:
    value = result.get(key, {})
    return value if isinstance(value, dict) else {}


def list_value(result: dict[str, Any], key: str) -> list[str]:
    value = result.get(key, [])
    if not isinstance(value, list):
        return [safe_text(value) or TO_CONFIRM]
    return [safe_text(item) or TO_CONFIRM for item in value] or [TO_CONFIRM]


def empty_result(status: str, message: str, warnings: list[str] | None = None, has_results: bool = False) -> dict[str, Any]:
    warning_items = list(dict.fromkeys([message, *(warnings or [])]))
    results_status = "partial" if has_results else "blocked"
    return {
        "completion_status": status,
        "refined_manuscript_positioning": TO_CONFIRM,
        "working_title_direction": TO_CONFIRM,
        "central_argument": TO_CONFIRM,
        "intended_manuscript_flow": warning_items,
        "section_level_outline": {
            "introduction": [TO_CONFIRM],
            "review_of_related_literature": [TO_CONFIRM],
            "methodology": [TO_CONFIRM],
            "results": ["To be confirmed."],
            "discussion": ["To be confirmed."],
            "conclusion_recommendations": [TO_CONFIRM],
        },
        "introduction_outline": {
            "opening_context": [TO_CONFIRM],
            "problem_background": [TO_CONFIRM],
            "evidence_based_gap": [TO_CONFIRM],
            "local_context": [TO_CONFIRM],
            "study_purpose": [TO_CONFIRM],
            "research_questions_or_objectives": [TO_CONFIRM],
            "significance": [TO_CONFIRM],
            "scope_and_delimitations": [TO_CONFIRM],
            "suggested_citation_anchors": [TO_CONFIRM],
            "claims_to_avoid": ["Do not draft from blocked outline context."],
            "to_be_confirmed": warning_items,
        },
        "rrl_outline": {
            "rrl_framing": TO_CONFIRM,
            "themes": [],
            "direct_evidence_section": [TO_CONFIRM],
            "indirect_evidence_section": [TO_CONFIRM],
            "methodological_literature_section": [TO_CONFIRM],
            "synthesis_toward_gap": [TO_CONFIRM],
            "claims_to_avoid": ["Do not invent citations."],
            "to_be_confirmed": warning_items,
        },
        "methodology_outline": {
            "research_design": TO_CONFIRM,
            "study_setting": TO_CONFIRM,
            "population_and_sampling": TO_CONFIRM,
            "variables": [TO_CONFIRM],
            "data_sources": [TO_CONFIRM],
            "measures_and_operational_definitions": [TO_CONFIRM],
            "statistical_analysis_plan": [TO_CONFIRM],
            "ethical_considerations": TO_CONFIRM,
            "limitations_of_method": [TO_CONFIRM],
            "to_be_confirmed": warning_items,
        },
        "results_outline": {
            "completion_status": results_status,
            "available_statistical_inputs": [TO_CONFIRM],
            "proposed_results_organization": [TO_CONFIRM],
            "table_and_figure_plan": [TO_CONFIRM],
            "results_by_research_question": [TO_CONFIRM],
            "required_statistical_outputs": [TO_CONFIRM],
            "missing_results_to_confirm": warning_items,
            "claims_not_allowed_yet": ["Do not claim statistical significance or findings until supplied by the user."],
        },
        "discussion_outline": {
            "opening_summary_of_expected_results": [TO_CONFIRM],
            "interpretation_plan": [TO_CONFIRM],
            "relationship_to_literature_synthesis": [TO_CONFIRM],
            "implications": [TO_CONFIRM],
            "limitations": [TO_CONFIRM],
            "recommendations": [TO_CONFIRM],
            "conclusion_direction": [TO_CONFIRM],
            "claims_to_avoid": ["Do not interpret results that are not supplied."],
            "to_be_confirmed": warning_items,
        },
        "citation_and_evidence_use_rules": ["Use only supplied local citation keys."],
        "claims_to_avoid": ["Do not invent results, sources, statistics, or institutional facts."],
        "items_to_confirm": warning_items,
        "outline_map_rows": [],
        "readiness": {
            "ready_for_drafting": [TO_CONFIRM],
            "partially_ready": warning_items,
            "blocked_until_more_inputs": warning_items,
            "human_review_needed": ["Review outline before Stage 09 writing."],
            "recommended_next_step": message,
        },
    }


def dry_run_result(warnings: list[str], has_results: bool) -> dict[str, Any]:
    return empty_result("partial", "Dry run only. No OpenAI request was made.", warnings, has_results)


def build_request_payload(
    model: str,
    refined_context: str,
    original_context: str,
    synthesis_context: str,
    gap_context: str,
    evidence_context: str = "",
    metadata_context: str = "",
    results_context: str = "",
    prefer_refined: bool = True,
    include_results_outline: bool = True,
) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_outline_prompt(
            refined_context,
            original_context,
            synthesis_context,
            gap_context,
            evidence_context,
            metadata_context,
            results_context,
            prefer_refined,
            include_results_outline,
        ),
        input_data={
            "refined_context": refined_context,
            "original_context": original_context,
            "synthesis_context": synthesis_context,
            "gap_context": gap_context,
            "evidence_context": evidence_context,
            "metadata_context": metadata_context,
            "results_context": results_context,
            "prefer_refined": prefer_refined,
            "include_results_outline": include_results_outline,
        },
        schema=outline_schema(),
        schema_name="stage08_outline",
    )


def call_openai_outline(
    api_key: str,
    model: str,
    refined_context: str,
    original_context: str,
    synthesis_context: str,
    gap_context: str,
    evidence_context: str = "",
    metadata_context: str = "",
    results_context: str = "",
    prefer_refined: bool = True,
    include_results_outline: bool = True,
    timeout: int = 180,
    retries: int = 2,
) -> dict[str, Any]:
    return AIClient(api_key=api_key, default_model=model).responses_json(
        instructions=build_outline_prompt(
            refined_context,
            original_context,
            synthesis_context,
            gap_context,
            evidence_context,
            metadata_context,
            results_context,
            prefer_refined,
            include_results_outline,
        ),
        input_data={
            "refined_context": refined_context,
            "original_context": original_context,
            "synthesis_context": synthesis_context,
            "gap_context": gap_context,
            "evidence_context": evidence_context,
            "metadata_context": metadata_context,
            "results_context": results_context,
            "prefer_refined": prefer_refined,
            "include_results_outline": include_results_outline,
        },
        schema=outline_schema(),
        schema_name="stage08_outline",
        timeout=timeout,
        retries=retries,
    )


def normalize_outline_rows(result: dict[str, Any], warnings: list[str], has_results: bool) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, item in enumerate(result.get("outline_map_rows", []), start=1):
        if not isinstance(item, dict):
            warnings.append(f"Outline map row {index} was not an object; skipped.")
            continue
        row = {column: safe_text(item.get(column, "")) for column in OUTLINE_MAP_COLUMNS if column != "outline_id"}
        row["outline_id"] = f"OUT-{len(rows) + 1:04d}"
        for required in ["manuscript_section", "subsection"]:
            if not row.get(required):
                warnings.append(f"{row['outline_id']} missing {required}; filled with To be confirmed.")
                row[required] = TO_CONFIRM
        if row["manuscript_section"] not in MANUSCRIPT_SECTIONS:
            warnings.append(f"Invalid manuscript_section for {row['outline_id']}; coerced to to_be_confirmed.")
            row["manuscript_section"] = "to_be_confirmed"
        if row["readiness_status"] not in OUTLINE_READINESS_STATUSES:
            warnings.append(f"Invalid readiness_status for {row['outline_id']}; coerced to to_be_confirmed.")
            row["readiness_status"] = "to_be_confirmed"
        if row["manuscript_section"] in {"results", "discussion"} and not has_results and row["readiness_status"] == "ready":
            warnings.append(f"{row['outline_id']} depends on missing statistical results; readiness_status set to blocked.")
            row["readiness_status"] = "blocked"
        for column in OUTLINE_MAP_COLUMNS:
            row[column] = row.get(column) or TO_CONFIRM
        rows.append({column: row[column] for column in OUTLINE_MAP_COLUMNS})
    return rows


def normalize_result(result: dict[str, Any], has_results: bool) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    warnings = [safe_text(item) for item in result.get("items_to_confirm", []) if safe_text(item)]
    if result.get("completion_status") not in {"completed", "partial", "blocked"}:
        warnings.append("Invalid completion_status; coerced to partial.")
        result["completion_status"] = "partial"
    for key in ["refined_manuscript_positioning", "working_title_direction", "central_argument"]:
        if not safe_text(result.get(key, "")):
            warnings.append(f"Missing {key}; filled with To be confirmed.")
            result[key] = TO_CONFIRM
    for key in ["section_level_outline", "introduction_outline", "rrl_outline", "methodology_outline", "results_outline", "discussion_outline", "readiness"]:
        if not isinstance(result.get(key), dict):
            warnings.append(f"Missing {key}; filled with placeholder.")
            result[key] = empty_result("partial", TO_CONFIRM, [], has_results)[key]
    results = dict_value(result, "results_outline")
    if results.get("completion_status") not in OUTLINE_READINESS_STATUSES:
        warnings.append("Invalid results completion_status; coerced to to_be_confirmed.")
        results["completion_status"] = "to_be_confirmed"
    if not has_results and results.get("completion_status") == "ready":
        warnings.append("Results outline marked ready without statistical inputs; coerced to blocked.")
        results["completion_status"] = "blocked"
        missing = results.get("missing_results_to_confirm", [])
        results["missing_results_to_confirm"] = list(dict.fromkeys([*(missing if isinstance(missing, list) else []), "Statistical results are To be confirmed."]))
    rows = normalize_outline_rows(result, warnings, has_results)
    result["items_to_confirm"] = list(dict.fromkeys([*warnings, *list_value(result, "items_to_confirm")]))
    return result, rows, warnings


def write_manuscript_outline(path: Path, result: dict[str, Any], model: str, input_paths: list[Path], allowed_citations: set[str]) -> None:
    section_outline = dict_value(result, "section_level_outline")
    lines = ["# Manuscript Outline", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    lines.extend(["## Completion Status", "", safe_text(result.get("completion_status", "")) or TO_CONFIRM, ""])
    lines.extend(["## Inputs Used", ""])
    lines.extend([f"- {path}" for path in input_paths] or ["- none"])
    lines.append("")
    for heading, key in [
        ("Refined Manuscript Positioning", "refined_manuscript_positioning"),
        ("Working Title or Title Direction", "working_title_direction"),
        ("Central Argument", "central_argument"),
    ]:
        lines.extend([f"## {heading}", "", sanitize_citation_markers(safe_text(result.get(key, "")) or TO_CONFIRM, allowed_citations), ""])
    lines.extend(["## Intended Manuscript Flow", ""])
    lines.extend(markdown_bullets(result.get("intended_manuscript_flow", []), allowed_citations))
    lines.extend(["", "## Section-Level Outline", ""])
    for label, key in [
        ("I. Introduction", "introduction"),
        ("II. Review of Related Literature", "review_of_related_literature"),
        ("III. Methodology", "methodology"),
        ("IV. Results", "results"),
        ("V. Discussion", "discussion"),
        ("VI. Conclusion and Recommendations", "conclusion_recommendations"),
    ]:
        lines.extend([f"### {label}", ""])
        lines.extend(markdown_bullets(section_outline.get(key, []), allowed_citations))
        lines.append("")
    for heading, key in [
        ("Citation and Evidence Use Rules", "citation_and_evidence_use_rules"),
        ("Claims to Avoid", "claims_to_avoid"),
        ("Items To Be Confirmed", "items_to_confirm"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(result.get(key, []), allowed_citations))
        lines.append("")
    readiness = dict_value(result, "readiness")
    lines.extend(["## Recommended Next Step", "", safe_text(readiness.get("recommended_next_step", "")) or TO_CONFIRM, ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_list_outline(path: Path, title: str, sections: list[tuple[str, Any]], allowed_citations: set[str], model: str) -> None:
    lines = [f"# {title}", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    for heading, value in sections:
        lines.extend([f"## {heading}", ""])
        if isinstance(value, str):
            lines.append(sanitize_citation_markers(value or TO_CONFIRM, allowed_citations))
        else:
            lines.extend(markdown_bullets(value, allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_rrl_outline(path: Path, result: dict[str, Any], model: str, allowed_citations: set[str]) -> None:
    rrl = dict_value(result, "rrl_outline")
    lines = ["# Review of Related Literature Outline", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    lines.extend(["## RRL Framing", "", sanitize_citation_markers(safe_text(rrl.get("rrl_framing", "")) or TO_CONFIRM, allowed_citations), ""])
    themes = rrl.get("themes", [])
    if not isinstance(themes, list) or not themes:
        themes = [{"theme": TO_CONFIRM, "key_evidence_to_discuss": [TO_CONFIRM], "suggested_citation_anchors": [TO_CONFIRM], "relationship_to_current_study": TO_CONFIRM, "limitations_or_cautions": [TO_CONFIRM]}]
    for index, theme in enumerate(themes, start=1):
        if not isinstance(theme, dict):
            continue
        lines.extend([f"## Theme {index}: {safe_text(theme.get('theme', '')) or TO_CONFIRM}", "", "### Key evidence to discuss", ""])
        lines.extend(markdown_bullets(theme.get("key_evidence_to_discuss", []), allowed_citations))
        lines.extend(["", "### Suggested citation anchors", ""])
        lines.extend(markdown_bullets(theme.get("suggested_citation_anchors", []), allowed_citations))
        lines.extend(["", "### Relationship to current study", "", sanitize_citation_markers(safe_text(theme.get("relationship_to_current_study", "")) or TO_CONFIRM, allowed_citations), ""])
        lines.extend(["### Limitations/cautions", ""])
        lines.extend(markdown_bullets(theme.get("limitations_or_cautions", []), allowed_citations))
        lines.append("")
    for heading, key in [
        ("Direct Evidence Section", "direct_evidence_section"),
        ("Indirect / Allied Health / Education Evidence Section", "indirect_evidence_section"),
        ("Methodological Literature Section", "methodological_literature_section"),
        ("Synthesis Toward Gap", "synthesis_toward_gap"),
        ("Claims to Avoid", "claims_to_avoid"),
        ("To Be Confirmed", "to_be_confirmed"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(markdown_bullets(rrl.get(key, []), allowed_citations))
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_outputs(project_dir: Path, result: dict[str, Any], rows: list[dict[str, str]], model: str, input_paths: list[Path], allowed_citations: set[str]) -> dict[str, Path]:
    p = paths(project_dir)
    p["outline_dir"].mkdir(parents=True, exist_ok=True)
    write_manuscript_outline(p["manuscript"], result, model, input_paths, allowed_citations)
    intro = dict_value(result, "introduction_outline")
    write_list_outline(
        p["introduction"],
        "Introduction Outline",
        [
            ("Opening Context", intro.get("opening_context", [])),
            ("Problem Background", intro.get("problem_background", [])),
            ("Evidence-Based Gap", intro.get("evidence_based_gap", [])),
            ("Local / Institutional / Philippine Context", intro.get("local_context", [])),
            ("Study Purpose", intro.get("study_purpose", [])),
            ("Research Questions or Objectives", intro.get("research_questions_or_objectives", [])),
            ("Significance of the Study", intro.get("significance", [])),
            ("Scope and Delimitations", intro.get("scope_and_delimitations", [])),
            ("Suggested Citation Anchors", intro.get("suggested_citation_anchors", [])),
            ("Claims to Avoid", intro.get("claims_to_avoid", [])),
            ("To Be Confirmed", intro.get("to_be_confirmed", [])),
        ],
        allowed_citations,
        model,
    )
    write_rrl_outline(p["rrl"], result, model, allowed_citations)
    method = dict_value(result, "methodology_outline")
    write_list_outline(
        p["methodology"],
        "Methodology Outline",
        [
            ("Research Design", method.get("research_design", "")),
            ("Study Setting", method.get("study_setting", "")),
            ("Population and Sampling", method.get("population_and_sampling", "")),
            ("Variables", method.get("variables", [])),
            ("Data Sources", method.get("data_sources", [])),
            ("Measures and Operational Definitions", method.get("measures_and_operational_definitions", [])),
            ("Statistical Analysis Plan", method.get("statistical_analysis_plan", [])),
            ("Ethical Considerations", method.get("ethical_considerations", "")),
            ("Limitations of Method", method.get("limitations_of_method", [])),
            ("To Be Confirmed", method.get("to_be_confirmed", [])),
        ],
        allowed_citations,
        model,
    )
    results = dict_value(result, "results_outline")
    write_list_outline(
        p["results"],
        "Results Outline",
        [
            ("Completion Status", results.get("completion_status", TO_CONFIRM)),
            ("Available Statistical Inputs", results.get("available_statistical_inputs", [])),
            ("Proposed Results Organization", results.get("proposed_results_organization", [])),
            ("Table and Figure Plan", results.get("table_and_figure_plan", [])),
            ("Results by Research Question", results.get("results_by_research_question", [])),
            ("Required Statistical Outputs", results.get("required_statistical_outputs", [])),
            ("Missing Results To Confirm", results.get("missing_results_to_confirm", [])),
            ("Claims Not Allowed Yet", results.get("claims_not_allowed_yet", [])),
        ],
        allowed_citations,
        model,
    )
    discussion = dict_value(result, "discussion_outline")
    write_list_outline(
        p["discussion"],
        "Discussion Outline",
        [
            ("Opening Summary of Expected Results", discussion.get("opening_summary_of_expected_results", [])),
            ("Interpretation Plan", discussion.get("interpretation_plan", [])),
            ("Relationship to Literature Synthesis", discussion.get("relationship_to_literature_synthesis", [])),
            ("Implications", discussion.get("implications", [])),
            ("Limitations", discussion.get("limitations", [])),
            ("Recommendations", discussion.get("recommendations", [])),
            ("Conclusion Direction", discussion.get("conclusion_direction", [])),
            ("Claims to Avoid", discussion.get("claims_to_avoid", [])),
            ("To Be Confirmed", discussion.get("to_be_confirmed", [])),
        ],
        allowed_citations,
        model,
    )
    pd.DataFrame(rows, columns=OUTLINE_MAP_COLUMNS).fillna("").to_csv(p["map"], index=False, encoding="utf-8")
    write_readiness_checklist(p["checklist"], result)
    return p


def write_readiness_checklist(path: Path, result: dict[str, Any]) -> None:
    readiness = dict_value(result, "readiness")
    lines = ["# Outline Readiness Checklist", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for heading, key in [
        ("Ready for Drafting", "ready_for_drafting"),
        ("Partially Ready", "partially_ready"),
        ("Blocked Until More Inputs Are Added", "blocked_until_more_inputs"),
        ("Human Review Needed", "human_review_needed"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend([f"- {safe_text(item) or TO_CONFIRM}" for item in readiness.get(key, [])] if isinstance(readiness.get(key), list) else [f"- {TO_CONFIRM}"])
        lines.append("")
    lines.extend(["## Recommended Next Step", "", safe_text(readiness.get("recommended_next_step", "")) or TO_CONFIRM, ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_log(
    log_path: Path,
    model: str,
    project_dir: Path,
    input_paths: list[Path],
    output_paths: list[Path],
    outline_rows_written: int,
    dry_run: bool,
    overwrite: bool,
    prefer_refined: bool,
    include_results_outline: bool,
    warnings: list[str],
) -> None:
    write_ai_run_log(
        log_path,
        task_name="stage08_outline",
        model=model,
        input_paths=input_paths,
        output_paths=output_paths,
        counts={
            "project_path": project_dir,
            "outline_map_rows_written": outline_rows_written,
            "dry_run": str(dry_run).lower(),
            "overwrite": str(overwrite).lower(),
            "prefer_refined": str(prefer_refined).lower(),
            "include_results_outline": str(include_results_outline).lower(),
        },
        errors=warnings,
        prompt_version=PROMPT_VERSION,
    )


def run_ai_outline(
    project_dir: Path,
    model: str,
    dry_run: bool,
    overwrite: bool,
    no_backup: bool,
    strict: bool,
    prefer_refined: bool,
    include_results_outline: bool,
    max_input_chars: int | None,
) -> dict[str, Any]:
    p = paths(project_dir)
    p["outline_dir"].mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    existing = existing_outputs(p)
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing Stage 08 outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup or not existing else backup_outputs(existing)

    refined_context = ""
    refined_paths: list[Path] = []
    refined_warnings: list[str] = []
    if prefer_refined:
        outline_context = read_text_file(p["outline_context"])
        if outline_context:
            refined_context += f"# Stage 07B outline context: _context_for_outline.md\n\n{outline_context}"
            refined_paths.append(p["outline_context"])
        refined_text, refined_file_paths, refined_warnings = read_named_context(p["brief_dir"], REFINED_CONTEXT_FILES, "Refined Stage 00", max_input_chars, warn_missing=False)
        if refined_text:
            refined_context = compact_text("\n\n".join(part for part in [refined_context, refined_text] if part), max_input_chars)
            refined_paths.extend(refined_file_paths)

    original_context, original_paths, original_warnings = read_named_context(p["brief_dir"], ORIGINAL_CONTEXT_FILES, "Original Stage 00", max_input_chars, warn_missing=False)
    if not refined_context and not original_context:
        message = "Stage 00 project context must be completed before Stage 08 outline generation."
        if strict:
            raise FileNotFoundError(message)
        result = empty_result("blocked", message, [], has_results=False)
        write_outputs(project_dir, result, [], model, [], set())
        write_log(p["log"], model, project_dir, [], output_files(p) + [p["log"]], 0, dry_run, overwrite, prefer_refined, include_results_outline, [message])
        return {"status": "blocked", "rows_written": 0, "paths": p, "warnings": [message], "backups": backups}

    synthesis_context, synthesis_paths, synthesis_warnings = read_named_context(p["stage06_dir"], STAGE06_FILES, "Stage 06", max_input_chars)
    gap_context, gap_paths, gap_warnings = read_named_context(p["stage07_dir"], STAGE07_FILES, "Stage 07", max_input_chars)
    warnings.extend(refined_warnings)
    warnings.extend(original_warnings)
    warnings.extend(synthesis_warnings)
    warnings.extend(gap_warnings)

    study_notes = read_text_file(p["study_notes"], max_input_chars)
    study_paths = [p["study_notes"]] if study_notes else []
    if not study_notes:
        warnings.append(f"Missing or empty study notes input: {p['study_notes']}")

    results_context, results_paths, results_warnings, has_results = read_results_context(project_dir, include_results_outline, max_input_chars)
    warnings.extend(results_warnings)
    evidence_context, evidence_path, evidence_citations = read_csv_context(p["evidence"])
    metadata_context, metadata_path, metadata_citations = read_metadata_context(project_dir)

    input_paths = [*refined_paths, *original_paths, *synthesis_paths, *gap_paths, *study_paths, *results_paths]
    if evidence_path:
        input_paths.append(evidence_path)
    if metadata_path:
        input_paths.append(metadata_path)

    context_for_original = compact_text("\n\n".join(part for part in [original_context, f"# Study notes\n\n{study_notes}" if study_notes else ""] if part), max_input_chars)
    allowed_citations = {
        key
        for key in [
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", refined_context),
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", original_context),
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", synthesis_context),
            *re.findall(r"\[@([A-Za-z0-9_.:-]+)\]", gap_context),
            *evidence_citations,
            *metadata_citations,
        ]
        if key and key != "ToBeConfirmed"
    }

    if dry_run:
        result = dry_run_result(warnings, has_results)
    else:
        load_dotenv(repo_root() / ".env")
        api_key = require_api_key(dry_run=False)
        result = call_openai_outline(
            api_key or "",
            model,
            refined_context,
            context_for_original,
            synthesis_context,
            gap_context,
            evidence_context,
            metadata_context,
            results_context,
            prefer_refined,
            include_results_outline,
        )
    result, rows, validation_warnings = normalize_result(result, has_results)
    warnings = list(dict.fromkeys([*warnings, *validation_warnings]))
    result["items_to_confirm"] = list(dict.fromkeys([*list_value(result, "items_to_confirm"), *warnings]))
    write_outputs(project_dir, result, rows, model, input_paths, allowed_citations)
    write_log(p["log"], model, project_dir, input_paths, output_files(p) + [p["log"]], len(rows), dry_run, overwrite, prefer_refined, include_results_outline, warnings)
    return {"status": result.get("completion_status", "completed"), "rows_written": len(rows), "paths": p, "warnings": warnings, "backups": backups}


def parse_bool_flag(value: str) -> bool:
    return value.strip().lower() not in {"0", "false", "no", "off"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to build Stage 08 manuscript and section outlines.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=default_model(), help="OpenAI model for outline generation")
    parser.add_argument("--dry-run", action="store_true", help="Write status outputs without calling OpenAI")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing existing Stage 08 outputs")
    parser.add_argument("--no-backup", action="store_true", help="Skip timestamped backups when overwriting")
    parser.add_argument("--strict", action="store_true", help="Fail if required context files are missing")
    parser.add_argument("--prefer-refined", type=parse_bool_flag, default=True, help="Prefer refined Stage 00 and Stage 07B context when present")
    parser.add_argument("--include-results-outline", type=parse_bool_flag, default=True, help="Include Results outline planning")
    parser.add_argument("--max-input-chars", type=int, help="Maximum context characters per input group")
    args = parser.parse_args()

    summary = run_ai_outline(
        project_dir=resolve_project(args.project),
        model=args.model,
        dry_run=args.dry_run,
        overwrite=args.overwrite,
        no_backup=args.no_backup,
        strict=args.strict,
        prefer_refined=args.prefer_refined,
        include_results_outline=args.include_results_outline,
        max_input_chars=args.max_input_chars,
    )
    print(f"status={summary['status']} outline_rows={summary['rows_written']}")
    print(f"manuscript_outline={summary['paths']['manuscript']}")
    print(f"introduction_outline={summary['paths']['introduction']}")
    print(f"rrl_outline={summary['paths']['rrl']}")
    print(f"methodology_outline={summary['paths']['methodology']}")
    print(f"results_outline={summary['paths']['results']}")
    print(f"discussion_outline={summary['paths']['discussion']}")


if __name__ == "__main__":
    main()
