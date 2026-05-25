from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Paper:
    title: str = ""
    abstract: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    publication_date: str = ""
    journal_or_source: str = ""
    publisher: str = ""
    doi: str = ""
    pmid: str = ""
    pmcid: str = ""
    arxiv_id: str = ""
    semantic_scholar_id: str = ""
    openalex_id: str = ""
    core_id: str = ""
    url: str = ""
    landing_page_url: str = ""
    pdf_url: str = ""
    is_open_access: bool | None = None
    oa_status: str = ""
    license: str = ""
    source_provider: str = ""
    source_record_id: str = ""
    source_providers: list[str] = field(default_factory=list)
    citation_count: int | None = None
    reference_count: int | None = None
    influential_citation_count: int | None = None
    fields_of_study: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    publication_types: list[str] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
    raw_by_provider: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0

    def __post_init__(self) -> None:
        if self.doi:
            self.doi = normalize_doi(self.doi)
        if self.pmcid and not self.pmcid.upper().startswith("PMC"):
            self.pmcid = f"PMC{self.pmcid}"
        if self.source_provider and self.source_provider not in self.source_providers:
            self.source_providers.append(self.source_provider)
        if self.source_provider and self.raw and self.source_provider not in self.raw_by_provider:
            self.raw_by_provider[self.source_provider] = self.raw


def normalize_doi(value: str) -> str:
    doi = (value or "").strip()
    doi = doi.removeprefix("https://doi.org/")
    doi = doi.removeprefix("http://doi.org/")
    doi = doi.removeprefix("https://dx.doi.org/")
    doi = doi.removeprefix("http://dx.doi.org/")
    if doi.lower().startswith("doi:"):
        doi = doi[4:].strip()
    return doi.lower()

