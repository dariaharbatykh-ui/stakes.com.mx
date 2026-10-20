#!/usr/bin/env python3
"""Проверка одной страницы src/pages/<slug>.html: python3 tools_check_page.py <slug>"""
import json, re, sys
from pathlib import Path
slug = sys.argv[1]
raw = Path(f"src/pages/{slug}.html").read_text(encoding="utf-8")
m = re.match(r"\s*<!--(\{.*?\})-->\s*(.*)", raw, re.S)
errs = []
if not m:
    sys.exit("no JSON header")
meta = json.loads(m.group(1)); body = m.group(2)
for k in ("title", "description", "h1", "lead", "crumb"):
    if not meta.get(k): errs.append(f"missing {k}")
if len(meta.get("title", "")) > 60: errs.append(f"title {len(meta['title'])} > 60")
if len(meta.get("description", "")) > 160: errs.append(f"description {len(meta['description'])} > 160")
for bad in ("stake.mx", "stake.com", "sitio oficial", "oficial", "help.stake", "@stake.mx", "editorial", "redacción", "Ventajas", "Desventajas"):
    for where, txt in (("meta", json.dumps(meta, ensure_ascii=False)), ("body", body)):
        hits = [x for x in re.findall(r".{0,30}" + re.escape(bad) + r".{0,30}", txt, re.I) if "identificación oficial" not in x.lower()]
        if hits: errs.append(f"forbidden '{bad}' in {where}: {hits[:2]}")
h2 = re.findall(r'<h2 id="[^"]+"(?: data-tab="[^"]+")?>', body)
if len(h2) < 6: errs.append(f"only {len(h2)} h2 sections")
if re.search(r"<h1", body): errs.append("h1 in body (h1 comes from JSON)")
# Первый экран всегда даёт 2 кнопки (регистрация + приложение); здесь считаются кнопки в тексте и offer
cta = len(re.findall(r"\{\{cta(box)?:", body)) + (1 if meta.get("offer") else 0)
if cta > 3: errs.append(f"{cta} partner buttons in body+offer > 3")
if "{{" in re.sub(r"\{\{(cta|ctabox|games|topgames|art|icon|phones):[^}]*\}\}|\{\{topgames\}\}|\{\{updated\}\}", "", body): errs.append("unknown shortcode")
if 'class="faq"' not in body: errs.append("no FAQ section")
links = re.findall(r'href="(/[^"#]*)"', body)
PLANNED = {"originales-de-stake", "slots", "casino-en-vivo", "blackjack", "apuestas-futbol", "apuestas-tenis",
           "apuestas-cricket", "apuestas-hockey", "apuestas-esports"}
for l in links:
    name = l.strip("/") or "index"
    if name not in PLANNED and not Path("src/pages/" + name + ".html").exists(): errs.append(f"link to missing page {l}")
if len(links) != len(set(links)): errs.append("same internal URL linked more than once")
words = len(re.sub(r"<[^>]+>|\{\{[^}]+\}\}", " ", body).split())
print(f"{slug}: {words} words, {len(h2)} h2, title {len(meta['title'])}, desc {len(meta['description'])}, partner buttons {cta}")
print("ERRORS:\n- " + "\n- ".join(errs) if errs else "OK")
