from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.human_input import build_input_packet as mod


def make_project(tmp_path: Path, outlines: bool = True) -> Path:
    project = tmp_path / "project"
    outline = project / "08_outline"
    brief = project / "00_brief"
    input_dir = project / "input"
    gap = project / "07_gap_analysis"
    for path in [outline, brief, input_dir, gap]:
        path.mkdir(parents=True)
    (brief / "research_brief.md").write_text("RTLE prediction study. Variables: grades and pre-board.", encoding="utf-8")
    (brief / "research_questions.md").write_text("Which predictors are associated with RTLE outcomes?", encoding="utf-8")
    (input_dir / "study_notes.md").write_text("Study design: predictive correlational. Sample size: To be confirmed.", encoding="utf-8")
    (gap / "problem_statement_refined.md").write_text("Institution and timeframe are To be confirmed.", encoding="utf-8")
    if outlines:
        (outline / "manuscript_outline.md").write_text("## Items To Be Confirmed\n- sample size\n- ethical approval\n", encoding="utf-8")
        (outline / "methodology_outline.md").write_text("Population: To be confirmed. Data source missing. Ethical approval To be confirmed.", encoding="utf-8")
        (outline / "results_outline.md").write_text("statistical_results.md is empty. Required statistical outputs missing. Table and figure plan blocked.", encoding="utf-8")
        pd.DataFrame(
            [{"outline_id": "OUT-0001", "manuscript_section": "results", "subsection": "Model", "readiness_status": "blocked"}]
        ).to_csv(outline / "outline_map.csv", index=False)
    return project


def test_builds_packet_from_outline_files_with_to_be_confirmed_markers(tmp_path: Path):
    project = make_project(tmp_path)

    result = mod.run_build_packet(project, False, False, False, False, "both", False, "gpt-5-nano", True)

    assert result["questions"] >= 10
    text = (project / "human_input" / "human_input_packet.md").read_text(encoding="utf-8")
    assert "Human Input Packet" in text
    assert "ethical" in text.lower()


def test_works_without_openai_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_build_packet(project, False, False, False, False, "both", False, "gpt-5-nano", True)

    assert result["questions"] > 0


def test_missing_outline_files_writes_partial_packet_unless_strict(tmp_path: Path):
    project = make_project(tmp_path, outlines=False)

    result = mod.run_build_packet(project, False, False, False, False, "both", False, "gpt-5-nano", True)

    assert any("Stage 08 outline files are missing" in warning for warning in result["warnings"])
    assert (project / "human_input" / "human_input_packet.md").exists()
    with pytest.raises(FileNotFoundError):
        mod.run_build_packet(project, True, False, True, False, "both", False, "gpt-5-nano", True)


def test_questions_csv_has_required_columns(tmp_path: Path):
    project = make_project(tmp_path)

    mod.run_build_packet(project, False, False, False, False, "both", False, "gpt-5-nano", True)
    df = pd.read_csv(project / "human_input" / "human_input_questions.csv", dtype=str).fillna("")

    assert list(df.columns) == mod.QUESTION_COLUMNS


def test_baseline_required_questions_always_included(tmp_path: Path):
    project = make_project(tmp_path, outlines=False)

    mod.run_build_packet(project, False, False, False, False, "both", False, "gpt-5-nano", True)
    questions = (project / "human_input" / "human_input_questions.csv").read_text(encoding="utf-8")

    assert "What final or working title" in questions
    assert "What is the confirmed study design" in questions
    assert "What statistical outputs are available" in questions


def test_existing_packet_not_overwritten_without_overwrite(tmp_path: Path):
    project = make_project(tmp_path)
    human = project / "human_input"
    human.mkdir()
    (human / "human_input_packet.md").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        mod.run_build_packet(project, False, False, False, False, "both", False, "gpt-5-nano", True)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path):
    project = make_project(tmp_path)
    human = project / "human_input"
    human.mkdir()
    packet = human / "human_input_packet.md"
    packet.write_text("existing", encoding="utf-8")

    result = mod.run_build_packet(project, True, False, False, False, "both", False, "gpt-5-nano", True)
    assert result["backups"]
    packet.write_text("existing again", encoding="utf-8")
    result_no_backup = mod.run_build_packet(project, True, True, False, False, "both", False, "gpt-5-nano", True)
    assert result_no_backup["backups"] == []
