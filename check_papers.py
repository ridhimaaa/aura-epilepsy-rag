import json

with open("data/papers.json", encoding="utf-8") as f:
    papers = json.load(f)

print(f"Total papers: {len(papers)}")
print(f"Papers with a DOI: {sum(1 for p in papers if p['doi'])}")

for p in papers[:5]:
    print(f"\n[{p['year']}] {p['title']}")
    print(f"  Journal: {p['journal']}")
    print(f"  Type: {', '.join(p['pub_types'])}")
    print(f"  DOI: {p['doi']}")
    print(f"  {p['abstract'][:200]}...")