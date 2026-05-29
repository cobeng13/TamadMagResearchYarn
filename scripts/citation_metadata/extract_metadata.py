from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


METADATA_COLUMNS = [
    "paper_id",
    "citation_key",
    "title",
    "authors",
    "year",
    "source_type",
    "journal_or_repository",
    "volume",
    "issue",
    "pages",
    "doi",
    "url",
    "publisher",
    "country_or_context",
    "local_source_file",
    "local_markdown_file",
    "metadata_status",
    "notes",
]

KEY_MAP_COLUMNS = [
    "paper_id",
    "citation_key",
    "short_in_text_citation",
    "full_apa_reference",
    "metadata_status",
    "notes",
]

TO_CONFIRM = "To be confirmed."
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


@dataclass
class SourceRecord:
    paper_id: str
    source_file: Path
    markdown_file: Path
    text: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def paths(project_dir: Path) -> dict[str, Path]:
    return {
        "manifest": project_dir / "03_markdown" / "ingestion_manifest.csv",
        "cleaned_dir": project_dir / "03_markdown" / "cleaned_md",
        "candidate": project_dir / "01_literature_search" / "candidate_papers.csv",
        "download_queue": project_dir / "02_sources" / "download_queue.csv",
        "success": project_dir / "02_sources" / "download_results" / "success.csv",
        "metadata_dir": project_dir / "04_metadata",
        "metadata_table": project_dir / "04_metadata" / "metadata_table.csv",
        "key_map": project_dir / "04_metadata" / "citation_key_map.csv",
        "apa": project_dir / "04_metadata" / "references_apa7.md",
        "bib": project_dir / "04_metadata" / "references.bib",
        "issues": project_dir / "04_metadata" / "metadata_issues.md",
    }


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return " ".join(str(value).strip().split())


def normalize_doi(value: Any) -> str:
    text = safe_text(value)
    text = re.sub(r"^https?://(dx\.)?doi\.org/", "", text, flags=re.IGNORECASE)
    text = text.rstrip(".,;)")
    return text.lower()


def normalize_title(value: str) -> str:
    return re.sub(r"\W+", " ", safe_text(value).lower()).strip()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", safe_text(value).lower())


def tokens(value: str) -> set[str]:
    stop = {"a", "an", "and", "as", "for", "in", "of", "on", "the", "to", "with", "using", "from", "pdf"}
    text = re.sub(r"([a-z])([0-9])", r"\1 \2", safe_text(value).lower())
    text = re.sub(r"([0-9])([a-z])", r"\1 \2", text)
    return {part for part in re.findall(r"[a-z0-9]+", text) if (len(part) > 2 or part.isdigit()) and part not in stop}


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("") if path.exists() else pd.DataFrame()


def load_sources(project_dir: Path) -> list[SourceRecord]:
    p = paths(project_dir)
    manifest = load_csv(p["manifest"])
    records: list[SourceRecord] = []
    if not manifest.empty and {"paper_id", "source_file", "output_cleaned_md"}.issubset(manifest.columns):
        for _, row in manifest.iterrows():
            markdown = Path(safe_text(row.get("output_cleaned_md", "")))
            source_file = Path(safe_text(row.get("source_file", "")))
            if markdown.exists():
                records.append(
                    SourceRecord(
                        paper_id=safe_text(row.get("paper_id", "")) or source_file.stem or markdown.stem,
                        source_file=source_file,
                        markdown_file=markdown,
                        text=markdown.read_text(encoding="utf-8", errors="replace"),
                    )
                )
    elif p["cleaned_dir"].exists():
        for markdown in sorted(p["cleaned_dir"].glob("*.md")):
            records.append(SourceRecord(markdown.stem, Path(""), markdown, markdown.read_text(encoding="utf-8", errors="replace")))
    return records


def build_indexes(project_dir: Path) -> dict[str, Any]:
    p = paths(project_dir)
    candidate = load_csv(p["candidate"])
    queue = load_csv(p["download_queue"])
    success = load_csv(p["success"])

    candidate_by_id = {safe_text(row.get("candidate_id", "")): row for _, row in candidate.iterrows()} if not candidate.empty else {}
    candidate_by_doi = {normalize_doi(row.get("doi", "")): row for _, row in candidate.iterrows() if normalize_doi(row.get("doi", ""))} if not candidate.empty else {}
    candidate_rows = [row for _, row in candidate.iterrows()] if not candidate.empty else []
    queue_by_filename = {safe_text(row.get("target_filename", "")): row for _, row in queue.iterrows() if safe_text(row.get("target_filename", ""))} if not queue.empty else {}
    success_by_filename = {safe_text(row.get("filename", "")): row for _, row in success.iterrows() if safe_text(row.get("filename", ""))} if not success.empty else {}
    return {
        "candidate_by_id": candidate_by_id,
        "candidate_by_doi": candidate_by_doi,
        "candidate_rows": candidate_rows,
        "queue_by_filename": queue_by_filename,
        "success_by_filename": success_by_filename,
    }


def first_pages(text: str, max_chars: int = 8000) -> str:
    return str(text or "")[:max_chars]


def scan_doi(text: str) -> str:
    match = DOI_RE.search(text or "")
    return normalize_doi(match.group(0)) if match else ""


def scan_year(text: str) -> str:
    years = [int(match.group(0)) for match in YEAR_RE.finditer(first_pages(text, 12000))]
    likely = [year for year in years if 1900 <= year <= 2030]
    return str(Counter(likely).most_common(1)[0][0]) if likely else ""


def scan_title(text: str, skip_values: list[str] | None = None) -> str:
    skip_slugs = {slug(value) for value in skip_values or [] if value}
    for line in first_pages(text, 4000).splitlines():
        candidate = safe_text(re.sub(r"^#+\s*", "", line))
        if slug(candidate) in skip_slugs:
            continue
        if 20 <= len(candidate) <= 220 and not candidate.lower().startswith(("source file:", "pages detected:", "page ")):
            return candidate
    return ""


def match_candidate(record: SourceRecord, indexes: dict[str, Any]) -> pd.Series | None:
    filename = record.source_file.name
    success = indexes["success_by_filename"].get(filename)
    if success is not None:
        candidate_id = safe_text(success.get("candidate_id", ""))
        if candidate_id in indexes["candidate_by_id"]:
            return indexes["candidate_by_id"][candidate_id]
    queue = indexes["queue_by_filename"].get(filename)
    if queue is not None:
        candidate_id = safe_text(queue.get("candidate_id", ""))
        if candidate_id in indexes["candidate_by_id"]:
            return indexes["candidate_by_id"][candidate_id]
        return queue
    source_slug = slug(record.source_file.stem)
    source_tokens = tokens(record.source_file.stem)
    best_row: pd.Series | None = None
    best_score = 0.0
    for row in indexes["candidate_rows"]:
        title = safe_text(row.get("title", ""))
        title_slug = slug(title)
        if title and title_slug[:40] and (title_slug[:40] in source_slug or (len(source_slug) >= 25 and source_slug[:40] in title_slug)):
            return row
        title_tokens = tokens(title)
        if not title_tokens:
            continue
        shared_title_tokens = len(source_tokens & title_tokens)
        overlap = shared_title_tokens / max(len(source_tokens), 1)
        bonus = 0.0
        author_family = first_author_family(safe_text(row.get("authors", ""))).lower()
        year = safe_text(row.get("year", ""))
        if author_family != "unknown" and author_family in source_tokens:
            bonus += 0.25
        if year and year in source_tokens:
            bonus += 0.25
        score = overlap + bonus
        if score > best_score and ((shared_title_tokens >= 3 and overlap >= 0.45) or bonus >= 0.5):
            best_row = row
            best_score = score
    if best_row is not None:
        return best_row
    text_doi = scan_doi(record.text)
    if text_doi and text_doi in indexes["candidate_by_doi"]:
        return indexes["candidate_by_doi"][text_doi]
    return None


def split_authors(authors: str) -> list[str]:
    text = safe_text(authors)
    if not text:
        return []
    if ";" in text:
        return [part.strip() for part in text.split(";") if part.strip()]
    return [part.strip() for part in re.split(r"\s+and\s+|,\s+(?=[A-Z][A-Za-z'.-]+\s+[A-Z])", text) if part.strip()]


def first_author_family(authors: str) -> str:
    if not authors or safe_text(authors) == TO_CONFIRM:
        return "Unknown"
    items = split_authors(authors)
    if not items:
        return "Unknown"
    first = items[0]
    if "," in first:
        return safe_text(first.split(",", 1)[0])
    parts = first.split()
    return re.sub(r"\W+", "", parts[-1]) if parts else "Unknown"


def title_words(title: str) -> str:
    stop = {"a", "an", "and", "as", "for", "in", "of", "on", "the", "to", "with", "using", "from"}
    words = [re.sub(r"\W+", "", word).title() for word in safe_text(title).split() if word.lower() not in stop]
    words = [word for word in words if word]
    return "".join(words[:4]) or "Source"


def make_key(row: dict[str, str], used: Counter[str]) -> str:
    year = row.get("year") if row.get("year") and row.get("year") != TO_CONFIRM else "YearToConfirm"
    base = f"{first_author_family(row.get('authors', ''))}{year}{title_words(row.get('title', ''))}"
    base = re.sub(r"\W+", "", base) or "UnknownYearToConfirmSource"
    used[base] += 1
    if used[base] == 1:
        return base
    return f"{base}{chr(ord('a') + used[base] - 2)}"


def infer_source_type(row: dict[str, str], text: str) -> str:
    source_type = safe_text(row.get("source_type", ""))
    if source_type:
        return source_type
    if row.get("journal_or_repository") and row.get("journal_or_repository") != TO_CONFIRM:
        return "journal_article"
    haystack = f"{row.get('journal_or_repository', '')} {text[:3000]}".lower()
    if "thesis" in haystack or "dissertation" in haystack:
        return "thesis"
    return TO_CONFIRM


def extract_volume_issue_pages(text: str) -> tuple[str, str, str]:
    sample = first_pages(text, 10000)
    volume = issue = pages = ""
    match = re.search(r"\b(?:vol\.?|volume)\s*(\d+)", sample, re.IGNORECASE)
    if match:
        volume = match.group(1)
    match = re.search(r"\b(?:no\.?|issue)\s*(\d+)", sample, re.IGNORECASE)
    if match:
        issue = match.group(1)
    match = re.search(r"\bpp\.?\s*(\d+\s*[-–]\s*\d+)", sample, re.IGNORECASE)
    if match:
        pages = re.sub(r"\s+", "", match.group(1))
    return volume, issue, pages


def country_context(text: str) -> str:
    sample = first_pages(text, 12000).lower()
    contexts = []
    for name in ["Philippines", "Indonesia", "Malaysia", "Japan", "United States", "Southeast Asia"]:
        if name.lower() in sample:
            contexts.append(name)
    return "; ".join(dict.fromkeys(contexts))


def metadata_from_record(record: SourceRecord, match: pd.Series | None) -> dict[str, str]:
    source: dict[str, str] = {}
    if match is not None:
        source = {str(key): safe_text(value) for key, value in match.items()}
    volume, issue, pages = extract_volume_issue_pages(record.text)
    doi = normalize_doi(source.get("doi", "")) or scan_doi(record.text)
    title = source.get("title", "") or scan_title(record.text, [record.source_file.stem, record.paper_id])
    authors = source.get("authors", "")
    year = source.get("year", "") or scan_year(record.text)
    journal = source.get("journal_or_repository", "") or source.get("database_or_source", "")
    row = {
        "paper_id": source.get("candidate_id", "") or (f"doi:{doi}" if doi else record.paper_id),
        "citation_key": "",
        "title": title or TO_CONFIRM,
        "authors": authors or TO_CONFIRM,
        "year": year or TO_CONFIRM,
        "source_type": "",
        "journal_or_repository": journal or TO_CONFIRM,
        "volume": volume or TO_CONFIRM,
        "issue": issue or TO_CONFIRM,
        "pages": pages or TO_CONFIRM,
        "doi": doi or TO_CONFIRM,
        "url": source.get("url", "") or source.get("pdf_url", "") or TO_CONFIRM,
        "publisher": source.get("publisher", "") or TO_CONFIRM,
        "country_or_context": country_context(record.text) or TO_CONFIRM,
        "local_source_file": str(record.source_file),
        "local_markdown_file": str(record.markdown_file),
        "metadata_status": "",
        "notes": "",
    }
    row["source_type"] = infer_source_type(row, record.text)
    issues = row_issues(row, matched=match is not None)
    row["metadata_status"] = "needs_review" if issues else "complete"
    row["notes"] = "; ".join(issues) if issues else "Deterministic metadata extraction."
    return row


def row_issues(row: dict[str, str], matched: bool) -> list[str]:
    issues = []
    if not matched:
        issues.append("No matching candidate/download metadata found; used local markdown only.")
    for field in ["title", "authors", "year", "journal_or_repository"]:
        if row.get(field) == TO_CONFIRM:
            issues.append(f"Missing {field}.")
    for field in ["volume", "issue", "pages", "doi", "publisher"]:
        if row.get(field) == TO_CONFIRM:
            issues.append(f"{field} to confirm.")
    return issues


def apa_author(authors: str) -> str:
    items = split_authors(authors)
    if not items:
        return TO_CONFIRM
    formatted = []
    for author in items:
        if "," in author:
            formatted.append(author)
            continue
        parts = author.split()
        if len(parts) == 1:
            formatted.append(parts[0])
        else:
            initials = " ".join(f"{part[0]}." for part in parts[:-1] if part)
            formatted.append(f"{parts[-1]}, {initials}")
    if len(formatted) == 1:
        return formatted[0]
    return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"


def apa_reference(row: dict[str, str]) -> str:
    authors = apa_author(row["authors"]) if row["authors"] != TO_CONFIRM else TO_CONFIRM
    year = row["year"] if row["year"] != TO_CONFIRM else TO_CONFIRM
    title = row["title"]
    journal = row["journal_or_repository"]
    volume = "" if row["volume"] == TO_CONFIRM else row["volume"]
    issue = "" if row["issue"] == TO_CONFIRM else f"({row['issue']})"
    pages = "" if row["pages"] == TO_CONFIRM else f", {row['pages']}"
    doi_or_url = ""
    if row["doi"] != TO_CONFIRM:
        doi_or_url = f" https://doi.org/{row['doi']}"
    elif row["url"] != TO_CONFIRM:
        doi_or_url = f" {row['url']}"
    journal_part = f"{journal}, {volume}{issue}{pages}." if journal != TO_CONFIRM else f"{TO_CONFIRM}."
    return f"{authors} ({year}). {title}. {journal_part}{doi_or_url}".strip()


def in_text_citation(row: dict[str, str]) -> str:
    family = first_author_family(row["authors"] if row["authors"] != TO_CONFIRM else "")
    year = row["year"] if row["year"] != TO_CONFIRM else "n.d."
    return f"({family}, {year})"


def bib_type(row: dict[str, str]) -> str:
    source_type = row["source_type"].lower()
    if "thesis" in source_type:
        return "phdthesis"
    if "conference" in source_type:
        return "inproceedings"
    if row["journal_or_repository"] != TO_CONFIRM:
        return "article"
    return "misc"


def bibtex_escape(value: str) -> str:
    return safe_text(value).replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def bibtex_entry(row: dict[str, str]) -> str:
    fields = {
        "title": row["title"],
        "author": " and ".join(split_authors(row["authors"])) if row["authors"] != TO_CONFIRM else "",
        "year": row["year"] if row["year"] != TO_CONFIRM else "",
        "journal": row["journal_or_repository"] if row["journal_or_repository"] != TO_CONFIRM else "",
        "volume": row["volume"] if row["volume"] != TO_CONFIRM else "",
        "number": row["issue"] if row["issue"] != TO_CONFIRM else "",
        "pages": row["pages"] if row["pages"] != TO_CONFIRM else "",
        "doi": row["doi"] if row["doi"] != TO_CONFIRM else "",
        "url": row["url"] if row["url"] != TO_CONFIRM else "",
        "publisher": row["publisher"] if row["publisher"] != TO_CONFIRM else "",
    }
    lines = [f"@{bib_type(row)}{{{row['citation_key']},"]
    for key, value in fields.items():
        if value:
            lines.append(f"  {key} = {{{bibtex_escape(value)}}},")
    lines.append("}")
    return "\n".join(lines)


def build_outputs(rows: list[dict[str, str]], project_dir: Path, overwrite: bool = False) -> dict[str, Any]:
    p = paths(project_dir)
    p["metadata_dir"].mkdir(parents=True, exist_ok=True)
    for output in [p["metadata_table"], p["key_map"], p["apa"], p["bib"], p["issues"]]:
        if output.exists() and not overwrite:
            raise FileExistsError(f"Refusing to overwrite existing metadata output without --overwrite: {output}")

    metadata = pd.DataFrame(rows, columns=METADATA_COLUMNS).fillna("")
    metadata.to_csv(p["metadata_table"], index=False, encoding="utf-8")

    key_rows = [
        {
            "paper_id": row["paper_id"],
            "citation_key": row["citation_key"],
            "short_in_text_citation": in_text_citation(row),
            "full_apa_reference": apa_reference(row),
            "metadata_status": row["metadata_status"],
            "notes": row["notes"],
        }
        for row in rows
    ]
    pd.DataFrame(key_rows, columns=KEY_MAP_COLUMNS).to_csv(p["key_map"], index=False, encoding="utf-8")
    write_apa(p["apa"], rows)
    write_bib(p["bib"], rows)
    write_issues(p["issues"], rows)
    return {"metadata": metadata, "paths": p}


def write_apa(path: Path, rows: list[dict[str, str]]) -> None:
    complete = sorted([row for row in rows if row["metadata_status"] == "complete"], key=lambda row: row["citation_key"])
    incomplete = sorted([row for row in rows if row["metadata_status"] != "complete"], key=lambda row: row["citation_key"])
    lines = ["# APA 7 References", ""]
    for row in complete:
        lines.append(f"- {apa_reference(row)}")
    lines.extend(["", "## Metadata To Confirm", ""])
    for row in incomplete:
        lines.append(f"- Not final-ready: {apa_reference(row)}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_bib(path: Path, rows: list[dict[str, str]]) -> None:
    useful = [row for row in rows if row["title"] != TO_CONFIRM and (row["authors"] != TO_CONFIRM or row["doi"] != TO_CONFIRM or row["url"] != TO_CONFIRM)]
    path.write_text("\n\n".join(bibtex_entry(row) for row in useful).rstrip() + ("\n" if useful else ""), encoding="utf-8")


def write_issues(path: Path, rows: list[dict[str, str]]) -> None:
    lines = ["# Metadata Issues", ""]
    if not rows:
        lines.append("No source records were available. To be confirmed.")
    else:
        for row in rows:
            if row["metadata_status"] != "complete":
                lines.append(f"- `{row['citation_key']}` / `{row['paper_id']}`: {row['notes']}")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def extract_metadata(project_dir: Path, overwrite: bool = False, dry_run: bool = False, limit: int | None = None) -> dict[str, Any]:
    records = load_sources(project_dir)
    if limit is not None:
        records = records[:limit]
    indexes = build_indexes(project_dir)
    used: Counter[str] = Counter()
    rows: list[dict[str, str]] = []
    for record in records:
        row = metadata_from_record(record, match_candidate(record, indexes))
        row["citation_key"] = make_key(row, used)
        rows.append(row)
    add_duplicate_notes(rows)
    if dry_run:
        return {"records": len(records), "needs_review": sum(1 for row in rows if row["metadata_status"] != "complete"), "rows": rows, "paths": paths(project_dir)}
    output = build_outputs(rows, project_dir, overwrite=overwrite)
    return {"records": len(records), "needs_review": sum(1 for row in rows if row["metadata_status"] != "complete"), "rows": rows, "paths": output["paths"]}


def add_duplicate_notes(rows: list[dict[str, str]]) -> None:
    doi_counts = Counter(row["doi"] for row in rows if row.get("doi") and row["doi"] != TO_CONFIRM)
    for row in rows:
        doi = row.get("doi", "")
        if doi and doi != TO_CONFIRM and doi_counts[doi] > 1:
            note = f"Possible duplicate DOI appears in {doi_counts[doi]} local source records."
            row["notes"] = f"{row['notes']}; {note}" if row.get("notes") else note
            row["metadata_status"] = "needs_review"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract deterministic citation metadata from local markdown and project CSVs.")
    parser.add_argument("--project", default="projects/sample_project", help="Project directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing 04_metadata outputs")
    parser.add_argument("--dry-run", action="store_true", help="Inspect records without writing outputs")
    parser.add_argument("--limit", type=int, help="Maximum records to process")
    args = parser.parse_args()
    summary = extract_metadata(resolve_project(args.project), overwrite=args.overwrite, dry_run=args.dry_run, limit=args.limit)
    print(f"records={summary['records']} needs_review={summary['needs_review']}")
    if not args.dry_run:
        print(f"metadata_table={summary['paths']['metadata_table']}")
        print(f"references_apa7={summary['paths']['apa']}")


if __name__ == "__main__":
    main()
