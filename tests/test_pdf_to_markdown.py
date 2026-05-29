from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.document_ingestion import pdf_to_markdown
from scripts.document_ingestion.pdf_to_markdown import ExtractionResult, ingest_pdfs


def make_project(tmp_path: Path, names: list[str] | None = None) -> Path:
    project = tmp_path / "project"
    pdf_dir = project / "02_sources" / "pdf"
    pdf_dir.mkdir(parents=True)
    for name in names or ["paper.pdf"]:
        (pdf_dir / name).write_bytes(b"%PDF fake")
    return project


def test_ingests_pdf_to_raw_and_cleaned_markdown(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path, ["Relevant Paper.pdf"])
    monkeypatch.setattr(
        pdf_to_markdown,
        "extract_pdf_pages",
        lambda path: ExtractionResult(
            pages=[
                "Abstract\n" + ("This is a study with extractable article text. " * 20),
                "References\n" + ("A. Source. " * 60),
            ],
            page_count=2,
        ),
    )

    result = ingest_pdfs(project)

    assert result["files_found"] == 1
    assert result["converted"] == 1
    raw = project / "03_markdown" / "raw_md" / "relevant-paper.md"
    cleaned = project / "03_markdown" / "cleaned_md" / "relevant-paper.md"
    assert raw.exists()
    assert cleaned.exists()
    assert "<!-- page 1 -->" in raw.read_text(encoding="utf-8")
    assert "## Page 1" in cleaned.read_text(encoding="utf-8")
    manifest = pd.read_csv(project / "03_markdown" / "ingestion_manifest.csv", dtype=str).fillna("")
    assert manifest.loc[0, "conversion_status"] == "converted"
    assert manifest.loc[0, "needs_manual_review"] == "no"


def test_image_only_pdf_is_failed_and_not_claimed_converted(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    monkeypatch.setattr(pdf_to_markdown, "extract_pdf_pages", lambda path: ExtractionResult(pages=["", ""], page_count=2))

    result = ingest_pdfs(project)

    assert result["converted"] == 0
    assert result["failed"] == 1
    assert not list((project / "03_markdown" / "raw_md").glob("*.md"))
    manifest = pd.read_csv(project / "03_markdown" / "ingestion_manifest.csv", dtype=str).fillna("")
    assert manifest.loc[0, "conversion_status"] == "failed"
    assert manifest.loc[0, "needs_manual_review"] == "yes"


def test_dry_run_writes_no_files(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    monkeypatch.setattr(
        pdf_to_markdown,
        "extract_pdf_pages",
        lambda path: ExtractionResult(pages=["Text"], page_count=1),
    )

    result = ingest_pdfs(project, dry_run=True)

    assert result["files_found"] == 1
    assert not (project / "03_markdown").exists()


def test_existing_markdown_is_not_overwritten_without_flag(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path, ["Paper.pdf"])
    raw = project / "03_markdown" / "raw_md" / "paper.md"
    cleaned = project / "03_markdown" / "cleaned_md" / "paper.md"
    raw.parent.mkdir(parents=True)
    cleaned.parent.mkdir(parents=True)
    raw.write_text("existing raw", encoding="utf-8")
    cleaned.write_text("existing cleaned", encoding="utf-8")
    monkeypatch.setattr(
        pdf_to_markdown,
        "extract_pdf_pages",
        lambda path: ExtractionResult(pages=["new text"], page_count=1),
    )

    ingest_pdfs(project)
    assert raw.read_text(encoding="utf-8") == "existing raw"
    assert cleaned.read_text(encoding="utf-8") == "existing cleaned"

    ingest_pdfs(project, overwrite=True)
    assert "new text" in raw.read_text(encoding="utf-8")
