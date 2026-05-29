from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.evidence_extraction import ai_extract_evidence as mod


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    brief = project / "00_brief"
    markdown_dir = project / "03_markdown" / "cleaned_md"
    metadata_dir = project / "04_metadata"
    brief.mkdir(parents=True)
    markdown_dir.mkdir(parents=True)
    metadata_dir.mkdir(parents=True)
    (brief / "research_brief.md").write_text("Predicting board exam success from academic records.", encoding="utf-8")
    markdown = markdown_dir / "paper.md"
    markdown.write_text(
        "# Paper\n\n## Page 1\n\nThe study examined mock board scores and licensure examination performance.\n"
        "Regression analysis showed mock board scores predicted board performance.\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "paper_id": "paper",
                "citation_key": "Santos2024Paper",
                "title": "Mock Board Predictors",
                "authors": "Maria Santos; Juan Cruz",
                "year": "2024",
                "journal_or_repository": "Journal of Testing",
                "doi": "10.1234/example",
                "local_markdown_file": str(markdown),
                "metadata_status": "complete",
            }
        ]
    ).to_csv(metadata_dir / "metadata_table.csv", index=False)
    return project


def fake_result() -> dict[str, object]:
    return {
        "row_index": 0,
        "paper_id": "paper",
        "citation_key": "Santos2024Paper",
        "summary": {
            "paper_id": "paper",
            "full_citation": "Santos and Cruz (2024). Mock Board Predictors.",
            "research_purpose": "To examine predictors of licensure performance.",
            "study_design": "Predictive correlational study.",
            "population_sample": "Radiologic technology students.",
            "setting_context": "To be confirmed.",
            "variables": "Mock board scores; licensure examination performance.",
            "instruments_measures": "Mock board examination; licensure exam.",
            "statistical_methods": "Regression analysis.",
            "key_findings": "Mock board scores predicted board performance.",
            "limitations": "To be confirmed.",
            "relevance_to_current_study": "Directly relevant predictor evidence.",
            "useful_concepts_for_introduction": "Academic predictors can inform licensure preparation.",
            "useful_concepts_for_rrl": "Mock board scores as predictor evidence.",
            "useful_concepts_for_discussion": "Compare predictive value with current results.",
            "exact_source_location_if_available": "Page 1.",
            "confidence_rating": "High",
        },
        "evidence_rows": [
            {
                "paper_id": "paper",
                "citation_key": "Santos2024Paper",
                "theme": "Mock board predictors",
                "study_design": "Predictive correlational study",
                "population": "Radiologic technology students",
                "variables": "Mock board scores; licensure examination performance",
                "key_finding": "Mock board scores predicted board performance.",
                "relevance_to_current_study": "Directly relevant.",
                "source_location": "Page 1",
                "confidence_rating": "High",
                "notes": "Extracted from local markdown.",
            }
        ],
        "extraction_issues": [],
    }


def test_build_request_payload_uses_structured_schema_and_guardrails(tmp_path: Path):
    project = make_project(tmp_path)
    metadata, _ = mod.load_metadata(project)
    paper = mod.paper_payload(0, metadata.loc[0], "markdown text")
    payload = mod.build_request_payload("gpt-5-mini", "research context", paper)

    assert payload["model"] == "gpt-5-mini"
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert "Do not use web knowledge" in payload["instructions"]
    encoded = payload["input"][0]["content"][0]["text"]
    assert json.loads(encoded)["paper"]["markdown"] == "markdown text"


def test_dry_run_counts_extractable_markdown(tmp_path: Path):
    project = make_project(tmp_path)

    result = mod.run_evidence_extraction(
        project_dir=project,
        model="gpt-5-mini",
        limit=None,
        offset=0,
        max_md_chars=1000,
        dry_run=True,
        overwrite=False,
    )

    assert result["selected"] == 1
    assert result["processed"] == 0
    assert not (project / "05_evidence_extraction").exists()


def test_run_evidence_extraction_writes_summary_table_and_log(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    monkeypatch.setattr(mod, "get_api_key", lambda dotenv_path=None: "test-key")
    monkeypatch.setattr(mod, "call_openai_evidence_extraction", lambda api_key, model, research_context, paper: fake_result())

    result = mod.run_evidence_extraction(
        project_dir=project,
        model="gpt-5-mini",
        limit=1,
        offset=0,
        max_md_chars=1000,
        dry_run=False,
        overwrite=False,
    )

    assert result["processed"] == 1
    assert result["evidence_rows"] == 1
    evidence = pd.read_csv(project / "05_evidence_extraction" / "evidence_table.csv", dtype=str).fillna("")
    assert list(evidence.columns) == mod.EVIDENCE_COLUMNS
    assert evidence.loc[0, "theme"] == "Mock board predictors"
    summaries = list((project / "05_evidence_extraction" / "paper_summaries").glob("*.md"))
    assert len(summaries) == 1
    assert "## Key Findings" in summaries[0].read_text(encoding="utf-8")
    assert (project / "05_evidence_extraction" / "extraction_log.md").exists()


def test_prefers_ai_checked_metadata_when_available(tmp_path: Path):
    project = make_project(tmp_path)
    checked = project / "04_metadata" / "metadata_table_ai_checked.csv"
    metadata = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    metadata.loc[0, "citation_key"] = "Checked2024Paper"
    metadata.to_csv(checked, index=False)

    loaded, source = mod.load_metadata(project)

    assert source == checked
    assert loaded.loc[0, "citation_key"] == "Checked2024Paper"
