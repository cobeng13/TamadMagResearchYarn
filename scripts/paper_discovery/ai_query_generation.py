from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ai.client import AIClient, load_dotenv, require_api_key
from scripts.ai.logging import write_ai_run_log
from scripts.ai.prompts import build_query_generation_prompt
from scripts.ai.schemas import QUERY_EXPECTED_LEVELS, QUERY_PROVIDERS, query_generation_schema
from scripts.paper_discovery.generate_search_queries import generate_queries


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_PROVIDERS = ["openalex", "crossref", "semantic_scholar", "pubmed", "europe_pmc", "arxiv", "core"]
BRIEF_FILES = [
    "research_brief.md",
    "research_questions.md",
    "variables.md",
    "inclusion_exclusion_criteria.md",
    "search_keywords.md",
    "source_strategy.md",
    "writing_scope.md",
    "agent_instructions.md",
]
VARIANT_COLUMNS = [
    "query_id",
    "provider",
    "query_family",
    "query_text",
    "purpose",
    "expected_recall",
    "expected_precision",
    "notes",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def default_model() -> str:
    return os.getenv("AI_QUERY_MODEL", "").strip() or os.getenv("AI_DISCOVERY_MODEL", "").strip() or "gpt-5-mini"


def paths(project_dir: Path) -> dict[str, Path]:
    literature = project_dir / "01_literature_search"
    return {
        "brief_dir": project_dir / "00_brief",
        "literature": literature,
        "plan": literature / "ai_query_plan.md",
        "variants": literature / "ai_query_variants.csv",
        "search_ai": literature / "search_queries_ai.md",
        "search": literature / "search_queries.md",
        "log": project_dir / "logs" / "ai_query_generation_log.md",
    }


def parse_providers(value: str | list[str] | None) -> list[str]:
    raw = value if isinstance(value, list) else str(value or ",".join(DEFAULT_PROVIDERS)).split(",")
    providers: list[str] = []
    for item in raw:
        provider = normalize_provider(str(item).strip())
        if provider and provider not in providers:
            providers.append(provider)
    return providers or list(DEFAULT_PROVIDERS)


def normalize_provider(value: str) -> str:
    provider = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {"semantic_scholar": "semantic_scholar", "semanticscholar": "semantic_scholar", "europepmc": "europe_pmc"}
    provider = aliases.get(provider, provider)
    return provider if provider in QUERY_PROVIDERS else "general"


def read_stage00_context(project_dir: Path) -> tuple[str, list[Path]]:
    brief_dir = paths(project_dir)["brief_dir"]
    chunks: list[str] = []
    used: list[Path] = []
    for name in BRIEF_FILES:
        path = brief_dir / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        chunks.append(f"# {name}\n\n{text}")
        used.append(path)
    return "\n\n".join(chunks).strip(), used


def build_request_payload(model: str, brief_context: str, providers: list[str], limit: int, min_provider_queries: int, max_provider_queries: int) -> dict[str, Any]:
    return AIClient(api_key="payload-build-only", default_model=model).build_payload(
        model=model,
        instructions=build_query_generation_prompt(brief_context, providers, limit, min_provider_queries, max_provider_queries),
        input_data={
            "brief_context": brief_context,
            "providers": providers,
            "limit": limit,
            "min_provider_queries": min_provider_queries,
            "max_provider_queries": max_provider_queries,
        },
        schema=query_generation_schema(),
        schema_name="paper_discovery_query_generation",
    )


def call_openai_query_generation(
    api_key: str,
    model: str,
    brief_context: str,
    providers: list[str],
    limit: int,
    min_provider_queries: int,
    max_provider_queries: int,
    timeout: int = 120,
    retries: int = 2,
) -> dict[str, Any]:
    return AIClient(api_key=api_key, default_model=model).responses_json(
        instructions=build_query_generation_prompt(brief_context, providers, limit, min_provider_queries, max_provider_queries),
        input_data={
            "brief_context": brief_context,
            "providers": providers,
            "limit": limit,
            "min_provider_queries": min_provider_queries,
            "max_provider_queries": max_provider_queries,
        },
        schema=query_generation_schema(),
        schema_name="paper_discovery_query_generation",
        timeout=timeout,
        retries=retries,
    )


def empty_result(message: str) -> dict[str, Any]:
    return {
        "topic_summary": message,
        "core_concepts": [],
        "inclusion_boundaries": [],
        "exclusion_boundaries": [],
        "provider_strategy": [],
        "query_families": [],
        "warnings": [message],
        "recommended_general_queries": [],
        "suggested_next_step": "Add Stage 00 brief files, then rerun AI query generation.",
    }


def dry_run_result(project_dir: Path, model: str, providers: list[str], limit: int) -> dict[str, Any]:
    queries = generate_queries(project_dir, max_queries=limit)
    return {
        "topic_summary": "Dry run only. No OpenAI request was made; queries below are deterministic placeholders for preview.",
        "core_concepts": ["Dry run prompt preview", "Deterministic query seed output"],
        "inclusion_boundaries": ["Use only after human review."],
        "exclusion_boundaries": ["No AI-generated source records were created."],
        "provider_strategy": [
            {"provider": provider, "recommended_use": "Dry-run preview only.", "notes": "No AI call was made."}
            for provider in providers
        ],
        "query_families": [
            {
                "family_name": "dry_run_deterministic_preview",
                "purpose": "Preview likely query direction without calling OpenAI.",
                "queries": [
                    {
                        "provider": "general",
                        "query_text": query,
                        "purpose": "Deterministic placeholder query for review.",
                        "expected_recall": "medium",
                        "expected_precision": "medium",
                        "notes": "Dry run; not AI-generated.",
                    }
                    for query in queries
                ],
            }
        ],
        "warnings": [f"Dry run for model {model}; no API call was made."],
        "recommended_general_queries": queries,
        "suggested_next_step": "Run without --dry-run to request AI-generated query variants, then review before applying.",
    }


def normalize_level(value: Any, warnings: list[str], field: str, query_text: str) -> str:
    level = str(value or "").strip().lower()
    if level in QUERY_EXPECTED_LEVELS:
        return level
    warnings.append(f"Invalid {field} value for query '{query_text[:80]}'; coerced to medium.")
    return "medium"


def normalize_result(result: dict[str, Any], providers: list[str], limit: int) -> tuple[dict[str, Any], list[dict[str, str]], list[str]]:
    warnings = [str(item) for item in result.get("warnings", []) if str(item).strip()]
    allowed = set(providers) | {"general"}
    variants: list[dict[str, str]] = []
    query_number = 1
    for family in result.get("query_families", []):
        if not isinstance(family, dict):
            continue
        family_name = safe_text(family.get("family_name", "")) or "general"
        for query in family.get("queries", []):
            if not isinstance(query, dict) or len(variants) >= limit:
                continue
            query_text = safe_text(query.get("query_text", ""))
            if not query_text:
                continue
            provider = normalize_provider(safe_text(query.get("provider", "")))
            if provider not in allowed:
                warnings.append(f"Provider '{provider}' not requested for query '{query_text[:80]}'; coerced to general.")
                provider = "general"
            variants.append(
                {
                    "query_id": f"aiq_{query_number:03d}",
                    "provider": provider,
                    "query_family": family_name,
                    "query_text": query_text,
                    "purpose": safe_text(query.get("purpose", "")),
                    "expected_recall": normalize_level(query.get("expected_recall", ""), warnings, "expected_recall", query_text),
                    "expected_precision": normalize_level(query.get("expected_precision", ""), warnings, "expected_precision", query_text),
                    "notes": safe_text(query.get("notes", "")),
                }
            )
            query_number += 1

    general = [safe_text(query) for query in result.get("recommended_general_queries", []) if safe_text(query)]
    if not general:
        general = [row["query_text"] for row in variants if row["provider"] == "general"]
    result["warnings"] = warnings
    result["recommended_general_queries"] = dedupe_search_inputs(general)[:limit]
    return result, variants, warnings


def safe_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def dedupe_search_inputs(queries: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for query in queries:
        cleaned = safe_text(query)
        if len(cleaned.split()) < 2:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(cleaned)
    return deduped


def write_plan(path: Path, result: dict[str, Any], warnings: list[str]) -> None:
    lines = [
        "# AI Query Plan",
        "",
        "## Research Topic Summary",
        "",
        safe_text(result.get("topic_summary", "")) or "To be confirmed.",
        "",
        "## Core Concepts",
        "",
        *bullet_lines(result.get("core_concepts", [])),
        "",
        "## Inclusion Boundaries",
        "",
        *bullet_lines(result.get("inclusion_boundaries", [])),
        "",
        "## Exclusion Boundaries",
        "",
        *bullet_lines(result.get("exclusion_boundaries", [])),
        "",
        "## Recommended Provider Strategy",
        "",
    ]
    strategy = result.get("provider_strategy", [])
    if strategy:
        for item in strategy:
            if isinstance(item, dict):
                lines.append(f"- {normalize_provider(safe_text(item.get('provider', 'general')))}: {safe_text(item.get('recommended_use', ''))} {safe_text(item.get('notes', ''))}".strip())
    else:
        lines.append("- To be confirmed.")
    lines.extend(["", "## Query Families", ""])
    families = result.get("query_families", [])
    if families:
        for family in families:
            if isinstance(family, dict):
                lines.append(f"- {safe_text(family.get('family_name', 'general'))}: {safe_text(family.get('purpose', ''))}")
    else:
        lines.append("- To be confirmed.")
    lines.extend(["", "## Warnings", "", *bullet_lines(warnings or result.get("warnings", [])), "", "## Suggested Next Step", "", safe_text(result.get("suggested_next_step", "")) or "Review generated queries before running discovery."])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def bullet_lines(values: Any) -> list[str]:
    items = [safe_text(value) for value in values if safe_text(value)] if isinstance(values, list) else []
    return [f"- {item}" for item in items] or ["- To be confirmed."]


def write_variants_csv(path: Path, variants: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=VARIANT_COLUMNS)
        writer.writeheader()
        writer.writerows(variants)


def write_search_queries_ai(path: Path, result: dict[str, Any], variants: list[dict[str, str]], model: str) -> None:
    provider_rows: dict[str, list[str]] = {}
    for row in variants:
        provider_rows.setdefault(row["provider"], []).append(row["query_text"])
    lines = [
        "# AI-Generated Search Queries",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Model: {model}",
        "",
        "## Recommended General Queries",
        "",
        *[f"- {query}" for query in result.get("recommended_general_queries", [])],
        "",
        "## Provider-Specific Query Notes",
        "",
    ]
    for provider in sorted(provider_rows):
        if provider == "general":
            continue
        lines.append(f"### {provider_title(provider)}")
        lines.extend(f"- {query}" for query in provider_rows[provider])
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def provider_title(provider: str) -> str:
    return {
        "openalex": "OpenAlex",
        "crossref": "Crossref",
        "semantic_scholar": "Semantic Scholar",
        "pubmed": "PubMed",
        "europe_pmc": "Europe PMC",
        "arxiv": "arXiv",
        "core": "CORE",
        "general": "General",
    }.get(provider, provider.title())


def backup_file(path: Path) -> str:
    if not path.exists():
        return ""
    backup = path.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak.md")
    backup.write_bytes(path.read_bytes())
    return str(backup)


def apply_queries(search_path: Path, queries: list[str], overwrite: bool, no_backup: bool) -> str:
    selected = dedupe_search_inputs(queries)
    backup_path = "" if no_backup else backup_file(search_path)
    search_path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    section = ["", f"# AI Query Suggestions - {stamp}", "", "These are search inputs only, not source records or screening decisions.", ""]
    section.extend(f"- {query}" for query in selected)
    section.append("")
    if overwrite or not search_path.exists():
        lines = [
            "# Search Queries",
            "",
            f"Updated from AI query suggestions on {stamp}.",
            "These are search inputs only, not source records or screening decisions.",
            "",
            "## First-Pass Discovery Queries",
            "",
            *[f"- {query}" for query in selected],
            "",
        ]
        search_path.write_text("\n".join(lines), encoding="utf-8")
    else:
        existing = search_path.read_text(encoding="utf-8")
        search_path.write_text(existing.rstrip() + "\n" + "\n".join(section), encoding="utf-8")
    return backup_path


def write_log(
    log_path: Path,
    model: str,
    project_dir: Path,
    input_paths: list[Path],
    output_paths: list[Path],
    providers: list[str],
    query_count: int,
    dry_run: bool,
    apply: bool,
    overwrite: bool,
    warnings: list[str],
) -> None:
    write_ai_run_log(
        log_path,
        task_name="ai_query_generation",
        model=model,
        input_paths=input_paths,
        output_paths=output_paths,
        counts={
            "project_path": project_dir,
            "providers_requested": ",".join(providers),
            "query_count": query_count,
            "dry_run": str(dry_run).lower(),
            "apply": str(apply).lower(),
            "overwrite": str(overwrite).lower(),
        },
        errors=warnings,
        prompt_version="query_generation_v1",
    )


def run_ai_query_generation(
    project_dir: Path,
    model: str,
    limit: int,
    providers: list[str],
    dry_run: bool,
    apply: bool,
    overwrite: bool,
    no_backup: bool,
    min_provider_queries: int,
    max_provider_queries: int,
) -> dict[str, Any]:
    p = paths(project_dir)
    p["literature"].mkdir(parents=True, exist_ok=True)
    brief_context, input_paths = read_stage00_context(project_dir)
    output_paths = [p["plan"], p["variants"], p["search_ai"], p["log"]]

    if not brief_context:
        message = "Blocked: no non-empty Stage 00 brief files were found."
        result = empty_result(message)
        result, variants, warnings = normalize_result(result, providers, limit)
        write_plan(p["plan"], result, warnings)
        write_variants_csv(p["variants"], variants)
        write_search_queries_ai(p["search_ai"], result, variants, model)
        write_log(p["log"], model, project_dir, input_paths, output_paths, providers, 0, dry_run, apply, overwrite, warnings)
        return {"status": "blocked", "queries": 0, "paths": p, "warnings": warnings, "backup_path": ""}

    if dry_run:
        result = dry_run_result(project_dir, model, providers, limit)
    else:
        load_dotenv(repo_root() / ".env")
        api_key = require_api_key(dry_run=False)
        result = call_openai_query_generation(api_key or "", model, brief_context, providers, limit, min_provider_queries, max_provider_queries)

    result, variants, warnings = normalize_result(result, providers, limit)
    write_plan(p["plan"], result, warnings)
    write_variants_csv(p["variants"], variants)
    write_search_queries_ai(p["search_ai"], result, variants, model)

    backup_path = ""
    if apply and not dry_run:
        queries = list(result.get("recommended_general_queries", []))
        if not queries:
            queries = [row["query_text"] for row in variants if row["provider"] == "general"]
        backup_path = apply_queries(p["search"], queries, overwrite=overwrite, no_backup=no_backup)
        output_paths.append(p["search"])
    elif apply and dry_run:
        warnings.append("--apply was ignored because --dry-run was used.")

    write_log(p["log"], model, project_dir, input_paths, output_paths, providers, len(variants), dry_run, apply, overwrite, warnings)
    return {"status": "ok", "queries": len(variants), "paths": p, "warnings": warnings, "backup_path": backup_path}


def main() -> None:
    parser = argparse.ArgumentParser(description="Use OpenAI to generate paper discovery query plans and provider-specific variants.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--model", default=default_model(), help="OpenAI model for query generation")
    parser.add_argument("--limit", type=int, default=40, help="Maximum total query variants to write")
    parser.add_argument("--providers", default=",".join(DEFAULT_PROVIDERS), help="Comma-separated providers")
    parser.add_argument("--dry-run", action="store_true", help="Write a local preview without calling OpenAI")
    parser.add_argument("--apply", action="store_true", help="Write or merge selected AI queries into search_queries.md")
    parser.add_argument("--overwrite", action="store_true", help="Replace search_queries.md when used with --apply")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup when modifying search_queries.md")
    parser.add_argument("--min-provider-queries", type=int, default=3, help="Minimum useful queries per relevant provider")
    parser.add_argument("--max-provider-queries", type=int, default=8, help="Maximum useful queries per relevant provider")
    args = parser.parse_args()

    summary = run_ai_query_generation(
        project_dir=resolve_project(args.project),
        model=args.model,
        limit=args.limit,
        providers=parse_providers(args.providers),
        dry_run=args.dry_run,
        apply=args.apply,
        overwrite=args.overwrite,
        no_backup=args.no_backup,
        min_provider_queries=args.min_provider_queries,
        max_provider_queries=args.max_provider_queries,
    )
    print(f"status={summary['status']} queries={summary['queries']}")
    print(f"query_plan={summary['paths']['plan']}")
    print(f"query_variants={summary['paths']['variants']}")
    print(f"search_queries_ai={summary['paths']['search_ai']}")
    if summary["backup_path"]:
        print(f"backup_path={summary['backup_path']}")


if __name__ == "__main__":
    main()
