from __future__ import annotations

from pathlib import Path

from scripts.ai.logging import write_ai_run_log


def test_ai_run_log_records_metadata_without_full_source_text(tmp_path: Path):
    log_path = tmp_path / "ai_run_log.md"
    long_markdown = "FULL PAPER TEXT " * 100

    write_ai_run_log(
        log_path,
        task_name="metadata_check",
        model="gpt-5-nano",
        input_paths=[tmp_path / "paper.md"],
        output_paths=[tmp_path / "metadata_table_ai_checked.csv"],
        counts={"attempted": 1, "succeeded": 1, "failed": 0},
        errors=[f"row 1 failed; {long_markdown}"],
        prompt_version="metadata_check_v1",
    )

    text = log_path.read_text(encoding="utf-8")
    assert "metadata_check" in text
    assert "gpt-5-nano" in text
    assert "metadata_table_ai_checked.csv" in text
    assert text.count("FULL PAPER TEXT") < 40

