from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from scripts.results.ingest_statresults import MANIFEST_COLUMNS, run_ingest


def make_project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / "input").mkdir(parents=True)
    return project


def test_missing_statresults_writes_unavailable_unless_strict(tmp_path: Path):
    project = make_project(tmp_path)

    result = run_ingest(project, None, overwrite=False, no_backup=True, strict=False, include_raw_tables=False, max_file_chars=None)

    assert result["extracted"] == 0
    assert "unavailable" in (project / "input" / "results_availability.md").read_text(encoding="utf-8")
    assert (project / "logs" / "statresults_ingest_log.md").exists()


def test_missing_statresults_strict_fails(tmp_path: Path):
    project = make_project(tmp_path)

    with pytest.raises(FileNotFoundError):
        run_ingest(project, None, overwrite=False, no_backup=True, strict=True, include_raw_tables=False, max_file_chars=None)


def test_empty_statresults_writes_status(tmp_path: Path):
    project = make_project(tmp_path)
    (project / "statresults").mkdir()

    result = run_ingest(project, None, overwrite=False, no_backup=True, strict=False, include_raw_tables=False, max_file_chars=None)

    assert result["rows"] == 0
    assert "unavailable" in (project / "input" / "results_availability.md").read_text(encoding="utf-8")


def test_extracts_md_txt_and_csv(tmp_path: Path):
    project = make_project(tmp_path)
    stat = project / "statresults"
    stat.mkdir()
    (stat / "summary.md").write_text("# Results\np = 0.01", encoding="utf-8")
    (stat / "notes.txt").write_text("Regression output", encoding="utf-8")
    (stat / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    result = run_ingest(project, None, overwrite=False, no_backup=True, strict=False, include_raw_tables=False, max_file_chars=None)
    compiled = (project / "input" / "statistical_results_compiled.md").read_text(encoding="utf-8")

    assert result["extracted"] == 3
    assert "Regression output" in compiled
    assert "a,b" in compiled


def test_manifest_has_required_columns(tmp_path: Path):
    project = make_project(tmp_path)
    stat = project / "statresults"
    stat.mkdir()
    (stat / "table.csv").write_text("a,b\n1,2\n", encoding="utf-8")

    run_ingest(project, None, overwrite=False, no_backup=True, strict=False, include_raw_tables=False, max_file_chars=None)
    df = pd.read_csv(project / "input" / "statistical_results_manifest.csv")

    assert list(df.columns) == MANIFEST_COLUMNS


def test_skips_unsupported_file_types(tmp_path: Path):
    project = make_project(tmp_path)
    stat = project / "statresults"
    stat.mkdir()
    (stat / "plot.png").write_bytes(b"png")

    run_ingest(project, None, overwrite=False, no_backup=True, strict=False, include_raw_tables=False, max_file_chars=None)
    df = pd.read_csv(project / "input" / "statistical_results_manifest.csv")

    assert df.loc[0, "extraction_status"] == "skipped_unsupported"


def test_existing_outputs_not_overwritten_without_overwrite(tmp_path: Path):
    project = make_project(tmp_path)
    stat = project / "statresults"
    stat.mkdir()
    (stat / "a.md").write_text("content", encoding="utf-8")
    (project / "input" / "statistical_results_compiled.md").write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError):
        run_ingest(project, None, overwrite=False, no_backup=True, strict=False, include_raw_tables=False, max_file_chars=None)


def test_overwrite_creates_backups_unless_no_backup(tmp_path: Path):
    project = make_project(tmp_path)
    stat = project / "statresults"
    stat.mkdir()
    (stat / "a.md").write_text("content", encoding="utf-8")
    for name in ["statistical_results_compiled.md", "results_availability.md"]:
        (project / "input" / name).write_text("existing", encoding="utf-8")

    result = run_ingest(project, None, overwrite=True, no_backup=False, strict=False, include_raw_tables=False, max_file_chars=None)

    assert result["backups"]
    assert list((project / "input").glob("*.bak.md"))
