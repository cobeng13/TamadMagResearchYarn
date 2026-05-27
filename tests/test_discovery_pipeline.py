from __future__ import annotations

import pandas as pd

import scripts.paper_discovery.run_discovery_pipeline as discovery_pipeline
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.run_discovery_pipeline import run_pipeline


def test_main_discovery_pipeline_imports():
    assert callable(discovery_pipeline.main)
    assert callable(discovery_pipeline.run_pipeline)


def test_missing_search_queries_creates_template_and_exits(tmp_path):
    project = tmp_path / "project"
    summary = run_pipeline(project, max_results=5, config={})
    query_file = project / "01_literature_search" / "search_queries.md"
    candidate_file = project / "01_literature_search" / "candidate_papers.csv"
    assert summary == {"queries": 0, "incoming_rows": 0, "candidate_rows": 0, "failures": 0}
    assert query_file.exists()
    assert "will not invent queries" in query_file.read_text(encoding="utf-8")
    assert candidate_file.exists()
    assert pd.read_csv(candidate_file).empty


def test_pipeline_writes_canonical_candidates_with_mocked_results(tmp_path, monkeypatch):
    project = tmp_path / "project"
    search_dir = project / "01_literature_search"
    search_dir.mkdir(parents=True)
    (search_dir / "search_queries.md").write_text("- licensure predictors\n", encoding="utf-8")

    def fake_search_all(query, limit_per_provider, year_from, year_to, providers, config):
        return [
            Paper(
                title="Academic predictors",
                authors=["A Santos"],
                year=2024,
                doi="10.1/ABC",
                source_provider="pubmed",
                citation_count=3,
                score=5.0,
            )
        ]

    monkeypatch.setattr("scripts.paper_discovery.run_discovery_pipeline.search_all", fake_search_all)
    summary = run_pipeline(project, max_results=10, providers=["pubmed"], year_from=2020, year_to=2026, config={})
    df = pd.read_csv(search_dir / "candidate_papers.csv", dtype=str).fillna("")
    assert summary["queries"] == 1
    assert summary["candidate_rows"] == 1
    assert df.iloc[0]["candidate_id"] == "doi:10.1/abc"
    assert df.iloc[0]["screening_status"] == "unscreened"
    assert df.iloc[0]["human_decision"] == ""
    assert df.iloc[0]["search_query"] == "licensure predictors"
    assert df.iloc[0]["source_providers"] == "pubmed"


def test_pipeline_preserves_existing_human_review_fields(tmp_path, monkeypatch):
    project = tmp_path / "project"
    search_dir = project / "01_literature_search"
    search_dir.mkdir(parents=True)
    (search_dir / "search_queries.md").write_text("- licensure predictors\n", encoding="utf-8")
    pd.DataFrame(
        [
            {
                "candidate_id": "doi:10.1/abc",
                "title": "Academic predictors",
                "doi": "10.1/abc",
                "screening_status": "included",
                "human_decision": "include",
                "human_notes": "Human reviewed.",
                "source_providers": "openalex",
            }
        ]
    ).to_csv(search_dir / "candidate_papers.csv", index=False)

    def fake_search_all(*args, **kwargs):
        return [Paper(title="Academic predictors", doi="10.1/ABC", source_provider="pubmed", abstract="Updated abstract.")]

    monkeypatch.setattr("scripts.paper_discovery.run_discovery_pipeline.search_all", fake_search_all)
    run_pipeline(project, max_results=10, config={})
    df = pd.read_csv(search_dir / "candidate_papers.csv", dtype=str).fillna("")
    assert len(df) == 1
    assert df.iloc[0]["screening_status"] == "included"
    assert df.iloc[0]["human_decision"] == "include"
    assert df.iloc[0]["human_notes"] == "Human reviewed."
    assert df.iloc[0]["source_providers"] == "openalex; pubmed"
    assert df.iloc[0]["abstract"] == "Updated abstract."


def test_pipeline_continues_after_query_failure(tmp_path, monkeypatch):
    project = tmp_path / "project"
    search_dir = project / "01_literature_search"
    search_dir.mkdir(parents=True)
    (search_dir / "search_queries.md").write_text("- bad query\n- good query\n", encoding="utf-8")

    def fake_search_all(query, *args, **kwargs):
        if query == "bad query":
            raise RuntimeError("provider failure")
        return [Paper(title="Good result", year=2024, source_provider="core")]

    monkeypatch.setattr("scripts.paper_discovery.run_discovery_pipeline.search_all", fake_search_all)
    summary = run_pipeline(project, max_results=10, config={})
    df = pd.read_csv(search_dir / "candidate_papers.csv", dtype=str).fillna("")
    assert summary["failures"] == 1
    assert len(df) == 1
    assert df.iloc[0]["title"] == "Good result"
