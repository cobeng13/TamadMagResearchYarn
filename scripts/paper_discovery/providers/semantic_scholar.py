from __future__ import annotations

from typing import Any

from scripts.paper_discovery.config import env_or_config
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, clean_text, parse_int

FIELDS = ",".join(
    [
        "title",
        "abstract",
        "authors",
        "year",
        "venue",
        "publicationDate",
        "externalIds",
        "url",
        "openAccessPdf",
        "citationCount",
        "referenceCount",
        "influentialCitationCount",
        "fieldsOfStudy",
        "publicationTypes",
    ]
)


class SemanticScholarProvider(BaseProvider):
    name = "semantic_scholar"
    base_url = "https://api.semanticscholar.org/graph/v1"

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        params: dict[str, Any] = {"query": query, "limit": min(limit, 100), "fields": FIELDS}
        if year_from or year_to:
            params["year"] = f"{year_from or ''}-{year_to or ''}"
        data = self.request_json("GET", f"{self.base_url}/paper/search", params=params, headers=self.headers())
        return [self.to_paper(item) for item in data.get("data", [])]

    def get_by_doi(self, doi: str) -> Paper | None:
        data = self.request_json("GET", f"{self.base_url}/paper/DOI:{normalize_doi(doi)}", params={"fields": FIELDS}, headers=self.headers())
        return self.to_paper(data) if data else None

    def get_by_id(self, identifier: str) -> Paper | None:
        data = self.request_json("GET", f"{self.base_url}/paper/{identifier}", params={"fields": FIELDS}, headers=self.headers())
        return self.to_paper(data) if data else None

    def headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"}
        api_key = env_or_config(self.config, "SEMANTIC_SCHOLAR_API_KEY", "semantic_scholar_api_key")
        if api_key:
            headers["x-api-key"] = api_key
        return headers

    def to_paper(self, item: dict[str, Any]) -> Paper:
        external = item.get("externalIds") or {}
        oa_pdf = item.get("openAccessPdf") or {}
        return Paper(
            title=clean_text(item.get("title")),
            abstract=clean_text(item.get("abstract")),
            authors=[a.get("name", "") for a in item.get("authors", []) if a.get("name")],
            year=parse_int(item.get("year")),
            publication_date=item.get("publicationDate") or "",
            journal_or_source=item.get("venue") or "",
            doi=normalize_doi(external.get("DOI") or ""),
            pmid=str(external.get("PubMed") or ""),
            pmcid=str(external.get("PubMedCentral") or ""),
            arxiv_id=str(external.get("ArXiv") or ""),
            semantic_scholar_id=item.get("paperId") or "",
            url=item.get("url") or "",
            pdf_url=oa_pdf.get("url") or "",
            is_open_access=bool(oa_pdf.get("url")) if oa_pdf else None,
            source_provider=self.name,
            source_record_id=item.get("paperId") or "",
            citation_count=parse_int(item.get("citationCount")),
            reference_count=parse_int(item.get("referenceCount")),
            influential_citation_count=parse_int(item.get("influentialCitationCount")),
            fields_of_study=item.get("fieldsOfStudy") or [],
            publication_types=item.get("publicationTypes") or [],
            raw=item,
        )

