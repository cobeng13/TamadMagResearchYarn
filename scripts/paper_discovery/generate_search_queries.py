from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


DEFAULT_PROJECT = Path("projects/sample_project")
DEFAULT_MAX_QUERIES = 24


CORE_SEED_QUERIES = [
    "radiologic technologist licensure examination academic performance predictors",
    "radiologic technology board examination academic performance pre-board examination",
    "radiography education licensure examination predictors academic performance",
    "radiologic technology students board exam predictors",
    "radiologic technologist licensure examination Philippines academic performance",
    "pre-board examination performance licensure examination success",
    "mock board examination licensure examination academic performance",
    "professional course grades licensure examination performance allied health",
    "clinical internship performance licensure examination success allied health",
    "terminal competency examination licensure examination predictors",
    "comprehensive examination predictive validity licensure examination",
    "health professions licensure examination predictors academic performance",
    "allied health students licensure examination academic performance Philippines",
    "nursing licensure examination academic performance predictors Philippines",
    "medical technology licensure examination academic performance predictors Philippines",
    "predictive validity academic performance board examination health professions education",
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_project(project: str | Path) -> Path:
    path = Path(project)
    return path if path.is_absolute() else repo_root() / path


def read_text_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def clean_query(value: str) -> str:
    query = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", value.strip())
    query = query.replace("“", '"').replace("”", '"')
    query = re.sub(r"\s+", " ", query)
    return query.strip()


def normalize_for_key(value: str) -> str:
    return re.sub(r"\W+", " ", value.lower()).strip()


def strip_boolean_syntax(value: str) -> str:
    text = value
    text = re.sub(r"\bAND\b|\bOR\b|\bNOT\b", " ", text, flags=re.I)
    text = text.replace("(", " ").replace(")", " ").replace('"', " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_bullets_and_numbered_lines(text: str) -> list[str]:
    queries: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if re.match(r"^(?:[-*]|\d+[.)])\s+", stripped):
            cleaned = clean_query(stripped)
            if looks_like_query(cleaned):
                queries.append(cleaned)
    return queries


def extract_explicit_search_queries(text: str) -> list[str]:
    queries: list[str] = []
    for line in text.splitlines():
        cleaned = clean_query(line)
        if not cleaned:
            continue
        if re.search(r"\b(?:AND|OR)\b", cleaned):
            queries.append(cleaned)
    return queries


def extract_quoted_terms(text: str) -> list[str]:
    terms = []
    for term in re.findall(r'"([^"]{3,80})"', text):
        if not re.search(r"\b(?:To be confirmed|content)\b", term, flags=re.I):
            terms.append(term.strip())
    return list(dict.fromkeys(terms))


def looks_like_query(value: str) -> bool:
    lowered = value.lower()
    rejected_starts = (
        "what ",
        "is ",
        "do ",
        "does ",
        "which ",
        "whether ",
        "h0:",
        "h1:",
        "descriptive statistics",
        "correlation analysis",
        "predictive analysis",
        "academic year",
        "time elapsed",
    )
    rejected_fragments = [
        "if available",
        "to be confirmed",
        "in terms of:",
        "statistical tests",
        "items to be confirmed",
    ]
    if lowered.startswith(rejected_starts) or any(fragment in lowered for fragment in rejected_fragments):
        return False
    search_terms = [
        "licensure",
        "board",
        "radiologic",
        "radiography",
        "academic",
        "pre-board",
        "mock board",
        "predictive",
        "clinical",
        "internship",
        "allied health",
    ]
    outcomes = ["licensure", "board examination", "board exam", "certification"]
    predictors = ["academic", "grades", "pre-board", "mock board", "clinical", "internship", "predictive", "predictor", "predictors", "competency", "comprehensive"]
    populations = ["radiologic", "radiography", "allied health", "health professions", "nursing", "medical technology"]
    has_search_term = any(term in lowered for term in search_terms)
    has_concept_pair = any(term in lowered for term in outcomes) and (any(term in lowered for term in predictors) or any(term in lowered for term in populations))
    return has_search_term and has_concept_pair and len(value.split()) >= 4


def build_term_combinations(text: str) -> list[str]:
    terms = set(extract_quoted_terms(text))
    lowered = text.lower()
    if "radiologic technology" in lowered:
        terms.add("radiologic technology")
    if "radiologic technologist licensure examination" in lowered:
        terms.add("radiologic technologist licensure examination")
    if "philippines" in lowered:
        terms.add("Philippines")

    populations = [
        term
        for term in [
            "radiologic technology",
            "radiologic technologist",
            "radiography",
            "allied health",
            "health professions education",
        ]
        if term in {t.lower() for t in terms} or term in lowered
    ]
    outcomes = [
        term
        for term in [
            "licensure examination",
            "board examination",
            "board exam performance",
            "licensure success",
            "licensure performance",
        ]
        if term in {t.lower() for t in terms} or term in lowered
    ]
    predictors = [
        term
        for term in [
            "academic performance",
            "professional course grades",
            "pre-board examination",
            "mock board examination",
            "clinical performance",
            "internship performance",
            "comprehensive examination",
            "terminal competency",
            "predictive validity",
        ]
        if term in {t.lower() for t in terms} or term in lowered
    ]

    combinations: list[str] = []
    for population in populations[:4]:
        for outcome in outcomes[:3]:
            for predictor in predictors[:4]:
                combinations.append(f"{population} {outcome} {predictor}")
    if "philippines" in lowered:
        combinations.extend(
            [
                "radiologic technology licensure examination Philippines",
                "allied health licensure examination academic performance Philippines",
                "pre-board examination licensure examination Philippines",
            ]
        )
    return combinations


def generate_queries(project_dir: Path, max_queries: int = DEFAULT_MAX_QUERIES) -> list[str]:
    brief_dir = project_dir / "00_brief"
    source_paths = [
        brief_dir / "_ai_response.md",
        brief_dir / "research_brief.md",
        brief_dir / "research_questions.md",
        brief_dir / "search_keywords.md",
        brief_dir / "source_strategy.md",
    ]
    combined = "\n\n".join(read_text_if_exists(path) for path in source_paths)
    candidates: list[str] = []
    candidates.extend(extract_explicit_search_queries(combined))
    boolean_variants = [strip_boolean_syntax(query) for query in candidates if re.search(r"\b(?:AND|OR)\b", query)]
    candidates.extend(boolean_variants)
    candidates.extend(build_term_combinations(combined))
    candidates.extend(CORE_SEED_QUERIES)
    return dedupe_queries(candidates)[:max_queries]


def dedupe_queries(queries: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for query in queries:
        cleaned = clean_query(query)
        if not looks_like_query(cleaned):
            continue
        key = normalize_for_key(cleaned)
        if key and key not in seen:
            seen.add(key)
            deduped.append(cleaned)
    return deduped


def read_existing_queries(path: Path) -> list[str]:
    if not path.exists():
        return []
    queries: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = clean_query(line)
        if cleaned and not cleaned.startswith("#") and looks_like_query(cleaned):
            queries.append(cleaned)
    return queries


def write_search_queries(path: Path, generated: list[str], preserve_existing: bool = True) -> None:
    existing = read_existing_queries(path) if preserve_existing else []
    merged = dedupe_queries([*generated, *existing])
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# Search Queries",
        "",
        f"Generated from `00_brief/_ai_response.md` and brief files on {stamp}.",
        "These are search queries only; they are not source records or screening decisions.",
        "",
        "## First-Pass Discovery Queries",
        "",
    ]
    lines.extend(f"- {query}" for query in merged)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate first-pass paper discovery queries from stage 00 brief outputs.")
    parser.add_argument("--project", default=str(DEFAULT_PROJECT), help="Project directory")
    parser.add_argument("--max-queries", type=int, default=DEFAULT_MAX_QUERIES, help="Maximum generated queries to write")
    parser.add_argument("--replace", action="store_true", help="Replace existing queries instead of preserving them")
    parser.add_argument("--dry-run", action="store_true", help="Print generated queries without writing search_queries.md")
    args = parser.parse_args()

    project_dir = resolve_project(args.project)
    queries = generate_queries(project_dir, max_queries=args.max_queries)
    output_path = project_dir / "01_literature_search" / "search_queries.md"
    if args.dry_run:
        for query in queries:
            print(query)
        return
    write_search_queries(output_path, queries, preserve_existing=not args.replace)
    print(f"wrote_queries={len(read_existing_queries(output_path))} path={output_path}")


if __name__ == "__main__":
    main()
