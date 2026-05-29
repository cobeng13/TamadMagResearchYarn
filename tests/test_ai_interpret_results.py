from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.ai.schemas import RESULTS_BY_OBJECTIVE_COLUMNS, STATISTICAL_FINDINGS_COLUMNS
from scripts.results import ai_interpret_results as mod


def make_project(tmp_path: Path, with_results: bool = True) -> Path:
    project = tmp_path / "project"
    for folder in ["input", "00_brief", "08_outline", "07_gap_analysis"]:
        (project / folder).mkdir(parents=True, exist_ok=True)
    (project / "00_brief" / "research_questions.md").write_text("# Objectives\n1. Describe clustered grades.", encoding="utf-8")
    (project / "00_brief" / "variables.md").write_text("# Variables", encoding="utf-8")
    (project / "input" / "human_confirmed_context.md").write_text("# Context", encoding="utf-8")
    (project / "input" / "methodology_details.md").write_text("# Methodology", encoding="utf-8")
    (project / "08_outline" / "results_outline.md").write_text("# Results Outline", encoding="utf-8")
    (project / "08_outline" / "discussion_outline.md").write_text("# Discussion Outline", encoding="utf-8")
    if with_results:
        (project / "input" / "statistical_results_compiled.md").write_text("# Compiled\nmodel p = 0.01 significant", encoding="utf-8")
        (project / "input" / "statistical_results.md").write_text("# Statistical Results\nn=92", encoding="utf-8")
        (project / "input" / "statistical_results_manifest.csv").write_text("result_file_id,source_path\nSTAT-0001,result.md\n", encoding="utf-8")
        (project / "input" / "results_availability.md").write_text("# Results Availability\nready", encoding="utf-8")
    return project


def fake_response() -> dict:
    return {
        "completion_status": "completed",
        "inputs_used": ["statistical_results_compiled.md"],
        "study_objectives_or_research_questions": ["Objective 1"],
        "results_availability_summary": "Results supplied.",
        "findings_by_objective": [
            {
                "objective_id": "OBJ-001",
                "objective_text": "Describe clustered grades.",
                "available_results": ["statistical_results_compiled.md"],
                "statistical_test_or_model": "Descriptive statistics",
                "key_numerical_findings": ["n=92"],
                "p_value_or_ci": "not_reported",
                "significance_status": "not_tested",
                "plain_language_result": "Descriptive output supplied.",
                "interpretation_boundary": "Non-causal.",
                "result_readiness": "ready_for_results_draft",
                "missing_items": [],
                "notes": "",
            }
        ],
        "overall_results_pattern": "Partial pattern.",
        "results_ready_to_write": ["Objective 1"],
        "results_partial": [],
        "results_missing": [],
        "statistical_claims_allowed": ["Report supplied n."],
        "statistical_claims_not_allowed": ["Do not invent p-values."],
        "notes_for_results_writer": ["Use source values only."],
        "notes_for_discussion_writer": ["Planning cue only."],
        "recommended_tables": [
            {
                "table_title": "Descriptive Characteristics",
                "purpose": "Summarize variables.",
                "source_result_files": ["statistical_results_compiled.md"],
                "required_columns": ["variable", "mean"],
                "available": ["n"],
                "missing": ["mean"],
                "notes": "",
            }
        ],
        "recommended_figures": [],
        "missing_results_to_confirm": {
            "required_before_results_drafting": [],
            "required_before_discussion_drafting": [],
            "missing_by_objective": [],
            "missing_tables_or_figures": [],
            "missing_statistical_details": [],
            "human_or_statistician_followup_questions": [],
        },
        "statistical_findings": [
            {
                "objective_id": "OBJ-001",
                "source_file": "statistical_results_compiled.md",
                "finding_type": "descriptive",
                "variable_or_predictor": "clustered grades",
                "outcome": "none",
                "statistical_method": "descriptive",
                "reported_value": "n=92",
                "p_value": "not_reported",
                "confidence_interval": "not_reported",
                "interpretation": "Sample size supplied.",
                "writing_use": "results",
                "caution_level": "low",
                "notes": "",
            }
        ],
    }


def test_dry_run_works_without_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_ai_interpret(project, "gpt-5-mini", dry_run=True, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)

    assert result["status"] == "partial"
    assert (project / "09_drafts" / "results" / "results_interpretation_notes.md").exists()


def test_missing_results_writes_blocked_and_does_not_call_ai(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, with_results=False)
    called = False

    def fail_call(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("should not call AI")

    monkeypatch.setattr(mod, "call_openai_results", fail_call)
    result = mod.run_ai_interpret(project, "gpt-5-mini", dry_run=False, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)

    assert result["status"] == "blocked"
    assert not called
    assert "No statistical results" in (project / "09_drafts" / "results" / "results_interpretation_notes.md").read_text(encoding="utf-8")


def test_partial_results_continue_with_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    (project / "input" / "results_availability.md").write_text("partial\nMissing Table 2", encoding="utf-8")
    monkeypatch.setattr(mod, "call_openai_results", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(mod, "require_api_key", lambda dry_run=False: "test")

    result = mod.run_ai_interpret(project, "gpt-5-mini", dry_run=False, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)

    assert result["objectives"] == 1


def test_mocked_ai_response_writes_all_outputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr(mod, "call_openai_results", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(mod, "require_api_key", lambda dry_run=False: "test")

    mod.run_ai_interpret(project, "gpt-5-mini", dry_run=False, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=True)

    out = project / "09_drafts" / "results"
    assert (out / "results_interpretation_notes.md").exists()
    assert (out / "results_table_notes.md").exists()
    assert (out / "missing_results_to_confirm.md").exists()
    assert (out / "results_by_objective.csv").exists()
    assert (out / "statistical_findings_matrix.csv").exists()
    assert (project / "logs" / "ai_results_interpretation_log.md").exists()


def test_csv_outputs_have_required_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr(mod, "call_openai_results", lambda *args, **kwargs: fake_response())
    monkeypatch.setattr(mod, "require_api_key", lambda dry_run=False: "test")

    mod.run_ai_interpret(project, "gpt-5-mini", dry_run=False, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)

    out = project / "09_drafts" / "results"
    assert list(pd.read_csv(out / "results_by_objective.csv").columns) == RESULTS_BY_OBJECTIVE_COLUMNS
    assert list(pd.read_csv(out / "statistical_findings_matrix.csv").columns) == STATISTICAL_FINDINGS_COLUMNS


def test_invalid_enum_values_are_coerced_and_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    response = fake_response()
    response["findings_by_objective"][0]["significance_status"] = "very_significant"
    response["findings_by_objective"][0]["result_readiness"] = "done"
    response["statistical_findings"][0]["finding_type"] = "bad"
    response["statistical_findings"][0]["writing_use"] = "bad"
    response["statistical_findings"][0]["caution_level"] = "bad"
    monkeypatch.setattr(mod, "call_openai_results", lambda *args, **kwargs: response)
    monkeypatch.setattr(mod, "require_api_key", lambda dry_run=False: "test")

    mod.run_ai_interpret(project, "gpt-5-mini", dry_run=False, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)
    log = (project / "logs" / "ai_results_interpretation_log.md").read_text(encoding="utf-8")

    assert "invalid significance_status" in log
    assert "to_be_confirmed" in pd.read_csv(project / "09_drafts" / "results" / "statistical_findings_matrix.csv").to_csv(index=False)


def test_significant_without_source_support_is_downgraded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    (project / "input" / "statistical_results_compiled.md").write_text("# Compiled\nmodel output only", encoding="utf-8")
    response = fake_response()
    response["findings_by_objective"][0]["significance_status"] = "significant"
    response["findings_by_objective"][0]["p_value_or_ci"] = "not_reported"
    monkeypatch.setattr(mod, "call_openai_results", lambda *args, **kwargs: response)
    monkeypatch.setattr(mod, "require_api_key", lambda dry_run=False: "test")

    mod.run_ai_interpret(project, "gpt-5-mini", dry_run=False, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)
    df = pd.read_csv(project / "09_drafts" / "results" / "results_by_objective.csv")

    assert df.loc[0, "significance_status"] == "to_be_confirmed"


def test_existing_outputs_not_overwritten_without_overwrite(tmp_path: Path):
    project = make_project(tmp_path)
    out = project / "09_drafts" / "results"
    out.mkdir(parents=True)
    (out / "results_interpretation_notes.md").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        mod.run_ai_interpret(project, "gpt-5-mini", dry_run=True, overwrite=False, no_backup=True, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path):
    project = make_project(tmp_path)
    out = project / "09_drafts" / "results"
    out.mkdir(parents=True)
    (out / "results_interpretation_notes.md").write_text("existing", encoding="utf-8")

    result = mod.run_ai_interpret(project, "gpt-5-mini", dry_run=True, overwrite=True, no_backup=False, strict=False, max_input_chars=None, objectives=None, include_discussion_cues=False)

    assert result["backups"]
    assert list(out.glob("*.bak.md"))
