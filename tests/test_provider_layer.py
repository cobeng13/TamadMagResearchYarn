from __future__ import annotations

import json
from pathlib import Path

from scripts.paper_discovery.discovery.dedupe import dedupe_papers
from scripts.paper_discovery.discovery.search import search_all
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.providers.arxiv import ArxivProvider
from scripts.paper_discovery.providers.core import CoreProvider
from scripts.paper_discovery.providers.europe_pmc import EuropePmcProvider
from scripts.paper_discovery.providers.pubmed import PubMedProvider
from scripts.paper_discovery.providers.semantic_scholar import SemanticScholarProvider


class FakeResponse:
    def __init__(self, data=None, text: str = "", status_code: int = 200):
        self.data = data
        self.text = text or (json.dumps(data) if data is not None else "")
        self.status_code = status_code
        self.headers = {}

    def json(self):
        return self.data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        return self.responses.pop(0)


def test_semantic_scholar_parses_response_and_api_key_header(monkeypatch):
    monkeypatch.setenv("SEMANTIC_SCHOLAR_API_KEY", "secret")
    session = FakeSession(
        [
            FakeResponse(
                {
                    "data": [
                        {
                            "paperId": "S2-1",
                            "title": "Academic predictors",
                            "abstract": "A study.",
                            "authors": [{"name": "A Santos"}],
                            "year": 2024,
                            "venue": "Journal",
                            "publicationDate": "2024-01-02",
                            "externalIds": {"DOI": "10.1/ABC", "PubMed": "123", "PubMedCentral": "PMC99", "ArXiv": "2401.1"},
                            "url": "https://example.test",
                            "openAccessPdf": {"url": "https://example.test/a.pdf"},
                            "citationCount": 5,
                            "referenceCount": 10,
                            "influentialCitationCount": 2,
                            "fieldsOfStudy": ["Medicine"],
                            "publicationTypes": ["JournalArticle"],
                        }
                    ]
                }
            )
        ]
    )
    papers = SemanticScholarProvider({}, session=session).search("academic predictors")
    assert papers[0].doi == "10.1/abc"
    assert papers[0].pmid == "123"
    assert papers[0].pdf_url.endswith(".pdf")
    assert session.calls[0]["headers"]["x-api-key"] == "secret"


def test_semantic_scholar_omits_api_key_when_missing(monkeypatch):
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    session = FakeSession([FakeResponse({"data": []})])
    SemanticScholarProvider({}, session=session).search("x")
    assert "x-api-key" not in session.calls[0]["headers"]


def test_pubmed_batches_ids_and_parses_missing_abstract():
    xml = """<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>1</PMID><Article><ArticleTitle>Title</ArticleTitle><Journal><Title>Journal</Title><JournalIssue><PubDate><Year>2020</Year></PubDate></JournalIssue></Journal><AuthorList><Author><ForeName>A</ForeName><LastName>B</LastName></Author></AuthorList><PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList></Article></MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="doi">10.2/X</ArticleId><ArticleId IdType="pmc">PMC1</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""
    session = FakeSession([FakeResponse(text=xml), FakeResponse(text=xml)])
    provider = PubMedProvider({"contact_email": "a@example.com"}, session=session, sleeper=lambda _: None)
    papers = provider.fetch_pmids(["1", "2", "3"], batch_size=2)
    assert len(session.calls) == 2
    assert session.calls[0]["params"]["id"] == "1,2"
    assert papers[0].abstract == ""
    assert papers[0].doi == "10.2/x"


def test_pubmed_includes_optional_api_params(monkeypatch):
    monkeypatch.setenv("NCBI_API_KEY", "k")
    monkeypatch.setenv("NCBI_TOOL", "tool")
    monkeypatch.setenv("CONTACT_EMAIL", "a@example.com")
    provider = PubMedProvider({}, session=FakeSession([]), sleeper=lambda _: None)
    params = provider.common_params()
    assert params["api_key"] == "k"
    assert params["tool"] == "tool"
    assert params["email"] == "a@example.com"
    assert provider.rate_limit.min_interval_seconds == 0.1


def test_europe_pmc_parses_sample_response():
    data = {"resultList": {"result": [{"title": "T", "abstractText": "A", "authorString": "A B, C D", "journalTitle": "J", "pubYear": "2022", "firstPublicationDate": "2022-01-01", "doi": "10.3/Y", "pmid": "9", "pmcid": "PMC9", "citedByCount": "7", "isOpenAccess": "Y", "fullTextUrlList": {"fullTextUrl": [{"documentStyle": "pdf", "url": "https://x/y.pdf"}]}}]}}
    papers = EuropePmcProvider({}, session=FakeSession([FakeResponse(data)])).search("x")
    assert papers[0].pmcid == "PMC9"
    assert papers[0].pdf_url.endswith(".pdf")
    assert papers[0].citation_count == 7


def test_arxiv_parser_and_rate_limiter_is_configured():
    xml = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom"><entry><id>http://arxiv.org/abs/2401.00001v1</id><updated>2024-01-02T00:00:00Z</updated><published>2024-01-01T00:00:00Z</published><title>Test Paper</title><summary>Abstract</summary><author><name>A B</name></author><arxiv:doi>10.4/Z</arxiv:doi><category term="cs.AI"/><link href="http://arxiv.org/abs/2401.00001v1" rel="alternate"/><link title="pdf" href="http://arxiv.org/pdf/2401.00001v1" type="application/pdf"/></entry></feed>"""
    provider = ArxivProvider({}, session=FakeSession([FakeResponse(text=xml)]), sleeper=lambda _: None)
    papers = provider.search("test")
    assert provider.rate_limit.min_interval_seconds == 3.0
    assert papers[0].arxiv_id == "2401.00001v1"
    assert papers[0].pdf_url.endswith("2401.00001v1")


def test_core_parses_sample_response_and_optional_key(monkeypatch):
    monkeypatch.setenv("CORE_API_KEY", "core-secret")
    data = {"results": [{"id": "c1", "title": "Core paper", "abstract": "A", "authors": [{"name": "A B"}], "yearPublished": 2021, "doi": "10.5/A", "downloadUrl": "https://x/p.pdf", "repositories": [{"name": "Repo"}]}]}
    session = FakeSession([FakeResponse(data)])
    papers = CoreProvider({}, session=session).search("x")
    assert papers[0].core_id == "c1"
    assert papers[0].publisher == "Repo"
    assert session.calls[0]["headers"]["Authorization"] == "Bearer core-secret"


def test_dedupe_merges_doi_pmid_and_arxiv_duplicates():
    papers = dedupe_papers(
        [
            Paper(title="A", doi="10.1/X", source_provider="crossref"),
            Paper(title="A", doi="10.1/x", abstract="longer abstract", source_provider="semantic_scholar"),
            Paper(title="B", pmid="1", source_provider="pubmed"),
            Paper(title="B", pmid="1", pdf_url="https://x/b.pdf", source_provider="europe_pmc"),
            Paper(title="C", arxiv_id="2401.1", source_provider="arxiv"),
            Paper(title="C", arxiv_id="2401.1", citation_count=2, source_provider="semantic_scholar"),
        ]
    )
    assert len(papers) == 3
    assert papers[0].abstract == "longer abstract"
    assert papers[1].pdf_url.endswith("b.pdf")
    assert papers[2].citation_count == 2


def test_search_all_returns_partial_results_when_provider_fails(monkeypatch, caplog):
    class GoodProvider:
        def __init__(self, config):
            pass

        def search(self, *args, **kwargs):
            return [Paper(title="Good", year=2024, source_provider="good")]

    class BadProvider:
        def __init__(self, config):
            pass

        def search(self, *args, **kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr("scripts.paper_discovery.discovery.search.PROVIDER_CLASSES", {"good": GoodProvider, "bad": BadProvider})
    papers = search_all("good", providers=["good", "bad"], config={})
    assert [paper.title for paper in papers] == ["Good"]
    assert "continuing with partial results" in caplog.text
    assert "Traceback" not in caplog.text


def test_env_example_contains_new_variables():
    text = Path(".env.example").read_text(encoding="utf-8")
    for name in [
        "OPENALEX_API_KEY",
        "SEMANTIC_SCHOLAR_API_KEY",
        "NCBI_API_KEY",
        "NCBI_TOOL",
        "CONTACT_EMAIL",
        "CORE_API_KEY",
        "ENABLE_PUBMED",
        "ENABLE_CORE",
    ]:
        assert name in text
