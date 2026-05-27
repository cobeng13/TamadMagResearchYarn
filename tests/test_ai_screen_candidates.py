from __future__ import annotations

import json

import pandas as pd

from scripts.paper_discovery.ai_screen_candidates import (
    apply_screenings,
    build_request_payload,
    ensure_ai_columns,
    extract_output_text,
    rows_to_screen,
)


def test_rows_to_screen_skips_human_reviewed_and_existing_ai_rows():
    df = ensure_ai_columns(
        pd.DataFrame(
            [
                {"title": "A", "abstract": "licensure", "screening_status": "unscreened"},
                {"title": "B", "abstract": "licensure", "screening_status": "included", "human_decision": "include"},
                {"title": "C", "abstract": "licensure", "screening_status": "unscreened", "ai_screened_at": "done"},
                {"title": "", "abstract": "", "screening_status": "unscreened"},
            ]
        )
    )
    assert rows_to_screen(df) == [0]
    assert rows_to_screen(df, force=True, include_human_reviewed=True) == [0, 1, 2]


def test_apply_screenings_writes_ai_columns_only():
    df = ensure_ai_columns(
        pd.DataFrame(
            [
                {
                    "candidate_id": "doi:1",
                    "title": "Relevant",
                    "screening_status": "included",
                    "human_decision": "include",
                    "human_notes": "Keep this.",
                }
            ]
        )
    )
    updated = apply_screenings(
        df,
        [
            {
                "row_index": 0,
                "candidate_id": "doi:1",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": 0.92,
                "ai_reason": "Directly about licensure predictors.",
                "ai_suggested_action": "screen_full_text",
                "ai_key_terms": ["licensure", "academic performance"],
                "ai_metadata_warnings": "",
            }
        ],
        model="gpt-5-nano",
        screened_at="2026-05-27 10:00:00",
    )
    assert updated == 1
    assert df.loc[0, "screening_status"] == "included"
    assert df.loc[0, "human_decision"] == "include"
    assert df.loc[0, "human_notes"] == "Keep this."
    assert df.loc[0, "ai_relevance_label"] == "highly_relevant"
    assert df.loc[0, "ai_suggested_action"] == "screen_full_text"
    assert df.loc[0, "ai_model"] == "gpt-5-nano"


def test_build_request_payload_uses_structured_output_schema():
    payload = build_request_payload(
        "gpt-5-nano",
        "Research brief",
        [{"row_index": 0, "candidate_id": "x", "title": "Paper", "abstract": "Abstract"}],
    )
    assert payload["model"] == "gpt-5-nano"
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert "screenings" in payload["text"]["format"]["schema"]["properties"]


def test_extract_output_text_from_responses_shape():
    expected = {"screenings": [{"row_index": 0}]}
    response_json = {"output": [{"content": [{"type": "output_text", "text": json.dumps(expected)}]}]}
    assert json.loads(extract_output_text(response_json)) == expected

