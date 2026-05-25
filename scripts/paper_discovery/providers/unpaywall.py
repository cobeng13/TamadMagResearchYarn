from __future__ import annotations

from typing import Any

from scripts.paper_discovery.config import env_or_config
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider


class UnpaywallProvider(BaseProvider):
    name = "unpaywall"
    api_url = "https://api.unpaywall.org/v2"

    def get_by_doi(self, doi: str) -> Paper | None:
        email = env_or_config(self.config, "CONTACT_EMAIL", "unpaywall_email") or env_or_config(self.config, "UNPAYWALL_EMAIL", "unpaywall_email")
        if not email:
            raise ValueError("Unpaywall requires CONTACT_EMAIL, UNPAYWALL_EMAIL, or config unpaywall_email.")
        data = self.request_json("GET", f"{self.api_url}/{normalize_doi(doi)}", params={"email": email}, headers=self.headers())
        return self.to_paper(data) if data else None

    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"}

    def to_paper(self, data: dict[str, Any]) -> Paper:
        location = best_location(data) or {}
        return Paper(
            title=data.get("title") or "",
            doi=normalize_doi(data.get("doi") or ""),
            landing_page_url=location.get("url") or location.get("url_for_landing_page") or data.get("doi_url") or "",
            pdf_url=location.get("url_for_pdf") or "",
            is_open_access=data.get("is_oa"),
            oa_status=data.get("oa_status") or "",
            license=location.get("license") or "",
            source_provider=self.name,
            source_record_id=data.get("doi") or "",
            raw=data,
        )


def best_location(data: dict[str, Any]) -> dict[str, Any] | None:
    locations = []
    if data.get("best_oa_location"):
        locations.append(data["best_oa_location"])
    locations.extend(data.get("oa_locations") or [])
    for location in locations:
        if location.get("url_for_pdf") or location.get("url") or location.get("url_for_landing_page"):
            return location
    return None

