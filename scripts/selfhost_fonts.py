#!/usr/bin/env python3
"""Download Google Fonts used by the site and write a local @font-face CSS.

Usage: python3 scripts/selfhost_fonts.py   (output: assets/fonts/)
"""
import pathlib, re, urllib.request

URL = ("https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;"
       "1,6..72,300..600&family=Inter:wght@400;500;600&display=swap")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15"
out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "fonts"
out.mkdir(parents=True, exist_ok=True)

def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()

css = get(URL).decode()
def local(m):
    name = m.group(1).rsplit("/", 2)
    fname = f"{name[-2]}-{name[-1]}"
    if not (out / fname).exists():
        (out / fname).write_bytes(get(m.group(1)))
    return f"url(assets/fonts/{fname})"
css = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", local, css)
(out / "fonts.css").write_text(css)
print(len(list(out.glob("*.woff2"))), "font files")
