from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from scripts.paper_discovery.download_pdfs import download_pdfs


PDF_BYTES = b"%PDF-1.4\nbody\n%%EOF\n"


class MockResponse:
    def __init__(self, body: bytes, content_type: str = "application/pdf", status_code: int = 200):
        self.body = body
        self.headers = {"Content-Type": content_type}
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size: int):
        yield self.body


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    sources = project / "02_sources"
    sources.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "candidate_id": "c1",
                "title": "High PDF",
                "year": "2024",
                "doi": "10.1/high",
                "pdf_url": "https://example.test/high.pdf",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.95",
                "download_status": "queued",
                "target_filename": "c1_2024_high-pdf.pdf",
            },
            {
                "candidate_id": "c2",
                "title": "Missing PDF",
                "year": "2023",
                "doi": "10.1/missing",
                "pdf_url": "",
                "ai_relevance_label": "highly_relevant",
                "ai_confidence": "0.80",
                "download_status": "queued",
                "target_filename": "c2_2023_missing-pdf.pdf",
            },
            {
                "candidate_id": "c3",
                "title": "Possible PDF",
                "year": "2022",
                "doi": "10.1/possible",
                "pdf_url": "https://example.test/possible.pdf",
                "ai_relevance_label": "possibly_relevant",
                "ai_confidence": "0.70",
                "download_status": "queued",
                "target_filename": "c3_2022_possible-pdf.pdf",
            },
        ]
    ).to_csv(sources / "download_queue.csv", index=False)
    return project


def test_downloads_mocked_pdf_response_and_writes_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    result = download_pdfs(project, tags=["highly_relevant"], retries=0)
    saved = project / "02_sources" / "pdf" / "c1_2024_high-pdf.pdf"
    assert saved.read_bytes() == PDF_BYTES
    assert (project / "02_sources" / "download_results" / "success.csv").exists()
    assert result["success"]["candidate_id"].tolist() == ["c1"]


def test_writes_failed_when_pdf_url_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    result = download_pdfs(project, tags=["highly_relevant"], retries=0)
    failed = result["failed"][result["failed"]["candidate_id"] == "c2"].iloc[0]
    assert failed["reason"] == "missing_pdf_url"


def test_writes_failed_when_response_is_not_pdf_like(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(b"<html></html>", "text/html"))
    result = download_pdfs(project, tags=["possibly_relevant"], retries=0)
    assert result["failed"].iloc[0]["reason"] == "not_pdf_response"
    assert not (project / "02_sources" / "pdf" / "c3_2022_possible-pdf.pdf").exists()


def test_does_not_overwrite_existing_file_unless_requested(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    pdf = project / "02_sources" / "pdf" / "c1_2024_high-pdf.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.4\nexisting\n")
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    result = download_pdfs(project, tags=["highly_relevant"], retries=0)
    assert pdf.read_bytes() == b"%PDF-1.4\nexisting\n"
    assert result["success"].iloc[0]["reason"] == "file_already_exists"

    download_pdfs(project, tags=["highly_relevant"], overwrite=True, retries=0)
    assert pdf.read_bytes() == PDF_BYTES


def test_computes_sha256(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    result = download_pdfs(project, tags=["possibly_relevant"], retries=0)
    assert result["success"].iloc[0]["sha256"] == hashlib.sha256(PDF_BYTES).hexdigest()


def test_supports_tag_filtering(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    result = download_pdfs(project, tags=["possibly_relevant"], retries=0)
    assert result["selected_count"] == 1
    assert result["success"]["candidate_id"].tolist() == ["c3"]


def test_dry_run_writes_no_downloaded_pdfs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    project = make_project(tmp_path)
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    result = download_pdfs(project, tags=["highly_relevant"], dry_run=True, retries=0)
    assert result["selected_count"] == 2
    assert not (project / "02_sources" / "pdf").exists()
    assert not (project / "02_sources" / "download_results").exists()


def test_does_not_print_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    project = make_project(tmp_path)
    monkeypatch.setenv("UNPAYWALL_EMAIL", "secret@example.test")
    monkeypatch.setattr("scripts.paper_discovery.download_pdfs.requests.get", lambda *a, **k: MockResponse(PDF_BYTES))
    download_pdfs(project, tags=["possibly_relevant"], retries=0)
    captured = capsys.readouterr()
    assert "secret@example.test" not in captured.out
    assert "secret@example.test" not in captured.err
