#!/usr/bin/env python3
"""Fetch abstracts and citations-per-year from OpenAlex for every DOI in publications.json.

Writes publication-counts.json (published with the site: {doi: {year: cites}}) and
publication-abstracts.json (local reference only, NOT published) used for writing paper-notes.json.
Run after fetch_publications.py.
"""
import json, urllib.request, urllib.parse

pubs = json.load(open("publications.json"))
dois = [p["doi"] for p in pubs if p.get("doi")]
out = {}

def abstract(inv):
    if not inv:
        return ""
    words = {}
    for w, pos in inv.items():
        for i in pos:
            words[i] = w
    return " ".join(words[i] for i in sorted(words))

for i in range(0, len(dois), 25):
    chunk = dois[i:i + 25]
    q = urllib.parse.urlencode({
        "filter": "doi:" + "|".join("https://doi.org/" + d for d in chunk),
        "per-page": 50,
        "select": "doi,abstract_inverted_index,counts_by_year",
    })
    req = urllib.request.Request("https://api.openalex.org/works?" + q,
                                 headers={"User-Agent": "kierczak-website/1.0"})
    with urllib.request.urlopen(req) as r:
        for w in json.load(r)["results"]:
            d = (w["doi"] or "").replace("https://doi.org/", "")
            out[d.lower()] = {"abstract": abstract(w.get("abstract_inverted_index")),
                              "counts": {str(c["year"]): c["cited_by_count"] for c in w.get("counts_by_year", [])}}

res = {d: out.get(d.lower(), {"abstract": "", "counts": {}}) for d in dois}
json.dump({d: v["abstract"] for d, v in res.items()}, open("publication-abstracts.json", "w"), indent=1, ensure_ascii=False)
json.dump({d: v["counts"] for d, v in res.items() if v["counts"]}, open("publication-counts.json", "w"), separators=(",", ":"))
print(len(res), "papers;", sum(1 for v in res.values() if v["abstract"]), "with abstracts")
