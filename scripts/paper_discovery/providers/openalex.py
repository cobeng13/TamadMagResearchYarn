from __future__ import annotations

from typing import Any

from scripts.paper_discovery.config import env_or_config
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, clean_text, parse_int


class OpenAlexProvider(BaseProvider):
    name = "openalex"
    works_url = "https://api.openalex.org/works"

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        params: dict[str, Any] = {"search": query, "per-page": limit}
        api_key = env_or_config(self.config, "OPENALEX_API_KEY", "openalex_api_key")
        if not api_key:
            raise ValueError("OpenAlex requires OPENALEX_API_KEY or config openalex_api_key.")
        params["api_key"] = api_key
        mailto = env_or_config(self.config, "CONTACT_EMAIL", "openalex_email") or env_or_config(self.config, "OPENALEX_EMAIL", "openalex_email")
        if mailto:
            params["mailto"] = mailto
        filters = []
        if year_from:
            filters.append(f"from_publication_date:{year_from}-01-01")
        if year_to:
            filters.append(f"to_publication_date:{year_to}-12-31")
        if filters:
            params["filter"] = ",".join(filters)
        data = self.request_json("GET", self.works_url, params=params, headers=self.headers())
        return [self.to_paper(item) for item in data.get("results", [])]

    def get_by_doi(self, doi: str) -> Paper | None:
        api_key = env_or_config(self.config, "OPENALEX_API_KEY", "openalex_api_key")
        if not api_key:
            raise ValueError("OpenAlex requires OPENALEX_API_KEY or config openalex_api_key.")
        data = self.request_json("GET", f"{self.works_url}/doi:{normalize_doi(doi)}", params={"api_key": api_key}, headers=self.headers())
        return self.to_paper(data) if data else None

    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"}

    def to_paper(self, work: dict[str, Any]) -> Paper:
        authors = [
            author.get("author", {}).get("display_name", "")
            for author in work.get("authorships", [])
            if author.get("author", {}).get("display_name")
        ]
        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}
        oa = work.get("open_access") or {}
        pdf_url = (primary_location.get("pdf_url") or oa.get("oa_url") or "")
        return Paper(
            title=clean_text(work.get("title")),
            abstract=abstract_from_index(work.get("abstract_inverted_index")),
            authors=authors,
            year=parse_int(work.get("publication_year")),
            publication_date=work.get("publication_date") or "",
            journal_or_source=source.get("display_name") or "",
            publisher=source.get("host_organization_name") or "",
            doi=normalize_doi(work.get("doi") or ""),
            openalex_id=work.get("id") or "",
            url=work.get("doi") or work.get("id") or "",
            landing_page_url=primary_location.get("landing_page_url") or "",
            pdf_url=pdf_url,
            is_open_access=oa.get("is_oa"),
            oa_status=oa.get("oa_status") or "",
            source_provider=self.name,
            source_record_id=work.get("id") or "",
            citation_count=parse_int(work.get("cited_by_count")),
            fields_of_study=[c.get("display_name", "") for c in work.get("concepts", [])[:8] if c.get("display_name")],
            raw=work,
        )


def abstract_from_index(index: dict[str, list[int]] | None) -> str:
    if not index:
        return ""
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for position in positions:
            words.append((position, word))
    return " ".join(word for _, word in sorted(words))

