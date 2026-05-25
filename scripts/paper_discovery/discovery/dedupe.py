from __future__ import annotations

import difflib
import re

from scripts.paper_discovery.models import Paper


def dedupe_papers(papers: list[Paper]) -> list[Paper]:
    merged: list[Paper] = []
    for paper in papers:
        match = find_duplicate(merged, paper)
        if match is None:
            merged.append(paper)
        else:
            merge_paper(match, paper)
    return merged


def find_duplicate(existing: list[Paper], paper: Paper) -> Paper | None:
    for candidate in existing:
        if paper.doi and candidate.doi and paper.doi == candidate.doi:
            return candidate
        if paper.pmid and candidate.pmid and paper.pmid == candidate.pmid:
            return candidate
        if paper.pmcid and candidate.pmcid and paper.pmcid.upper() == candidate.pmcid.upper():
            return candidate
        if paper.arxiv_id and candidate.arxiv_id and paper.arxiv_id == candidate.arxiv_id:
            return candidate
        if paper.year and candidate.year and paper.year == candidate.year and normalized_title(paper.title) == normalized_title(candidate.title):
            return candidate
        if paper.title and candidate.title and title_similarity(paper.title, candidate.title) >= 0.94:
            return candidate
    return None


def merge_paper(target: Paper, incoming: Paper) -> Paper:
    for attr in [
        "doi",
        "pmid",
        "pmcid",
        "arxiv_id",
        "semantic_scholar_id",
        "openalex_id",
        "core_id",
        "url",
        "landing_page_url",
        "oa_status",
        "license",
        "journal_or_source",
        "publisher",
        "publication_date",
    ]:
        if not getattr(target, attr) and getattr(incoming, attr):
            setattr(target, attr, getattr(incoming, attr))
    if incoming.abstract and len(incoming.abstract) > len(target.abstract):
        target.abstract = incoming.abstract
    if incoming.pdf_url and not target.pdf_url:
        target.pdf_url = incoming.pdf_url
    if incoming.is_open_access is True:
        target.is_open_access = True
    if incoming.citation_count is not None and (target.citation_count is None or incoming.citation_count > target.citation_count):
        target.citation_count = incoming.citation_count
    if incoming.reference_count is not None and target.reference_count is None:
        target.reference_count = incoming.reference_count
    if incoming.influential_citation_count is not None and target.influential_citation_count is None:
        target.influential_citation_count = incoming.influential_citation_count
    target.authors = target.authors or incoming.authors
    target.fields_of_study = sorted(set(target.fields_of_study + incoming.fields_of_study))
    target.keywords = sorted(set(target.keywords + incoming.keywords))
    target.publication_types = sorted(set(target.publication_types + incoming.publication_types))
    for provider in incoming.source_providers or [incoming.source_provider]:
        if provider and provider not in target.source_providers:
            target.source_providers.append(provider)
    target.raw_by_provider.update(incoming.raw_by_provider)
    if incoming.source_provider and incoming.raw:
        target.raw_by_provider[incoming.source_provider] = incoming.raw
    return target


def normalized_title(title: str) -> str:
    return re.sub(r"\W+", " ", title.lower()).strip()


def title_similarity(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, normalized_title(left), normalized_title(right)).ratio()

