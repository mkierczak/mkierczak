#!/usr/bin/env python3
"""Fetch Marcin Kierczak's publications from OpenAlex into publications.json."""
import json, urllib.request, urllib.parse

AUTHOR = "A5036927183"
# Works OpenAlex wrongly attributes to this author (matched by DOI); never include them.
EXCLUDE = {"10.1371/journal.pgen.1002316"}
FIELDS = "doi,title,publication_year,publication_date,type,cited_by_count,authorships,primary_location,biblio"
out, page = [], 1
while True:
    q = urllib.parse.urlencode({"filter": f"raw_author_name.search:Kierczak", "per-page": 100,
                                "page": page, "select": FIELDS})
    req = urllib.request.Request(f"https://api.openalex.org/works?{q}",
                                 headers={"User-Agent": "kierczak-website/1.0"})
    with urllib.request.urlopen(req) as r:
        d = json.load(r)
    out += d["results"]
    if len(d["results"]) < 100:
        break
    page += 1

def is_marcin(w):
    for a in w["authorships"]:
        n = (a.get("raw_author_name") or a["author"]["display_name"]).strip()
        if (a["author"]["id"] or "").endswith(AUTHOR):
            return True
        if "kierczak" in n.lower() and n[:1].upper() == "M":
            return True
    return False

def is_me(a):
    n = (a.get("raw_author_name") or a["author"]["display_name"]).strip()
    return (a["author"]["id"] or "").endswith(AUTHOR) or ("kierczak" in n.lower() and n[:1].upper() == "M")

pubs, seen = [], set()
for w in out:
    if not is_marcin(w) or (w["title"] or "").startswith("Additional file"):
        continue
    if w["type"] not in ("article", "review", "preprint"):
        continue
    doi = (w.get("doi") or "").replace("https://doi.org/", "")
    src = (w.get("primary_location") or {}).get("source") or {}
    journal = src.get("display_name") or ""
    key = (w["title"] or "").lower().strip()
    if not doi or doi.lower() in EXCLUDE or not journal or key in seen:
        continue
    seen.add(key)
    b = w.get("biblio") or {}
    pages = b.get("first_page") or ""
    if pages and b.get("last_page") and b["last_page"] != pages:
        pages += "–" + b["last_page"]
    pubs.append({
        "title": w["title"].rstrip("."),
        "authors": [("Marcin Kierczak" if is_me(a) else a["author"]["display_name"]) for a in w["authorships"]],
        "journal": journal, "year": w["publication_year"], "date": w["publication_date"],
        "volume": b.get("volume") or "", "issue": b.get("issue") or "", "pages": pages,
        "doi": doi, "citations": w["cited_by_count"], "type": w["type"],
    })
# Canonicalise journal, volume, issue and pages from Crossref when available.
for p in pubs:
    try:
        req = urllib.request.Request("https://api.crossref.org/works/" + urllib.parse.quote(p["doi"]),
                                     headers={"User-Agent": "kierczak-website/1.0"})
        m = json.load(urllib.request.urlopen(req, timeout=20))["message"]
    except Exception:
        continue
    if m.get("container-title"):
        p["journal"] = m["container-title"][0]
    for k, ck in (("volume", "volume"), ("issue", "issue"), ("pages", "page")):
        if m.get(ck):
            p[k] = m[ck].replace("-", "–")

pubs.sort(key=lambda p: p["date"], reverse=True)
json.dump(pubs, open("publications.json", "w"), ensure_ascii=False, indent=1)
print(len(pubs), "publications")
