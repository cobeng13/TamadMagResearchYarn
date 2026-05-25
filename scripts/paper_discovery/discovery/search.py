from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Any

from scripts.paper_discovery.config import enabled_provider, load_config
from scripts.paper_discovery.discovery.dedupe import dedupe_papers
from scripts.paper_discovery.discovery.rank import rank_papers
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.providers import (
    ArxivProvider,
    CoreProvider,
    CrossrefProvider,
    EuropePmcProvider,
    OpenAlexProvider,
    PubMedProvider,
    SemanticScholarProvider,
)

LOGGER = logging.getLogger(__name__)

PROVIDER_CLASSES = {
    "openalex": OpenAlexProvider,
    "crossref": CrossrefProvider,
    "semantic_scholar": SemanticScholarProvider,
    "pubmed": PubMedProvider,
    "europe_pmc": EuropePmcProvider,
    "arxiv": ArxivProvider,
    "core": CoreProvider,
}


def search_all(
    query: str,
    limit_per_provider: int = 20,
    year_from: int | None = None,
    year_to: int | None = None,
    providers: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> list[Paper]:
    config = config if config is not None else load_config()
    selected = providers or list(PROVIDER_CLASSES)
    collected: list[Paper] = []
    for provider_name in selected:
        normalized = provider_name.strip().lower()
        if normalized not in PROVIDER_CLASSES:
            LOGGER.warning("Unknown provider skipped: %s", provider_name)
            continue
        if providers is None and not enabled_provider(config, normalized):
            continue
        provider = PROVIDER_CLASSES[normalized](config)
        try:
            papers = provider.search(query, limit=limit_per_provider, year_from=year_from, year_to=year_to)
            for paper in papers:
                paper.source_provider = paper.source_provider or normalized
                if normalized not in paper.source_providers:
                    paper.source_providers.append(normalized)
            collected.extend(papers)
            LOGGER.info("Provider %s returned %s papers", normalized, len(papers))
        except Exception as exc:
            LOGGER.exception("Provider %s failed: %s", normalized, exc)
    return rank_papers(dedupe_papers(collected), query)


def export_papers_csv(papers: list[Paper], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = [
        "score",
        "title",
        "year",
        "doi",
        "pmid",
        "pmcid",
        "arxiv_id",
        "source_providers",
        "is_open_access",
        "pdf_url",
        "citation_count",
        "url",
        "abstract",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for paper in papers:
            writer.writerow(
                {
                    "score": paper.score,
                    "title": paper.title,
                    "year": paper.year or "",
                    "doi": paper.doi,
                    "pmid": paper.pmid,
                    "pmcid": paper.pmcid,
                    "arxiv_id": paper.arxiv_id,
                    "source_providers": "; ".join(paper.source_providers),
                    "is_open_access": paper.is_open_access,
                    "pdf_url": paper.pdf_url,
                    "citation_count": paper.citation_count or "",
                    "url": paper.url or paper.landing_page_url,
                    "abstract": paper.abstract,
                }
            )

