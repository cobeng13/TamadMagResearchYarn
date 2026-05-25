from __future__ import annotations

import math
import re
from datetime import datetime

from scripts.paper_discovery.models import Paper

BIOMEDICAL_TERMS = {"pubmed", "pmc", "biomedical", "clinical", "health", "medical", "medicine", "radiology", "licensure"}


def rank_papers(papers: list[Paper], query: str) -> list[Paper]:
    for paper in papers:
        paper.score = score_paper(paper, query)
    return sorted(papers, key=lambda paper: paper.score, reverse=True)


def score_paper(paper: Paper, query: str) -> float:
    query_terms = terms(query)
    score = 0.0
    score += overlap(query_terms, terms(paper.title)) * 4.0
    score += overlap(query_terms, terms(paper.abstract)) * 2.0
    if paper.citation_count:
        score += min(math.log1p(paper.citation_count), 6.0)
    if paper.year:
        current_year = datetime.now().year
        if paper.year >= current_year - 5:
            score += 2.0
        elif paper.year >= current_year - 10:
            score += 1.0
    if paper.pdf_url or paper.is_open_access:
        score += 1.5
    if is_biomedical_query(query_terms) and any(provider in paper.source_providers for provider in ["pubmed", "europe_pmc"]):
        score += 1.5
    if not paper.title:
        score -= 3.0
    if not paper.year:
        score -= 1.0
    return round(score, 4)


def terms(value: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", (value or "").lower()) if len(term) > 2}


def overlap(query_terms: set[str], text_terms: set[str]) -> float:
    if not query_terms or not text_terms:
        return 0.0
    return len(query_terms & text_terms) / len(query_terms)


def is_biomedical_query(query_terms: set[str]) -> bool:
    return bool(query_terms & BIOMEDICAL_TERMS)

