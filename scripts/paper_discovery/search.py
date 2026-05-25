from __future__ import annotations

import argparse
import logging
from pathlib import Path

from scripts.paper_discovery.config import load_config
from scripts.paper_discovery.discovery.search import export_papers_csv, search_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Search scholarly providers and return normalized candidate papers.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=20, help="Results per provider")
    parser.add_argument("--providers", help="Comma-separated provider names")
    parser.add_argument("--year-from", type=int)
    parser.add_argument("--year-to", type=int)
    parser.add_argument("--export", type=Path, help="CSV export path")
    parser.add_argument("--config", type=Path, help="Path to paper discovery config.yaml")
    parser.add_argument("--log-level", default="WARNING")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.WARNING), format="%(levelname)s %(name)s: %(message)s")
    config = load_config(args.config)
    providers = [part.strip() for part in args.providers.split(",")] if args.providers else None
    papers = search_all(args.query, args.limit, args.year_from, args.year_to, providers, config)
    if args.export:
        export_papers_csv(papers, args.export)
    for paper in papers[: args.limit]:
        identifiers = paper.doi or paper.pmid or paper.arxiv_id or paper.source_record_id
        oa = "OA" if paper.is_open_access or paper.pdf_url else "no OA"
        print(f"{paper.score:>5.2f} | {paper.year or ''} | {identifiers} | {oa} | {', '.join(paper.source_providers)} | {paper.title}")


if __name__ == "__main__":
    main()

