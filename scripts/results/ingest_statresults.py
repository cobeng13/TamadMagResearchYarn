from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ai.logging import write_ai_run_log


DEFAULT_PROJECT = Path("projects/sample_project")
MANIFEST_COLUMNS = [
    "result_file_id",
    "source_path",
    "filename",
    "file_type",
    "size_bytes",
    "modified_at",
    "rows_detected",
    "columns_detected",
    "extraction_status",
    "extraction_warning",
    "included_in_compiled",
    "notes",
]
EXTRACTION_STATUSES = {"extracted", "skipped_unsupported", "skipped_empty", "failed", "to_be_confirmed"}
TEXT_TYPES = {".md", ".txt"}
TABLE_TYPES = {".csv", ".tsv"}
SUPPORTED_TYPES = TEXT_TYPES | TABLE_TYPES | {".json", ".xlsx", ".xls", ".docx", ".pdf"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def paths(project_dir: Path, statresults_dir: Path | None = None) -> dict[str, Path]:
    stat_dir = statresults_dir or project_dir / "statresults"
    if not stat_dir.is_absolute():
        stat_dir = repo_root() / stat_dir
    return {
        "statresults": stat_dir,
        "raw_tables": project_dir / "input" / "raw_tables",
        "input": project_dir / "input",
        "manifest": project_dir / "input" / "statistical_results_manifest.csv",
        "compiled": project_dir / "input" / "statistical_results_compiled.md",
        "availability": project_dir / "input" / "results_availability.md",
        "log": project_dir / "logs" / "statresults_ingest_log.md",
    }


def output_files(p: dict[str, Path]) -> list[Path]:
    return [p["manifest"], p["compiled"], p["availability"]]


def backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = path.with_suffix(f".{stamp}.bak{path.suffix}")
    out.write_bytes(path.read_bytes())
    return out


def backup_existing(files: list[Path]) -> list[Path]:
    backups: list[Path] = []
    for path in files:
        backed = backup(path)
        if backed:
            backups.append(backed)
    return backups


def compact(text: str, max_chars: int | None) -> tuple[str, bool]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if max_chars and len(normalized) > max_chars:
        return normalized[:max_chars] + "\n\n[Truncated by --max-file-chars.]", True
    return normalized, False


def read_text(path: Path, max_chars: int | None) -> tuple[str, int, int, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    extracted, truncated = compact(text, max_chars)
    warning = "Truncated by --max-file-chars." if truncated else ""
    return extracted, "", "", warning


def read_table(path: Path, max_chars: int | None) -> tuple[str, int, int, str]:
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    df = pd.read_csv(path, sep=sep, dtype=str).fillna("")
    preview = df.head(100).to_csv(index=False)
    extracted, truncated = compact(preview, max_chars)
    warning = "Table preview limited to first 100 rows."
    if truncated:
        warning += " Truncated by --max-file-chars."
    return extracted, int(df.shape[0]), int(df.shape[1]), warning


def read_json(path: Path, max_chars: int | None) -> tuple[str, int, int, str]:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    text = json.dumps(data, indent=2, ensure_ascii=False)
    rows = len(data) if isinstance(data, list) else ""
    cols = len(data[0]) if isinstance(data, list) and data and isinstance(data[0], dict) else (len(data) if isinstance(data, dict) else "")
    extracted, truncated = compact(text, max_chars)
    warning = "Truncated by --max-file-chars." if truncated else ""
    return extracted, rows, cols, warning


def read_xlsx(path: Path, max_chars: int | None) -> tuple[str, int, int, str]:
    try:
        book = pd.read_excel(path, sheet_name=None, dtype=str)
    except ImportError as exc:
        raise RuntimeError(f"xlsx support requires an installed Excel dependency: {exc}") from exc
    parts: list[str] = []
    rows = 0
    cols = 0
    for sheet, df in book.items():
        df = df.fillna("")
        rows += int(df.shape[0])
        cols = max(cols, int(df.shape[1]))
        parts.append(f"## Sheet: {sheet}\n\n{df.head(100).to_csv(index=False)}")
    extracted, truncated = compact("\n\n".join(parts), max_chars)
    warning = "Excel preview limited to first 100 rows per sheet."
    if truncated:
        warning += " Truncated by --max-file-chars."
    return extracted, rows, cols, warning


def read_docx(path: Path, max_chars: int | None) -> tuple[str, int, int, str]:
    try:
        from docx import Document  # type: ignore
    except ImportError as exc:
        raise RuntimeError(f"docx support requires python-docx: {exc}") from exc
    doc = Document(str(path))
    text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
    extracted, truncated = compact(text, max_chars)
    warning = "Truncated by --max-file-chars." if truncated else ""
    return extracted, "", "", warning


def extract_file(path: Path, max_chars: int | None) -> tuple[str, Any, Any, str, str]:
    suffix = path.suffix.lower()
    if path.stat().st_size == 0:
        return "", "", "", "skipped_empty", "File is empty."
    try:
        if suffix in TEXT_TYPES:
            content, rows, cols, warning = read_text(path, max_chars)
        elif suffix in TABLE_TYPES:
            content, rows, cols, warning = read_table(path, max_chars)
        elif suffix == ".json":
            content, rows, cols, warning = read_json(path, max_chars)
        elif suffix == ".xlsx":
            content, rows, cols, warning = read_xlsx(path, max_chars)
        elif suffix == ".docx":
            content, rows, cols, warning = read_docx(path, max_chars)
        elif suffix == ".xls":
            return "", "", "", "skipped_unsupported", "Legacy .xls extraction is not supported unless project dependencies add it; export to .xlsx, .csv, or .md."
        elif suffix == ".pdf":
            return "", "", "", "skipped_unsupported", "PDF OCR/text extraction is not supported here; export to text, CSV, or markdown first."
        else:
            return "", "", "", "skipped_unsupported", "Unsupported file type."
        return content, rows, cols, "extracted" if content.strip() else "skipped_empty", warning
    except Exception as exc:
        return "", "", "", "failed", str(exc)


def discover_files(stat_dir: Path, raw_tables: Path, include_raw_tables: bool) -> list[Path]:
    files: list[Path] = []
    if stat_dir.exists():
        files.extend(path for path in sorted(stat_dir.rglob("*")) if path.is_file())
    if include_raw_tables and raw_tables.exists():
        files.extend(path for path in sorted(raw_tables.rglob("*")) if path.is_file())
    return files


def render_compiled(rows: list[dict[str, Any]], contents: dict[str, str]) -> str:
    lines = ["# Statistical Results Compiled From statresults/", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    extracted = sum(1 for row in rows if row["extraction_status"] == "extracted")
    skipped = len(rows) - extracted
    lines.extend(["## Source Manifest Summary", "", f"- Files listed: {len(rows)}", f"- Files extracted: {extracted}", f"- Files skipped/failed: {skipped}", ""])
    for row in rows:
        lines.extend([f"## File: {row['filename']}", "", f"Source path: {row['source_path']}", f"Extraction status: {row['extraction_status']}", ""])
        if row["extraction_warning"]:
            lines.extend([f"Extraction warning: {row['extraction_warning']}", ""])
        lines.extend(["### Extracted Content", ""])
        content = contents.get(row["result_file_id"], "").strip()
        lines.append(content if content else "No extracted content.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_availability(rows: list[dict[str, Any]]) -> str:
    extracted = [row for row in rows if row["extraction_status"] == "extracted"]
    skipped = [row for row in rows if row["extraction_status"] != "extracted"]
    status = "ready" if extracted and not skipped else ("partial" if extracted else "unavailable")
    lines = ["# Results Availability", "", f"Generated/applied: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "", "## Status", "", status, ""]
    lines.extend(["## Available Statistical Input Files", ""])
    lines.extend([f"- {row['filename']} ({row['source_path']})" for row in extracted] or ["- none"])
    lines.extend(["", "## Files Skipped", ""])
    lines.extend([f"- {row['filename']}: {row['extraction_status']} - {row['extraction_warning']}" for row in skipped] or ["- none"])
    lines.extend(["", "## Missing or Unsupported Files", ""])
    lines.extend([f"- {row['source_path']}" for row in skipped] or ["- none"])
    lines.extend(["", "## Recommended Next Step", ""])
    if extracted:
        lines.append("Run Stage 10A AI interpretation after reviewing the compiled statistical results.")
    else:
        lines.append("Add AI-readable statistical output files to statresults/ as .md, .txt, .csv, .tsv, .json, or supported .xlsx files.")
    return "\n".join(lines).rstrip() + "\n"


def run_ingest(
    project_dir: Path,
    statresults_dir: Path | None,
    overwrite: bool,
    no_backup: bool,
    strict: bool,
    include_raw_tables: bool,
    max_file_chars: int | None,
) -> dict[str, Any]:
    p = paths(project_dir, statresults_dir)
    p["input"].mkdir(parents=True, exist_ok=True)
    existing = [path for path in output_files(p) if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing results ingest outputs without --overwrite: {', '.join(str(path) for path in existing)}")
    backups = [] if no_backup else backup_existing(existing)
    warnings: list[str] = []
    if not p["statresults"].exists():
        message = f"Missing statresults folder: {p['statresults']}"
        if strict:
            raise FileNotFoundError(message)
        warnings.append(message)
    files = discover_files(p["statresults"], p["raw_tables"], include_raw_tables)
    if not files:
        message = "No statistical result files were found."
        if strict:
            raise FileNotFoundError(message)
        warnings.append(message)
    rows: list[dict[str, Any]] = []
    contents: dict[str, str] = {}
    for index, file_path in enumerate(files, start=1):
        result_id = f"STAT-{index:04d}"
        content, rows_detected, columns_detected, status, warning = extract_file(file_path, max_file_chars)
        if warning:
            warnings.append(f"{file_path.name}: {warning}")
        rows.append({
            "result_file_id": result_id,
            "source_path": str(file_path),
            "filename": file_path.name,
            "file_type": file_path.suffix.lower(),
            "size_bytes": file_path.stat().st_size,
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "rows_detected": rows_detected,
            "columns_detected": columns_detected,
            "extraction_status": status if status in EXTRACTION_STATUSES else "to_be_confirmed",
            "extraction_warning": warning,
            "included_in_compiled": "yes" if status == "extracted" else "no",
            "notes": "",
        })
        if status == "extracted":
            contents[result_id] = content
    pd.DataFrame(rows, columns=MANIFEST_COLUMNS).to_csv(p["manifest"], index=False, encoding="utf-8")
    p["compiled"].write_text(render_compiled(rows, contents), encoding="utf-8")
    p["availability"].write_text(render_availability(rows), encoding="utf-8")
    write_ai_run_log(
        p["log"],
        task_name="stage10a_statresults_ingest",
        model="deterministic",
        input_paths=files,
        output_paths=[*output_files(p), p["log"]],
        counts={
            "project_path": project_dir,
            "statresults_dir": p["statresults"],
            "files_discovered": len(files),
            "files_extracted": sum(1 for row in rows if row["extraction_status"] == "extracted"),
            "include_raw_tables": str(include_raw_tables).lower(),
            "overwrite": str(overwrite).lower(),
        },
        errors=warnings,
        prompt_version="statresults_ingest_v1",
    )
    return {"rows": len(rows), "extracted": sum(1 for row in rows if row["extraction_status"] == "extracted"), "warnings": warnings, "backups": backups, "paths": p}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile AI-readable statistical output files from statresults/.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT))
    parser.add_argument("--statresults-dir")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--no-backup", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--include-raw-tables", action="store_true")
    parser.add_argument("--max-file-chars", type=int)
    args = parser.parse_args()
    project = resolve_project(args.project)
    result = run_ingest(
        project,
        Path(args.statresults_dir) if args.statresults_dir else None,
        args.overwrite,
        args.no_backup,
        args.strict,
        args.include_raw_tables,
        args.max_file_chars,
    )
    print(f"files={result['rows']} extracted={result['extracted']}")
    print(f"compiled={result['paths']['compiled']}")


if __name__ == "__main__":
    main()
