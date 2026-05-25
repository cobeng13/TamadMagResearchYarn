from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from scripts.paper_discovery.config import env_or_config
from scripts.paper_discovery.models import Paper
from scripts.paper_discovery.models.paper import normalize_doi
from scripts.paper_discovery.providers.base import BaseProvider, RateLimit, clean_text, parse_int


class PubMedProvider(BaseProvider):
    name = "pubmed"
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def default_min_interval(self) -> float:
        api_key = env_or_config(self.config, "NCBI_API_KEY", "ncbi_api_key")
        return 0.1 if api_key else 1 / 3

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.rate_limit = RateLimit(self.default_min_interval())

    def search(self, query: str, limit: int = 20, year_from: int | None = None, year_to: int | None = None, **kwargs: Any) -> list[Paper]:
        term = query
        if year_from or year_to:
            term = f"{query} AND ({year_from or 1800}:{year_to or 3000}[dp])"
        search_data = self.request_json(
            "GET",
            f"{self.base_url}/esearch.fcgi",
            params={**self.common_params(), "db": "pubmed", "term": term, "retmode": "json", "retmax": limit},
            headers=self.headers(),
        )
        pmids = search_data.get("esearchresult", {}).get("idlist", [])
        return self.fetch_pmids(pmids)

    def get_by_id(self, identifier: str) -> Paper | None:
        papers = self.fetch_pmids([identifier])
        return papers[0] if papers else None

    def fetch_pmids(self, pmids: list[str], batch_size: int = 100) -> list[Paper]:
        papers: list[Paper] = []
        for start in range(0, len(pmids), batch_size):
            batch = pmids[start : start + batch_size]
            if not batch:
                continue
            response = self.request(
                "GET",
                f"{self.base_url}/efetch.fcgi",
                params={**self.common_params(), "db": "pubmed", "id": ",".join(batch), "retmode": "xml"},
                headers=self.headers(),
            )
            root = ET.fromstring(response.text)
            papers.extend(self.article_to_paper(article) for article in root.findall(".//PubmedArticle"))
        return papers

    def common_params(self) -> dict[str, str]:
        params: dict[str, str] = {}
        tool = env_or_config(self.config, "NCBI_TOOL", "ncbi_tool", "research_agent")
        email = env_or_config(self.config, "CONTACT_EMAIL", "contact_email")
        api_key = env_or_config(self.config, "NCBI_API_KEY", "ncbi_api_key")
        if tool:
            params["tool"] = tool
        if email:
            params["email"] = email
        if api_key:
            params["api_key"] = api_key
        return params

    def headers(self) -> dict[str, str]:
        return {"User-Agent": self.config.get("user_agent") or "ResearchAgent/0.1"}

    def article_to_paper(self, article: ET.Element) -> Paper:
        medline = article.find("MedlineCitation")
        pubmed_data = article.find("PubmedData")
        pmid = text(medline, "PMID")
        article_node = medline.find("Article") if medline is not None else None
        journal = article_node.find("Journal") if article_node is not None else None
        pub_date_node = journal.find("JournalIssue/PubDate") if journal is not None else None
        year = parse_int(text(pub_date_node, "Year") or text(pub_date_node, "MedlineDate")[:4])
        ids = {}
        if pubmed_data is not None:
            for id_node in pubmed_data.findall("ArticleIdList/ArticleId"):
                id_type = id_node.attrib.get("IdType", "").lower()
                ids[id_type] = clean_text(id_node.text)
        authors = []
        if article_node is not None:
            for author in article_node.findall("AuthorList/Author"):
                name = clean_text(" ".join(part for part in [text(author, "ForeName"), text(author, "LastName")] if part))
                if name:
                    authors.append(name)
        abstracts = []
        if article_node is not None:
            abstracts = [clean_text(node.text) for node in article_node.findall("Abstract/AbstractText") if clean_text(node.text)]
        publication_types = []
        if article_node is not None:
            publication_types = [clean_text(node.text) for node in article_node.findall("PublicationTypeList/PublicationType") if clean_text(node.text)]
        return Paper(
            title=clean_text(text(article_node, "ArticleTitle")),
            abstract=" ".join(abstracts),
            authors=authors,
            year=year,
            publication_date=publication_date(pub_date_node),
            journal_or_source=clean_text(text(journal, "Title")),
            doi=normalize_doi(ids.get("doi", "")),
            pmid=pmid,
            pmcid=ids.get("pmc", ""),
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
            source_provider=self.name,
            source_record_id=pmid,
            publication_types=publication_types,
            raw={"pmid": pmid, "ids": ids},
        )


def text(parent: ET.Element | None, path: str) -> str:
    node = parent.find(path) if parent is not None else None
    return clean_text(node.text) if node is not None and node.text else ""


def publication_date(pub_date: ET.Element | None) -> str:
    if pub_date is None:
        return ""
    parts = [text(pub_date, "Year"), text(pub_date, "Month"), text(pub_date, "Day")]
    return "-".join(part for part in parts if part)

