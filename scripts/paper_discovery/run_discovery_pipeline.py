from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pandas as pd


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    return len(pd.read_csv(path, dtype=str).fillna(""))


def count_status(path: Path, column: str, value: str) -> int:
    if not path.exists():
        return 0
    df = pd.read_csv(path, dtype=str).fillna("")
    if column not in df.columns:
        return 0
    return int((df[column] == value).sum())


def run_step(script: str, args: list[str]) -> tuple[int, str]:
    command = [sys.executable, str(Path(__file__).with_name(script)), *args]
    completed = subprocess.run(command, cwd=repo_root(), text=True, capture_output=True, check=False)
    output = "\n".join(part for part in [completed.stdout.strip(), completed.stderr.strip()] if part)
    return completed.returncode, output


def main() -> None:
    parser = argparse.ArgumentParser(description="Run paper discovery, enrichment, OA lookup, and PDF download.")
    parser.add_argument("--project", default="projects/sample_project", help="Project directory")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum OpenAlex results per query")
    parser.add_argument("--skip-download", action="store_true", help="Skip PDF download step")
    parser.add_argument("--force", action="store_true", help="Re-download existing PDFs")
    parser.add_argument("--config", type=Path, help="Path to config.yaml")
    args = parser.parse_args()

    project_dir = Path(args.project)
    if not project_dir.is_absolute():
        project_dir = repo_root() / project_dir

    common = ["--project", str(project_dir)]
    if args.config:
        common.extend(["--config", str(args.config)])

    steps: list[tuple[str, list[str]]] = [
        ("search_openalex.py", [*common, "--max-results", str(args.max_results)]),
        ("enrich_crossref.py", common),
        ("find_oa_pdfs.py", common),
    ]
    if not args.skip_download:
        download_args = [*common]
        if args.force:
            download_args.append("--force")
        steps.append(("download_pdfs.py", download_args))

    failures = 0
    for script, step_args in steps:
        code, output = run_step(script, step_args)
        print(f"\n[{script}]\n{output}")
        if code != 0:
            failures += 1
            print(f"Step failed with exit code {code}; continuing to summary.")
            break

    candidate_path = project_dir / "01_literature_search" / "candidate_papers.csv"
    queue_path = project_dir / "02_sources" / "download_queue.csv"
    candidates = count_rows(candidate_path)
    oa_records = count_rows(queue_path)
    downloaded = count_status(queue_path, "download_status", "downloaded")
    download_failures = count_status(queue_path, "download_status", "failed")

    print("\nSummary")
    print(f"candidate papers found: {candidates}")
    print(f"deduplicated count: {candidates}")
    print(f"OA records found: {oa_records}")
    print(f"PDFs downloaded: {downloaded}")
    print(f"failures: {failures + download_failures}")


if __name__ == "__main__":
    main()
