from __future__ import annotations

from typing import Any

from scripts.paper_discovery.config import env_or_config
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, clean_text, parse_int


class CrossrefProvider(BaseProvider):
    name = "crossref"
    works_url = "https://api.crossref.org/works"

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        params: dict[str, Any] = {"query.bibliographic": query, "rows": limit}
        if year_from:
            params["filter"] = f"from-pub-date:{year_from}"
            if year_to:
                params["filter"] += f",until-pub-date:{year_to}"
        elif year_to:
            params["filter"] = f"until-pub-date:{year_to}"
        params.update(self.polite_params())
        data = self.request_json("GET", self.works_url, params=params, headers=self.headers())
        return [self.to_paper(item) for item in data.get("message", {}).get("items", [])]

    def get_by_doi(self, doi: str) -> Paper | None:
        data = self.request_json("GET", f"{self.works_url}/{normalize_doi(doi)}", params=self.polite_params(), headers=self.headers())
        item = data.get("message", {})
        return self.to_paper(item) if item else None

    def polite_params(self) -> dict[str, str]:
        email = env_or_config(self.config, "CONTACT_EMAIL", "crossref_email") or env_or_config(self.config, "CROSSREF_EMAIL", "crossref_email")
        return {"mailto": email} if email else {}

    def headers(self) -> dict[str, str]:
        headers = {"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"}
        token = env_or_config(self.config, "CROSSREF_PLUS_API_KEY", "crossref_plus_api_key")
        if token:
            headers["Crossref-Plus-API-Token"] = f"Bearer {token}"
        return headers

    def to_paper(self, item: dict[str, Any]) -> Paper:
        authors = [
            clean_text(" ".join(part for part in [author.get("given", ""), author.get("family", "")] if part))
            for author in item.get("author", [])
        ]
        date_parts = (item.get("published-print") or item.get("published-online") or item.get("issued") or {}).get("date-parts") or []
        pub_date = "-".join(str(part) for part in date_parts[0]) if date_parts and date_parts[0] else ""
        title = (item.get("title") or [""])[0]
        return Paper(
            title=clean_text(title),
            abstract=clean_text(item.get("abstract")),
            authors=authors,
            year=parse_int(date_parts[0][0] if date_parts and date_parts[0] else None),
            publication_date=pub_date,
            journal_or_source=(item.get("container-title") or [""])[0],
            publisher=item.get("publisher") or "",
            doi=normalize_doi(item.get("DOI") or ""),
            url=item.get("URL") or "",
            source_provider=self.name,
            source_record_id=item.get("DOI") or item.get("URL") or "",
            citation_count=parse_int(item.get("is-referenced-by-count")),
            reference_count=parse_int(item.get("reference-count")),
            publication_types=item.get("type", "").split() if item.get("type") else [],
            raw=item,
        )

