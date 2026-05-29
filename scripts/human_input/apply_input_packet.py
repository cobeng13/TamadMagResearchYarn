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

from scripts.ai.logging import write_ai_run_log
from scripts.human_input.build_input_packet import QUESTION_COLUMNS, STATUS_COLUMNS, DEFAULT_PROJECT, TO_CONFIRM, resolve_project


def paths(project_dir: Path) -> dict[str, Path]:
    human = project_dir / "human_input"
    return {
        "input_dir": project_dir / "input",
        "human_dir": human,
        "answers": human / "human_input_answers.md",
        "questions": human / "human_input_questions.csv",
        "status": human / "human_input_status.csv",
        "confirmed": project_dir / "input" / "human_confirmed_context.md",
        "methodology": project_dir / "input" / "methodology_details.md",
        "stats": project_dir / "input" / "statistical_results.md",
        "results_availability": project_dir / "input" / "results_availability.md",
        "report": human / "human_input_apply_report.md",
        "log": project_dir / "logs" / "human_input_apply_log.md",
    }


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = path.with_suffix(f".{stamp}.bak{path.suffix}")
    out.write_bytes(path.read_bytes())
    return out


def parse_answers(path: Path) -> dict[str, str]:
    text = read_text(path)
    answers: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(HI-\d{4})\s*$", text, flags=re.M))
    for index, match in enumerate(matches):
        qid = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end]
        answer_match = re.search(r"Answer:\s*(.*)", block, flags=re.S)
        answer = answer_match.group(1).strip() if answer_match else ""
        answer = re.split(r"\nQuestion:\s*", answer, maxsplit=1)[0].strip()
        answers[qid] = answer
    return answers


def answer_status(answer: str) -> str:
    stripped = answer.strip()
    if not stripped:
        return "unanswered"
    if stripped.lower() in {"to be confirmed", "to be confirmed."}:
        return "to_be_confirmed"
    if stripped.lower() in {"n/a", "na", "not applicable"}:
        return "not_applicable"
    return "answered"


def load_questions(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing questions CSV: {path}")
    df = pd.read_csv(path, dtype=str).fillna("")
    missing = [column for column in QUESTION_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Questions CSV missing columns: {', '.join(missing)}")
    return df


def grouped_answers(df: pd.DataFrame, answers: dict[str, str]) -> dict[str, list[tuple[pd.Series, str, str]]]:
    groups: dict[str, list[tuple[pd.Series, str, str]]] = {}
    for _, row in df.iterrows():
        qid = str(row["question_id"])
        answer = answers.get(qid, "")
        status = answer_status(answer)
        groups.setdefault(str(row["target_file"]), []).append((row, answer, status))
    return groups


def section_for_category(category: str) -> str:
    lower = category.lower()
    if "method" in lower:
        return "Methodology Details"
    if "data" in lower or "results" in lower:
        return "Data and Results Details"
    if "ethical" in lower:
        return "Ethical and Administrative Details"
    if "claim" in lower or "scope" in lower:
        return "Scope Boundaries"
    if "style" in lower:
        return "Terminology Preferences"
    return "Study Identity and Framing"


def render_context(title: str, grouped: list[tuple[pd.Series, str, str]], categories: list[str]) -> str:
    lines = ["", f"# {title}", "", f"Generated/applied: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    for category in categories:
        lines.extend([f"## {category}", ""])
        items = [(row, ans, status) for row, ans, status in grouped if section_for_category(str(row["category"])) == category and status == "answered"]
        if not items:
            lines.append(TO_CONFIRM)
        else:
            for row, ans, _ in items:
                lines.extend([f"### {row['question_id']}", "", f"Question: {row['question']}", "", ans.strip(), ""])
        lines.append("")
    tbc = [(row, ans, status) for row, ans, status in grouped if status in {"unanswered", "to_be_confirmed"}]
    lines.extend(["## To Be Confirmed", ""])
    lines.extend([f"- {row['question_id']}: {row['question']}" for row, _, _ in tbc] or ["- none"])
    return "\n".join(lines).rstrip() + "\n"


def write_or_append(path: Path, content: str, overwrite: bool, no_backup: bool, append_if_exists: bool = False) -> Path | None:
    path.parent.mkdir(parents=True, exist_ok=True)
    backup_path = None if no_backup or not path.exists() else backup(path)
    if append_if_exists and path.exists() and path.read_text(encoding="utf-8", errors="replace").strip() and not overwrite:
        path.write_text(path.read_text(encoding="utf-8", errors="replace").rstrip() + "\n\n" + content.lstrip(), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")
    return backup_path


def results_status(rows: list[tuple[pd.Series, str, str]]) -> str:
    answered = [ans for _, ans, status in rows if status == "answered"]
    if answered:
        text = "\n".join(answered).lower()
        if "ready" in text:
            return "ready"
        return "partial"
    if any(status == "to_be_confirmed" for _, _, status in rows):
        return "to_be_confirmed"
    return "unavailable"


def render_results_availability(rows: list[tuple[pd.Series, str, str]]) -> str:
    status = results_status(rows)
    answered = [(row, ans) for row, ans, st in rows if st == "answered"]
    missing = [(row, st) for row, _, st in rows if st in {"unanswered", "to_be_confirmed"}]
    lines = ["# Results Availability", "", f"Generated/applied: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "", "## Status", "", status, "", "## Available Statistical Inputs", ""]
    lines.extend([f"- {row['question_id']}: {ans}" for row, ans in answered] or ["- none"])
    lines.extend(["", "## Missing Statistical Inputs", ""])
    lines.extend([f"- {row['question_id']}: {row['question']} ({st})" for row, st in missing] or ["- none"])
    lines.extend(["", "## Sections Blocked Until Results Are Added", "", "- Results", "- Discussion", "", "## Notes", "", TO_CONFIRM, ""])
    return "\n".join(lines).rstrip() + "\n"


def render_statistical_results(rows: list[tuple[pd.Series, str, str]]) -> str:
    answered = [(row, ans) for row, ans, st in rows if st == "answered"]
    lines = ["# Statistical Results Supplied by Human", "", f"Generated/applied: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "", "## Available Results", ""]
    lines.extend([f"### {row['question_id']}\n\n{ans}" for row, ans in answered] or [TO_CONFIRM])
    lines.extend(["", "## Tables/Figures", "", TO_CONFIRM, "", "## Tests Run", "", TO_CONFIRM, "", "## Results by Research Question", "", TO_CONFIRM, "", "## Missing Results", "", TO_CONFIRM, "", "## To Be Confirmed", "", TO_CONFIRM, ""])
    return "\n".join(lines).rstrip() + "\n"


def write_report(path: Path, parsed: dict[str, str], applied: list[Path], missing_required: list[str], warnings: list[str], dry_run: bool) -> None:
    lines = ["# Human Input Apply Report", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "", "## Summary", "", f"- Dry run: {str(dry_run).lower()}", f"- Answers parsed: {len(parsed)}", f"- Files updated: {len(applied)}", "", "## Answers Parsed", ""]
    lines.extend(f"- {qid}: {answer_status(ans)}" for qid, ans in sorted(parsed.items()))
    lines.extend(["", "## Answers Applied", ""])
    lines.extend(f"- {path}" for path in applied) or lines.append("- none")
    lines.extend(["", "## Answers Still Missing", ""])
    lines.extend(f"- {item}" for item in missing_required) or lines.append("- none")
    lines.extend(["", "## Files Updated", ""])
    lines.extend(f"- {path}" for path in applied) or lines.append("- none")
    lines.extend(["", "## Files Not Updated", ""])
    if dry_run:
        lines.append("- Project input files were not updated because --dry-run was used.")
    else:
        lines.append("- none")
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in warnings) or lines.append("- none")
    lines.extend(["", "## Recommended Next Step", "", "Review applied input files before Stage 09 writing.", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def run_apply(project_dir: Path, answers_path: Path, questions_path: Path, overwrite: bool, no_backup: bool, strict: bool, dry_run: bool) -> dict[str, Any]:
    p = paths(project_dir)
    p["input_dir"].mkdir(parents=True, exist_ok=True)
    p["human_dir"].mkdir(parents=True, exist_ok=True)
    df = load_questions(answers_path if False else questions_path)
    answers = parse_answers(answers_path)
    known = set(df["question_id"].tolist())
    unknown = sorted(set(answers) - known)
    warnings = [f"Unknown QID ignored: {qid}" for qid in unknown]
    if unknown and strict:
        raise ValueError(warnings[0])
    missing_required = [
        str(row["question_id"])
        for _, row in df.iterrows()
        if row["priority"] == "required_before_drafting" and answer_status(answers.get(str(row["question_id"]), "")) == "unanswered"
    ]
    if missing_required and strict:
        raise ValueError(f"Required drafting answers missing: {', '.join(missing_required)}")
    groups = grouped_answers(df, answers)
    applied: list[Path] = []
    backups: list[Path] = []
    if not dry_run:
        confirmed_rows = groups.get("input/human_confirmed_context.md", [])
        methodology_rows = groups.get("input/methodology_details.md", [])
        results_rows = groups.get("input/statistical_results.md", [])
        availability_rows = [*groups.get("input/results_availability.md", []), *results_rows]
        if confirmed_rows:
            b = write_or_append(p["confirmed"], render_context("Human-Confirmed Context", confirmed_rows, ["Study Identity and Framing", "Local/Institutional Context", "Scope Boundaries", "Claims to Avoid", "Terminology Preferences"]), overwrite, no_backup)
            applied.append(p["confirmed"]); backups.extend([b] if b else [])
        if methodology_rows:
            b = write_or_append(p["methodology"], render_context("Methodology Details Supplied by Human", methodology_rows, ["Methodology Details", "Ethical and Administrative Details"]), overwrite, no_backup)
            applied.append(p["methodology"]); backups.extend([b] if b else [])
        if results_rows and any(st == "answered" for _, _, st in results_rows):
            b = write_or_append(p["stats"], render_statistical_results(results_rows), overwrite, no_backup, append_if_exists=True)
            applied.append(p["stats"]); backups.extend([b] if b else [])
        b = write_or_append(p["results_availability"], render_results_availability(availability_rows), overwrite, no_backup)
        applied.append(p["results_availability"]); backups.extend([b] if b else [])
    status_rows = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for _, row in df.iterrows():
        qid = str(row["question_id"])
        st = answer_status(answers.get(qid, ""))
        status_rows.append({
            "question_id": qid,
            "status": st,
            "answered_at": now if st == "answered" else "",
            "answer_source": str(answers_path) if st != "unanswered" else "",
            "applied_to": "; ".join(str(path) for path in applied) if st == "answered" and not dry_run else "",
            "applied_at": now if st == "answered" and not dry_run else "",
            "notes": "",
        })
    pd.DataFrame(status_rows, columns=STATUS_COLUMNS).to_csv(p["status"], index=False, encoding="utf-8")
    write_report(p["report"], answers, applied, missing_required, warnings, dry_run)
    write_ai_run_log(
        p["log"],
        task_name="stage08b_human_input_apply",
        model="deterministic",
        input_paths=[answers_path, questions_path],
        output_paths=[p["status"], p["report"], p["log"], *applied],
        counts={"project_path": project_dir, "answers_parsed": len(answers), "files_updated": len(applied), "dry_run": str(dry_run).lower()},
        errors=warnings,
        prompt_version="human_input_apply_v1",
    )
    return {"answers": len(answers), "applied": applied, "warnings": warnings, "backups": [b for b in backups if b], "paths": p}


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply completed Stage 08B human input answers into project input files.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT))
    parser.add_argument("--answers")
    parser.add_argument("--questions")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    project = resolve_project(args.project)
    p = paths(project)
    result = run_apply(project, Path(args.answers) if args.answers else p["answers"], Path(args.questions) if args.questions else p["questions"], args.overwrite, args.no_backup, args.strict, args.dry_run)
    print(f"answers={result['answers']} files_updated={len(result['applied'])}")
    print(f"report={result['paths']['report']}")


if __name__ == "__main__":
    main()
