#!/usr/bin/env python3
"""Собирает статический сайт stakes.com.mx из src/ в public/.

Страница = src/pages/<slug>.html: сверху JSON с метаданными в <!--{ ... }-->,
ниже HTML контента. Запуск: python3 build.py
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
OUT = ROOT / "public"

SITE = "https://stakes.com.mx"
SITE_NAME = "Stakes.com.mx"
UPDATED_ISO = "2026-10-20"
UPDATED_TXT = "20 de octubre de 2026"
# Партнёрские ссылки: регистрация и приложение.
AFF = {
    "reg": "https://scm.stakes.com.mx/?top=playeer",
    "app": "https://scm.stakes.com.mx/?top=playeer&max",
}

ICONS = {
    "home": '<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "user": '<circle cx="10" cy="8" r="4"/><path d="M2 21c0-4 4-6 8-6s8 2 8 6"/><path d="M19 8v6M16 11h6"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>',
    "phone": '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>',
    "gift": '<rect x="3" y="8" width="18" height="5" rx="1"/><path d="M5 13v8h14v-8M12 8v13M12 8c-2-4-6-4-6-1s6 1 6 1zm0 0c2-4 6-4 6-1s-6 1-6 1z"/>',
    "ticket": '<path d="M3 7a2 2 0 0 0 2-2h14a2 2 0 0 0 2 2v3a2 2 0 0 0 0 4v3a2 2 0 0 0-2 2H5a2 2 0 0 0-2-2v-3a2 2 0 0 0 0-4z"/><path d="M14 5v14" stroke-dasharray="2 2"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
    "dice": '<rect x="3" y="3" width="18" height="18" rx="4"/><circle cx="8.5" cy="8.5" r="1.3" fill="currentColor"/><circle cx="15.5" cy="15.5" r="1.3" fill="currentColor"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/>',
    "ball": '<circle cx="12" cy="12" r="9"/><path d="M12 7l4 3-1.5 5h-5L8 10z"/><path d="M12 3v4M21 10l-5 0M3 10h5M7 20l2.5-5M17 20l-2.5-5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
}


def icon(name):
    return (f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


SIDE_MAIN = [
    ("/", "Inicio", "home"),
    ("/registro/", "Registro", "user"),
    ("/iniciar-sesion/", "Iniciar sesión", "key"),
    ("/app/", "Stake app", "phone"),
    ("/bono-de-bienvenida/", "Bonos y promociones", "gift"),
    ("/codigo-promocional/", "Código promocional", "ticket"),
    ("/metodos-de-pago/", "Depósitos y retiros", "card"),
]
SIDE_HELP = [
    ("/juego-responsable/", "Juego responsable", "shield"),
    ("/sobre-nosotros/", "Sobre nosotros", "info"),
    ("/contacto/", "Contacto", "mail"),
]
BOTTOM_NAV = [
    ("/casino/", "Casino", "dice"),
    ("/apuestas-deportivas/", "Deportes", "ball"),
    ("/bono-de-bienvenida/", "Bonos", "gift"),
    ("/app/", "App", "phone"),
]

FOOTER_GUIDES = [
    ("/registro/", "Registro en Stake"),
    ("/iniciar-sesion/", "Iniciar sesión"),
    ("/app/", "Stake app"),
    ("/bono-de-bienvenida/", "Bonos y promociones"),
    ("/codigo-promocional/", "Código promocional"),
    ("/metodos-de-pago/", "Depósitos y retiros"),
    ("/casino/", "Stake casino"),
    ("/apuestas-deportivas/", "Apuestas deportivas"),
]
FOOTER_SITE = [
    ("/sobre-nosotros/", "Sobre nosotros"),
    ("/contacto/", "Contacto"),
    ("/juego-responsable/", "Juego responsable"),
]
FOOTER_LEGAL = [
    ("/aviso-de-privacidad/", "Aviso de privacidad"),
    ("/politica-de-cookies/", "Política de cookies"),
    ("/terminos-y-condiciones/", "Términos y condiciones"),
    ("/descargo-de-responsabilidad/", "Descargo de responsabilidad"),
]

GAME_COLORS = [
    ("#1475e1", "#0b2f5c"), ("#7b2ff7", "#2a0f5c"), ("#00b84a", "#063d1c"),
    ("#ff7a00", "#5c2300"), ("#e8114b", "#4f0619"), ("#00a3c4", "#053a47"),
    ("#d4a017", "#4a3500"), ("#c13ad9", "#3d0a47"),
]


def esc(s):
    return html.escape(s, quote=True)


def cta(text, style="", link="reg"):
    cls = "btn" + (" btn-" + style if style else "")
    return (f'<a class="{cls}" href="{esc(AFF[link])}" target="_blank" '
            f'rel="nofollow sponsored">{esc(text)}</a>')


def expand(body):
    """Шорткоды: {{cta:Текст|green|app}}, {{ctabox:Заголовок|Подпись|Кнопка|app}},
    последний параметр — тип ссылки: reg (по умолчанию) или app;
    {{games:Название/Провайдер;...}}, {{updated}}."""
    def _cta(m):
        parts = m.group(1).split("|")
        return cta(parts[0], parts[1] if len(parts) > 1 else "",
                   parts[2] if len(parts) > 2 else "reg")

    def _box(m):
        head, sub, btn, link = (m.group(1).split("|") + ["", "", "", ""])[:4]
        return (f'<div class="cta-box"><p>{esc(head)}<small>{esc(sub)}</small></p>'
                f'{cta(btn, "green", link or "reg")}</div>')

    def _games(m):
        items = [g.strip() for g in m.group(1).split(";") if g.strip()]
        out = []
        for i, g in enumerate(items):
            name, prov = (g.split("/") + [""])[:2]
            c1, c2 = GAME_COLORS[i % len(GAME_COLORS)]
            out.append(f'<div class="game"><div class="art" style="--g1:{c1};--g2:{c2}">'
                       f'<b>{esc(name)}</b></div><span>{esc(prov)}</span></div>')
        return '<div class="games">' + "".join(out) + "</div>"

    body = re.sub(r"\{\{cta:([^}]+)\}\}", _cta, body)
    body = re.sub(r"\{\{ctabox:([^}]+)\}\}", _box, body)
    body = re.sub(r"\{\{games:([^}]+)\}\}", _games, body)
    body = body.replace("{{updated}}", UPDATED_TXT)
    return body


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def short_label(text):
    t = strip_tags(text)
    if t.lower().startswith("preguntas frecuentes"):
        return "FAQ"
    for cut in (" en Stake México", " de Stake México", " sobre Stake México"):
        t = t.replace(cut, "")
    t = re.sub(r":.*$", "", t).strip()
    return t[:1].upper() + t[1:]


def toc_from(body):
    items = re.findall(r'<h2 id="([^"]+)"(?: data-tab="([^"]+)")?>(.*?)</h2>', body, re.S)
    if len(items) < 3:
        return ""
    lis = "".join(f'<li><a href="#{i}">{esc(tab or short_label(t))}</a></li>' for i, tab, t in items)
    return f'<nav class="tabs" aria-label="En esta página"><ul>{lis}</ul></nav>'


def faq_schema(body):
    pairs = re.findall(r"<summary>(.*?)</summary>\s*<div>(.*?)</div>\s*</details>", body, re.S)
    if not pairs:
        return None
    return {
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": strip_tags(q),
            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)},
        } for q, a in pairs],
    }


def url_of(slug):
    return "/" if slug == "index" else f"/{slug}/"


def side_links(items, current):
    out = []
    for href, label, ico in items:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<li><a href="{href}"{cur}>{icon(ico)}<span>{label}</span></a></li>')
    return "".join(out)


def links(items):
    return "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items)


LOGO = (f'<a class="logo" href="/" aria-label="{SITE_NAME} inicio">'
        f'<span class="logo-mark" aria-hidden="true">S</span><span class="logo-txt">Stakes<small>.com.mx</small></span></a>')


def sidebar(current):
    def tile(href, label, cls, ico):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a class="side-tile {cls}" href="{href}"{cur}>{icon(ico)}<span>{label}</span></a>'
    return f'''<aside class="sidebar" id="sidebar" aria-label="Menú">
  <div class="side-head">{LOGO}</div>
  <div class="side-tiles">{tile("/casino/", "Casino", "tile-casino", "dice")}{tile("/apuestas-deportivas/", "Deportes", "tile-sports", "ball")}</div>
  <nav class="side-group" aria-label="Guías"><ul>{side_links(SIDE_MAIN, current)}</ul></nav>
  <nav class="side-group" aria-label="Ayuda"><ul>{side_links(SIDE_HELP, current)}</ul></nav>
  <p class="side-note"><span class="badge-18">18+</span> Juega con responsabilidad</p>
</aside>
<div class="scrim" data-close-menu hidden></div>'''


def header(current, with_cta=True):
    actions = ""
    if with_cta:
        actions = ('<div class="top-actions">'
                   + cta("Iniciar sesión", "ghost").replace('class="btn btn-ghost"', 'class="btn btn-ghost btn-sm hide-xs"')
                   + cta("Registrarse").replace('class="btn"', 'class="btn btn-sm"')
                   + "</div>")
    return f'''<header class="topbar">
  <button class="burger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="sidebar">{icon("menu")}</button>
  <div class="topbar-logo">{LOGO}</div>
  {actions}
</header>'''


def bottom_nav(current):
    items = [f'<li><button type="button" class="open-menu" aria-controls="sidebar">{icon("menu")}<span>Menú</span></button></li>']
    for href, label, ico in BOTTOM_NAV:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{href}"{cur}>{icon(ico)}<span>{label}</span></a></li>')
    return '<nav class="bottom-nav" aria-label="Navegación rápida"><ul>' + "".join(items) + "</ul></nav>"


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        {LOGO}
        <p>Guía en español sobre Stake México: registro, verificación, pagos en pesos, casino y apuestas deportivas.</p>
        <div class="badges"><span class="badge">18+</span><span class="badge">Juego responsable</span></div>
      </div>
      <div><h2>Guías</h2><ul>{links(FOOTER_GUIDES)}</ul></div>
      <div><h2>Sitio</h2><ul>{links(FOOTER_SITE)}</ul></div>
      <div><h2>Legal</h2><ul>{links(FOOTER_LEGAL)}</ul></div>
    </div>
    <div class="disclaimer">
      <p>{SITE_NAME} es un sitio informativo independiente sobre Stake: no opera juegos ni acepta apuestas o pagos. Algunos enlaces son de afiliado: si te registras a través de ellos, el sitio puede recibir una comisión sin costo para ti.</p>
      <p>Stake en México es operado por Producciones Móviles S.A. de C.V., titular del permiso DGAJS/SCEVF/P-06/2005-TER expedido por la Secretaría de Gobernación, en unión de Unocapali La Paz Operadora, S.A. de C.V. Solo para mayores de 18 años. Juega con responsabilidad: si el juego deja de ser diversión, llama a la Línea de la Vida 800 911 2000.</p>
      <p>© 2026 {SITE_NAME}</p>
    </div>
  </div>
</footer>'''


def page_html(slug, meta, body):
    url = url_of(slug)
    canonical = SITE + url
    kind = meta.get("type", "commercial")
    body = expand(body)

    crumbs = ""
    graph = []
    if slug != "index":
        label = meta.get("crumb", meta["h1"])
        crumbs = (f'<nav class="crumbs" aria-label="Migas de pan"><a href="/">Inicio</a>'
                  f'<span aria-hidden="true">›</span><span>{esc(label)}</span></nav>')
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Inicio", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": label, "item": canonical},
            ],
        })
    else:
        graph.append({"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/",
                      "name": SITE_NAME, "inLanguage": "es-MX"})
        graph.append({"@type": "Organization", "@id": SITE + "/#org", "name": SITE_NAME,
                      "url": SITE + "/", "email": "contacto@stakes.com.mx"})

    graph.append({
        "@type": "WebPage" if kind == "legal" else "Article",
        "headline": meta["h1"],
        "description": meta["description"],
        "url": canonical,
        "inLanguage": "es-MX",
        "dateModified": UPDATED_ISO,
        "datePublished": UPDATED_ISO,
        "author": {"@type": "Organization", "name": SITE_NAME, "url": SITE + "/"},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE + "/"},
    })
    fs = faq_schema(body)
    if fs:
        graph.append(fs)
    for extra in meta.get("schema", []):
        graph.append(extra)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)

    hero_side = ""
    if meta.get("offer"):
        o = meta["offer"]
        lis = "".join(f"<li>{esc(x)}</li>" for x in o["points"])
        hero_side = (f'<aside class="offer-card"><span class="tag">{esc(o["tag"])}</span>'
                     f'<div class="offer-art" aria-hidden="true"><span></span><span></span><span></span></div>'
                     f'<div class="big">{esc(o["title"])}</div><ul>{lis}</ul>'
                     f'{cta(o["button"], "green", o.get("link", "reg"))}'
                     f'<p class="fine">18+ · Aplican términos y condiciones de Stake · Juega con responsabilidad</p></aside>')

    actions = ""
    if meta.get("hero_buttons"):
        btns = []
        for i, b in enumerate(meta["hero_buttons"]):
            text, _, link = b.partition("|")
            btns.append(cta(text, "" if i == 0 else "ghost", link or "reg"))
        actions = '<div class="hero-actions">' + "".join(btns) + "</div>"

    meta_line = ""
    if kind != "legal":
        meta_line = (f'<div class="meta-line"><span>Actualizado: <time datetime="{UPDATED_ISO}">{UPDATED_TXT}</time></span>'
                     f'</div>')
    else:
        meta_line = f'<div class="meta-line"><span>Última actualización: <time datetime="{UPDATED_ISO}">{UPDATED_TXT}</time></span></div>'

    lead = f'<p class="lead">{meta["lead"]}</p>' if meta.get("lead") else ""
    hero = f'''<section class="hero">
  <div class="wrap">
    {crumbs}
    <div class="hero-grid"{' style="grid-template-columns:1fr"' if not hero_side else ''}>
      <div>
        <h1>{esc(meta["h1"])}</h1>
        {meta_line}
        {lead}
        {actions}
      </div>
      {hero_side}
    </div>
  </div>
</section>'''

    toc = toc_from(body) if kind != "legal" else ""
    page_cls = "page" + (" narrow" if kind != "commercial" else "")

    robots = meta.get("robots", "index, follow, max-image-preview:large")
    og_type = "website" if slug == "index" else "article"

    return f'''<!doctype html>
<html lang="es-MX">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta["title"])}</title>
<meta name="description" content="{esc(meta["description"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es-MX" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:locale" content="es_MX">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{esc(meta["title"])}">
<meta property="og:description" content="{esc(meta["description"])}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#0f212e">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="preload" href="/assets/fonts/manrope-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
{sidebar(url)}
<div class="shell">
{header(url, kind == "commercial")}
<main id="main">
{hero}
{toc}
<div class="{page_cls}">
  <article class="content{' legal' if kind == 'legal' else ''}">
{body}
  </article>
</div>
</main>
{footer()}
</div>
{bottom_nav(url)}
<script src="/assets/site.js" defer></script>
</body>
</html>
'''


def parse(path):
    raw = path.read_text(encoding="utf-8").replace("{{updated}}", UPDATED_TXT)
    m = re.match(r"\s*<!--(\{.*?\})-->\s*(.*)", raw, re.S)
    if not m:
        sys.exit(f"{path}: нет JSON-шапки")
    return json.loads(m.group(1)), m.group(2)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / "assets", OUT / "assets")

    errors = []
    titles, descs = {}, {}
    pages = sorted((SRC / "pages").glob("*.html"))
    sitemap = []
    for p in pages:
        slug = p.stem
        meta, body = parse(p)
        t, d = meta["title"], meta["description"]
        if len(t) > 60:
            errors.append(f"{slug}: title {len(t)} > 60")
        if len(d) > 160:
            errors.append(f"{slug}: description {len(d)} > 160")
        if t in titles:
            errors.append(f"{slug}: title дублирует {titles[t]}")
        if d in descs:
            errors.append(f"{slug}: description дублирует {descs[d]}")
        titles[t], descs[d] = slug, slug

        out = page_html(slug, meta, body)
        if "{{" in out:
            errors.append(f"{slug}: остался шорткод")
        if slug == "404":
            (OUT / "404.html").write_text(out, encoding="utf-8")
            continue
        dest = OUT / "index.html" if slug == "index" else OUT / slug / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        if "noindex" not in meta.get("robots", ""):
            prio = meta.get("priority", "0.5")
            sitemap.append(f"  <url><loc>{SITE}{url_of(slug)}</loc><lastmod>{UPDATED_ISO}</lastmod><priority>{prio}</priority></url>")
        print(f"{url_of(slug):34} T({len(t)}) D({len(d)})")

    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(sitemap) + "\n</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n",
        encoding="utf-8")

    if errors:
        print("\nОШИБКИ:\n" + "\n".join(errors))
        sys.exit(1)
    print(f"\nГотово: {len(pages)} страниц → {OUT}")


if __name__ == "__main__":
    main()
