from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.citation_metadata.extract_metadata import extract_metadata


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    cleaned = project / "03_markdown" / "cleaned_md"
    pdf = project / "02_sources" / "pdf"
    lit = project / "01_literature_search"
    cleaned.mkdir(parents=True)
    pdf.mkdir(parents=True)
    lit.mkdir(parents=True)
    (pdf / "paper.pdf").write_bytes(b"%PDF")
    (cleaned / "paper.md").write_text(
        "# Local PDF\n\n## Page 1\n\nDeterministic Citation Paper\n\nDOI: 10.1234/example.2024\n"
        "Published in the Philippines. Vol. 5 No. 2 pp. 10-20\n",
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "paper_id": "paper",
                "source_file": str(pdf / "paper.pdf"),
                "output_raw_md": str(project / "03_markdown" / "raw_md" / "paper.md"),
                "output_cleaned_md": str(cleaned / "paper.md"),
                "conversion_status": "converted",
                "quality_notes": "",
                "needs_manual_review": "no",
            }
        ]
    ).to_csv(project / "03_markdown" / "ingestion_manifest.csv", index=False)
    pd.DataFrame(
        [
            {
                "candidate_id": "doi:10.1234/example.2024",
                "title": "Deterministic Citation Paper",
                "authors": "Maria Santos; Juan Cruz",
                "year": "2024",
                "journal_or_repository": "Journal of Testing",
                "publisher": "Testing Publisher",
                "source_type": "journal_article",
                "doi": "10.1234/example.2024",
                "url": "https://doi.org/10.1234/example.2024",
            }
        ]
    ).to_csv(lit / "candidate_papers.csv", index=False)
    return project


def test_extracts_metadata_and_writes_required_outputs(tmp_path: Path):
    project = make_project(tmp_path)
    result = extract_metadata(project)

    assert result["records"] == 1
    metadata_path = project / "04_metadata" / "metadata_table.csv"
    key_map_path = project / "04_metadata" / "citation_key_map.csv"
    apa_path = project / "04_metadata" / "references_apa7.md"
    bib_path = project / "04_metadata" / "references.bib"
    issues_path = project / "04_metadata" / "metadata_issues.md"
    for path in [metadata_path, key_map_path, apa_path, bib_path, issues_path]:
        assert path.exists()
    metadata = pd.read_csv(metadata_path, dtype=str).fillna("")
    assert metadata.loc[0, "title"] == "Deterministic Citation Paper"
    assert metadata.loc[0, "doi"] == "10.1234/example.2024"
    assert metadata.loc[0, "citation_key"].startswith("Santos2024")
    assert "Santos" in apa_path.read_text(encoding="utf-8")
    assert "@article" in bib_path.read_text(encoding="utf-8")


def test_doi_scan_fallback_when_candidate_missing(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "01_literature_search" / "candidate_papers.csv").unlink()

    result = extract_metadata(project)

    assert result["needs_review"] == 1
    metadata = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    assert metadata.loc[0, "doi"] == "10.1234/example.2024"
    assert metadata.loc[0, "metadata_status"] == "needs_review"


def test_refuses_overwrite_without_flag(tmp_path: Path):
    project = make_project(tmp_path)
    output = project / "04_metadata"
    output.mkdir()
    (output / "metadata_table.csv").write_text("existing\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        extract_metadata(project)
    assert (output / "metadata_table.csv").read_text(encoding="utf-8") == "existing\n"


def test_dry_run_writes_no_outputs(tmp_path: Path):
    project = make_project(tmp_path)
    result = extract_metadata(project, dry_run=True)
    assert result["records"] == 1
    assert not (project / "04_metadata").exists()


def test_unknown_author_uses_unknown_in_citation_key(tmp_path: Path):
    project = make_project(tmp_path)
    candidates = pd.read_csv(project / "01_literature_search" / "candidate_papers.csv", dtype=str).fillna("")
    candidates.loc[0, "authors"] = ""
    candidates.to_csv(project / "01_literature_search" / "candidate_papers.csv", index=False)

    extract_metadata(project)

    metadata = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    assert metadata.loc[0, "citation_key"].startswith("Unknown2024")


def test_matches_manual_filename_to_candidate_title(tmp_path: Path):
    project = make_project(tmp_path)
    source = project / "02_sources" / "pdf" / "paper.pdf"
    manual_source = project / "02_sources" / "pdf" / "Deterministic Citation.pdf"
    source.rename(manual_source)
    manifest = pd.read_csv(project / "03_markdown" / "ingestion_manifest.csv", dtype=str).fillna("")
    manifest.loc[0, "source_file"] = str(manual_source)
    manifest.to_csv(project / "03_markdown" / "ingestion_manifest.csv", index=False)

    extract_metadata(project)

    metadata = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    assert metadata.loc[0, "paper_id"] == "doi:10.1234/example.2024"
    assert metadata.loc[0, "authors"] == "Maria Santos; Juan Cruz"


def test_filename_heading_is_not_used_as_title_without_metadata(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "01_literature_search" / "candidate_papers.csv").unlink()
    (project / "03_markdown" / "cleaned_md" / "paper.md").write_text(
        "# paper\n\n## Page 1\n\nActual Extracted Article Title\n\nDOI: 10.1234/example.2024\n",
        encoding="utf-8",
    )

    extract_metadata(project)

    metadata = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    assert metadata.loc[0, "title"] == "Actual Extracted Article Title"


def test_does_not_match_generic_two_token_filename(tmp_path: Path):
    project = make_project(tmp_path)
    source = project / "02_sources" / "pdf" / "paper.pdf"
    generic_source = project / "02_sources" / "pdf" / "Radiologic Technology.pdf"
    source.rename(generic_source)
    manifest = pd.read_csv(project / "03_markdown" / "ingestion_manifest.csv", dtype=str).fillna("")
    manifest.loc[0, "source_file"] = str(generic_source)
    manifest.to_csv(project / "03_markdown" / "ingestion_manifest.csv", index=False)
    candidates = pd.read_csv(project / "01_literature_search" / "candidate_papers.csv", dtype=str).fillna("")
    candidates.loc[0, "candidate_id"] = "candidate:generic"
    candidates.loc[0, "title"] = "Radiologic Technology Licensure Examination Predictors"
    candidates.loc[0, "doi"] = ""
    candidates.to_csv(project / "01_literature_search" / "candidate_papers.csv", index=False)
    (project / "03_markdown" / "cleaned_md" / "paper.md").write_text(
        "# Radiologic Technology\n\n## Page 1\n\nActual Local Title\n",
        encoding="utf-8",
    )

    extract_metadata(project)

    metadata = pd.read_csv(project / "04_metadata" / "metadata_table.csv", dtype=str).fillna("")
    assert metadata.loc[0, "paper_id"] == "paper"
