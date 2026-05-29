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
from scripts.ai.prompts import build_results_interpretation_prompt
from scripts.ai.schemas import (
    CAUTION_LEVELS,
    FINDING_TYPES,
    RESULT_AVAILABLE_VALUES,
    RESULT_READINESS_VALUES,
    RESULT_WRITING_USES,
    RESULTS_BY_OBJECTIVE_COLUMNS,
    SIGNIFICANCE_STATUSES,
    STATISTICAL_FINDINGS_COLUMNS,
    results_interpretation_schema,
)


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-mini"
TO_CONFIRM = "To be confirmed."
PROMPT_VERSION = "results_interpretation_v1"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return os.getenv("AI_RESULTS_MODEL", "").strip() or os.getenv("AI_OUTLINE_MODEL", "").strip() or DEFAULT_MODEL


def paths(project_dir: Path) -> dict[str, Path]:
    out = project_dir / "09_drafts" / "results"
    return {
        "input": project_dir / "input",
        "out": out,
        "compiled": project_dir / "input" / "statistical_results_compiled.md",
        "stats": project_dir / "input" / "statistical_results.md",
        "manifest": project_dir / "input" / "statistical_results_manifest.csv",
        "availability": project_dir / "input" / "results_availability.md",
        "human_context": project_dir / "input" / "human_confirmed_context.md",
        "methodology": project_dir / "input" / "methodology_details.md",
        "rq_refined": project_dir / "00_brief" / "research_questions_refined.md",
        "rq": project_dir / "00_brief" / "research_questions.md",
        "variables": project_dir / "00_brief" / "variables.md",
        "results_outline": project_dir / "08_outline" / "results_outline.md",
        "discussion_outline": project_dir / "08_outline" / "discussion_outline.md",
        "readiness": project_dir / "08_outline" / "outline_readiness_checklist.md",
        "problem": project_dir / "07_gap_analysis" / "problem_statement_refined.md",
        "synthesis": project_dir / "06_synthesis" / "synthesis_notes.md",
        "contribution": project_dir / "07_gap_analysis" / "study_contribution.md",
        "notes": out / "results_interpretation_notes.md",
        "table_notes": out / "results_table_notes.md",
        "missing": out / "missing_results_to_confirm.md",
        "by_objective": out / "results_by_objective.csv",
        "findings": out / "statistical_findings_matrix.csv",
        "log": project_dir / "logs" / "ai_results_interpretation_log.md",
    }


def output_files(p: dict[str, Path]) -> list[Path]:
    return [p["notes"], p["table_notes"], p["missing"], p["by_objective"], p["findings"]]


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return " ".join(str(value).strip().split())


def read_text(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    return text[:max_chars] if max_chars else text


def read_csv_text(path: Path, max_chars: int | None = None) -> str:
    if not path.exists():
        return ""
    try:
        text = pd.read_csv(path, dtype=str).fillna("").to_csv(index=False)
    except Exception:
        text = read_text(path)
    return text[:max_chars] if max_chars else text


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = path.with_suffix(f".{stamp}.bak{path.suffix}")
    out.write_bytes(path.read_bytes())
    return out


def backup_existing(files: list[Path]) -> list[Path]:
    backups: list[Path] = []
    for path in files:
        backed = backup(path)
        if backed:
            backups.append(backed)
    return backups


def join_context(items: list[tuple[str, Path, str]]) -> str:
    return "\n\n".join(f"# {label}: {path.name}\n\n{text}" for label, path, text in items if text.strip())


def listify(value: Any) -> list[str]:
    if isinstance(value, list):
        return [safe_text(item) or TO_CONFIRM for item in value] or [TO_CONFIRM]
    text = safe_text(value)
    return [text] if text else [TO_CONFIRM]


def bullets(values: Any) -> list[str]:
    return [f"- {item}" for item in listify(values)]


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def has_statistical_results(results_context: str) -> bool:
    text = results_context.strip().lower()
    if not text:
        return False
    blocked_markers = ["no extracted content", "unavailable", "no statistical result files were found"]
    return not all(marker in text for marker in blocked_markers)


def empty_result(status: str, message: str, include_discussion_cues: bool = False) -> dict[str, Any]:
    return {
        "completion_status": status,
        "inputs_used": [],
        "study_objectives_or_research_questions": [TO_CONFIRM],
        "results_availability_summary": message,
        "findings_by_objective": [],
        "overall_results_pattern": TO_CONFIRM,
        "results_ready_to_write": [],
        "results_partial": [],
        "results_missing": [message],
        "statistical_claims_allowed": ["Only claims directly supported by supplied statistical outputs may be used."],
        "statistical_claims_not_allowed": ["Do not invent numerical results, p-values, coefficients, or significance claims."],
        "notes_for_results_writer": [message],
        "notes_for_discussion_writer": [message] if include_discussion_cues else [],
        "recommended_tables": [],
        "recommended_figures": [],
        "missing_results_to_confirm": {
            "required_before_results_drafting": [message],
            "required_before_discussion_drafting": [message],
            "missing_by_objective": [TO_CONFIRM],
            "missing_tables_or_figures": [TO_CONFIRM],
            "missing_statistical_details": [TO_CONFIRM],
            "human_or_statistician_followup_questions": ["Provide AI-readable statistical outputs in statresults/."],
        },
        "statistical_findings": [],
    }


def build_request_payload(
    model: str,
    project_context: str,
    methodology_context: str,
    research_questions_context: str,
    results_context: str,
    results_outline_context: str,
    discussion_outline_context: str,
    include_discussion_cues: bool,
) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_results_interpretation_prompt(
            project_context,
            methodology_context,
            research_questions_context,
            results_context,
            results_outline_context,
            discussion_outline_context,
            include_discussion_cues,
        ),
        input_data={
            "project_context": project_context,
            "methodology_context": methodology_context,
            "research_questions_context": research_questions_context,
            "results_context": results_context,
            "results_outline_context": results_outline_context,
            "discussion_outline_context": discussion_outline_context,
            "include_discussion_cues": include_discussion_cues,
        },
        schema=results_interpretation_schema(),
        schema_name="stage10a_results_interpretation",
    )


def call_openai_results(
    api_key: str,
    model: str,
    project_context: str,
    methodology_context: str,
    research_questions_context: str,
    results_context: str,
    results_outline_context: str,
    discussion_outline_context: str,
    include_discussion_cues: bool,
) -> dict[str, Any]:
    return AIClient(api_key=api_key, default_model=model).responses_json(
        instructions=build_results_interpretation_prompt(
            project_context,
            methodology_context,
            research_questions_context,
            results_context,
            results_outline_context,
            discussion_outline_context,
            include_discussion_cues,
        ),
        input_data={
            "project_context": project_context,
            "methodology_context": methodology_context,
            "research_questions_context": research_questions_context,
            "results_context": results_context,
            "results_outline_context": results_outline_context,
            "discussion_outline_context": discussion_outline_context,
            "include_discussion_cues": include_discussion_cues,
        },
        schema=results_interpretation_schema(),
        schema_name="stage10a_results_interpretation",
        timeout=180,
        retries=2,
    )


def source_supports_significance(row: dict[str, str], results_context: str) -> bool:
    p_or_ci = safe_text(row.get("p_value_or_ci") or row.get("p_value") or row.get("confidence_interval"))
    if p_or_ci and p_or_ci.lower() not in {"to be confirmed", "to be confirmed.", "not reported", "not_reported", "n/a"}:
        return True
    source = safe_text(row.get("source_file"))
    if source and source.lower() != "to be confirmed":
        pattern = re.escape(source)
        match = re.search(pattern + r".{0,1500}", results_context, flags=re.I | re.S)
        if match and re.search(r"\bsignificant|p\s*[<=>]", match.group(0), flags=re.I):
            return True
    return bool(re.search(r"\bsignificant|p\s*[<=>]", results_context, flags=re.I))


def normalize_result(result: dict[str, Any], results_context: str) -> tuple[dict[str, Any], list[dict[str, str]], list[dict[str, str]], list[str]]:
    warnings: list[str] = []
    if result.get("completion_status") not in {"completed", "partial", "blocked"}:
        warnings.append("Invalid completion_status; coerced to partial.")
        result["completion_status"] = "partial"
    objective_rows: list[dict[str, str]] = []
    for index, item in enumerate(result.get("findings_by_objective", []), start=1):
        obj = dict_value(item)
        row = {
            "objective_id": safe_text(obj.get("objective_id")) or f"OBJ-{index:03d}",
            "objective_text": safe_text(obj.get("objective_text")) or TO_CONFIRM,
            "result_available": "yes" if listify(obj.get("available_results")) != [TO_CONFIRM] else "to_be_confirmed",
            "source_file": "; ".join(listify(obj.get("available_results"))),
            "statistical_test_or_model": safe_text(obj.get("statistical_test_or_model")) or TO_CONFIRM,
            "key_numerical_result": "; ".join(listify(obj.get("key_numerical_findings"))),
            "p_value_or_ci": safe_text(obj.get("p_value_or_ci")) or TO_CONFIRM,
            "significance_status": safe_text(obj.get("significance_status")) or "to_be_confirmed",
            "direction_or_relationship": safe_text(obj.get("plain_language_result")) or TO_CONFIRM,
            "result_readiness": safe_text(obj.get("result_readiness")) or "to_be_confirmed",
            "missing_items": "; ".join(listify(obj.get("missing_items"))),
            "notes": safe_text(obj.get("notes")),
        }
        if row["result_available"] not in RESULT_AVAILABLE_VALUES:
            warnings.append(f"{row['objective_id']} invalid result_available; coerced to to_be_confirmed.")
            row["result_available"] = "to_be_confirmed"
        if row["significance_status"] not in SIGNIFICANCE_STATUSES:
            warnings.append(f"{row['objective_id']} invalid significance_status; coerced to to_be_confirmed.")
            row["significance_status"] = "to_be_confirmed"
        if row["significance_status"] == "significant" and not source_supports_significance(row, results_context):
            warnings.append(f"{row['objective_id']} marked significant without supplied p-value/CI/significance support; coerced to to_be_confirmed.")
            row["significance_status"] = "to_be_confirmed"
            row["notes"] = (row["notes"] + " " if row["notes"] else "") + "Significance support To be confirmed."
        if row["result_readiness"] not in RESULT_READINESS_VALUES:
            warnings.append(f"{row['objective_id']} invalid result_readiness; coerced to to_be_confirmed.")
            row["result_readiness"] = "to_be_confirmed"
        objective_rows.append({column: row.get(column, TO_CONFIRM) for column in RESULTS_BY_OBJECTIVE_COLUMNS})

    finding_rows: list[dict[str, str]] = []
    for index, item in enumerate(result.get("statistical_findings", []), start=1):
        finding = dict_value(item)
        row = {column: safe_text(finding.get(column, "")) for column in STATISTICAL_FINDINGS_COLUMNS if column != "finding_id"}
        row["finding_id"] = f"FIND-{index:04d}"
        row["source_file"] = row.get("source_file") or TO_CONFIRM
        if row.get("finding_type") not in FINDING_TYPES:
            warnings.append(f"{row['finding_id']} invalid finding_type; coerced to to_be_confirmed.")
            row["finding_type"] = "to_be_confirmed"
        if row.get("writing_use") not in RESULT_WRITING_USES:
            warnings.append(f"{row['finding_id']} invalid writing_use; coerced to to_be_confirmed.")
            row["writing_use"] = "to_be_confirmed"
        if row.get("caution_level") not in CAUTION_LEVELS:
            warnings.append(f"{row['finding_id']} invalid caution_level; coerced to to_be_confirmed.")
            row["caution_level"] = "to_be_confirmed"
        if re.search(r"\bsignificant\b", row.get("interpretation", ""), flags=re.I) and not source_supports_significance(row, results_context):
            warnings.append(f"{row['finding_id']} interpretation claimed significance without supplied support; caution set to to_be_confirmed.")
            row["caution_level"] = "to_be_confirmed"
            row["interpretation"] = "To be confirmed."
        for column in STATISTICAL_FINDINGS_COLUMNS:
            row[column] = row.get(column) or TO_CONFIRM
        finding_rows.append({column: row[column] for column in STATISTICAL_FINDINGS_COLUMNS})
    return result, objective_rows, finding_rows, warnings


def render_notes(result: dict[str, Any], model: str, input_paths: list[Path], include_discussion_cues: bool) -> str:
    lines = ["# Results Interpretation Notes", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    lines.extend(["## Completion Status", "", safe_text(result.get("completion_status")) or TO_CONFIRM, ""])
    lines.extend(["## Inputs Used", ""])
    lines.extend([f"- {path}" for path in input_paths] or ["- none"])
    for heading, key in [
        ("Study Objectives / Research Questions", "study_objectives_or_research_questions"),
        ("Results Availability Summary", "results_availability_summary"),
    ]:
        lines.extend(["", f"## {heading}", ""])
        value = result.get(key)
        if isinstance(value, list):
            lines.extend(bullets(value))
        else:
            lines.append(safe_text(value) or TO_CONFIRM)
    lines.extend(["", "## Findings by Objective", ""])
    for item in result.get("findings_by_objective", []):
        obj = dict_value(item)
        lines.extend([f"### {safe_text(obj.get('objective_id')) or 'Objective'}", ""])
        lines.extend([
            f"* Available result(s): {'; '.join(listify(obj.get('available_results')))}",
            f"* Statistical test/model: {safe_text(obj.get('statistical_test_or_model')) or TO_CONFIRM}",
            f"* Key numerical findings: {'; '.join(listify(obj.get('key_numerical_findings')))}",
            f"* Significance status: {safe_text(obj.get('significance_status')) or TO_CONFIRM}",
            f"* Plain-language result: {safe_text(obj.get('plain_language_result')) or TO_CONFIRM}",
            f"* Interpretation boundary: {safe_text(obj.get('interpretation_boundary')) or TO_CONFIRM}",
            f"* To be confirmed: {'; '.join(listify(obj.get('missing_items')))}",
            "",
        ])
    for heading, key in [
        ("Overall Results Pattern", "overall_results_pattern"),
        ("Results That Are Ready to Write", "results_ready_to_write"),
        ("Results That Are Partial", "results_partial"),
        ("Results That Are Missing", "results_missing"),
        ("Statistical Claims Allowed", "statistical_claims_allowed"),
        ("Statistical Claims Not Allowed", "statistical_claims_not_allowed"),
        ("Notes for Results Writer", "notes_for_results_writer"),
    ]:
        lines.extend([f"## {heading}", ""])
        value = result.get(key)
        lines.extend(bullets(value) if isinstance(value, list) else [safe_text(value) or TO_CONFIRM])
        lines.append("")
    if include_discussion_cues:
        lines.extend(["## Notes for Discussion Writer", ""])
        lines.extend(bullets(result.get("notes_for_discussion_writer", [])))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_table_notes(result: dict[str, Any], model: str) -> str:
    lines = ["# Results Table Notes", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", "", "## Recommended Tables", ""]
    for idx, table in enumerate(result.get("recommended_tables", []), start=1):
        item = dict_value(table)
        lines.extend([f"### Table {idx}. {safe_text(item.get('table_title')) or TO_CONFIRM}", ""])
        for label, key in [("Purpose", "purpose"), ("Source result files", "source_result_files"), ("Required columns", "required_columns"), ("Available", "available"), ("Missing", "missing"), ("Notes", "notes")]:
            value = item.get(key)
            lines.extend([f"{label}:"])
            lines.extend(bullets(value) if isinstance(value, list) else [safe_text(value) or TO_CONFIRM])
            lines.append("")
    lines.extend(["## Recommended Figures", ""])
    for idx, fig in enumerate(result.get("recommended_figures", []), start=1):
        item = dict_value(fig)
        lines.extend([f"### Figure {idx}. {safe_text(item.get('figure_title')) or TO_CONFIRM}", "", f"Purpose: {safe_text(item.get('purpose')) or TO_CONFIRM}", ""])
    lines.extend(["## Tables/Figures Not Yet Ready", ""])
    lines.extend(bullets(result.get("results_missing", [])))
    lines.extend(["", "## Formatting Notes", "", "- Do not create final tables unless all values are supplied.", "- Do not invent table values.", ""])
    return "\n".join(lines).rstrip() + "\n"


def render_missing(result: dict[str, Any], model: str) -> str:
    missing = dict_value(result.get("missing_results_to_confirm"))
    lines = ["# Missing Results To Confirm", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Model: {model}", ""]
    for heading, key in [
        ("Required Before Results Drafting", "required_before_results_drafting"),
        ("Required Before Discussion Drafting", "required_before_discussion_drafting"),
        ("Missing by Objective", "missing_by_objective"),
        ("Missing Tables/Figures", "missing_tables_or_figures"),
        ("Missing Statistical Details", "missing_statistical_details"),
        ("Human/Statistician Follow-up Questions", "human_or_statistician_followup_questions"),
    ]:
        lines.extend([f"## {heading}", ""])
        lines.extend(bullets(missing.get(key, [])))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(project_dir: Path, result: dict[str, Any], objective_rows: list[dict[str, str]], finding_rows: list[dict[str, str]], model: str, input_paths: list[Path], include_discussion_cues: bool) -> dict[str, Path]:
    p = paths(project_dir)
    p["out"].mkdir(parents=True, exist_ok=True)
    p["notes"].write_text(render_notes(result, model, input_paths, include_discussion_cues), encoding="utf-8")
    p["table_notes"].write_text(render_table_notes(result, model), encoding="utf-8")
    p["missing"].write_text(render_missing(result, model), encoding="utf-8")
    pd.DataFrame(objective_rows, columns=RESULTS_BY_OBJECTIVE_COLUMNS).to_csv(p["by_objective"], index=False, encoding="utf-8")
    pd.DataFrame(finding_rows, columns=STATISTICAL_FINDINGS_COLUMNS).to_csv(p["findings"], index=False, encoding="utf-8")
    return p


def collect_inputs(project_dir: Path, max_input_chars: int | None) -> tuple[str, str, str, str, str, str, list[Path], list[str]]:
    p = paths(project_dir)
    warnings: list[str] = []
    results_items = []
    for label, key in [("compiled statistical results", "compiled"), ("human statistical results", "stats"), ("results manifest", "manifest"), ("results availability", "availability")]:
        path = p[key]
        text = read_csv_text(path, max_input_chars) if path.suffix == ".csv" else read_text(path, max_input_chars)
        if text:
            results_items.append((label, path, text))
        else:
            warnings.append(f"Missing or empty {label}: {path}")
    project_items = []
    for label, key in [("human confirmed context", "human_context"), ("problem statement", "problem"), ("synthesis notes", "synthesis"), ("study contribution", "contribution")]:
        text = read_text(p[key], max_input_chars)
        if text:
            project_items.append((label, p[key], text))
    methodology = read_text(p["methodology"], max_input_chars)
    rq_items = []
    for label, key in [("refined research questions", "rq_refined"), ("research questions", "rq"), ("variables", "variables")]:
        text = read_text(p[key], max_input_chars)
        if text:
            rq_items.append((label, p[key], text))
    results_outline = "\n\n".join(read_text(p[key], max_input_chars) for key in ["results_outline", "readiness"] if read_text(p[key], max_input_chars))
    discussion_outline = read_text(p["discussion_outline"], max_input_chars)
    input_paths = [path for _, path, _ in [*results_items, *project_items, *rq_items]]
    for key in ["methodology", "results_outline", "readiness", "discussion_outline"]:
        if p[key].exists():
            input_paths.append(p[key])
    return join_context(project_items), methodology, join_context(rq_items), join_context(results_items), results_outline, discussion_outline, input_paths, warnings


def run_ai_interpret(
    project_dir: Path,
    model: str,
    dry_run: bool,
    overwrite: bool,
    no_backup: bool,
    strict: bool,
    max_input_chars: int | None,
    objectives: str | None,
    include_discussion_cues: bool,
) -> dict[str, Any]:
    p = paths(project_dir)
    p["out"].mkdir(parents=True, exist_ok=True)
    existing = [path for path in output_files(p) if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing Stage 10A outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup else backup_existing(existing)
    project_context, methodology_context, rq_context, results_context, results_outline, discussion_outline, input_paths, warnings = collect_inputs(project_dir, max_input_chars)
    if objectives:
        rq_context += f"\n\n# Objective filter requested\n\n{objectives}"
    has_results = has_statistical_results(results_context)
    if not has_results:
        message = "No statistical results are available for interpretation."
        if strict:
            raise FileNotFoundError(message)
        result = empty_result("blocked", message, include_discussion_cues)
        result, objective_rows, finding_rows, validation = normalize_result(result, results_context)
        warnings = [*warnings, message, *validation]
        write_outputs(project_dir, result, objective_rows, finding_rows, model, input_paths, include_discussion_cues)
        write_log(p, model, project_dir, input_paths, warnings, dry_run, overwrite, strict, include_discussion_cues, 0, 0)
        return {"status": "blocked", "objectives": 0, "findings": 0, "warnings": warnings, "backups": backups, "paths": p}
    if dry_run:
        result = empty_result("partial", "Dry run only. No OpenAI request was made.", include_discussion_cues)
        result["results_availability_summary"] = "Statistical inputs were detected, but interpretation was not run because --dry-run was used."
    else:
        load_dotenv(repo_root() / ".env")
        api_key = require_api_key(dry_run=False)
        result = call_openai_results(api_key or "", model, project_context, methodology_context, rq_context, results_context, results_outline, discussion_outline, include_discussion_cues)
    result, objective_rows, finding_rows, validation = normalize_result(result, results_context)
    warnings = list(dict.fromkeys([*warnings, *validation]))
    write_outputs(project_dir, result, objective_rows, finding_rows, model, input_paths, include_discussion_cues)
    write_log(p, model, project_dir, input_paths, warnings, dry_run, overwrite, strict, include_discussion_cues, len(objective_rows), len(finding_rows))
    return {"status": result.get("completion_status", "partial"), "objectives": len(objective_rows), "findings": len(finding_rows), "warnings": warnings, "backups": backups, "paths": p}


def write_log(
    p: dict[str, Path],
    model: str,
    project_dir: Path,
    input_paths: list[Path],
    warnings: list[str],
    dry_run: bool,
    overwrite: bool,
    strict: bool,
    include_discussion_cues: bool,
    objectives_count: int,
    findings_count: int,
) -> None:
    write_ai_run_log(
        p["log"],
        task_name="stage10a_results_interpretation",
        model=model,
        input_paths=input_paths,
        output_paths=[*output_files(p), p["log"]],
        counts={
            "project_path": project_dir,
            "dry_run": str(dry_run).lower(),
            "overwrite": str(overwrite).lower(),
            "strict": str(strict).lower(),
            "include_discussion_cues": str(include_discussion_cues).lower(),
            "objectives_mapped": objectives_count,
            "findings_extracted_mapped": findings_count,
        },
        errors=warnings,
        prompt_version=PROMPT_VERSION,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Interpret supplied statistical results into structured Stage 10A notes.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT))
    parser.add_argument("--model", default=default_model())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--max-input-chars", type=int)
    parser.add_argument("--objectives")
    parser.add_argument("--include-discussion-cues", action="store_true")
    args = parser.parse_args()
    result = run_ai_interpret(resolve_project(args.project), args.model, args.dry_run, args.overwrite, args.no_backup, args.strict, args.max_input_chars, args.objectives, args.include_discussion_cues)
    print(f"status={result['status']} objectives={result['objectives']} findings={result['findings']}")
    print(f"notes={result['paths']['notes']}")


if __name__ == "__main__":
    main()
