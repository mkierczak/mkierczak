#!/usr/bin/env python3
"""Post-render: drop Quarto's ES6 polyfill <script> from cdnjs (modern browsers don't need it)."""
import pathlib, re

PAT = re.compile(r'[ \t]*<script src="https://cdnjs\.cloudflare\.com/polyfill/[^"]*"></script>\n?')
for f in pathlib.Path("docs").rglob("*.html"):
    s = f.read_text(encoding="utf-8")
    t = PAT.sub("", s)
    if t != s:
        f.write_text(t, encoding="utf-8")
