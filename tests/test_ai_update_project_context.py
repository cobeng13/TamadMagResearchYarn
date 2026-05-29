from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.ai.schemas import PROJECT_CONTEXT_CHANGE_COLUMNS
from scripts.project_update import ai_update_project_context as mod


def make_project(tmp_path: Path, stage06_files: list[str] | None = None, stage07_files: list[str] | None = None, with_citations: bool = True) -> Path:
    project = tmp_path / "project"
    brief = project / "00_brief"
    stage06 = project / "06_synthesis"
    stage07 = project / "07_gap_analysis"
    evidence = project / "05_evidence_extraction"
    metadata = project / "04_metadata"
    for path in [brief, stage06, stage07, evidence, metadata]:
        path.mkdir(parents=True)
    (brief / "research_brief.md").write_text("Original focus: predict RTLE success from academic and pre-board indicators.", encoding="utf-8")
    (brief / "research_questions.md").write_text("Which academic variables predict RTLE outcomes?", encoding="utf-8")
    (brief / "variables.md").write_text("Predictors: academic grades, pre-board scores. Outcome: RTLE performance.", encoding="utf-8")
    (brief / "inclusion_exclusion_criteria.md").write_text("Include RTLE and allied health licensure prediction evidence.", encoding="utf-8")
    (brief / "search_keywords.md").write_text("radiologic technology; licensure; prediction", encoding="utf-8")
    (brief / "source_strategy.md").write_text("Prefer direct RTLE evidence, then allied health background.", encoding="utf-8")
    (brief / "writing_scope.md").write_text("Do not make causal claims.", encoding="utf-8")
    (brief / "agent_instructions.md").write_text("Use local project files only.", encoding="utf-8")

    citation = "Santos2024Predictors" if with_citations else ""
    selected06 = stage06_files if stage06_files is not None else mod.STAGE06_FILES
    if "synthesis_matrix.csv" in selected06:
        pd.DataFrame(
            [
                {
                    "synthesis_id": "SYN-0001",
                    "theme": "Pre-board performance",
                    "citation_key": citation,
                    "paper_id": "paper-1",
                    "key_finding": "Pre-board scores predicted licensure performance.",
                    "evidence_role": "direct_support",
                }
            ]
        ).to_csv(stage06 / "synthesis_matrix.csv", index=False)
    if "theme_matrix.md" in selected06:
        marker = " [@Santos2024Predictors]" if with_citations else ""
        (stage06 / "theme_matrix.md").write_text(f"# Theme Matrix\n\nDirect predictor evidence.{marker}\n", encoding="utf-8")
    if "literature_map.md" in selected06:
        (stage06 / "literature_map.md").write_text("# Literature Map\n\nLocal evidence remains limited.\n", encoding="utf-8")
    if "synthesis_notes.md" in selected06:
        (stage06 / "synthesis_notes.md").write_text("# Synthesis Notes\n\nUse cautiously.\n", encoding="utf-8")

    selected07 = stage07_files if stage07_files is not None else mod.STAGE07_FILES
    if "research_gap_analysis.md" in selected07:
        marker = " [@Santos2024Predictors]" if with_citations else ""
        (stage07 / "research_gap_analysis.md").write_text(f"# Research Gap Analysis\n\nLimited local RTLE evidence{marker}.\n", encoding="utf-8")
    if "study_contribution.md" in selected07:
        (stage07 / "study_contribution.md").write_text("# Study Contribution\n\nLocal-context contribution.\n", encoding="utf-8")
    if "problem_statement_refined.md" in selected07:
        (stage07 / "problem_statement_refined.md").write_text("# Refined Problem Statement\n\nLocal predictive framing.\n", encoding="utf-8")
    if "gap_matrix.csv" in selected07:
        pd.DataFrame(
            [
                {
                    "gap_id": "GAP-0001",
                    "gap_type": "local_philippine_gap",
                    "gap_statement": "Limited local evidence.",
                    "supporting_synthesis_source": "literature_map.md",
                }
            ]
        ).to_csv(stage07 / "gap_matrix.csv", index=False)

    pd.DataFrame(
        [
            {
                "paper_id": "paper-1",
                "citation_key": citation,
                "theme": "Pre-board predictors",
                "key_finding": "Pre-board scores predicted licensure performance.",
            }
        ]
    ).to_csv(evidence / "evidence_table.csv", index=False)
    pd.DataFrame(
        [{"paper_id": "paper-1", "citation_key": citation, "title": "Predictors", "authors": "Santos", "year": "2024"}]
    ).to_csv(metadata / "metadata_table.csv", index=False)
    return project


def fake_update_result() -> dict[str, object]:
    return {
        "completion_status": "completed",
        "original_study_focus": "The original project focused on RTLE prediction from academic and pre-board indicators.",
        "evidence_informed_study_focus": "The supplied synthesis suggests a cautious local-context RTLE prediction study [@Santos2024Predictors].",
        "refined_background": "Within the reviewed evidence, pre-board evidence is direct while allied-health evidence is background.",
        "defensible_research_gap": "A defensible positioning is limited local-context evidence for RTLE prediction.",
        "refined_contribution": "The study may contribute local-context predictive evidence.",
        "current_study_positioning": "Predictive, not causal.",
        "scope_boundaries": ["Use direct RTLE evidence first.", "Use allied-health evidence as background only."],
        "claims_to_avoid": ["Do not claim causality.", "Do not claim no studies exist."],
        "to_be_confirmed": [],
        "refined_research_questions": {
            "original_research_questions": ["Which academic variables predict RTLE outcomes?"],
            "refinement_notes": ["Align questions with available predictor variables."],
            "main_research_question": "Which available academic and pre-board indicators predict RTLE outcomes in the current dataset?",
            "specific_research_questions": ["To what extent are pre-board indicators associated with RTLE outcomes?"],
            "questions_to_remove_merge_or_reword": ["Remove questions requiring unavailable variables."],
            "rationale_for_changes": ["Stage 07 gap analysis supports local-context framing."],
            "to_be_confirmed": ["Current dataset fields are To be confirmed."],
        },
        "refined_writing_scope": {
            "manuscript_positioning": "Local-context predictive validation.",
            "included_scope": ["Academic and pre-board indicators."],
            "excluded_scope": ["Causal effectiveness claims."],
            "evidence_boundaries": ["Direct RTLE evidence outranks allied-health background."],
            "literature_use_rules": ["Use only supplied citation keys."],
            "local_context_framing": "Institutional details are To be confirmed.",
            "terminology_preferences": ["predictive", "associated"],
            "claims_allowed": ["The study can examine associations."],
            "claims_not_allowed": ["The study proves causality."],
            "to_be_confirmed": ["Institutional context."],
        },
        "refined_agent_instructions": {
            "general_rules": ["Use refined files when present."],
            "stage_08_outline_instructions": ["Build the outline around cautious local-context prediction."],
            "stage_09_writer_instructions": ["Do not draft unsupported novelty claims."],
            "results_and_discussion_instructions": ["Separate results from discussion."],
            "citation_and_claim_safety_rules": ["Do not invent citations."],
            "gap_informed_positioning_rules": ["Use Stage 07 gap language cautiously."],
            "to_be_confirmed": ["Confirm dataset variables."],
        },
        "outline_context": {
            "refined_paper_positioning": "Local-context RTLE prediction.",
            "defensible_gap": "Limited local-context evidence.",
            "refined_research_questions": ["Which available indicators predict RTLE outcomes?"],
            "recommended_argument_flow": ["Context", "Predictor evidence", "Local gap", "Current study."],
            "sections_needing_caution": ["Novelty", "causality"],
            "required_inputs_before_final_outline": ["Confirmed dataset variables."],
        },
        "writer_context": {
            "core_framing": "Cautious local-context prediction.",
            "safe_claims": ["The study examines predictive associations."],
            "claims_to_avoid": ["No unsupported causal claims."],
            "citation_use_rules": ["Use supplied citations only."],
            "evidence_hierarchy": ["Direct RTLE evidence", "Allied-health background"],
            "preferred_terms": ["predictive association"],
            "gap_and_contribution_language": ["A defensible positioning is limited local-context evidence."],
            "to_be_confirmed": ["Institutional details."],
        },
        "main_framing_changes": ["Shifted from broad prediction to local-context predictive positioning."],
        "research_question_changes": ["Aligned questions with available/expected data."],
        "scope_changes": ["Added explicit claim boundaries."],
        "downstream_cascade_notes": ["Stage 08 and 09 should prefer refined files."],
        "human_review_checklist": ["Approve refined framing before outlining."],
        "change_rows": [
            {
                "file_target": "00_brief/research_brief_refined.md",
                "change_type": "framing_update",
                "original_point": "Broad RTLE prediction.",
                "refined_point": "Local-context predictive validation.",
                "rationale": "Stage 07 identified a local-context gap.",
                "evidence_source": "07_gap_analysis/research_gap_analysis.md",
                "caution_level": "moderate",
                "human_review_needed": "yes",
                "notes": "Requires human approval.",
            },
            {
                "file_target": "00_brief/writing_scope_refined.md",
                "change_type": "bad_type",
                "original_point": "",
                "refined_point": "Avoid causal claims.",
                "rationale": "",
                "evidence_source": "Stage 06",
                "caution_level": "extreme",
                "human_review_needed": "maybe",
                "notes": "",
            },
        ],
    }


def run_default(project: Path, monkeypatch: pytest.MonkeyPatch, **kwargs):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_project_context_update", lambda *args, **kwargs: fake_update_result())
    params = {
        "project_dir": project,
        "model": "gpt-5-mini",
        "dry_run": False,
        "overwrite": False,
        "no_backup": False,
        "strict": False,
        "apply_to_originals": False,
        "max_input_chars": None,
    }
    params.update(kwargs)
    return mod.run_ai_project_context_update(**params)


def test_dry_run_works_without_openai_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_ai_project_context_update(
        project_dir=project,
        model="gpt-5-mini",
        dry_run=True,
        overwrite=False,
        no_backup=False,
        strict=False,
        apply_to_originals=False,
        max_input_chars=None,
    )

    assert result["status"] == "partial"
    assert (project / "00_brief" / "project_context_update_summary.md").exists()
    assert not (project / "00_brief" / "research_brief_refined.md").exists()
    assert (project / "logs" / "ai_project_context_update_log.md").exists()


def test_missing_stage07_files_writes_blocked_without_ai_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, stage07_files=[])
    monkeypatch.setattr(mod, "call_openai_project_context_update", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("AI should not be called")))

    result = mod.run_ai_project_context_update(
        project_dir=project,
        model="gpt-5-mini",
        dry_run=False,
        overwrite=False,
        no_backup=False,
        strict=False,
        apply_to_originals=False,
        max_input_chars=None,
    )

    assert result["status"] == "blocked"
    assert "Stage 07 gap-analysis outputs must be completed" in (project / "00_brief" / "project_context_update_blocked.md").read_text(encoding="utf-8")


def test_partial_stage06_or_stage07_inputs_still_run_with_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, stage06_files=["theme_matrix.md"], stage07_files=["research_gap_analysis.md"])

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    assert any("Missing or empty Stage 06 input" in warning for warning in result["warnings"])
    assert any("Missing or empty Stage 07 input" in warning for warning in result["warnings"])


def test_mocked_ai_response_writes_all_refined_outputs_context_summary_changes_and_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    for path in [
        "00_brief/research_brief_refined.md",
        "00_brief/research_questions_refined.md",
        "00_brief/writing_scope_refined.md",
        "00_brief/agent_instructions_refined.md",
        "08_outline/_context_for_outline.md",
        "09_drafts/_context_for_writers.md",
        "00_brief/project_context_update_summary.md",
        "00_brief/project_context_changes.csv",
        "logs/ai_project_context_update_log.md",
    ]:
        assert (project / path).exists()


def test_project_context_changes_csv_has_required_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    run_default(project, monkeypatch)
    changes = pd.read_csv(project / "00_brief" / "project_context_changes.csv", dtype=str).fillna("")

    assert list(changes.columns) == PROJECT_CONTEXT_CHANGE_COLUMNS


def test_invalid_enum_values_are_coerced_and_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)
    changes = pd.read_csv(project / "00_brief" / "project_context_changes.csv", dtype=str).fillna("")
    invalid = changes[changes["change_id"] == "CTX-0002"].iloc[0]

    assert invalid["change_type"] == "to_be_confirmed"
    assert invalid["caution_level"] == "to_be_confirmed"
    assert invalid["human_review_needed"] == "yes"
    assert any("Invalid change_type" in warning for warning in result["warnings"])
    assert any("Invalid caution_level" in warning for warning in result["warnings"])


def test_existing_refined_outputs_are_not_overwritten_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    existing = project / "00_brief" / "research_brief_refined.md"
    existing.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        run_default(project, monkeypatch)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    existing = project / "00_brief" / "research_brief_refined.md"
    existing.write_text("existing", encoding="utf-8")

    result = run_default(project, monkeypatch, overwrite=True)
    assert result["backups"]
    assert result["backups"][0].exists()

    existing.write_text("existing again", encoding="utf-8")
    result_no_backup = run_default(project, monkeypatch, overwrite=True, no_backup=True)
    assert result_no_backup["backups"] == []


def test_default_mode_does_not_modify_original_stage00_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    original = (project / "00_brief" / "research_brief.md").read_text(encoding="utf-8")

    run_default(project, monkeypatch)

    assert (project / "00_brief" / "research_brief.md").read_text(encoding="utf-8") == original


def test_apply_to_originals_requires_overwrite_and_backs_up_original_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    with pytest.raises(ValueError):
        run_default(project, monkeypatch, apply_to_originals=True)

    result = run_default(project, monkeypatch, apply_to_originals=True, overwrite=True)
    assert result["backups"]
    assert "Refined Research Brief" in (project / "00_brief" / "research_brief.md").read_text(encoding="utf-8")
    assert any(path.name.startswith("research_brief.") and ".bak" in path.name for path in result["backups"])


def test_output_does_not_include_invented_citation_keys_when_none_are_supplied(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, with_citations=False)

    run_default(project, monkeypatch)
    text = (project / "00_brief" / "research_brief_refined.md").read_text(encoding="utf-8")

    assert "[@Santos2024Predictors]" not in text
    assert "[@ToBeConfirmed]" in text
