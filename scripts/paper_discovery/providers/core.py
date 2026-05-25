from __future__ import annotations

from typing import Any

from scripts.paper_discovery.config import env_or_config
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, clean_text, listify, parse_int


class CoreProvider(BaseProvider):
    name = "core"
    search_url = "https://api.core.ac.uk/v3/search/works"

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        core_query = query
        if year_from:
            core_query += f" AND yearPublished>={year_from}"
        if year_to:
            core_query += f" AND yearPublished<={year_to}"
        data = self.request_json("POST", self.search_url, json={"q": core_query, "limit": limit}, headers=self.headers())
        results = data.get("results") if isinstance(data, dict) else data
        return [self.to_paper(item) for item in results or []]

    def headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"}
        api_key = env_or_config(self.config, "CORE_API_KEY", "core_api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    def to_paper(self, item: dict[str, Any]) -> Paper:
        download_url = item.get("downloadUrl") or item.get("download_url") or ""
        source_url = item.get("sourceFulltextUrls", [""])[0] if isinstance(item.get("sourceFulltextUrls"), list) and item.get("sourceFulltextUrls") else ""
        identifiers = item.get("identifiers") or []
        doi = item.get("doi") or first_identifier(identifiers, "doi")
        authors = item.get("authors") or []
        author_names = [a.get("name", "") if isinstance(a, dict) else str(a) for a in authors]
        repositories = item.get("repositories") or []
        repository = repositories[0].get("name", "") if repositories and isinstance(repositories[0], dict) else ""
        return Paper(
            title=clean_text(item.get("title")),
            abstract=clean_text(item.get("abstract")),
            authors=[clean_text(a) for a in author_names if clean_text(a)],
            year=parse_int(item.get("yearPublished") or item.get("year")),
            publication_date=item.get("datePublished") or item.get("publishedDate") or "",
            journal_or_source=item.get("journal") or repository,
            publisher=item.get("publisher") or repository,
            doi=normalize_doi(doi or ""),
            core_id=str(item.get("id") or item.get("coreId") or ""),
            url=item.get("sourceUrl") or source_url,
            landing_page_url=item.get("sourceUrl") or source_url,
            pdf_url=download_url,
            is_open_access=bool(download_url or source_url),
            source_provider=self.name,
            source_record_id=str(item.get("id") or item.get("coreId") or ""),
            keywords=listify(item.get("topics")),
            raw=item,
        )


def first_identifier(identifiers: list[Any], kind: str) -> str:
    for identifier in identifiers:
        text = str(identifier)
        if text.lower().startswith(f"{kind}:"):
            return text.split(":", 1)[1]
    return ""

