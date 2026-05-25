from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any

from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, RateLimit, clean_text, parse_int

ATOM = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivProvider(BaseProvider):
    name = "arxiv"
    api_url = "https://export.arxiv.org/api/query"

    def default_min_interval(self) -> float:
        return 3.0

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.rate_limit = RateLimit(3.0)

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        params = {"search_query": f"all:{query}", "start": 0, "max_results": limit}
        response = self.request("GET", self.api_url, params=params, headers={"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"})
        papers = [self.entry_to_paper(entry) for entry in ET.fromstring(response.text).findall("a:entry", ATOM)]
        if year_from or year_to:
            papers = [p for p in papers if p.year and (year_from is None or p.year >= year_from) and (year_to is None or p.year <= year_to)]
        return papers

    def get_by_id(self, identifier: str) -> Paper | None:
        response = self.request("GET", self.api_url, params={"id_list": identifier}, headers={"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"})
        entries = ET.fromstring(response.text).findall("a:entry", ATOM)
        return self.entry_to_paper(entries[0]) if entries else None

    def entry_to_paper(self, entry: ET.Element) -> Paper:
        entry_id = clean_text(find_text(entry, "a:id"))
        arxiv_id = entry_id.rsplit("/", 1)[-1]
        pdf_url = ""
        landing_url = entry_id
        for link in entry.findall("a:link", ATOM):
            href = link.attrib.get("href", "")
            if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
                pdf_url = href
            if link.attrib.get("rel") == "alternate":
                landing_url = href
        published = find_text(entry, "a:published")
        categories = [cat.attrib.get("term", "") for cat in entry.findall("a:category", ATOM) if cat.attrib.get("term")]
        return Paper(
            title=clean_text(find_text(entry, "a:title")),
            abstract=clean_text(find_text(entry, "a:summary")),
            authors=[clean_text(find_text(author, "a:name")) for author in entry.findall("a:author", ATOM)],
            year=parse_int(published[:4]),
            publication_date=published[:10],
            doi=normalize_doi(find_text(entry, "arxiv:doi")),
            arxiv_id=arxiv_id,
            url=landing_url,
            landing_page_url=landing_url,
            pdf_url=pdf_url,
            is_open_access=True,
            oa_status="green",
            source_provider=self.name,
            source_record_id=arxiv_id,
            fields_of_study=categories,
            raw={"id": entry_id, "updated": find_text(entry, "a:updated"), "categories": categories},
        )


def find_text(entry: ET.Element, path: str) -> str:
    node = entry.find(path, ATOM)
    return node.text or "" if node is not None else ""


def normalize_arxiv_id(value: str) -> str:
    value = value.strip()
    value = re.sub(r"^https?://arxiv\.org/abs/", "", value)
    value = re.sub(r"^arxiv:", "", value, flags=re.I)
    return value

