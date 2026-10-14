"""Rebuild index.html after re-running analysis.py.
Usage (from the repository root):  python analysis.py && python tools/build_page.py
"""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
html = (root / "tools" / "template.html").read_text(encoding="utf-8")
data = (root / "results.json").read_text(encoding="utf-8")
(root / "index.html").write_text(html.replace("__RESULTS__", data), encoding="utf-8")
print("index.html rebuilt from results.json")
