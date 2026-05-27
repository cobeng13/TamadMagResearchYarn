from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pandas as pd

from scripts.paper_discovery.models.paper import normalize_doi


CANONICAL_CANDIDATE_COLUMNS = [
    "candidate_id",
    "title",
    "authors",
    "year",
    "publication_date",
    "journal_or_repository",
    "publisher",
    "source_type",
    "database_or_source",
    "source_providers",
    "search_query",
    "doi",
    "pmid",
    "pmcid",
    "arxiv_id",
    "semantic_scholar_id",
    "openalex_id",
    "core_id",
    "url",
    "pdf_url",
    "is_open_access",
    "oa_status",
    "license",
    "abstract",
    "keywords",
    "fields_of_study",
    "publication_types",
    "citation_count",
    "reference_count",
    "influential_citation_count",
    "ranking_score",
    "access_type",
    "screening_status",
    "screening_reason",
    "human_decision",
    "human_notes",
    "metadata_warnings",
    "date_added",
    "date_updated",
]

HUMAN_REVIEW_COLUMNS = {"screening_status", "screening_reason", "human_decision", "human_notes"}


def validate_candidate_row(row: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for column in CANONICAL_CANDIDATE_COLUMNS:
        if column not in row:
            errors.append(f"Missing column: {column}")
    if str(row.get("screening_status", "")).strip() == "":
        errors.append("screening_status is required")
    return errors


def normalize_candidate_row(row: dict[str, Any]) -> dict[str, str]:
    source = {str(key): value for key, value in row.items()}
    normalized = {column: "" for column in CANONICAL_CANDIDATE_COLUMNS}
    for column in CANONICAL_CANDIDATE_COLUMNS:
        normalized[column] = serialize_value(source.get(column, ""))

    normalized["doi"] = normalize_doi(normalized["doi"])
    normalized["pmcid"] = normalize_pmcid(normalized["pmcid"])
    normalized["authors"] = serialize_list(source.get("authors", normalized["authors"]))
    normalized["source_providers"] = serialize_list(source.get("source_providers", normalized["source_providers"]))
    normalized["keywords"] = serialize_list(source.get("keywords", normalized["keywords"]))
    normalized["fields_of_study"] = serialize_list(source.get("fields_of_study", normalized["fields_of_study"]))
    normalized["publication_types"] = serialize_list(source.get("publication_types", normalized["publication_types"]))
    normalized["is_open_access"] = normalize_bool_string(source.get("is_open_access", normalized["is_open_access"]))

    if not normalized["screening_status"]:
        normalized["screening_status"] = "unscreened"
    if not normalized["candidate_id"]:
        normalized["candidate_id"] = generate_candidate_id(normalized)
    return normalized


def normalize_candidate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=CANONICAL_CANDIDATE_COLUMNS)
    rows = [normalize_candidate_row(row) for row in df.fillna("").to_dict(orient="records")]
    return pd.DataFrame(rows, columns=CANONICAL_CANDIDATE_COLUMNS).fillna("")


def from_paper_model(paper: Any, search_query: str | None = None) -> dict[str, str]:
    row = {
        "title": getattr(paper, "title", ""),
        "abstract": getattr(paper, "abstract", ""),
        "authors": getattr(paper, "authors", []),
        "year": getattr(paper, "year", ""),
        "publication_date": getattr(paper, "publication_date", ""),
        "journal_or_repository": getattr(paper, "journal_or_source", ""),
        "publisher": getattr(paper, "publisher", ""),
        "database_or_source": getattr(paper, "source_provider", ""),
        "source_providers": getattr(paper, "source_providers", []) or [getattr(paper, "source_provider", "")],
        "search_query": search_query or "",
        "doi": getattr(paper, "doi", ""),
        "pmid": getattr(paper, "pmid", ""),
        "pmcid": getattr(paper, "pmcid", ""),
        "arxiv_id": getattr(paper, "arxiv_id", ""),
        "semantic_scholar_id": getattr(paper, "semantic_scholar_id", ""),
        "openalex_id": getattr(paper, "openalex_id", ""),
        "core_id": getattr(paper, "core_id", ""),
        "url": getattr(paper, "url", "") or getattr(paper, "landing_page_url", ""),
        "pdf_url": getattr(paper, "pdf_url", ""),
        "is_open_access": getattr(paper, "is_open_access", ""),
        "oa_status": getattr(paper, "oa_status", ""),
        "license": getattr(paper, "license", ""),
        "keywords": getattr(paper, "keywords", []),
        "fields_of_study": getattr(paper, "fields_of_study", []),
        "publication_types": getattr(paper, "publication_types", []),
        "citation_count": getattr(paper, "citation_count", ""),
        "reference_count": getattr(paper, "reference_count", ""),
        "influential_citation_count": getattr(paper, "influential_citation_count", ""),
        "ranking_score": getattr(paper, "score", ""),
        "access_type": getattr(paper, "oa_status", ""),
        "screening_status": "unscreened",
    }
    return normalize_candidate_row(row)


def from_legacy_openalex_row(row: dict[str, Any]) -> dict[str, str]:
    mapped = {
        "title": row.get("title", ""),
        "authors": row.get("authors", ""),
        "year": row.get("year", ""),
        "journal_or_repository": row.get("source", ""),
        "database_or_source": row.get("database", "OpenAlex"),
        "source_providers": "openalex",
        "doi": row.get("doi", ""),
        "url": row.get("url", ""),
        "openalex_id": row.get("openalex_id", ""),
        "access_type": row.get("access_type", ""),
        "oa_status": row.get("access_type", ""),
        "screening_status": row.get("screening_status", "unscreened"),
        "screening_reason": row.get("reason_for_decision", ""),
        "human_notes": row.get("notes", ""),
        "abstract": row.get("abstract", ""),
    }
    return normalize_candidate_row(mapped)


def from_provider_export_row(row: dict[str, Any]) -> dict[str, str]:
    mapped = {
        "ranking_score": row.get("score", ""),
        "title": row.get("title", ""),
        "year": row.get("year", ""),
        "doi": row.get("doi", ""),
        "pmid": row.get("pmid", ""),
        "pmcid": row.get("pmcid", ""),
        "arxiv_id": row.get("arxiv_id", ""),
        "source_providers": row.get("source_providers", ""),
        "is_open_access": row.get("is_open_access", ""),
        "pdf_url": row.get("pdf_url", ""),
        "citation_count": row.get("citation_count", ""),
        "url": row.get("url", ""),
        "abstract": row.get("abstract", ""),
        "screening_status": row.get("screening_status", "unscreened"),
    }
    for column in CANONICAL_CANDIDATE_COLUMNS:
        if column in row and column not in mapped:
            mapped[column] = row[column]
    return normalize_candidate_row(mapped)


def papers_to_candidate_dataframe(papers: list[Any], search_query: str | None = None) -> pd.DataFrame:
    rows = [from_paper_model(paper, search_query=search_query) for paper in papers]
    return pd.DataFrame(rows, columns=CANONICAL_CANDIDATE_COLUMNS).fillna("")


def merge_candidate_dataframes(existing: pd.DataFrame, incoming: pd.DataFrame, timestamp: str | None = None) -> pd.DataFrame:
    timestamp = timestamp or datetime.now().strftime("%Y-%m-%d")
    existing_norm = normalize_candidate_dataframe(existing)
    incoming_norm = normalize_candidate_dataframe(incoming)
    rows: list[dict[str, str]] = []

    for row in existing_norm.to_dict(orient="records"):
        normalized = normalize_candidate_row(row)
        if not normalized["date_added"]:
            normalized["date_added"] = timestamp
        rows.append(normalized)

    for row in incoming_norm.to_dict(orient="records"):
        normalized = normalize_candidate_row(row)
        match_index = find_matching_row_index(rows, normalized)
        if match_index is None:
            normalized["date_added"] = normalized["date_added"] or timestamp
            normalized["date_updated"] = normalized["date_updated"] or timestamp
            rows.append(normalized)
        else:
            rows[match_index] = merge_candidate_rows(rows[match_index], normalized, timestamp)

    return pd.DataFrame(rows, columns=CANONICAL_CANDIDATE_COLUMNS).fillna("")


def merge_candidate_rows(existing: dict[str, str], incoming: dict[str, str], timestamp: str) -> dict[str, str]:
    merged = normalize_candidate_row(existing)
    incoming = normalize_candidate_row(incoming)
    for column in CANONICAL_CANDIDATE_COLUMNS:
        if column in HUMAN_REVIEW_COLUMNS and merged.get(column):
            continue
        if column == "source_providers":
            merged[column] = merge_semicolon_values(merged.get(column, ""), incoming.get(column, ""))
        elif column in {"keywords", "fields_of_study", "publication_types"}:
            merged[column] = merge_semicolon_values(merged.get(column, ""), incoming.get(column, ""))
        elif not merged.get(column) and incoming.get(column):
            merged[column] = incoming[column]
    merged["date_updated"] = timestamp
    if not merged["date_added"]:
        merged["date_added"] = incoming.get("date_added", "") or timestamp
    return merged


def find_matching_row_index(rows: list[dict[str, str]], incoming: dict[str, str]) -> int | None:
    for idx, row in enumerate(rows):
        if rows_match(row, incoming):
            return idx
    return None


def rows_match(left: dict[str, str], right: dict[str, str]) -> bool:
    left = normalize_candidate_row(left)
    right = normalize_candidate_row(right)
    if left["candidate_id"] and right["candidate_id"] and left["candidate_id"] == right["candidate_id"]:
        return True
    for key in ["doi", "pmid", "pmcid", "arxiv_id"]:
        if left[key] and right[key] and left[key].lower() == right[key].lower():
            return True
    return bool(left["title"] and right["title"] and left["year"] and right["year"] and normalize_title(left["title"]) == normalize_title(right["title"]) and left["year"] == right["year"])


def generate_candidate_id(row: dict[str, Any]) -> str:
    doi = normalize_doi(serialize_value(row.get("doi", "")))
    if doi:
        return f"doi:{doi}"
    pmid = serialize_value(row.get("pmid", ""))
    if pmid:
        return f"pmid:{pmid}"
    pmcid = normalize_pmcid(serialize_value(row.get("pmcid", "")))
    if pmcid:
        return f"pmcid:{pmcid}"
    arxiv_id = serialize_value(row.get("arxiv_id", ""))
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    openalex_id = serialize_value(row.get("openalex_id", ""))
    if openalex_id:
        return f"openalex:{openalex_id}"
    semantic_scholar_id = serialize_value(row.get("semantic_scholar_id", ""))
    if semantic_scholar_id:
        return f"semantic_scholar:{semantic_scholar_id}"
    core_id = serialize_value(row.get("core_id", ""))
    if core_id:
        return f"core:{core_id}"
    title_slug = slugify_text(normalize_title(serialize_value(row.get("title", ""))), max_length=80)
    year = serialize_value(row.get("year", ""))
    return f"title_year:{title_slug}-{year}".rstrip("-") if title_slug else ""


def serialize_value(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, (list, tuple, set)):
        return serialize_list(value)
    return " ".join(str(value).strip().split())


def serialize_list(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        parts = re.split(r"\s*;\s*|\s*,\s*", value)
    elif isinstance(value, (list, tuple, set)):
        parts = [serialize_value(item) for item in value]
    else:
        parts = [serialize_value(value)]
    return "; ".join(dict.fromkeys(part for part in parts if part))


def merge_semicolon_values(left: str, right: str) -> str:
    return serialize_list([*split_semicolon_values(left), *split_semicolon_values(right)])


def split_semicolon_values(value: str) -> list[str]:
    return [part.strip() for part in str(value or "").split(";") if part.strip()]


def normalize_bool_string(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    text = serialize_value(value)
    if text.lower() in {"true", "false"}:
        return text.lower()
    return text


def normalize_pmcid(value: str) -> str:
    text = serialize_value(value)
    if text and not text.upper().startswith("PMC"):
        return f"PMC{text}"
    return text


def normalize_title(title: str) -> str:
    return re.sub(r"\W+", " ", str(title or "").lower()).strip()


def slugify_text(value: str, max_length: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return slug[:max_length].rstrip("-")
