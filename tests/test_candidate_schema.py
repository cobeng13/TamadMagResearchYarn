from __future__ import annotations

import pandas as pd

from scripts.paper_discovery.candidate_schema import (
    CANONICAL_CANDIDATE_COLUMNS,
    from_legacy_openalex_row,
    from_paper_model,
    from_provider_export_row,
    merge_candidate_dataframes,
    normalize_candidate_row,
)
from scripts.paper_discovery.discovery.search import export_papers_csv
from scripts.paper_discovery.models import Paper


def test_canonical_columns_are_complete():
    required = [
        "candidate_id",
        "title",
        "authors",
        "year",
        "publication_date",
        "journal_or_repository",
        "publisher",
        "source_type",
        "database_or_source",
        "source_providers",
        "search_query",
        "doi",
        "pmid",
        "pmcid",
        "arxiv_id",
        "semantic_scholar_id",
        "openalex_id",
        "core_id",
        "url",
        "pdf_url",
        "is_open_access",
        "oa_status",
        "license",
        "abstract",
        "keywords",
        "fields_of_study",
        "publication_types",
        "citation_count",
        "reference_count",
        "influential_citation_count",
        "ranking_score",
        "access_type",
        "screening_status",
        "screening_reason",
        "human_decision",
        "human_notes",
        "metadata_warnings",
        "date_added",
        "date_updated",
    ]
    assert CANONICAL_CANDIDATE_COLUMNS == required


def test_normalize_candidate_row_fills_defaults_and_blanks():
    row = normalize_candidate_row({"title": "Academic Predictors", "year": 2024, "authors": ["A Santos", "B Cruz"]})
    assert set(row) == set(CANONICAL_CANDIDATE_COLUMNS)
    assert row["candidate_id"] == "title_year:academic-predictors-2024"
    assert row["authors"] == "A Santos; B Cruz"
    assert row["screening_status"] == "unscreened"
    assert row["human_decision"] == ""
    assert row["human_notes"] == ""
    assert row["abstract"] == ""


def test_candidate_id_generation_priority():
    assert normalize_candidate_row({"doi": "https://doi.org/10.1/ABC"})["candidate_id"] == "doi:10.1/abc"
    assert normalize_candidate_row({"pmid": "123"})["candidate_id"] == "pmid:123"
    assert normalize_candidate_row({"arxiv_id": "2401.00001v1"})["candidate_id"] == "arxiv:2401.00001v1"
    assert normalize_candidate_row({"openalex_id": "https://openalex.org/W1"})["candidate_id"] == "openalex:https://openalex.org/W1"
    assert normalize_candidate_row({"title": "Board Exam Performance!", "year": "2020"})["candidate_id"] == "title_year:board-exam-performance-2020"


def test_legacy_openalex_row_maps_to_canonical_fields():
    row = from_legacy_openalex_row(
        {
            "paper_id": "OA-1",
            "title": "Academic predictors",
            "authors": "A Santos; B Cruz",
            "year": "2024",
            "source": "Radiography Journal",
            "database": "OpenAlex",
            "url": "https://doi.org/10.2/X",
            "doi": "10.2/X",
            "access_type": "gold",
            "screening_status": "unscreened",
            "abstract": "Abstract text.",
        }
    )
    assert row["candidate_id"] == "doi:10.2/x"
    assert row["journal_or_repository"] == "Radiography Journal"
    assert row["database_or_source"] == "OpenAlex"
    assert row["source_providers"] == "openalex"
    assert row["oa_status"] == "gold"
    assert row["abstract"] == "Abstract text."


def test_paper_model_maps_without_dropping_metadata():
    paper = Paper(
        title="Licensure predictors",
        authors=["A Santos"],
        year=2023,
        publication_date="2023-01-02",
        journal_or_source="Journal",
        publisher="Publisher",
        doi="10.3/Y",
        pmid="9",
        pmcid="PMC9",
        arxiv_id="2301.1",
        semantic_scholar_id="S2",
        openalex_id="W1",
        core_id="C1",
        url="https://example.test",
        pdf_url="https://example.test/p.pdf",
        is_open_access=True,
        oa_status="green",
        license="cc-by",
        abstract="A study.",
        citation_count=7,
        reference_count=11,
        influential_citation_count=2,
        fields_of_study=["Medicine"],
        keywords=["licensure"],
        publication_types=["JournalArticle"],
        source_provider="pubmed",
        score=4.5,
    )
    row = from_paper_model(paper, search_query="licensure predictors")
    assert row["candidate_id"] == "doi:10.3/y"
    assert row["source_providers"] == "pubmed"
    assert row["fields_of_study"] == "Medicine"
    assert row["keywords"] == "licensure"
    assert row["publication_types"] == "JournalArticle"
    assert row["ranking_score"] == "4.5"
    assert row["search_query"] == "licensure predictors"


def test_provider_export_row_maps_to_canonical_fields():
    row = from_provider_export_row(
        {
            "score": "3.2",
            "title": "Provider export paper",
            "year": "2022",
            "doi": "10.4/Z",
            "source_providers": "openalex; semantic_scholar",
            "is_open_access": "true",
            "pdf_url": "https://example.test/p.pdf",
            "citation_count": "10",
            "url": "https://example.test",
            "abstract": "Export abstract.",
        }
    )
    assert row["candidate_id"] == "doi:10.4/z"
    assert row["ranking_score"] == "3.2"
    assert row["source_providers"] == "openalex; semantic_scholar"
    assert row["abstract"] == "Export abstract."


def test_multi_provider_export_defaults_to_canonical_candidate_schema(tmp_path):
    path = tmp_path / "candidate_papers.csv"
    export_papers_csv([Paper(title="Exported", doi="10.9/E", source_provider="openalex", score=2.0)], path, search_query="export query")
    df = pd.read_csv(path, dtype=str).fillna("")
    assert list(df.columns) == CANONICAL_CANDIDATE_COLUMNS
    assert df.iloc[0]["candidate_id"] == "doi:10.9/e"
    assert df.iloc[0]["search_query"] == "export query"


def test_merge_dedupes_doi_preserves_human_fields_and_merges_providers():
    existing = pd.DataFrame(
        [
            normalize_candidate_row(
                {
                    "title": "A",
                    "doi": "10.1/X",
                    "source_providers": "openalex",
                    "screening_status": "included",
                    "human_decision": "include",
                    "human_notes": "Reviewed by human.",
                }
            )
        ]
    )
    incoming = pd.DataFrame([normalize_candidate_row({"title": "A", "doi": "10.1/x", "source_providers": "pubmed", "abstract": "Long abstract."})])
    merged = merge_candidate_dataframes(existing, incoming, timestamp="2026-05-27")
    assert len(merged) == 1
    row = merged.iloc[0].to_dict()
    assert row["human_decision"] == "include"
    assert row["human_notes"] == "Reviewed by human."
    assert row["screening_status"] == "included"
    assert row["source_providers"] == "openalex; pubmed"
    assert row["abstract"] == "Long abstract."
    assert row["date_updated"] == "2026-05-27"


def test_merge_dedupes_title_year_when_identifiers_missing():
    existing = pd.DataFrame([normalize_candidate_row({"title": "Same Paper", "year": "2021", "source_providers": "core"})])
    incoming = pd.DataFrame([normalize_candidate_row({"title": "Same Paper", "year": "2021", "source_providers": "europe_pmc"})])
    merged = merge_candidate_dataframes(existing, incoming, timestamp="2026-05-27")
    assert len(merged) == 1
    assert merged.iloc[0]["source_providers"] == "core; europe_pmc"
