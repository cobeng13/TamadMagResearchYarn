from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.ai.schemas import OUTLINE_MAP_COLUMNS
from scripts.outline import ai_build_outline as mod


def make_project(
    tmp_path: Path,
    *,
    refined: bool = True,
    stage06_files: list[str] | None = None,
    stage07_files: list[str] | None = None,
    results: bool = True,
    with_citations: bool = True,
    stage00: bool = True,
) -> Path:
    project = tmp_path / "project"
    brief = project / "00_brief"
    outline = project / "08_outline"
    stage06 = project / "06_synthesis"
    stage07 = project / "07_gap_analysis"
    evidence = project / "05_evidence_extraction"
    metadata = project / "04_metadata"
    input_dir = project / "input"
    for path in [brief, outline, stage06, stage07, evidence, metadata, input_dir]:
        path.mkdir(parents=True)
    if stage00:
        (brief / "research_brief.md").write_text("Original broad RTLE prediction framing.", encoding="utf-8")
        (brief / "research_questions.md").write_text("Original question: Which variables predict RTLE outcomes?", encoding="utf-8")
        (brief / "variables.md").write_text("Academic grades; pre-board scores; RTLE outcome.", encoding="utf-8")
        (brief / "inclusion_exclusion_criteria.md").write_text("Include RTLE and allied-health licensure prediction.", encoding="utf-8")
        (brief / "writing_scope.md").write_text("Avoid causal claims.", encoding="utf-8")
        (brief / "agent_instructions.md").write_text("Use local files only.", encoding="utf-8")
    if refined:
        (outline / "_context_for_outline.md").write_text("REFINED OUTLINE CONTEXT: local-context predictive validation.", encoding="utf-8")
        (brief / "research_brief_refined.md").write_text("REFINED BRIEF: local-context RTLE prediction.", encoding="utf-8")
        (brief / "research_questions_refined.md").write_text("REFINED QUESTIONS: available indicators and RTLE outcomes.", encoding="utf-8")
        (brief / "writing_scope_refined.md").write_text("REFINED SCOPE: direct evidence first.", encoding="utf-8")
        (brief / "agent_instructions_refined.md").write_text("REFINED INSTRUCTIONS: prefer refined context.", encoding="utf-8")
    citation = "Santos2024Predictors" if with_citations else ""
    selected06 = stage06_files if stage06_files is not None else mod.STAGE06_FILES
    if "synthesis_matrix.csv" in selected06:
        pd.DataFrame([{"citation_key": citation, "theme": "Pre-board", "key_finding": "Predictor evidence."}]).to_csv(stage06 / "synthesis_matrix.csv", index=False)
    if "theme_matrix.md" in selected06:
        marker = " [@Santos2024Predictors]" if with_citations else ""
        (stage06 / "theme_matrix.md").write_text(f"# Theme Matrix\n\nDirect evidence{marker}.\n", encoding="utf-8")
    if "literature_map.md" in selected06:
        (stage06 / "literature_map.md").write_text("# Literature Map\n\nDirect and indirect evidence sections.\n", encoding="utf-8")
    if "synthesis_notes.md" in selected06:
        (stage06 / "synthesis_notes.md").write_text("# Synthesis Notes\n\nCaution about causality.\n", encoding="utf-8")
    selected07 = stage07_files if stage07_files is not None else mod.STAGE07_FILES
    if "research_gap_analysis.md" in selected07:
        marker = " [@Santos2024Predictors]" if with_citations else ""
        (stage07 / "research_gap_analysis.md").write_text(f"# Gap\n\nLimited local evidence{marker}.\n", encoding="utf-8")
    if "study_contribution.md" in selected07:
        (stage07 / "study_contribution.md").write_text("# Contribution\n\nLocal-context contribution.\n", encoding="utf-8")
    if "problem_statement_refined.md" in selected07:
        (stage07 / "problem_statement_refined.md").write_text("# Problem\n\nLocal predictive problem.", encoding="utf-8")
    if "gap_matrix.csv" in selected07:
        pd.DataFrame([{"gap_id": "GAP-0001", "gap_statement": "Limited local evidence."}]).to_csv(stage07 / "gap_matrix.csv", index=False)
    (input_dir / "study_notes.md").write_text("Study design: predictive correlational. Institution: To be confirmed.", encoding="utf-8")
    if results:
        (input_dir / "statistical_results.md").write_text("Regression table supplied by user. No p-values here.", encoding="utf-8")
    pd.DataFrame([{"citation_key": citation, "key_finding": "Pre-board predictor evidence."}]).to_csv(evidence / "evidence_table.csv", index=False)
    pd.DataFrame([{"citation_key": citation, "title": "Predictors"}]).to_csv(metadata / "metadata_table.csv", index=False)
    return project


def fake_outline_result() -> dict[str, object]:
    return {
        "completion_status": "completed",
        "refined_manuscript_positioning": "A cautious local-context RTLE prediction manuscript [@Santos2024Predictors].",
        "working_title_direction": "Predictive indicators of RTLE outcomes.",
        "central_argument": "The study examines predictive associations, not causality.",
        "intended_manuscript_flow": ["Context", "Evidence", "Gap", "Methods", "Results", "Discussion"],
        "section_level_outline": {
            "introduction": ["Establish RTLE prediction context."],
            "review_of_related_literature": ["Organize direct and indirect evidence."],
            "methodology": ["Describe predictive correlational design."],
            "results": ["Report supplied statistical outputs only."],
            "discussion": ["Compare supplied results with synthesis."],
            "conclusion_recommendations": ["Summarize cautious contribution."],
        },
        "introduction_outline": {
            "opening_context": ["RTLE performance matters to programs."],
            "problem_background": ["Predictor evidence exists."],
            "evidence_based_gap": ["Limited local-context evidence."],
            "local_context": ["Institutional facts are To be confirmed."],
            "study_purpose": ["Assess predictive indicators."],
            "research_questions_or_objectives": ["Which indicators predict RTLE outcomes?"],
            "significance": ["Program planning."],
            "scope_and_delimitations": ["Predictive association only."],
            "suggested_citation_anchors": ["[@Santos2024Predictors]"],
            "claims_to_avoid": ["No causal claims."],
            "to_be_confirmed": ["Institution."],
        },
        "rrl_outline": {
            "rrl_framing": "Use Stage 06 synthesis.",
            "themes": [
                {
                    "theme": "Pre-board performance",
                    "key_evidence_to_discuss": ["Predictor evidence."],
                    "suggested_citation_anchors": ["[@Santos2024Predictors]"],
                    "relationship_to_current_study": "Direct evidence.",
                    "limitations_or_cautions": ["Associational only."],
                }
            ],
            "direct_evidence_section": ["RTLE/licensure evidence."],
            "indirect_evidence_section": ["Allied-health evidence as background."],
            "methodological_literature_section": ["Predictive modeling studies."],
            "synthesis_toward_gap": ["Local gap."],
            "claims_to_avoid": ["No invented citations."],
            "to_be_confirmed": ["Coverage completeness."],
        },
        "methodology_outline": {
            "research_design": "Predictive correlational. To be confirmed.",
            "study_setting": "To be confirmed.",
            "population_and_sampling": "To be confirmed.",
            "variables": ["Academic grades", "Pre-board scores"],
            "data_sources": ["Institutional records. To be confirmed."],
            "measures_and_operational_definitions": ["To be confirmed."],
            "statistical_analysis_plan": ["Regression if supported by user data."],
            "ethical_considerations": "To be confirmed.",
            "limitations_of_method": ["Associational design."],
            "to_be_confirmed": ["Sample size."],
        },
        "results_outline": {
            "completion_status": "ready",
            "available_statistical_inputs": ["statistical_results.md"],
            "proposed_results_organization": ["Descriptives", "Prediction model"],
            "table_and_figure_plan": ["Table 1 variables", "Table 2 model"],
            "results_by_research_question": ["RQ1 model results."],
            "required_statistical_outputs": ["Coefficients"],
            "missing_results_to_confirm": ["p-values if not supplied."],
            "claims_not_allowed_yet": ["Do not claim significance unless supplied."],
        },
        "discussion_outline": {
            "opening_summary_of_expected_results": ["Use To be confirmed if results missing."],
            "interpretation_plan": ["Interpret supplied findings only."],
            "relationship_to_literature_synthesis": ["Compare with Stage 06."],
            "implications": ["Program planning."],
            "limitations": ["Local data."],
            "recommendations": ["Review curriculum planning implications."],
            "conclusion_direction": ["Cautious local contribution."],
            "claims_to_avoid": ["No unsupported effects."],
            "to_be_confirmed": ["Actual results."],
        },
        "citation_and_evidence_use_rules": ["Use supplied citation keys only."],
        "claims_to_avoid": ["Do not invent statistics."],
        "items_to_confirm": [],
        "outline_map_rows": [
            {
                "manuscript_section": "introduction",
                "subsection": "Evidence-based gap",
                "purpose": "Frame gap.",
                "source_basis": "Stage 07",
                "suggested_citation_keys": "Santos2024Predictors",
                "required_inputs": "Gap analysis",
                "readiness_status": "partial",
                "caution_notes": "Local evidence limited.",
            },
            {
                "manuscript_section": "results",
                "subsection": "",
                "purpose": "Report results.",
                "source_basis": "statistical_results.md",
                "suggested_citation_keys": "",
                "required_inputs": "Statistics",
                "readiness_status": "excellent",
                "caution_notes": "",
            },
        ],
        "readiness": {
            "ready_for_drafting": ["Introduction outline after review."],
            "partially_ready": ["RRL", "Methodology"],
            "blocked_until_more_inputs": ["Results if statistics missing."],
            "human_review_needed": ["Approve outline map."],
            "recommended_next_step": "Review Stage 08 before writing.",
        },
    }


def run_default(project: Path, monkeypatch: pytest.MonkeyPatch, **kwargs):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_outline", lambda *args, **kwargs: fake_outline_result())
    params = {
        "project_dir": project,
        "model": "gpt-5-mini",
        "dry_run": False,
        "overwrite": False,
        "no_backup": False,
        "strict": False,
        "prefer_refined": True,
        "include_results_outline": True,
        "max_input_chars": None,
    }
    params.update(kwargs)
    return mod.run_ai_outline(**params)


def test_dry_run_works_without_openai_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_ai_outline(project, "gpt-5-mini", True, False, False, False, True, True, None)

    assert result["status"] == "partial"
    assert "Dry run only" in (project / "08_outline" / "manuscript_outline.md").read_text(encoding="utf-8")
    assert (project / "logs" / "ai_outline_log.md").exists()


def test_missing_stage00_context_writes_blocked_without_ai_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, refined=False, stage00=False)
    monkeypatch.setattr(mod, "call_openai_outline", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("AI should not be called")))

    result = mod.run_ai_outline(project, "gpt-5-mini", False, False, False, False, True, True, None)

    assert result["status"] == "blocked"
    assert "Stage 00 project context must be completed" in (project / "08_outline" / "manuscript_outline.md").read_text(encoding="utf-8")


def test_refined_files_are_preferred_when_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, refined=True)
    captured = {}

    def fake_call(*args, **kwargs):
        captured["refined"] = args[2]
        captured["original"] = args[3]
        return fake_outline_result()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_outline", fake_call)

    mod.run_ai_outline(project, "gpt-5-mini", False, False, False, False, True, True, None)

    assert "REFINED OUTLINE CONTEXT" in captured["refined"]
    assert "Original broad RTLE" in captured["original"]


def test_original_files_used_when_refined_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, refined=False)
    captured = {}

    def fake_call(*args, **kwargs):
        captured["refined"] = args[2]
        captured["original"] = args[3]
        return fake_outline_result()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_outline", fake_call)

    mod.run_ai_outline(project, "gpt-5-mini", False, False, False, False, True, True, None)

    assert captured["refined"] == ""
    assert "Original broad RTLE" in captured["original"]


def test_missing_stage06_or_stage07_files_allows_partial_with_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, stage06_files=["theme_matrix.md"], stage07_files=["research_gap_analysis.md"])

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    assert any("Missing or empty Stage 06 input" in warning for warning in result["warnings"])
    assert any("Missing or empty Stage 07 input" in warning for warning in result["warnings"])


def test_mocked_ai_response_writes_all_outputs_plus_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    for path in [
        "manuscript_outline.md",
        "introduction_outline.md",
        "rrl_outline.md",
        "methodology_outline.md",
        "results_outline.md",
        "discussion_outline.md",
        "outline_map.csv",
        "outline_readiness_checklist.md",
    ]:
        assert (project / "08_outline" / path).exists()
    assert (project / "logs" / "ai_outline_log.md").exists()


def test_outline_map_has_required_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    run_default(project, monkeypatch)
    outline_map = pd.read_csv(project / "08_outline" / "outline_map.csv", dtype=str).fillna("")

    assert list(outline_map.columns) == OUTLINE_MAP_COLUMNS


def test_invalid_readiness_status_values_are_coerced_and_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)
    outline_map = pd.read_csv(project / "08_outline" / "outline_map.csv", dtype=str).fillna("")
    invalid = outline_map[outline_map["outline_id"] == "OUT-0002"].iloc[0]

    assert invalid["readiness_status"] == "to_be_confirmed"
    assert invalid["subsection"] == "To be confirmed."
    assert any("Invalid readiness_status" in warning for warning in result["warnings"])


def test_existing_outputs_not_overwritten_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    (project / "08_outline" / "manuscript_outline.md").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        run_default(project, monkeypatch)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    existing = project / "08_outline" / "manuscript_outline.md"
    existing.write_text("existing", encoding="utf-8")

    result = run_default(project, monkeypatch, overwrite=True)
    assert result["backups"]
    assert result["backups"][0].exists()

    existing.write_text("existing again", encoding="utf-8")
    result_no_backup = run_default(project, monkeypatch, overwrite=True, no_backup=True)
    assert result_no_backup["backups"] == []


def test_results_outline_blocked_when_statistical_results_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, results=False)

    result = run_default(project, monkeypatch)
    text = (project / "08_outline" / "results_outline.md").read_text(encoding="utf-8")
    outline_map = pd.read_csv(project / "08_outline" / "outline_map.csv", dtype=str).fillna("")
    result_row = outline_map[outline_map["manuscript_section"] == "results"].iloc[0]

    assert "blocked" in text
    assert result_row["readiness_status"] == "to_be_confirmed"
    assert any("Results outline marked ready without statistical inputs" in warning for warning in result["warnings"])


def test_output_does_not_include_invented_citation_keys_when_none_supplied(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, with_citations=False)

    run_default(project, monkeypatch)
    text = (project / "08_outline" / "manuscript_outline.md").read_text(encoding="utf-8")

    assert "[@Santos2024Predictors]" not in text
    assert "[@ToBeConfirmed]" in text
