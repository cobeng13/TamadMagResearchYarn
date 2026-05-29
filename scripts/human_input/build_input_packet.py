from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ai.client import AIClient, load_dotenv, require_api_key
from scripts.ai.logging import write_ai_run_log


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MODEL = "gpt-5-nano"
TO_CONFIRM = "To be confirmed."

QUESTION_COLUMNS = [
    "question_id",
    "priority",
    "category",
    "question",
    "why_needed",
    "used_by_stage",
    "target_file",
    "answer_type",
    "required_before",
    "detected_from",
    "default_value",
    "status",
    "notes",
]

STATUS_COLUMNS = ["question_id", "status", "answered_at", "answer_source", "applied_to", "applied_at", "notes"]
PRIORITIES = {"required_before_drafting", "required_before_results", "required_before_final", "optional"}
ANSWER_TYPES = {"short_text", "long_text", "yes_no", "choice", "list", "table", "file_path", "numeric", "date", "to_be_confirmed"}
STATUSES = {"unanswered", "answered", "to_be_confirmed", "not_applicable"}


@dataclass
class Question:
    category: str
    question: str
    why_needed: str
    used_by_stage: str
    target_file: str
    answer_type: str
    required_before: str
    detected_from: str = ""
    default_value: str = ""
    priority: str = "required_before_drafting"
    status: str = "unanswered"
    notes: str = ""
    question_id: str = ""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return os.getenv("AI_HUMAN_INPUT_MODEL", "").strip() or os.getenv("AI_OUTLINE_MODEL", "").strip() or DEFAULT_MODEL


def paths(project_dir: Path) -> dict[str, Path]:
    human = project_dir / "human_input"
    return {
        "outline_dir": project_dir / "08_outline",
        "brief_dir": project_dir / "00_brief",
        "stage07_dir": project_dir / "07_gap_analysis",
        "input_dir": project_dir / "input",
        "human_dir": human,
        "packet": human / "human_input_packet.md",
        "questions": human / "human_input_questions.csv",
        "answers": human / "human_input_answers.md",
        "status": human / "human_input_status.csv",
        "log": project_dir / "logs" / "human_input_packet_log.md",
    }


def output_files(p: dict[str, Path], fmt: str) -> list[Path]:
    outs = [p["answers"], p["status"]]
    if fmt in {"md", "both"}:
        outs.append(p["packet"])
    if fmt in {"csv", "both"}:
        outs.append(p["questions"])
    return outs


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace").strip() if path.exists() else ""


def read_inputs(project_dir: Path) -> tuple[dict[Path, str], list[str]]:
    p = paths(project_dir)
    files = [
        *[p["outline_dir"] / name for name in [
            "manuscript_outline.md",
            "introduction_outline.md",
            "rrl_outline.md",
            "methodology_outline.md",
            "results_outline.md",
            "discussion_outline.md",
            "outline_readiness_checklist.md",
        ]],
        *[p["brief_dir"] / name for name in [
            "research_brief_refined.md",
            "research_questions_refined.md",
            "writing_scope_refined.md",
            "agent_instructions_refined.md",
            "research_brief.md",
            "research_questions.md",
            "variables.md",
            "inclusion_exclusion_criteria.md",
        ]],
        p["input_dir"] / "study_notes.md",
        p["input_dir"] / "statistical_results.md",
        p["stage07_dir"] / "research_gap_analysis.md",
        p["stage07_dir"] / "problem_statement_refined.md",
        p["stage07_dir"] / "study_contribution.md",
    ]
    data: dict[Path, str] = {}
    warnings: list[str] = []
    for path in files:
        text = read_text(path)
        if text:
            data[path] = text
    outline_present = any(path.name.endswith("_outline.md") or path.name == "manuscript_outline.md" for path in data)
    if not outline_present:
        warnings.append("Stage 08 outline files are missing or empty; packet is partial.")
    return data, warnings


def backup_outputs(outputs: list[Path]) -> list[Path]:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backups: list[Path] = []
    for path in outputs:
        if path.exists():
            backup = path.with_suffix(f".{stamp}.bak{path.suffix}")
            backup.write_bytes(path.read_bytes())
            backups.append(backup)
    return backups


def baseline_questions() -> list[Question]:
    return [
        Question("Study Identity and Framing", "What final or working title should later agents use?", "Prevents later agents from inventing title wording.", "Stage 09 writing", "input/human_confirmed_context.md", "short_text", "before_drafting"),
        Question("Study Identity and Framing", "What preferred study framing should be used in manuscript drafts?", "Confirms the human-approved positioning.", "Stage 09 writing", "input/human_confirmed_context.md", "long_text", "before_drafting"),
        Question("Methodology Details", "What is the confirmed study design?", "Methodology prose requires a human-confirmed design.", "Methodology/Introduction", "input/methodology_details.md", "short_text", "before_drafting"),
        Question("Methodology Details", "What institution, local context, or anonymized setting wording may be used?", "Local context is human-dependent and may require anonymization.", "Introduction/Methodology", "input/methodology_details.md", "long_text", "before_drafting"),
        Question("Methodology Details", "What is the study timeframe or academic years covered?", "Timeframe should not be inferred.", "Methodology", "input/methodology_details.md", "short_text", "before_drafting"),
        Question("Methodology Details", "What population and sample are included, including sample size if known?", "Prevents invented sample details.", "Methodology/Results", "input/methodology_details.md", "long_text", "before_drafting"),
        Question("Methodology Details", "What inclusion and exclusion criteria were actually used?", "Confirms study boundaries.", "Methodology", "input/methodology_details.md", "long_text", "before_drafting"),
        Question("Methodology Details", "What variables and operational definitions are actually available?", "Prevents invented variables or measures.", "Methodology/Results", "input/methodology_details.md", "table", "before_drafting"),
        Question("Data and Results Details", "What statistical outputs are available for drafting Results?", "Results cannot be drafted without human-supplied outputs.", "Results/Discussion", "input/statistical_results.md", "long_text", "before_results", priority="required_before_results"),
        Question("Data and Results Details", "Are Results ready to draft now? If not, what is missing?", "Controls whether Stage 09+ can draft Results/Discussion.", "Results/Discussion", "input/results_availability.md", "choice", "before_results", priority="required_before_results"),
        Question("Ethical and Administrative Details", "What ethical approval, exemption, consent, or privacy handling should be stated?", "Ethics status is human-only information.", "Methodology", "input/methodology_details.md", "long_text", "before_drafting"),
        Question("Scope and Claims", "What known limitations should the manuscript acknowledge?", "Limitations should be human-reviewed.", "Discussion", "input/human_confirmed_context.md", "long_text", "before_final", priority="required_before_final"),
        Question("Scope and Claims", "What claims should writers avoid?", "Prevents overclaiming.", "All writing stages", "input/human_confirmed_context.md", "list", "before_drafting"),
        Question("Style Preferences", "Are there preferred terms, target journal rules, or disclosure preferences?", "Captures optional style and disclosure choices.", "All writing stages", "input/human_confirmed_context.md", "long_text", "before_final", priority="optional"),
        Question("Ethical and Administrative Details", "Should the local context or institution be anonymized?", "Avoids unwanted disclosure.", "Introduction/Methodology", "input/human_confirmed_context.md", "yes_no", "before_drafting"),
    ]


def infer_default(question: Question, inputs: dict[Path, str]) -> str:
    joined = "\n".join(inputs.values())
    if "design" in question.question.lower():
        match = re.search(r"(predictive correlational|correlational|retrospective|cross-sectional|descriptive)[^.:\n]*", joined, re.I)
        return match.group(0).strip() if match else ""
    if "variables" in question.question.lower():
        match = re.search(r"(variables?|predictors?|outcome)[^\n]{0,250}", joined, re.I)
        return match.group(0).strip() if match else ""
    if "title" in question.question.lower():
        match = re.search(r"working title[^:\n]*:\s*(.+)", joined, re.I)
        return match.group(1).strip() if match else ""
    return ""


def detected_questions(inputs: dict[Path, str], include_optional: bool) -> list[Question]:
    questions: list[Question] = []
    patterns = [
        ("Methodology Details", r"sample size|population|sampling", "Please confirm the exact population, sampling method, and sample size.", "Methodology/Results", "input/methodology_details.md"),
        ("Ethical and Administrative Details", r"ethical approval|ethics|consent|privacy", "Please provide the exact ethics/privacy wording to use.", "Methodology", "input/methodology_details.md"),
        ("Data and Results Details", r"statistical_results\.md is empty|results|table|figure|required statistical outputs", "Please provide available statistical results, tables, figures, or file paths.", "Results/Discussion", "input/statistical_results.md"),
        ("Methodology Details", r"data source|records used|timeframe|institution", "Please confirm the study setting, timeframe, and data sources.", "Methodology", "input/methodology_details.md"),
        ("Scope and Claims", r"claim not allowed|claims to avoid|limitation", "Please confirm claim boundaries and known limitations.", "All writing stages", "input/human_confirmed_context.md"),
    ]
    for path, text in inputs.items():
        lower = text.lower()
        for category, pattern, question, used_by, target in patterns:
            if re.search(pattern, lower):
                questions.append(
                    Question(
                        category=category,
                        question=question,
                        why_needed="Detected from outline/context markers that require human confirmation.",
                        used_by_stage=used_by,
                        target_file=target,
                        answer_type="long_text",
                        required_before="before_drafting",
                        detected_from=str(path),
                        priority="required_before_results" if "Results" in category else "required_before_drafting",
                    )
                )
    if include_optional:
        questions.append(Question("Style Preferences", "Do you have preferred heading style, target journal, or formatting constraints?", "Optional style direction for later stages.", "All writing stages", "input/human_confirmed_context.md", "long_text", "before_final", priority="optional"))
    return questions


def dedupe_and_number(questions: list[Question], inputs: dict[Path, str]) -> list[Question]:
    seen: set[tuple[str, str]] = set()
    final: list[Question] = []
    for q in questions:
        key = (q.category, q.question)
        if key in seen:
            continue
        seen.add(key)
        q.priority = q.priority if q.priority in PRIORITIES else "required_before_drafting"
        q.answer_type = q.answer_type if q.answer_type in ANSWER_TYPES else "to_be_confirmed"
        q.status = q.status if q.status in STATUSES else "unanswered"
        q.default_value = q.default_value or infer_default(q, inputs)
        final.append(q)
    for index, q in enumerate(final, start=1):
        q.question_id = f"HI-{index:04d}"
    return final


def questions_to_rows(questions: list[Question]) -> list[dict[str, str]]:
    return [{column: str(getattr(q, column, "")) for column in QUESTION_COLUMNS} for q in questions]


def improve_with_ai(questions: list[Question], model: str, dry_run: bool) -> list[Question]:
    if dry_run:
        return questions
    load_dotenv(repo_root() / ".env")
    api_key = require_api_key(dry_run=False)
    payload = "\n".join(f"{q.question_id}: {q.category}: {q.question}" for q in questions)
    prompt = (
        "Improve wording/grouping of these human-input questions without adding answers or new facts. "
        "Return plain lines in the same QID order as 'QID|category|question'."
    )
    text = AIClient(api_key=api_key, default_model=model).responses_text(instructions=prompt, input_text=payload, timeout=90)
    by_id = {q.question_id: q for q in questions}
    for line in text.splitlines():
        parts = [part.strip() for part in line.split("|", 2)]
        if len(parts) == 3 and parts[0] in by_id and parts[2]:
            by_id[parts[0]].category = parts[1] or by_id[parts[0]].category
            by_id[parts[0]].question = parts[2]
    return questions


def write_packet(path: Path, questions: list[Question], warnings: list[str]) -> None:
    lines = [
        "# Human Input Packet",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## How to Use This Packet",
        "",
        'Fill in the answer fields below. Leave unknown items as "To be confirmed."',
        "",
    ]
    if warnings:
        lines.extend(["## Status Notes", ""])
        lines.extend(f"- {warning}" for warning in warnings)
        lines.append("")
    groups = [
        ("Priority 1: Required Before Drafting", "required_before_drafting"),
        ("Priority 2: Required Before Results", "required_before_results"),
        ("Priority 2: Required Before Final Manuscript", "required_before_final"),
        ("Priority 3: Optional / Style Preferences", "optional"),
    ]
    for heading, priority in groups:
        subset = [q for q in questions if q.priority == priority]
        if not subset:
            continue
        lines.extend([f"## {heading}", ""])
        for q in subset:
            lines.extend([
                f"### {q.category}",
                "",
                f"QID: {q.question_id}",
                "Question:",
                q.question,
                "Answer:",
                "",
                "Why this is needed:",
                q.why_needed,
                "Used by:",
                q.used_by_stage,
                "",
            ])
    lines.extend(["## Summary of Blocked Sections", ""])
    blocked = [q for q in questions if q.priority in {"required_before_drafting", "required_before_results"}]
    lines.extend(f"- {q.question_id}: {q.used_by_stage}" for q in blocked)
    lines.extend(["", "## Next Step After Completing This Packet", "", "Run `python -m scripts.human_input.apply_input_packet --project projects/sample_project`.", ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_answers(path: Path, questions: list[Question]) -> None:
    lines = [
        "# Human Input Answers",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "Instructions:",
        'Please answer under each question. Keep "To be confirmed" if unknown.',
        "",
    ]
    for q in questions:
        lines.extend([f"## {q.question_id}", "", "Question:", q.question, "Answer:", "", ""])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=columns).fillna("").to_csv(path, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)


def write_log(path: Path, project_dir: Path, input_paths: list[Path], output_paths: list[Path], questions: list[Question], warnings: list[str], use_ai: bool, dry_run: bool, model: str) -> None:
    write_ai_run_log(
        path,
        task_name="stage08b_human_input_packet",
        model=model,
        input_paths=input_paths,
        output_paths=output_paths,
        counts={
            "project_path": project_dir,
            "questions_generated": len(questions),
            "required_questions": sum(q.priority != "optional" for q in questions),
            "use_ai": str(use_ai).lower(),
            "dry_run": str(dry_run).lower(),
        },
        errors=warnings,
        prompt_version="human_input_packet_v1",
    )


def run_build_packet(project_dir: Path, overwrite: bool, no_backup: bool, strict: bool, include_optional: bool, fmt: str, use_ai: bool, model: str, dry_run: bool) -> dict[str, Any]:
    p = paths(project_dir)
    p["human_dir"].mkdir(parents=True, exist_ok=True)
    outputs = output_files(p, fmt)
    existing = [path for path in outputs if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing human input outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup or not existing else backup_outputs(existing)
    inputs, warnings = read_inputs(project_dir)
    if warnings and strict:
        raise FileNotFoundError(warnings[0])
    questions = dedupe_and_number([*baseline_questions(), *detected_questions(inputs, include_optional)], inputs)
    if use_ai:
        questions = improve_with_ai(questions, model, dry_run)
    rows = questions_to_rows(questions)
    status_rows = [{column: "" for column in STATUS_COLUMNS} | {"question_id": q.question_id, "status": "unanswered"} for q in questions]
    if fmt in {"md", "both"}:
        write_packet(p["packet"], questions, warnings)
    if fmt in {"csv", "both"}:
        write_csv(p["questions"], rows, QUESTION_COLUMNS)
    write_answers(p["answers"], questions)
    write_csv(p["status"], status_rows, STATUS_COLUMNS)
    written = [path for path in outputs if path.exists()]
    write_log(p["log"], project_dir, list(inputs.keys()), [*written, p["log"]], questions, warnings, use_ai, dry_run, model)
    return {"questions": len(questions), "paths": p, "warnings": warnings, "backups": backups}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Stage 08B human input packet from outline and project context.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--include-optional", action="store_true")
    parser.add_argument("--format", choices=["md", "csv", "both"], default="both")
    parser.add_argument("--use-ai", action="store_true")
    parser.add_argument("--model", default=default_model())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = run_build_packet(resolve_project(args.project), args.overwrite, args.no_backup, args.strict, args.include_optional, args.format, args.use_ai, args.model, args.dry_run)
    print(f"questions={result['questions']}")
    print(f"packet={result['paths']['packet']}")
    print(f"answers={result['paths']['answers']}")


if __name__ == "__main__":
    main()
