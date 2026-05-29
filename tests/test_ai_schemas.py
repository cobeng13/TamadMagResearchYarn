from __future__ import annotations

from scripts.ai.schemas import (
    EVIDENCE_COLUMNS,
    GAP_MATRIX_COLUMNS,
    OUTLINE_MAP_COLUMNS,
    PROJECT_CONTEXT_CHANGE_COLUMNS,
    RESULTS_BY_OBJECTIVE_COLUMNS,
    SCREENING_ACTIONS,
    SCREENING_LABELS,
    STATISTICAL_FINDINGS_COLUMNS,
    SYNTHESIS_MATRIX_COLUMNS,
    candidate_screening_schema,
    evidence_extraction_schema,
    gap_analysis_schema,
    outline_schema,
    project_context_update_schema,
    results_interpretation_schema,
    synthesis_schema,
)


def test_screening_schema_uses_expected_labels_and_actions():
    schema = candidate_screening_schema()
    item = schema["properties"]["screenings"]["items"]

    assert item["properties"]["ai_relevance_label"]["enum"] == SCREENING_LABELS
    assert item["properties"]["ai_suggested_action"]["enum"] == SCREENING_ACTIONS
    assert "screen_full_text" in SCREENING_ACTIONS


def test_evidence_schema_preserves_table_columns():
    schema = evidence_extraction_schema()
    evidence_item = schema["properties"]["evidence_rows"]["items"]

    assert evidence_item["required"] == EVIDENCE_COLUMNS
    assert EVIDENCE_COLUMNS == [
        "paper_id",
        "citation_key",
        "theme",
        "study_design",
        "population",
        "variables",
        "key_finding",
        "relevance_to_current_study",
        "source_location",
        "confidence_rating",
        "notes",
    ]


def test_synthesis_schema_preserves_matrix_columns():
    schema = synthesis_schema()
    row = schema["properties"]["synthesis_rows"]["items"]

    assert ["synthesis_id", *row["required"]] == SYNTHESIS_MATRIX_COLUMNS
    assert "themes" in schema["properties"]


def test_gap_schema_preserves_gap_matrix_columns():
    schema = gap_analysis_schema()
    row = schema["properties"]["gap_rows"]["items"]

    assert ["gap_id", *row["required"]] == GAP_MATRIX_COLUMNS
    assert "contribution" in schema["properties"]


def test_project_context_schema_preserves_change_columns():
    schema = project_context_update_schema()
    row = schema["properties"]["change_rows"]["items"]

    assert ["change_id", *row["required"]] == PROJECT_CONTEXT_CHANGE_COLUMNS
    assert "outline_context" in schema["properties"]


def test_outline_schema_preserves_map_columns():
    schema = outline_schema()
    row = schema["properties"]["outline_map_rows"]["items"]

    assert ["outline_id", *row["required"]] == OUTLINE_MAP_COLUMNS
    assert "results_outline" in schema["properties"]


def test_results_interpretation_schema_preserves_result_columns():
    schema = results_interpretation_schema()
    objective_row = schema["properties"]["findings_by_objective"]["items"]
    finding_row = schema["properties"]["statistical_findings"]["items"]

    assert [
        "objective_id",
        "objective_text",
        "result_available",
        "source_file",
        "statistical_test_or_model",
        "key_numerical_result",
        "p_value_or_ci",
        "significance_status",
        "direction_or_relationship",
        "result_readiness",
        "missing_items",
        "notes",
    ] == RESULTS_BY_OBJECTIVE_COLUMNS
    assert ["finding_id", *finding_row["required"]] == STATISTICAL_FINDINGS_COLUMNS
    assert "recommended_tables" in schema["properties"]
    assert "significance_status" in objective_row["properties"]
