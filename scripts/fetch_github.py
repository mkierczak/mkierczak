#!/usr/bin/env python3
"""Fetch public GitHub stats for the Research page into github-stats.json.

Uses the public GitHub API (set GITHUB_TOKEN to raise the rate limit). The
rank letter follows the github-readme-stats formula (median/weight CDF blend).
"""
import collections, datetime, json, os, pathlib, urllib.parse, urllib.request

USER = "mkierczak"
OUT = pathlib.Path(__file__).resolve().parent.parent / "github-stats.json"
HEAD = {"User-Agent": "kierczak-website/1.0", "Accept": "application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"):
    HEAD["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

def api(path, **params):
    url = "https://api.github.com" + path + ("?" + urllib.parse.urlencode(params) if params else "")
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD)) as r:
        return json.load(r)

user = api(f"/users/{USER}")
repos, page = [], 1
while True:
    chunk = api(f"/users/{USER}/repos", per_page=100, page=page, type="owner")
    repos += chunk
    if len(chunk) < 100:
        break
    page += 1
own = [r for r in repos if not r["fork"]]
stars = sum(r["stargazers_count"] for r in own)
# GitHub's linguist labels plain .r files as Rebol; these are R scripts.
RENAME = {"Rebol": "R"}
langs = collections.Counter(RENAME.get(r["language"], r["language"]) for r in own if r["language"])

def count(path, q):
    return api(path, q=q, per_page=1)["total_count"]
commits = count("/search/commits", f"author:{USER}")
prs = count("/search/issues", f"author:{USER} type:pr")
issues = count("/search/issues", f"author:{USER} type:issue")
reviews = count("/search/issues", f"reviewed-by:{USER} type:pr")

def exp_cdf(x): return 1 - 2 ** -x
def lognorm_cdf(x): return x / (1 + x)
W = {"commits": 2, "prs": 3, "issues": 1, "reviews": 1, "stars": 4, "followers": 1}
score = 1 - (W["commits"] * exp_cdf(commits / 250) + W["prs"] * exp_cdf(prs / 50)
             + W["issues"] * exp_cdf(issues / 25) + W["reviews"] * exp_cdf(reviews / 2)
             + W["stars"] * lognorm_cdf(stars / 50) + W["followers"] * lognorm_cdf(user["followers"] / 10)) / sum(W.values())
levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]
thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
rank = levels[next(i for i, t in enumerate(thresholds) if score * 100 <= t)]

OUT.write_text(json.dumps({
    "user": USER, "url": user["html_url"], "asof": datetime.date.today().isoformat(),
    "repos": len(own), "stars": stars, "followers": user["followers"],
    "commits": commits, "prs": prs, "issues": issues, "reviews": reviews,
    "rank": rank, "languages": [{"name": n, "repos": c} for n, c in langs.most_common(8)],
}, indent=1))
print(OUT.read_text())
