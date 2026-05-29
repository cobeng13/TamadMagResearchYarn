from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.ai.schemas import SYNTHESIS_MATRIX_COLUMNS
from scripts.synthesis import ai_build_synthesis as mod


def make_project(tmp_path: Path, with_evidence: bool = True, with_summaries: bool = True) -> Path:
    project = tmp_path / "project"
    brief = project / "00_brief"
    evidence_dir = project / "05_evidence_extraction"
    metadata_dir = project / "04_metadata"
    brief.mkdir(parents=True)
    evidence_dir.mkdir(parents=True)
    metadata_dir.mkdir(parents=True)
    (brief / "research_brief.md").write_text("Predict RTLE success from academic and pre-board performance.", encoding="utf-8")
    (brief / "research_questions.md").write_text("Which academic variables predict board examination performance?", encoding="utf-8")
    if with_evidence:
        pd.DataFrame(
            [
                {
                    "paper_id": "paper-1",
                    "citation_key": "Santos2024Predictors",
                    "theme": "Pre-board predictors",
                    "study_design": "Predictive correlational study",
                    "population": "Radiologic technology students",
                    "variables": "Pre-board scores; licensure performance",
                    "key_finding": "Pre-board scores predicted licensure performance.",
                    "relevance_to_current_study": "Directly relevant predictor evidence.",
                    "source_location": "Page 1",
                    "confidence_rating": "High",
                    "notes": "Extracted from local markdown.",
                }
            ]
        ).to_csv(evidence_dir / "evidence_table.csv", index=False)
    if with_summaries:
        summaries = evidence_dir / "paper_summaries"
        summaries.mkdir(parents=True)
        (summaries / "paper-1.md").write_text("# Paper Summary: paper-1\n\n## Key Findings\nPre-board scores predicted licensure performance.\n", encoding="utf-8")
    pd.DataFrame(
        [{"paper_id": "paper-1", "citation_key": "Santos2024Predictors", "title": "Predictors", "authors": "Santos", "year": "2024"}]
    ).to_csv(metadata_dir / "metadata_table.csv", index=False)
    return project


def fake_synthesis_result() -> dict[str, object]:
    return {
        "completion_status": "completed",
        "themes": [
            {
                "theme": "Pre-board performance",
                "subthemes": ["Prediction"],
                "summary": "Pre-board performance appears as direct predictor evidence [@Santos2024Predictors].",
                "direct_evidence": ["Santos2024Predictors links pre-board scores to licensure performance."],
                "indirect_evidence": [],
                "mixed_or_conflicting_findings": [],
                "methodological_notes": ["Predictive correlational design."],
                "limitations_or_cautions": ["Do not infer causality."],
                "use_in_manuscript": ["review_of_related_literature"],
            }
        ],
        "synthesis_rows": [
            {
                "theme": "Pre-board performance",
                "subtheme": "Prediction",
                "citation_key": "Santos2024Predictors",
                "paper_id": "paper-1",
                "study_design": "Predictive correlational study",
                "population": "Radiologic technology students",
                "variables": "Pre-board scores; licensure performance",
                "key_finding": "Pre-board scores predicted licensure performance.",
                "evidence_role": "direct_support",
                "relationship_to_current_study": "Directly relevant to board exam prediction.",
                "strength_of_evidence": "moderate",
                "limitations_or_cautions": "Predictive association only.",
                "use_in_manuscript": "review_of_related_literature",
                "source_location": "Page 1",
                "confidence_rating": "High",
                "notes": "Traceable to Stage 05.",
            },
            {
                "theme": "Invalid row",
                "subtheme": "",
                "citation_key": "Invented2026",
                "paper_id": "invented-paper",
                "study_design": "To be confirmed.",
                "population": "To be confirmed.",
                "variables": "To be confirmed.",
                "key_finding": "To be confirmed.",
                "evidence_role": "bad_role",
                "relationship_to_current_study": "To be confirmed.",
                "strength_of_evidence": "excellent",
                "limitations_or_cautions": "To be confirmed.",
                "use_in_manuscript": "bad_use",
                "source_location": "To be confirmed.",
                "confidence_rating": "To be confirmed.",
                "notes": "Should be normalized.",
            },
        ],
        "literature_map": {
            "current_study_focus": "RTLE prediction.",
            "evidence_clusters": ["Pre-board prediction"],
            "directly_relevant_studies": ["Santos2024Predictors"],
            "adjacent_evidence": [],
            "methodological_evidence": ["Predictive correlational designs"],
            "gaps_identified": ["Local evidence remains limited."],
            "contradictions_or_mixed_findings": [],
            "next_stage_support": "Use for gap analysis, not manuscript prose.",
        },
        "claims_safe_to_use_later": ["Pre-board performance can be discussed as predictor evidence."],
        "claims_requiring_caution": ["Do not make causal claims."],
        "missing_evidence": [],
        "recommended_next_step": "Proceed to gap analysis.",
    }


def run_default(project: Path, monkeypatch: pytest.MonkeyPatch, **kwargs):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_synthesis", lambda *args, **kwargs: fake_synthesis_result())
    params = {
        "project_dir": project,
        "model": "gpt-5-mini",
        "dry_run": False,
        "overwrite": False,
        "no_backup": False,
        "limit": None,
        "batch_size": 20,
        "theme_hints": [],
        "include_background": False,
        "min_confidence": None,
        "strict": False,
    }
    params.update(kwargs)
    return mod.run_ai_synthesis(**params)


def test_dry_run_works_without_openai_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_ai_synthesis(
        project_dir=project,
        model="gpt-5-mini",
        dry_run=True,
        overwrite=False,
        no_backup=False,
        limit=None,
        batch_size=20,
        theme_hints=["pre-board"],
        include_background=False,
        min_confidence=None,
        strict=False,
    )

    assert result["status"] == "partial"
    notes = project / "06_synthesis" / "synthesis_notes.md"
    assert notes.exists()
    assert "Dry-run" in (project / "06_synthesis" / "theme_matrix.md").read_text(encoding="utf-8")


def test_missing_evidence_table_writes_blocked_notes_without_ai_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, with_evidence=False)
    monkeypatch.setattr(mod, "call_openai_synthesis", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("AI should not be called")))

    result = mod.run_ai_synthesis(
        project_dir=project,
        model="gpt-5-mini",
        dry_run=False,
        overwrite=False,
        no_backup=False,
        limit=None,
        batch_size=20,
        theme_hints=[],
        include_background=False,
        min_confidence=None,
        strict=False,
    )

    assert result["status"] == "blocked"
    assert "Stage 05 evidence extraction must be completed first" in (project / "06_synthesis" / "synthesis_notes.md").read_text(encoding="utf-8")


def test_evidence_table_only_runs_with_warning(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path, with_summaries=False)

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    assert any("Missing paper_summaries folder" in warning for warning in result["warnings"])


def test_mocked_ai_response_writes_all_outputs_and_required_columns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)

    assert result["rows_written"] == 2
    for path in ["synthesis_matrix.csv", "theme_matrix.md", "literature_map.md", "synthesis_notes.md"]:
        assert (project / "06_synthesis" / path).exists()
    assert (project / "logs" / "ai_synthesis_log.md").exists()
    matrix = pd.read_csv(project / "06_synthesis" / "synthesis_matrix.csv", dtype=str).fillna("")
    assert list(matrix.columns) == SYNTHESIS_MATRIX_COLUMNS


def test_invalid_enums_are_coerced_and_logged(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    result = run_default(project, monkeypatch)
    matrix = pd.read_csv(project / "06_synthesis" / "synthesis_matrix.csv", dtype=str).fillna("")
    invalid_row = matrix[matrix["theme"] == "Invalid row"].iloc[0]

    assert invalid_row["evidence_role"] == "to_be_confirmed"
    assert invalid_row["strength_of_evidence"] == "to_be_confirmed"
    assert invalid_row["use_in_manuscript"] == "to_be_confirmed"
    assert any("Invalid evidence_role" in warning for warning in result["warnings"])


def test_existing_outputs_not_overwritten_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    out = project / "06_synthesis"
    out.mkdir()
    (out / "synthesis_notes.md").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        run_default(project, monkeypatch)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    out = project / "06_synthesis"
    out.mkdir()
    notes = out / "synthesis_notes.md"
    notes.write_text("existing", encoding="utf-8")

    result = run_default(project, monkeypatch, overwrite=True)
    assert result["backups"]
    assert result["backups"][0].exists()

    notes.write_text("existing again", encoding="utf-8")
    result_no_backup = run_default(project, monkeypatch, overwrite=True, no_backup=True)
    assert result_no_backup["backups"] == []


def test_citation_keys_are_from_inputs_or_to_be_confirmed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)

    run_default(project, monkeypatch)
    matrix = pd.read_csv(project / "06_synthesis" / "synthesis_matrix.csv", dtype=str).fillna("")

    assert set(matrix["citation_key"]) <= {"Santos2024Predictors", "To be confirmed."}
    assert "To be confirmed." in set(matrix["citation_key"])


def test_strict_missing_evidence_raises(tmp_path: Path):
    project = make_project(tmp_path, with_evidence=False)

    with pytest.raises(FileNotFoundError):
        mod.run_ai_synthesis(
            project_dir=project,
            model="gpt-5-mini",
            dry_run=False,
            overwrite=False,
            no_backup=False,
            limit=None,
            batch_size=20,
            theme_hints=[],
            include_background=False,
            min_confidence=None,
            strict=True,
        )
