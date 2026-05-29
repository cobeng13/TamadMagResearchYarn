from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.citation_metadata.ai_check_metadata import (
    apply_checked_records,
    build_request_payload,
    run_ai_metadata_check,
    write_checked_outputs,
)
from scripts.citation_metadata.extract_metadata import METADATA_COLUMNS, TO_CONFIRM


def metadata_row(project: Path) -> dict[str, str]:
    markdown = project / "03_markdown" / "cleaned_md" / "paper.md"
    markdown.parent.mkdir(parents=True)
    markdown.write_text(
        "# Paper\n\nJournal of Evidence\n\nMaria Santos and Juan Cruz\n\nVolume 7 Issue 1 pp. 10-22\n",
        encoding="utf-8",
    )
    return {
        "paper_id": "paper",
        "citation_key": "UnknownYearToConfirmPaper",
        "title": "Paper",
        "authors": TO_CONFIRM,
        "year": TO_CONFIRM,
        "source_type": "journal_article",
        "journal_or_repository": TO_CONFIRM,
        "volume": TO_CONFIRM,
        "issue": TO_CONFIRM,
        "pages": TO_CONFIRM,
        "doi": TO_CONFIRM,
        "url": TO_CONFIRM,
        "publisher": TO_CONFIRM,
        "country_or_context": TO_CONFIRM,
        "local_source_file": str(project / "02_sources" / "pdf" / "paper.pdf"),
        "local_markdown_file": str(markdown),
        "metadata_status": "needs_review",
        "notes": "Python first pass.",
    }


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    metadata = project / "04_metadata"
    metadata.mkdir(parents=True)
    pd.DataFrame([metadata_row(project)], columns=METADATA_COLUMNS).to_csv(metadata / "metadata_table.csv", index=False)
    return project


def test_build_request_payload_uses_local_evidence_guardrails(tmp_path: Path):
    project = make_project(tmp_path)
    row = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("").loc[0]
    payload = build_request_payload(
        "gpt-5-nano",
        [{"row_index": 0, "current_metadata": row.to_dict(), "markdown": "Local markdown"}],
    )

    assert payload["model"] == "gpt-5-nano"
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["strict"] is True
    assert "Do not use outside knowledge" in payload["instructions"]
    encoded = payload["input"][0]["content"][0]["text"]
    assert json.loads(encoded)["records"][0]["markdown"] == "Local markdown"


def test_apply_checked_records_updates_metadata_and_audit_only_for_matching_rows(tmp_path: Path):
    project = make_project(tmp_path)
    df = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")

    revised, review, updated = apply_checked_records(
        df,
        [
            {
                "row_index": 0,
                "paper_id": "paper",
                "citation_key": "Santos2024Paper",
                "title": "Paper",
                "authors": "Maria Santos; Juan Cruz",
                "year": "2024",
                "source_type": "journal_article",
                "journal_or_repository": "Journal of Evidence",
                "volume": "7",
                "issue": "1",
                "pages": "10-22",
                "doi": TO_CONFIRM,
                "url": TO_CONFIRM,
                "publisher": TO_CONFIRM,
                "country_or_context": TO_CONFIRM,
                "local_source_file": "changed.pdf",
                "local_markdown_file": "changed.md",
                "metadata_status": "needs_review",
                "notes": "Publisher unresolved.",
                "ai_metadata_status": "needs_review",
                "ai_change_summary": "Filled authors and journal.",
                "ai_evidence_snippets": ["Maria Santos and Juan Cruz", "Journal of Evidence"],
                "ai_unresolved_fields": ["publisher"],
            }
        ],
        model="gpt-5-nano",
        checked_at="2026-05-29 09:00:00",
    )

    assert updated == 1
    assert revised.loc[0, "authors"] == "Maria Santos; Juan Cruz"
    assert revised.loc[0, "journal_or_repository"] == "Journal of Evidence"
    assert revised.loc[0, "local_markdown_file"] == df.loc[0, "local_markdown_file"]
    assert review.loc[0, "ai_change_summary"] == "Filled authors and journal."
    assert "Journal of Evidence" in review.loc[0, "ai_evidence_snippets"]


def test_write_checked_outputs_writes_revised_metadata_and_reference_files(tmp_path: Path):
    project = make_project(tmp_path)
    df = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    df.loc[0, "authors"] = "Maria Santos; Juan Cruz"
    df.loc[0, "year"] = "2024"
    df.loc[0, "journal_or_repository"] = "Journal of Evidence"
    review = pd.DataFrame(
        [
            {
                "paper_id": "paper",
                "citation_key": "Santos2024Paper",
                "row_index": "0",
                "ai_metadata_status": "needs_review",
                "ai_change_summary": "Checked.",
                "ai_evidence_snippets": "Journal of Evidence",
                "ai_unresolved_fields": "publisher",
                "ai_checked_at": "2026-05-29",
                "ai_model": "gpt-5-nano",
            }
        ]
    )

    paths = write_checked_outputs(project, df, review)

    assert paths["checked_metadata"].exists()
    assert paths["review"].exists()
    assert paths["apa"].exists()
    checked = pd.read_csv(paths["checked_metadata"], dtype=str).fillna("")
    assert checked.loc[0, "citation_key"].startswith("Santos2024")
    assert "Santos" in paths["apa"].read_text(encoding="utf-8")


def test_dry_run_counts_rows_without_api_call(tmp_path: Path):
    project = make_project(tmp_path)

    result = run_ai_metadata_check(
        project_dir=project,
        model="gpt-5-nano",
        batch_size=1,
        limit=None,
        offset=0,
        max_md_chars=1000,
        dry_run=True,
        apply=False,
    )

    assert result["selected"] == 1
    assert result["updated"] == 0
    assert not (project / "04_metadata" / "metadata_table_ai_checked.csv").exists()
