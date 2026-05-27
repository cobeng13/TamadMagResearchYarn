from __future__ import annotations

from scripts.paper_discovery.generate_search_queries import generate_queries, read_existing_queries, write_search_queries


def test_generate_queries_from_ai_response_and_brief_files(tmp_path):
    project = tmp_path / "project"
    brief = project / "00_brief"
    brief.mkdir(parents=True)
    (brief / "_ai_response.md").write_text(
        """
## Suggested Boolean Search Strings
1. ("Radiologic Technology" OR radiography) AND ("licensure examination" OR "board examination") AND ("academic performance" OR grades)
2. ("pre-board examination" OR "mock board examination") AND ("licensure examination" OR "board examination") AND Philippines
""",
        encoding="utf-8",
    )
    (brief / "research_brief.md").write_text("Philippines Radiologic Technologist Licensure Examination academic performance", encoding="utf-8")

    queries = generate_queries(project, max_queries=8)

    assert any("Radiologic Technology" in query and "academic performance" in query for query in queries)
    assert any("pre-board" in query and "Philippines" in query for query in queries)
    assert len(queries) <= 8


def test_write_search_queries_preserves_existing_queries(tmp_path):
    path = tmp_path / "project" / "01_literature_search" / "search_queries.md"
    path.parent.mkdir(parents=True)
    path.write_text("- custom licensure examination predictor query\n", encoding="utf-8")

    write_search_queries(path, ["radiologic technology licensure examination academic performance"], preserve_existing=True)

    text = path.read_text(encoding="utf-8")
    assert "custom licensure examination predictor query" in text
    assert "radiologic technology licensure examination academic performance" in text
    assert "not source records or screening decisions" in text


def test_write_search_queries_can_replace_existing_queries(tmp_path):
    path = tmp_path / "project" / "01_literature_search" / "search_queries.md"
    path.parent.mkdir(parents=True)
    path.write_text("- custom licensure examination predictor query\n", encoding="utf-8")

    write_search_queries(path, ["radiologic technology licensure examination academic performance"], preserve_existing=False)

    queries = read_existing_queries(path)
    assert queries == ["radiologic technology licensure examination academic performance"]

