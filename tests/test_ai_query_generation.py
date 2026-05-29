from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from scripts.paper_discovery import ai_query_generation as mod


def make_project(tmp_path: Path, with_brief: bool = True) -> Path:
    project = tmp_path / "project"
    brief = project / "00_brief"
    brief.mkdir(parents=True)
    if with_brief:
        (brief / "research_brief.md").write_text(
            "Predicting Radiologic Technologist Licensure Examination success from academic performance, pre-board results, and clinical internship indicators in the Philippines.",
            encoding="utf-8",
        )
        (brief / "search_keywords.md").write_text(
            '- "radiologic technology"\n- "licensure examination"\n- "academic performance"\n- Philippines\n',
            encoding="utf-8",
        )
    return project


def fake_ai_result() -> dict[str, object]:
    return {
        "topic_summary": "Search for education predictors of radiologic technology licensure success.",
        "core_concepts": ["radiologic technology", "licensure examination", "academic predictors"],
        "inclusion_boundaries": ["Education, assessment, prediction, licensure."],
        "exclusion_boundaries": ["Clinical imaging technique papers."],
        "provider_strategy": [
            {"provider": "pubmed", "recommended_use": "Allied-health education queries.", "notes": "Use Boolean variants."},
            {"provider": "openalex", "recommended_use": "Broad scholarly discovery.", "notes": "Use natural language."},
        ],
        "query_families": [
            {
                "family_name": "direct_rt_licensure",
                "purpose": "Find direct RT licensure predictor studies.",
                "queries": [
                    {
                        "provider": "pubmed",
                        "query_text": '("radiologic technology" OR radiography) AND licensure AND "academic performance"',
                        "purpose": "Precision-oriented biomedical search.",
                        "expected_recall": "medium",
                        "expected_precision": "high",
                        "notes": "Direct terminology.",
                    },
                    {
                        "provider": "openalex",
                        "query_text": "radiologic technology licensure examination academic performance Philippines",
                        "purpose": "Broad scholarly search.",
                        "expected_recall": "high",
                        "expected_precision": "medium",
                        "notes": "Philippine context.",
                    },
                    {
                        "provider": "not_a_provider",
                        "query_text": "health professions licensure examination predictors academic performance",
                        "purpose": "General fallback.",
                        "expected_recall": "unexpected",
                        "expected_precision": "bad",
                        "notes": "Invalid values should be normalized.",
                    },
                ],
            }
        ],
        "warnings": ["Allied-health terms may be noisy."],
        "recommended_general_queries": [
            "radiologic technology licensure examination academic performance Philippines",
            "health professions licensure examination predictors academic performance",
        ],
        "suggested_next_step": "Review query variants, then run discovery.",
    }


def test_dry_run_works_without_openai_key(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = mod.run_ai_query_generation(
        project_dir=project,
        model="gpt-5-mini",
        limit=5,
        providers=mod.parse_providers(None),
        dry_run=True,
        apply=False,
        overwrite=False,
        no_backup=False,
        min_provider_queries=3,
        max_provider_queries=8,
    )

    assert result["status"] == "ok"
    assert (project / "01_literature_search" / "ai_query_plan.md").exists()
    text = (project / "01_literature_search" / "search_queries_ai.md").read_text(encoding="utf-8")
    assert "Dry run" in (project / "01_literature_search" / "ai_query_plan.md").read_text(encoding="utf-8")
    assert "AI-Generated Search Queries" in text
    assert not (project / "01_literature_search" / "search_queries.md").exists()


def test_missing_brief_files_blocks_without_ai_call(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path, with_brief=False)

    def fail_call(*args, **kwargs):
        raise AssertionError("AI should not be called")

    monkeypatch.setattr(mod, "call_openai_query_generation", fail_call)
    result = mod.run_ai_query_generation(
        project_dir=project,
        model="gpt-5-mini",
        limit=10,
        providers=mod.parse_providers(None),
        dry_run=False,
        apply=False,
        overwrite=False,
        no_backup=False,
        min_provider_queries=3,
        max_provider_queries=8,
    )

    assert result["status"] == "blocked"
    assert "Blocked" in (project / "01_literature_search" / "ai_query_plan.md").read_text(encoding="utf-8")


def test_mocked_ai_response_writes_outputs_and_required_csv_columns(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_query_generation", lambda *args, **kwargs: fake_ai_result())

    result = mod.run_ai_query_generation(
        project_dir=project,
        model="gpt-5-mini",
        limit=20,
        providers=mod.parse_providers("openalex,pubmed"),
        dry_run=False,
        apply=False,
        overwrite=False,
        no_backup=False,
        min_provider_queries=3,
        max_provider_queries=8,
    )

    assert result["queries"] == 3
    plan = project / "01_literature_search" / "ai_query_plan.md"
    variants = project / "01_literature_search" / "ai_query_variants.csv"
    search_ai = project / "01_literature_search" / "search_queries_ai.md"
    log = project / "logs" / "ai_query_generation_log.md"
    assert plan.exists()
    assert variants.exists()
    assert search_ai.exists()
    assert log.exists()
    with variants.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0].keys()) == mod.VARIANT_COLUMNS
    assert {row["provider"] for row in rows} <= {"openalex", "pubmed", "general"}


def test_invalid_recall_precision_are_coerced_to_medium_with_warning(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_query_generation", lambda *args, **kwargs: fake_ai_result())

    result = mod.run_ai_query_generation(
        project_dir=project,
        model="gpt-5-mini",
        limit=20,
        providers=mod.parse_providers("openalex,pubmed"),
        dry_run=False,
        apply=False,
        overwrite=False,
        no_backup=False,
        min_provider_queries=3,
        max_provider_queries=8,
    )

    rows = pd.read_csv(project / "01_literature_search" / "ai_query_variants.csv", dtype=str).fillna("")
    invalid_row = rows[rows["provider"] == "general"].iloc[0]
    assert invalid_row["expected_recall"] == "medium"
    assert invalid_row["expected_precision"] == "medium"
    assert any("Invalid expected_recall" in warning for warning in result["warnings"])


def test_apply_without_overwrite_appends_and_creates_backup(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    search = project / "01_literature_search" / "search_queries.md"
    search.parent.mkdir(parents=True)
    search.write_text("# Search Queries\n\n- existing query licensure board academic performance\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_query_generation", lambda *args, **kwargs: fake_ai_result())

    result = mod.run_ai_query_generation(
        project_dir=project,
        model="gpt-5-mini",
        limit=20,
        providers=mod.parse_providers("openalex,pubmed"),
        dry_run=False,
        apply=True,
        overwrite=False,
        no_backup=False,
        min_provider_queries=3,
        max_provider_queries=8,
    )

    text = search.read_text(encoding="utf-8")
    assert "existing query" in text
    assert "# AI Query Suggestions -" in text
    assert result["backup_path"]
    assert Path(result["backup_path"]).exists()


def test_apply_with_overwrite_replaces_and_respects_no_backup(tmp_path: Path, monkeypatch):
    project = make_project(tmp_path)
    search = project / "01_literature_search" / "search_queries.md"
    search.parent.mkdir(parents=True)
    search.write_text("# Search Queries\n\n- old query to replace\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(mod, "call_openai_query_generation", lambda *args, **kwargs: fake_ai_result())

    result = mod.run_ai_query_generation(
        project_dir=project,
        model="gpt-5-mini",
        limit=20,
        providers=mod.parse_providers("openalex,pubmed"),
        dry_run=False,
        apply=True,
        overwrite=True,
        no_backup=True,
        min_provider_queries=3,
        max_provider_queries=8,
    )

    text = search.read_text(encoding="utf-8")
    assert "old query to replace" not in text
    assert "radiologic technology licensure examination academic performance Philippines" in text
    assert result["backup_path"] == ""


def test_build_request_payload_uses_structured_query_schema(tmp_path: Path):
    project = make_project(tmp_path)
    brief_context, _ = mod.read_stage00_context(project)
    payload = mod.build_request_payload("gpt-5-mini", brief_context, ["pubmed"], 10, 3, 8)

    assert payload["model"] == "gpt-5-mini"
    assert payload["text"]["format"]["type"] == "json_schema"
    assert payload["text"]["format"]["schema"]["properties"]["query_families"]
