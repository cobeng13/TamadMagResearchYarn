from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.human_input import apply_input_packet as mod
from scripts.human_input.build_input_packet import QUESTION_COLUMNS


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    human = project / "human_input"
    human.mkdir(parents=True)
    rows = [
        {
            "question_id": "HI-0001",
            "priority": "required_before_drafting",
            "category": "Study Identity and Framing",
            "question": "Title?",
            "why_needed": "Needed.",
            "used_by_stage": "Stage 09",
            "target_file": "input/human_confirmed_context.md",
            "answer_type": "short_text",
            "required_before": "before_drafting",
            "detected_from": "",
            "default_value": "",
            "status": "unanswered",
            "notes": "",
        },
        {
            "question_id": "HI-0002",
            "priority": "required_before_drafting",
            "category": "Methodology Details",
            "question": "Design?",
            "why_needed": "Needed.",
            "used_by_stage": "Methodology",
            "target_file": "input/methodology_details.md",
            "answer_type": "short_text",
            "required_before": "before_drafting",
            "detected_from": "",
            "default_value": "",
            "status": "unanswered",
            "notes": "",
        },
        {
            "question_id": "HI-0003",
            "priority": "required_before_results",
            "category": "Data and Results Details",
            "question": "Stats?",
            "why_needed": "Needed.",
            "used_by_stage": "Results",
            "target_file": "input/statistical_results.md",
            "answer_type": "long_text",
            "required_before": "before_results",
            "detected_from": "",
            "default_value": "",
            "status": "unanswered",
            "notes": "",
        },
        {
            "question_id": "HI-0004",
            "priority": "optional",
            "category": "Style Preferences",
            "question": "Style?",
            "why_needed": "Optional.",
            "used_by_stage": "All",
            "target_file": "input/human_confirmed_context.md",
            "answer_type": "long_text",
            "required_before": "before_final",
            "detected_from": "",
            "default_value": "",
            "status": "unanswered",
            "notes": "",
        },
    ]
    pd.DataFrame(rows, columns=QUESTION_COLUMNS).to_csv(human / "human_input_questions.csv", index=False)
    (human / "human_input_answers.md").write_text(
        """# Human Input Answers

## HI-0001

Question:
Title?
Answer:
Predictors of RTLE Performance

## HI-0002

Question:
Design?
Answer:
To be confirmed.

## HI-0003

Question:
Stats?
Answer:

## HI-0004

Question:
Style?
Answer:
N/A
""",
        encoding="utf-8",
    )
    return project


def test_parses_qid_answer_sections_correctly(tmp_path: Path):
    project = make_project(tmp_path)

    answers = mod.parse_answers(project / "human_input" / "human_input_answers.md")

    assert answers["HI-0001"] == "Predictors of RTLE Performance"
    assert answers["HI-0002"] == "To be confirmed."


def test_blank_to_confirm_and_na_statuses(tmp_path: Path):
    project = make_project(tmp_path)
    answers = mod.parse_answers(project / "human_input" / "human_input_answers.md")

    assert mod.answer_status(answers["HI-0003"]) == "unanswered"
    assert mod.answer_status(answers["HI-0002"]) == "to_be_confirmed"
    assert mod.answer_status(answers["HI-0004"]) == "not_applicable"


def test_creates_context_and_methodology_files(tmp_path: Path):
    project = make_project(tmp_path)

    mod.run_apply(project, project / "human_input" / "human_input_answers.md", project / "human_input" / "human_input_questions.csv", False, False, False, False)

    assert (project / "input" / "human_confirmed_context.md").exists()
    assert (project / "input" / "methodology_details.md").exists()


def test_does_not_overwrite_nonempty_stats_without_overwrite_and_appends(tmp_path: Path):
    project = make_project(tmp_path)
    stats = project / "input" / "statistical_results.md"
    stats.parent.mkdir(parents=True)
    stats.write_text("Existing stats", encoding="utf-8")
    answers = project / "human_input" / "human_input_answers.md"
    answers.write_text(answers.read_text(encoding="utf-8").replace("Answer:\n\n## HI-0004", "Answer:\nRegression coefficients supplied.\n\n## HI-0004"), encoding="utf-8")

    mod.run_apply(project, answers, project / "human_input" / "human_input_questions.csv", False, False, False, False)

    text = stats.read_text(encoding="utf-8")
    assert "Existing stats" in text
    assert "Regression coefficients supplied." in text


def test_dry_run_reports_but_does_not_update_input_files(tmp_path: Path):
    project = make_project(tmp_path)

    mod.run_apply(project, project / "human_input" / "human_input_answers.md", project / "human_input" / "human_input_questions.csv", False, False, False, True)

    assert not (project / "input" / "human_confirmed_context.md").exists()
    assert (project / "human_input" / "human_input_apply_report.md").exists()


def test_strict_fails_if_required_before_drafting_missing(tmp_path: Path):
    project = make_project(tmp_path)
    answers = project / "human_input" / "human_input_answers.md"
    answers.write_text(answers.read_text(encoding="utf-8").replace("Predictors of RTLE Performance", ""), encoding="utf-8")

    with pytest.raises(ValueError):
        mod.run_apply(project, answers, project / "human_input" / "human_input_questions.csv", False, False, True, False)


def test_unknown_qids_logged_and_ignored_unless_strict(tmp_path: Path):
    project = make_project(tmp_path)
    answers = project / "human_input" / "human_input_answers.md"
    answers.write_text(answers.read_text(encoding="utf-8") + "\n\n## HI-9999\n\nQuestion:\nUnknown\nAnswer:\nValue\n", encoding="utf-8")

    result = mod.run_apply(project, answers, project / "human_input" / "human_input_questions.csv", False, False, False, False)
    assert any("Unknown QID" in warning for warning in result["warnings"])
    with pytest.raises(ValueError):
        mod.run_apply(project, answers, project / "human_input" / "human_input_questions.csv", False, False, True, False)
