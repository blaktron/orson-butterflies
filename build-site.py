#!/usr/bin/env python3
"""Wrap the game fragment into a standalone HTML document under site/.

The game is authored as an Artifact fragment: no <!doctype>, <html>, <head> or
<body>, because the Artifact host supplies those. Serving it ourselves means
supplying them too, so this lifts the <title> and the font <link> tags out of
the fragment and into a real <head>.
"""
import pathlib
import re
import shutil

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "schnauzer-butterfly-chase.html"
OUT = ROOT / "site" / "index.html"

TITLE = "Schnauzer Butterfly Chase"
BLURB = ("A 3D dog-park romp: steer a giant schnauzer with the keyboard, "
         "catch butterflies before closing time, and hold on through the zoomies.")
ASSETS = ROOT / "assets"
RAW = "https://raw.githubusercontent.com/blaktron/orson-butterflies/main/assets"

fragment = SRC.read_text(encoding="utf-8")

# pull the title and the stylesheet/preconnect links up into the head
title_match = re.search(r"<title>(.*?)</title>\s*", fragment, re.S)
title = title_match.group(1).strip() if title_match else TITLE
fragment = re.sub(r"<title>.*?</title>\s*", "", fragment, count=1, flags=re.S)

links = re.findall(r'^\s*<link [^>]*>\s*$', fragment, re.M)
fragment = re.sub(r'^\s*<link [^>]*>\s*$\n?', "", fragment, flags=re.M)
head_links = "\n".join(link.strip() for link in links)

document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{BLURB}">
<meta name="theme-color" content="#12301c">
<meta name="color-scheme" content="dark">
<link rel="icon" type="image/svg+xml" href="icon.svg">
<link rel="apple-touch-icon" href="icon-512.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{BLURB}">
<meta property="og:image" content="{RAW}/icon-512.png">
<meta name="twitter:card" content="summary_large_image">
{head_links}
<style>
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;height:100%}}
  body{{background:#12301c;color:#f7efe1;overscroll-behavior:none;
       font:14px "Nunito",system-ui,-apple-system,"Segoe UI",sans-serif}}
  img{{max-width:100%}}
  [hidden]{{display:none!important}}
</style>
</head>
<body>
{fragment.strip()}
</body>
</html>
"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(document, encoding="utf-8")
print(f"wrote {OUT} ({len(document):,} bytes)")

for name in ("icon.svg", "icon-512.png"):
    src = ASSETS / name
    if src.exists():
        shutil.copy2(src, OUT.parent / name)
        print(f"copied {name}")
