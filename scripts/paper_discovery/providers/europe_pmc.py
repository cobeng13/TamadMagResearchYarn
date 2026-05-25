from __future__ import annotations

from typing import Any

from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, clean_text, listify, parse_int


class EuropePmcProvider(BaseProvider):
    name = "europe_pmc"
    search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        terms = [query]
        if year_from:
            terms.append(f"FIRST_PDATE:[{year_from}-01-01 TO 9999-12-31]")
        if year_to:
            terms.append(f"FIRST_PDATE:[0001-01-01 TO {year_to}-12-31]")
        params = {"query": " AND ".join(f"({term})" for term in terms), "format": "json", "pageSize": limit, "resultType": "core"}
        data = self.request_json("GET", self.search_url, params=params, headers={"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"})
        return [self.to_paper(item) for item in data.get("resultList", {}).get("result", [])]

    def get_by_doi(self, doi: str) -> Paper | None:
        results = self.search(f"DOI:{normalize_doi(doi)}", limit=1)
        return results[0] if results else None

    def to_paper(self, item: dict[str, Any]) -> Paper:
        full_text_urls = item.get("fullTextUrlList", {}).get("fullTextUrl", [])
        pdf_url = ""
        landing_url = item.get("doi") and f"https://doi.org/{item.get('doi')}" or ""
        for link in full_text_urls:
            url = link.get("url") or ""
            if link.get("documentStyle", "").lower() == "pdf" or url.lower().endswith(".pdf"):
                pdf_url = url
                break
            if not landing_url:
                landing_url = url
        return Paper(
            title=clean_text(item.get("title")),
            abstract=clean_text(item.get("abstractText")),
            authors=listify(item.get("authorString")),
            year=parse_int(item.get("pubYear")),
            publication_date=item.get("firstPublicationDate") or "",
            journal_or_source=item.get("journalTitle") or "",
            publisher=item.get("publisher") or "",
            doi=normalize_doi(item.get("doi") or ""),
            pmid=str(item.get("pmid") or ""),
            pmcid=str(item.get("pmcid") or ""),
            url=landing_url,
            landing_page_url=landing_url,
            pdf_url=pdf_url,
            is_open_access=str(item.get("isOpenAccess") or "").upper() == "Y",
            license=item.get("license") or "",
            source_provider=self.name,
            source_record_id=item.get("id") or item.get("pmid") or "",
            citation_count=parse_int(item.get("citedByCount")),
            publication_types=listify(item.get("pubType")),
            raw=item,
        )

