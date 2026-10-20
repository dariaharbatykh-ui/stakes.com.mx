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

NAV = [
    ("/", "Inicio"),
    ("/registro/", "Registro"),
    ("/iniciar-sesion/", "Iniciar sesión"),
    ("/app/", "App"),
    ("/bono-de-bienvenida/", "Bonos"),
    ("/metodos-de-pago/", "Pagos"),
    ("/casino/", "Casino"),
    ("/apuestas-deportivas/", "Apuestas"),
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
    ("#1f4c7a", "#132a3a"), ("#5b2a86", "#1a2c38"), ("#0f6b4f", "#132a3a"),
    ("#8a3b12", "#1a2c38"), ("#7a1f4c", "#132a3a"), ("#22577a", "#1a2c38"),
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
            out.append(f'<div class="game" style="--g1:{c1};--g2:{c2}">'
                       f'<b>{esc(name)}</b><span>{esc(prov)}</span></div>')
        return '<div class="games">' + "".join(out) + "</div>"

    body = re.sub(r"\{\{cta:([^}]+)\}\}", _cta, body)
    body = re.sub(r"\{\{ctabox:([^}]+)\}\}", _box, body)
    body = re.sub(r"\{\{games:([^}]+)\}\}", _games, body)
    body = body.replace("{{updated}}", UPDATED_TXT)
    return body


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def toc_from(body):
    items = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
    if len(items) < 3:
        return ""
    lis = "".join(f'<li><a href="#{i}">{strip_tags(t)}</a></li>' for i, t in items)
    return f'<nav class="toc" aria-label="Contenido"><strong>En esta página</strong><ol>{lis}</ol></nav>'


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


def nav_html(current):
    lis = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        lis.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    return "".join(lis)


def links(items):
    return "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in items)


def header(current, with_cta=True):
    head_cta = ""
    if with_cta:
        head_cta = ('<div class="header-cta">'
                    + cta("Ir a Stake", "green").replace('class="btn btn-green"', 'class="btn btn-green btn-sm"')
                    + "</div>")
    return f'''<a class="skip" href="#main">Saltar al contenido</a>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="/" aria-label="{SITE_NAME} inicio"><span class="logo-mark" aria-hidden="true">S</span>Stakes<small>.com.mx</small></a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="nav">Menú</button>
    <nav class="nav" id="nav" aria-label="Principal"><ul>{nav_html(current)}</ul></nav>
    {head_cta}
  </div>
</header>'''


def footer():
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="logo" href="/"><span class="logo-mark" aria-hidden="true">S</span>Stakes<small>.com.mx</small></a>
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
        "author": {"@type": "Organization", "name": "Equipo editorial " + SITE_NAME, "url": SITE + "/sobre-nosotros/"},
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
                     f'<div class="big">{esc(o["title"])}</div><ul>{lis}</ul>'
                     f'{cta(o["button"], "green", o.get("link", "reg"))}'
                     f'<p class="fine">18+ · Aplican términos y condiciones de Stake · Juega con responsabilidad</p></aside>')

    actions = ""
    if meta.get("hero_buttons"):
        btns = []
        for i, b in enumerate(meta["hero_buttons"]):
            text, _, link = b.partition("|")
            btns.append(cta(text, "green" if i == 0 else "ghost", link or "reg"))
        actions = '<div class="hero-actions">' + "".join(btns) + "</div>"

    meta_line = ""
    if kind != "legal":
        meta_line = (f'<div class="meta-line"><span>Actualizado: <time datetime="{UPDATED_ISO}">{UPDATED_TXT}</time></span>'
                     f'<span>Por: Equipo editorial {SITE_NAME}</span></div>')
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
    page_cls = "page wrap" + ("" if toc else " no-toc")
    author = ""
    if kind != "legal":
        author = (f'<div class="author"><div class="avatar" aria-hidden="true">S</div><div>'
                  f'<strong>Equipo editorial {SITE_NAME}</strong>'
                  f'<p>Cada dato sobre Stake se revisa antes de publicarse. '
                  f'Última revisión: {UPDATED_TXT}. <a href="/sobre-nosotros/">Cómo trabajamos</a>.</p></div></div>')

    sticky = ""
    body_cls = ""
    if kind == "commercial":
        sticky = f'<div class="sticky-cta"><span>Stake México · 18+ · pesos MXN</span>{cta("Registrarme", "green").replace("btn btn-green", "btn btn-green btn-sm")}</div>'
        body_cls = ' class="has-sticky"'

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
<link rel="stylesheet" href="/assets/style.css">
<script type="application/ld+json">{ld}</script>
</head>
<body{body_cls}>
{header(url, kind == "commercial")}
<main id="main">
{hero}
<div class="{page_cls}">
  {toc}
  <article class="content{' legal' if kind == 'legal' else ''}">
{body}
{author}
  </article>
</div>
</main>
{footer()}
{sticky}
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
