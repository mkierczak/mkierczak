#!/usr/bin/env python3
"""Build network.json (co-author, institution, theme and teaching graph) for the Research page.

Inputs: publication-network.json (scripts/fetch_publications.py),
research.qmd (DOIs under each theme) and network-extra.json (hand-edited).
"""
import collections, itertools, json, re

ME = "Marcin Kierczak"
extra = json.load(open("network-extra.json"))
pubs = json.load(open("publication-network.json"))
for p in pubs:
    p["names"] = [a["name"] for a in p["authors"]]
aliases = extra["aliases"]
inst_alias = extra["institution_aliases"]

def norm(n):
    n = n.replace("‐", "-").replace("‑", "-").strip()
    return aliases.get(n, n)

# Themes: DOIs linked inside each "### theme" block of research.qmd.
themes, cur = {}, None
for line in open("research.qmd", encoding="utf-8"):
    m = re.match(r"### (.+)", line)
    if m:
        cur = m.group(1).strip(); themes[cur] = set(); continue
    if line.startswith("## "):
        cur = None
    if cur:
        themes[cur] |= {d.lower() for d in re.findall(r"https://doi\.org/([^\s)]+)", line)}

papers = collections.Counter()
last = {}
pair = collections.Counter()
for p in pubs:
    names = {norm(a) for a in p["names"]} - {ME}
    for a in names:
        papers[a] += 1
        last[a] = max(last.get(a, 0), p["year"])
people = {a for a, n in papers.items() if n >= extra["min_papers"]}
for p in pubs:
    names = sorted({norm(a) for a in p["names"]} & people)
    for a, b in itertools.combinations(names, 2):
        pair[(a, b)] += 1

# Primary institution per person: most frequent among their papers (after aliasing).
inst_votes = collections.defaultdict(collections.Counter)
for p in pubs:
    for au in p["authors"]:
        a = norm(au["name"])
        if a in people:
            for i in au["institutions"]:
                inst_votes[a][inst_alias.get(i, i)] += 1
skip = {"Science for Life Laboratory", "National Bioinformatics Infrastructure Sweden"}
primary = {a: next((i for i, _ in v.most_common() if i not in skip), None) for a, v in inst_votes.items()}
inst_people = collections.Counter(i for i in primary.values() if i)
insts = {i for i, n in inst_people.items() if n >= extra["min_institution_people"]}

nodes = [{"id": ME, "type": "me", "label": ME, "papers": len(pubs)}]
links = []
for a in sorted(people):
    nodes.append({"id": a, "type": "person", "label": a, "papers": papers[a], "last": last[a],
                  "inst": primary.get(a) if primary.get(a) in insts else None})
    links.append({"source": ME, "target": a, "kind": "coauthor", "w": papers[a]})
for (a, b), w in pair.items():
    if w >= extra["min_pair_papers"]:
        links.append({"source": a, "target": b, "kind": "coauthor", "w": w})
for i in sorted(insts):
    nodes.append({"id": "inst:" + i, "type": "institution", "label": i, "people": inst_people[i]})
for a in sorted(people):
    if primary.get(a) in insts:
        links.append({"source": a, "target": "inst:" + primary[a], "kind": "affiliation", "w": 1})
for t, dois in themes.items():
    tp = [p for p in pubs if p["doi"] and p["doi"].lower() in dois]
    nodes.append({"id": "theme:" + t, "type": "theme", "label": t, "papers": len(tp)})
    links.append({"source": ME, "target": "theme:" + t, "kind": "theme", "w": len(tp)})
    c = collections.Counter(a for p in tp for a in {norm(x) for x in p["names"]} & people)
    for a, w in c.items():
        links.append({"source": a, "target": "theme:" + t, "kind": "theme", "w": w})
hub = extra["teaching"]["hub"]
nodes.append({"id": hub["id"], "type": "teaching", "label": hub["label"], "url": hub["url"], "role": "summer school"})
links.append({"source": ME, "target": hub["id"], "kind": "teaching", "w": 1})
for t in extra["teaching"]["people"]:
    nodes.append({"id": t["name"], "type": "teaching", "label": t["name"], "url": t["url"], "role": t["role"]})
    links.append({"source": t["name"], "target": hub["id"], "kind": "teaching", "w": 1})

ids = {n["id"] for n in nodes}
assert len(ids) == len(nodes), "duplicate node ids"
assert all(l["source"] in ids and l["target"] in ids for l in links)
others = {a: {"n": n, "year": last[a]} for a, n in sorted(papers.items()) if a not in people}
json.dump({"nodes": nodes, "links": links, "others": others}, open("network.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(nodes), "nodes,", len(links), "links;", len(people), "co-authors,", len(insts), "institutions,", len(themes), "themes")
