import requests
import json
import os
import time
import xml.etree.ElementTree as ET

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
QUERY = "epilepsy[MeSH Terms] AND hasabstract AND 2015:2025[dp] AND english[lang]"
MAX_PAPERS = 1000


def search_ids():
    """Ask PubMed for the IDs of papers matching our query."""
    r = requests.get(
        f"{BASE}/esearch.fcgi",
        params={
            "db": "pubmed",
            "term": QUERY,
            "retmax": MAX_PAPERS,
            "retmode": "json",
            "sort": "relevance",
        },
    )
    r.raise_for_status()
    return r.json()["esearchresult"]["idlist"]


def fetch_batch(ids):
    """Download full details for a batch of paper IDs."""
    r = requests.post(
        f"{BASE}/efetch.fcgi",
        data={"db": "pubmed", "id": ",".join(ids), "retmode": "xml"},
    )
    r.raise_for_status()
    return r.text


def parse_papers(xml_text):
    """Pull out the fields we care about from PubMed's XML."""
    root = ET.fromstring(xml_text)
    papers = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//MedlineCitation/PMID")

        title_el = art.find(".//ArticleTitle")
        title = "".join(title_el.itertext()) if title_el is not None else ""

        parts = []
        for at in art.findall(".//Abstract/AbstractText"):
            text = "".join(at.itertext()).strip()
            label = at.get("Label")
            parts.append(f"{label}: {text}" if label else text)
        abstract = " ".join(parts)

        year = art.findtext(".//JournalIssue/PubDate/Year")
        if not year:
            medline_date = art.findtext(".//JournalIssue/PubDate/MedlineDate") or ""
            year = medline_date[:4]

        doi = None
        for aid in art.findall(".//PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = aid.text

        pub_types = [
            pt.text for pt in art.findall(".//PublicationTypeList/PublicationType")
        ]

        if abstract and title:
            papers.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "year": year,
                    "journal": art.findtext(".//Journal/Title"),
                    "doi": doi,
                    "pub_types": pub_types,
                }
            )
    return papers


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    print("Searching PubMed...")
    ids = search_ids()
    print(f"Found {len(ids)} paper IDs")

    all_papers = []
    for i in range(0, len(ids), 200):
        batch = ids[i : i + 200]
        print(f"Downloading papers {i + 1} to {i + len(batch)}...")
        all_papers.extend(parse_papers(fetch_batch(batch)))
        time.sleep(0.5)  # be polite to PubMed's servers

    with open("data/papers.json", "w", encoding="utf-8") as f:
        json.dump(all_papers, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_papers)} papers to data/papers.json")
    print("\nExample paper:")
    print(all_papers[0]["title"])
    print(all_papers[0]["abstract"][:300], "...")