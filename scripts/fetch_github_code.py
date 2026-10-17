#!/usr/bin/env python3
"""Sample real code lines from my own public GitHub repos into github-code.json.

The Blog page background (assets/bg.js, motif "code") shows these lines. Forks,
vendored/minified/generated files, comments and anything that looks like a
credential, address or personal path are skipped. Set GITHUB_TOKEN to raise
the API rate limit.
"""
import json, os, pathlib, random, re, urllib.request

USER = "mkierczak"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "github-code.json"
EXT = {".R", ".r", ".py", ".sh", ".js", ".lua", ".php", ".nf", ".smk", ".css", ".scss"}
SKIP_PATH = re.compile(r"(^|/)(docs|_freeze|node_modules|vendor|site_libs|dist|build|mathjax|renv|packrat|\.venv)(/|$)|\.min\.|-min\.")
SKIP_LINE = re.compile(r"(?i)(passw|secret|token|api[_-]?key|@[a-z0-9.-]+\.[a-z]|https?://|/Users/|/home/|\b\d{1,3}(\.\d{1,3}){3}\b)")
COMMENT = ("content:", ".fa", "#", "//", "/*", "*", "--", "<!--", "'''", '"""')
HEAD = {"User-Agent": "kierczak-website/1.0", "Accept": "application/vnd.github+json"}
if os.environ.get("GITHUB_TOKEN"):
    HEAD["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEAD)) as r:
        return r.read()

repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"))
per_repo = {}
for r in repos:
    if r["fork"] or r["archived"]:
        continue
    name, branch = r["name"], r["default_branch"]
    tree = json.loads(get(f"https://api.github.com/repos/{USER}/{name}/git/trees/{branch}?recursive=1"))
    files = [t["path"] for t in tree.get("tree", [])
             if t["type"] == "blob" and pathlib.PurePosixPath(t["path"]).suffix in EXT
             and not SKIP_PATH.search(t["path"]) and t.get("size", 0) < 100_000]
    lines = set()
    for path in files:
        try:
            text = get(f"https://raw.githubusercontent.com/{USER}/{name}/{branch}/{path}").decode("utf-8")
        except Exception:
            continue
        for ln in text.splitlines():
            s = ln.strip()
            if (16 <= len(s) <= 64 and re.search(r"[A-Za-z]{3}", s) and not s.startswith(COMMENT)
                    and not SKIP_LINE.search(s) and "\t" not in s and s.isascii()):
                lines.add(s)
    if lines:
        per_repo[name] = sorted(lines)

rng = random.Random(42)
for v in per_repo.values():
    rng.shuffle(v)
picked, i = [], 0
while len(picked) < 80 and any(per_repo.values()):
    for name in sorted(per_repo):
        if per_repo[name] and len(picked) < 80:
            picked.append(per_repo[name].pop())
rng.shuffle(picked)
OUT.write_text(json.dumps({"user": USER, "lines": picked}, indent=0))
print(len(picked), "lines from", sorted(n for n in per_repo))
print("\n".join(picked[:15]))
