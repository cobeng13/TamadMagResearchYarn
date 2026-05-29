from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.paper_discovery.build_download_queue_from_ai import build_download_queue


def make_project(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    source_dir = project / "01_literature_search"
    source_dir.mkdir(parents=True)
    csv_path = source_dir / "candidate_papers.csv"
    pd.DataFrame(
        [
            {
                "candidate_id": "c1",
                "title": "High PDF",
                "authors": "A",
                "year": "2024",
                "doi": "10.1/high",
                "url": "https://example.test/high",
                "pdf_url": "https://example.test/high.pdf",
                "journal_or_repository": "Journal",
                "source_providers": "openalex",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.95",
                "ai_reason": "Direct",
                "ai_suggested_action": "screen_full_text",
                "ai_key_terms": "licensure",
                "ai_metadata_warnings": "",
                "access_type": "gold",
                "oa_status": "gold",
                "license": "cc-by",
            },
            {
                "candidate_id": "c2",
                "title": "Possible PDF",
                "authors": "B",
                "year": "2023",
                "doi": "10.1/possible",
                "url": "",
                "pdf_url": "https://example.test/possible.pdf",
                "journal_or_repository": "Repo",
                "source_providers": "semantic_scholar",
                "ai_relevance_label": "possibly_relevant",
                "ai_confidence": "0.80",
                "ai_reason": "Indirect",
                "ai_suggested_action": "screen_full_text",
                "ai_key_terms": "predictors",
                "ai_metadata_warnings": "",
                "access_type": "green",
                "oa_status": "green",
                "license": "",
            },
            {
                "candidate_id": "c3",
                "title": "Background PDF",
                "authors": "C",
                "year": "2022",
                "doi": "10.1/background",
                "url": "",
                "pdf_url": "https://example.test/background.pdf",
                "journal_or_repository": "Repo",
                "source_providers": "core",
                "ai_relevance_label": "background_only",
                "ai_confidence": "0.70",
                "ai_reason": "Context",
                "ai_suggested_action": "keep_for_background",
                "ai_key_terms": "education",
                "ai_metadata_warnings": "",
            },
            {
                "candidate_id": "c4",
                "title": "Out",
                "doi": "10.1/out",
                "pdf_url": "https://example.test/out.pdf",
                "ai_relevance_label": "out_of_scope",
                "ai_confidence": "0.99",
                "ai_suggested_action": "exclude_after_human_review",
            },
            {
                "candidate_id": "c5",
                "title": "Insufficient",
                "doi": "10.1/insufficient",
                "pdf_url": "https://example.test/insufficient.pdf",
                "ai_relevance_label": "insufficient_metadata",
                "ai_confidence": "0.30",
                "ai_suggested_action": "needs_metadata_check",
            },
            {
                "candidate_id": "c6",
                "title": "No Locator",
                "doi": "",
                "pdf_url": "",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.90",
                "ai_suggested_action": "screen_full_text",
            },
            {
                "candidate_id": "c7",
                "title": "DOI Only",
                "doi": "10.1/doi-only",
                "pdf_url": "",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.90",
                "ai_suggested_action": "screen_full_text",
            },
            {
                "candidate_id": "c8",
                "title": "Low Confidence",
                "doi": "10.1/low",
                "pdf_url": "https://example.test/low.pdf",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.40",
                "ai_suggested_action": "screen_full_text",
            },
            {
                "candidate_id": "c9",
                "title": "Wrong Action",
                "doi": "10.1/action",
                "pdf_url": "https://example.test/action.pdf",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.92",
                "ai_suggested_action": "keep_for_background",
            },
        ]
    ).to_csv(csv_path, index=False)
    return project, csv_path


def test_filters_highly_relevant_only(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, overwrite=True)
    assert result["queue"]["candidate_id"].tolist() == ["c1", "c8"]
    assert set(result["excluded"]["download_reason"]) >= {
        "skipped_tag_not_selected",
        "skipped_no_doi_or_pdf_url",
        "needs_oa_lookup",
        "skipped_action_not_selected",
    }


def test_filters_highly_and_possibly_relevant(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, tags=["highly_relevant", "possibly_relevant"], overwrite=True)
    assert result["queue"]["candidate_id"].tolist() == ["c1", "c2", "c8"]


def test_filters_all_three_review_tags_with_actions(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(
        project,
        tags=["highly_relevant", "possibly_relevant", "background_only"],
        actions=["screen_full_text", "keep_for_background"],
        overwrite=True,
    )
    assert result["queue"]["candidate_id"].tolist() == ["c1", "c2", "c3", "c8", "c9"]


def test_excludes_out_of_scope_and_insufficient_metadata_by_default(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, overwrite=True)
    assert "c4" not in result["queue"]["candidate_id"].tolist()
    assert "c5" not in result["queue"]["candidate_id"].tolist()


def test_honors_min_confidence(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, min_confidence=0.70, overwrite=True)
    assert result["queue"]["candidate_id"].tolist() == ["c1"]
    low = result["excluded"][result["excluded"]["candidate_id"] == "c8"].iloc[0]
    assert low["download_reason"] == "skipped_low_confidence"


def test_honors_ai_suggested_action(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, actions=["keep_for_background"], overwrite=True)
    assert result["queue"]["candidate_id"].tolist() == ["c9"]
    skipped = result["excluded"][result["excluded"]["candidate_id"] == "c1"].iloc[0]
    assert skipped["download_reason"] == "skipped_action_not_selected"


def test_handles_missing_doi_and_pdf_url_safely(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, overwrite=True)
    no_locator = result["excluded"][result["excluded"]["candidate_id"] == "c6"].iloc[0]
    doi_only = result["excluded"][result["excluded"]["candidate_id"] == "c7"].iloc[0]
    assert no_locator["download_reason"] == "skipped_no_doi_or_pdf_url"
    assert doi_only["download_reason"] == "needs_oa_lookup"


def test_writes_tag_specific_files_and_excluded(tmp_path: Path):
    project, _ = make_project(tmp_path)
    build_download_queue(
        project,
        tags=["highly_relevant", "possibly_relevant", "background_only"],
        actions=["screen_full_text", "keep_for_background"],
        overwrite=True,
    )
    by_tag = project / "02_sources" / "download_queue_by_tag"
    assert (by_tag / "highly_relevant.csv").exists()
    assert (by_tag / "possibly_relevant.csv").exists()
    assert (by_tag / "background_only.csv").exists()
    assert (project / "02_sources" / "download_queue_excluded.csv").exists()


def test_does_not_overwrite_existing_queue_without_flag(tmp_path: Path):
    project, _ = make_project(tmp_path)
    queue_path = project / "02_sources" / "download_queue.csv"
    queue_path.parent.mkdir(parents=True)
    queue_path.write_text("existing\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        build_download_queue(project)
    assert queue_path.read_text(encoding="utf-8") == "existing\n"


def test_dry_run_writes_no_files(tmp_path: Path):
    project, _ = make_project(tmp_path)
    result = build_download_queue(project, dry_run=True)
    assert result["queued_count"] == 2
    assert not (project / "02_sources").exists()


def test_does_not_modify_candidate_papers(tmp_path: Path):
    project, csv_path = make_project(tmp_path)
    before = csv_path.read_bytes()
    build_download_queue(project, overwrite=True)
    assert csv_path.read_bytes() == before


def test_does_not_require_openai_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project, _ = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = build_download_queue(project, overwrite=True)
    assert result["queued_count"] == 2


def test_unpaywall_404_excludes_without_crashing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project, _ = make_project(tmp_path)

    class Response:
        status_code = 404

        def raise_for_status(self):
            raise AssertionError("404 should be handled before raise_for_status")

    monkeypatch.setenv("UNPAYWALL_EMAIL", "secret@example.test")
    monkeypatch.setattr("scripts.paper_discovery.build_download_queue_from_ai.requests.get", lambda *args, **kwargs: Response())
    result = build_download_queue(project, overwrite=True, use_unpaywall=True)
    doi_only = result["excluded"][result["excluded"]["candidate_id"] == "c7"].iloc[0]
    assert doi_only["download_reason"] == "no_legal_oa_pdf_found"
