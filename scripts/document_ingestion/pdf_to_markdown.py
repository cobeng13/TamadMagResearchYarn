from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


MANIFEST_COLUMNS = [
    "paper_id",
    "source_file",
    "output_raw_md",
    "output_cleaned_md",
    "conversion_status",
    "quality_notes",
    "needs_manual_review",
]


@dataclass
class ExtractionResult:
    pages: list[str]
    page_count: int
    encrypted: bool = False


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def slugify(value: str, max_length: int = 100) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return slug[:max_length].rstrip("-") or "document"


def output_paths(project_dir: Path) -> dict[str, Path]:
    base = project_dir / "03_markdown"
    return {
        "raw_dir": base / "raw_md",
        "cleaned_dir": base / "cleaned_md",
        "manifest": base / "ingestion_manifest.csv",
        "log": base / "ingestion_log.md",
    }


def pdf_dir(project_dir: Path) -> Path:
    return project_dir / "02_sources" / "pdf"


def safe_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().split())


def extract_pdf_pages(path: Path) -> ExtractionResult:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError("Missing dependency: install pypdf to extract PDF text.") from exc

    reader = PdfReader(str(path))
    encrypted = bool(getattr(reader, "is_encrypted", False))
    if encrypted:
        try:
            reader.decrypt("")
        except Exception:
            pass
    pages: list[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return ExtractionResult(pages=pages, page_count=len(reader.pages), encrypted=encrypted)


def raw_markdown(source_file: Path, result: ExtractionResult) -> str:
    lines = [
        f"# {source_file.stem}",
        "",
        f"Source file: `{source_file.name}`",
        f"Pages detected: {result.page_count}",
        "",
    ]
    for index, text in enumerate(result.pages, start=1):
        lines.extend([f"<!-- page {index} -->", "", clean_page_raw(text), ""])
    return "\n".join(lines).rstrip() + "\n"


def clean_page_raw(text: str) -> str:
    text = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_extracted_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"<!-- page (\d+) -->", r"\n\n## Page \1\n", text)
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"(?<![.!?:;\n])\n(?!\n|#|[-*]\s|\d+\.\s)", " ", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def quality_notes(result: ExtractionResult) -> tuple[str, str, str]:
    extracted_chars = sum(len(page.strip()) for page in result.pages)
    blank_pages = sum(1 for page in result.pages if not page.strip())
    notes: list[str] = []
    status = "converted"
    manual = "no"
    if result.encrypted:
        notes.append("PDF is encrypted or flagged encrypted; extraction attempted.")
        status = "partial"
        manual = "yes"
    if result.page_count == 0 or extracted_chars == 0:
        return "failed", "No extractable text found; possible scanned/image-only PDF.", "yes"
    if blank_pages:
        notes.append(f"{blank_pages} page(s) had no extractable text.")
        status = "partial"
        manual = "yes"
    if result.page_count and extracted_chars / result.page_count < 500:
        notes.append("Low extracted text volume; check for scanned pages, damaged extraction, or non-article file.")
        status = "partial"
        manual = "yes"
    return status, " ".join(notes) if notes else "Text extracted with page markers.", manual


def process_pdf(source_file: Path, raw_dir: Path, cleaned_dir: Path, overwrite: bool) -> dict[str, str]:
    paper_id = source_file.stem
    filename = f"{slugify(source_file.stem)}.md"
    raw_path = raw_dir / filename
    cleaned_path = cleaned_dir / filename

    if raw_path.exists() and cleaned_path.exists() and not overwrite:
        return {
            "paper_id": paper_id,
            "source_file": str(source_file),
            "output_raw_md": str(raw_path),
            "output_cleaned_md": str(cleaned_path),
            "conversion_status": "converted",
            "quality_notes": "Existing markdown found; skipped because overwrite is false.",
            "needs_manual_review": "no",
        }

    try:
        result = extract_pdf_pages(source_file)
        status, notes, manual = quality_notes(result)
        if status == "failed":
            return {
                "paper_id": paper_id,
                "source_file": str(source_file),
                "output_raw_md": "",
                "output_cleaned_md": "",
                "conversion_status": status,
                "quality_notes": notes,
                "needs_manual_review": manual,
            }
        raw = raw_markdown(source_file, result)
        cleaned = clean_extracted_text(raw)
        raw_dir.mkdir(parents=True, exist_ok=True)
        cleaned_dir.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(raw, encoding="utf-8")
        cleaned_path.write_text(cleaned, encoding="utf-8")
        return {
            "paper_id": paper_id,
            "source_file": str(source_file),
            "output_raw_md": str(raw_path),
            "output_cleaned_md": str(cleaned_path),
            "conversion_status": status,
            "quality_notes": notes,
            "needs_manual_review": manual,
        }
    except Exception as exc:
        return {
            "paper_id": paper_id,
            "source_file": str(source_file),
            "output_raw_md": "",
            "output_cleaned_md": "",
            "conversion_status": "failed",
            "quality_notes": safe_text(exc),
            "needs_manual_review": "yes",
        }


def ingest_pdfs(
    project_dir: Path,
    overwrite: bool = False,
    dry_run: bool = False,
    limit: int | None = None,
) -> dict[str, Any]:
    paths = output_paths(project_dir)
    source_dir = pdf_dir(project_dir)
    pdfs = sorted(source_dir.glob("*.pdf")) if source_dir.exists() else []
    if limit is not None:
        pdfs = pdfs[:limit]

    rows: list[dict[str, str]] = []
    if not dry_run:
        paths["raw_dir"].mkdir(parents=True, exist_ok=True)
        paths["cleaned_dir"].mkdir(parents=True, exist_ok=True)

    if not dry_run:
        for source_file in pdfs:
            rows.append(process_pdf(source_file, paths["raw_dir"], paths["cleaned_dir"], overwrite=overwrite))
        manifest = pd.DataFrame(rows, columns=MANIFEST_COLUMNS).fillna("")
        manifest.to_csv(paths["manifest"], index=False, encoding="utf-8")
        write_log(paths["log"], pdfs, rows)
    else:
        manifest = pd.DataFrame(columns=MANIFEST_COLUMNS)

    converted = sum(1 for row in rows if row["conversion_status"] in {"converted", "partial"})
    failed = sum(1 for row in rows if row["conversion_status"] == "failed")
    manual_review = sum(1 for row in rows if row["needs_manual_review"] == "yes")
    return {
        "files_found": len(pdfs),
        "converted": converted,
        "failed": failed,
        "manual_review": manual_review,
        "manifest": manifest,
        "paths": paths,
    }


def write_log(log_path: Path, pdfs: list[Path], rows: list[dict[str, str]]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    converted = [row for row in rows if row["conversion_status"] in {"converted", "partial"}]
    failed = [row for row in rows if row["conversion_status"] == "failed"]
    manual = [row for row in rows if row["needs_manual_review"] == "yes"]
    with log_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Document Ingestion Log\n\n")
        handle.write(f"Timestamp: {stamp}\n\n")
        handle.write(f"Conversion method: pypdf text extraction with page markers.\n\n")
        handle.write(f"Files found: {len(pdfs)}\n")
        handle.write(f"Files converted: {len(converted)}\n")
        handle.write(f"Files failed: {len(failed)}\n")
        handle.write(f"Manual review warnings: {len(manual)}\n\n")
        if not pdfs:
            handle.write("No source files were available. To be confirmed.\n")
            return
        handle.write("## Files\n\n")
        for row in rows:
            handle.write(f"- `{Path(row['source_file']).name}`: {row['conversion_status']}; manual_review={row['needs_manual_review']}; {row['quality_notes']}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert local PDF sources into raw and cleaned markdown.")
    parser.add_argument("--project", default="projects/sample_project", help="Project directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing markdown outputs")
    parser.add_argument("--dry-run", action="store_true", help="Count PDFs without writing markdown or manifest files")
    parser.add_argument("--limit", type=int, help="Maximum PDFs to process")
    args = parser.parse_args()

    summary = ingest_pdfs(resolve_project(args.project), overwrite=args.overwrite, dry_run=args.dry_run, limit=args.limit)
    print(
        f"files_found={summary['files_found']} converted={summary['converted']} "
        f"failed={summary['failed']} manual_review={summary['manual_review']}"
    )
    if not args.dry_run:
        print(f"manifest_path={summary['paths']['manifest']}")
        print(f"log_path={summary['paths']['log']}")


if __name__ == "__main__":
    main()
