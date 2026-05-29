from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.ai.schemas import GAP_MATRIX_COLUMNS
from scripts.gap_analysis import ai_gap_analysis as mod


def make_project(tmp_path: Path, stage06_files: list[str] | None = None, with_citations: bool = True) -> Path:
    project = tmp_path / "project"
    brief = project / "00_brief"
    stage06 = project / "06_synthesis"
    evidence_dir = project / "05_evidence_extraction"
    metadata_dir = project / "04_metadata"
    brief.mkdir(parents=True)
    stage06.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    metadata_dir.mkdir(parents=True)
    (brief / "research_brief.md").write_text("Predict RTLE success from academic and pre-board performance.", encoding="utf-8")
    (brief / "research_questions.md").write_text("Which academic variables predict RTLE outcomes?", encoding="utf-8")

    selected = stage06_files if stage06_files is not None else ["synthesis_matrix.csv", "theme_matrix.md", "literature_map.md", "synthesis_notes.md"]
    citation = "Santos2024Predictors" if with_citations else ""
    if "synthesis_matrix.csv" in selected:
        pd.DataFrame(
            [
                {
                    "synthesis_id": "SYN-0001",
                    "theme": "Pre-board performance",
                    "subtheme": "Prediction",
                    "citation_key": citation,
                    "paper_id": "paper-1",
                    "study_design": "Predictive correlational study",
                    "population": "Radiologic technology students",
                    "variables": "Pre-board scores; licensure performance",
                    "key_finding": "Pre-board scores predicted licensure performance.",
                    "evidence_role": "direct_support",
                    "relationship_to_current_study": "Directly relevant.",
                    "strength_of_evidence": "moderate",
                    "limitations_or_cautions": "Associational only.",
                    "use_in_manuscript": "review_of_related_literature",
                    "source_location": "Page 1",
                    "confidence_rating": "High",
                    "notes": "Traceable to Stage 05.",
                }
            ]
        ).to_csv(stage06 / "synthesis_matrix.csv", index=False)
    if "theme_matrix.md" in selected:
        marker = " [@Santos2024Predictors]" if with_citations else ""
        (stage06 / "theme_matrix.md").write_text(f"# Theme Matrix\n\nDirect predictor evidence.{marker}\n", encoding="utf-8")
    if "literature_map.md" in selected:
        (stage06 / "literature_map.md").write_text("# Literature Map\n\nLocal evidence remains limited.\n", encoding="utf-8")
    if "synthesis_notes.md" in selected:
        (stage06 / "synthesis_notes.md").write_text("# Synthesis Notes\n\nProceed to gap analysis.\n", encoding="utf-8")

    pd.DataFrame(
        [
            {
                "paper_id": "paper-1",
                "citation_key": citation,
                "theme": "Pre-board predictors",
                "study_design": "Predictive correlational study",
                "population": "Radiologic technology students",
                "variables": "Pre-board scores; RTLE performance",
                "key_finding": "Pre-board scores predicted licensure performance.",
                "relevance_to_current_study": "Directly relevant.",
                "source_location": "Page 1",
                "confidence_rating": "High",
                "notes": "Local markdown.",
            }
        ]
    ).to_csv(evidence_dir / "evidence_table.csv", index=False)
    pd.DataFrame(
        [{"paper_id": "paper-1", "citation_key": citation, "title": "Predictors", "authors": "Santos", "year": "2024"}]
    ).to_csv(metadata_dir / "metadata_table.csv", index=False)
    return project


def fake_gap_result() -> dict[str, object]:
    return {
        "completion_status": "completed",
        "current_study_focus": "RTLE prediction from academic and pre-board indicators.",
        "what_is_known": ["Pre-board performance appears in supplied synthesis as direct predictor evidence [@Santos2024Predictors]."],
        "what_remains_unknown": ["Whether the relationship holds in the current local setting remains To be confirmed."],
        "population_or_context_gaps": ["Current population fit requires confirmation."],
        "local_or_philippine_gaps": ["Limited local-context evidence was identified in the supplied synthesis."],
        "methodological_gaps": ["Most supplied evidence is associational or predictive, not causal."],
        "variable_or_measurement_gaps": ["Measurement alignment for academic and pre-board variables remains To be confirmed."],
        "evidence_limitations": ["Do not infer causality."],
        "direct_vs_indirect_evidence_balance": "Direct evidence exists but local evidence remains limited.",
        "safe_gap_statement": "The supplied synthesis identifies limited local evidence for RTLE prediction using academic and pre-board indicators.",
        "gap_claims_requiring_caution": ["Do not claim no studies exist."],
        "to_be_confirmed": [],
        "contribution": {
            "proposed_contribution_statement": "The study can contribute local-context evidence.",
            "contribution_types": ["local_context_contribution", "bad_type"],
            "contribution_rationale": "It addresses a local application of predictor evidence.",
            "safe_claims": ["The study can examine associations in the current dataset."],
            "claims_to_avoid": ["It should not claim causal effects."],
            "likely_stakeholders": ["Radiologic technology programs"],
            "manuscript_ready_contribution_statement": "This study may provide local-context evidence for RTLE prediction planning.",
        },
        "problem_statement": {
            "working_problem_statement": "Local RTLE prediction evidence remains limited.",
            "research_problem_context": "Academic and pre-board indicators are relevant in supplied synthesis.",
            "evidence_based_rationale": "The rationale is based on Stage 06 synthesis only.",
            "local_or_institutional_relevance": "To be confirmed.",
            "variables_and_outcome_focus": "Academic performance, pre-board scores, and RTLE outcomes.",
            "research_questions_alignment": "Aligned with supplied research questions.",
            "final_refined_problem_statement_draft": "The current study addresses a local planning problem, not a proven causal mechanism.",
            "assumptions_and_items_to_confirm": ["Institutional setting details are To be confirmed."],
        },
        "gap_rows": [
            {
                "gap_type": "local_philippine_gap",
                "gap_statement": "Limited local-context evidence was identified in the supplied synthesis.",
                "supporting_synthesis_source": "literature_map.md",
                "related_theme": "Pre-board performance",
                "evidence_basis": "Stage 06 synthesis.",
                "strength_of_gap": "moderate",
                "relevance_to_current_study": "Supports problem statement positioning.",
                "caution_level": "moderate",
                "recommended_use": "problem_statement",
                "notes": "Avoid universal novelty claims.",
            },
            {
                "gap_type": "bad_gap",
                "gap_statement": "Unsupported details require confirmation.",
                "supporting_synthesis_source": "To be confirmed.",
                "related_theme": "",
                "evidence_basis": "weak support",
                "strength_of_gap": "excellent",
                "relevance_to_current_study": "",
                "caution_level": "low",
                "recommended_use": "bad_use",
                "notes": "Should be normalized.",
            },
            {
                "gap_type": "methodological_gap",
                "gap_statement": "",
                "supporting_synthesis_source": "synthesis_notes.md",
                "related_theme": "Methods",
                "evidence_basis": "Stage 06 synthesis.",
                "strength_of_gap": "weak",
                "relevance_to_current_study": "To be confirmed.",
                "caution_level": "high",
                "recommended_use": "limitations",
                "notes": "Skip because statement is empty.",
            },
        ],
        "recommended_next_step": "Review Stage 07 outputs before outlining.",
    }


def run_default(project: Path, monkeypatch: pytest.MonkeyPatch, **kwargs):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_gap_analysis", lambda *args, **kwargs: fake_gap_result())
    params = {
        "project_dir": project,
        "model": "gpt-5-mini",
        "dry_run": False,
        "overwrite": False,
        "no_backup": False,
        "strict": False,
        "theme_filters": [],
        "include_weak_evidence": False,
        "max_input_chars": None,
    }
    params.update(kwargs)
    return mod.run_ai_gap_analysis(**params)


def test_dry_run_works_without_openai_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_ai_gap_analysis(
        project_dir=project,
        model="gpt-5-mini",
        dry_run=True,
        overwrite=False,
        no_backup=False,
        strict=False,
        theme_filters=["pre-board"],
        include_weak_evidence=False,
        max_input_chars=None,
    )

    assert result["status"] == "partial"
    assert "Dry run only" in (project / "07_gap_analysis" / "research_gap_analysis.md").read_text(encoding="utf-8")
    assert (project / "logs" / "ai_gap_analysis_log.md").exists()


def test_missing_stage06_files_writes_blocked_gap_analysis_without_ai_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, stage06_files=[])
    monkeypatch.setattr(mod, "call_openai_gap_analysis", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("AI should not be called")))

    result = mod.run_ai_gap_analysis(
        project_dir=project,
        model="gpt-5-mini",
        dry_run=False,
        overwrite=False,
        no_backup=False,
        strict=False,
        theme_filters=[],
        include_weak_evidence=False,
        max_input_chars=None,
    )

    assert result["status"] == "blocked"
    text = (project / "07_gap_analysis" / "research_gap_analysis.md").read_text(encoding="utf-8")
    assert "Stage 06 synthesis must be completed" in text


def test_partial_stage06_inputs_still_run_with_warnings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, stage06_files=["theme_matrix.md"])

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    assert any("Missing or empty Stage 06 input" in warning for warning in result["warnings"])


def test_mocked_ai_response_writes_all_stage07_outputs_plus_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    for path in ["research_gap_analysis.md", "study_contribution.md", "problem_statement_refined.md", "gap_matrix.csv"]:
        assert (project / "07_gap_analysis" / path).exists()
    assert (project / "logs" / "ai_gap_analysis_log.md").exists()


def test_gap_matrix_has_required_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    run_default(project, monkeypatch)
    matrix = pd.read_csv(project / "07_gap_analysis" / "gap_matrix.csv", dtype=str).fillna("")

    assert list(matrix.columns) == GAP_MATRIX_COLUMNS


def test_invalid_enum_values_are_coerced_and_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)
    matrix = pd.read_csv(project / "07_gap_analysis" / "gap_matrix.csv", dtype=str).fillna("")
    invalid_row = matrix[matrix["gap_statement"] == "Unsupported details require confirmation."].iloc[0]

    assert invalid_row["gap_type"] == "to_be_confirmed"
    assert invalid_row["strength_of_gap"] == "to_be_confirmed"
    assert invalid_row["recommended_use"] == "to_be_confirmed"
    assert invalid_row["caution_level"] == "moderate"
    assert any("Invalid gap_type" in warning for warning in result["warnings"])
    assert any("Invalid contribution_type" in warning for warning in result["warnings"])


def test_existing_outputs_not_overwritten_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    out = project / "07_gap_analysis"
    out.mkdir(exist_ok=True)
    (out / "research_gap_analysis.md").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        run_default(project, monkeypatch)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    out = project / "07_gap_analysis"
    out.mkdir(exist_ok=True)
    notes = out / "research_gap_analysis.md"
    notes.write_text("existing", encoding="utf-8")

    result = run_default(project, monkeypatch, overwrite=True)
    assert result["backups"]
    assert result["backups"][0].exists()

    notes.write_text("existing again", encoding="utf-8")
    result_no_backup = run_default(project, monkeypatch, overwrite=True, no_backup=True)
    assert result_no_backup["backups"] == []


def test_output_does_not_include_invented_citation_keys_when_none_supplied(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, with_citations=False)

    run_default(project, monkeypatch)
    text = (project / "07_gap_analysis" / "research_gap_analysis.md").read_text(encoding="utf-8")

    assert "[@Santos2024Predictors]" not in text
    assert "[@ToBeConfirmed]" in text


def test_strict_missing_stage06_raises(tmp_path: Path):
    project = make_project(tmp_path, stage06_files=[])

    with pytest.raises(FileNotFoundError):
        mod.run_ai_gap_analysis(
            project_dir=project,
            model="gpt-5-mini",
            dry_run=False,
            overwrite=False,
            no_backup=False,
            strict=True,
            theme_filters=[],
            include_weak_evidence=False,
            max_input_chars=None,
        )
