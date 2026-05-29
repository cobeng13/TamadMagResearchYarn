from __future__ import annotations

from scripts.ai.schemas import (
    EVIDENCE_COLUMNS,
    SCREENING_ACTIONS,
    SCREENING_LABELS,
    candidate_screening_schema,
    evidence_extraction_schema,
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
