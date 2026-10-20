#!/usr/bin/env python3
"""Собирает статический сайт stakes.com.mx из src/ в public/.

Страница = src/pages/<slug>.html: сверху JSON с метаданными в <!--{ ... }-->,
ниже HTML контента. Запуск: python3 build.py
"""
import hashlib
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
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
}


def icon(name):
    return (f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


SIDE_MAIN = [
    ("/", "Inicio", "home"),
    ("/app/", "Stake app", "phone"),
    ("/registro/", "Registro", "user"),
    ("/iniciar-sesion/", "Iniciar sesión", "key"),
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
    ("/app/", "Stake app"),
    ("/registro/", "Registro en Stake"),
    ("/iniciar-sesion/", "Iniciar sesión"),
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


def asset_ver(name):
    """Короткий хэш файла для ?v= — после правки CSS/JS браузеры и Cloudflare берут новую версию."""
    return hashlib.md5((SRC / "assets" / name).read_bytes()).hexdigest()[:8]


# Заголовки: каждое слово с большой буквы, кроме предлогов (и del/al = предлог + артикль).
# Первое слово заголовка и первое слово после «:», «?», «!», «.» — всегда с большой.
PREPOSITIONS = {
    "a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "durante", "en", "entre",
    "hacia", "hasta", "mediante", "para", "por", "según", "sin", "so", "sobre", "tras",
    "versus", "vs", "vía", "del", "al",
    "of",  # английский предлог в названиях игр: Gates of Olympus
}
_LEAD = "¿¡«“\"'(["
_TRAIL = "?!.,;:»”\"')]…"


def _tc_word(word, force):
    i = 0
    while i < len(word) and word[i] in _LEAD:
        i += 1
    j = len(word)
    while j > i and word[j - 1] in _TRAIL:
        j -= 1
    core = word[i:j]
    if not core or not core[0].isalpha():
        return word
    if any(c.isupper() for c in core[1:]):
        return word  # iPhone, eSports, NFL, SPEI — как есть
    if not force and core.lower() in PREPOSITIONS:
        core = core.lower()
    else:
        core = core[0].upper() + core[1:]
    return word[:i] + core + word[j:]


def title_case(text, start=True):
    """Возвращает (текст, start) — start=True, если следующее слово должно быть с большой."""
    out = []
    for part in re.split(r"(\s+)", text):
        if not part or part.isspace():
            out.append(part)
            continue
        out.append(_tc_word(part, start))
        stripped = part.rstrip("»”\"')")
        start = bool(stripped) and stripped[-1] in ":?!." or part in ("—", "–", "|")
    return "".join(out), start


def tc(text):
    return title_case(text)[0]


def tc_html(fragment):
    """Title case только для текста между тегами (иконки и разметка не трогаются)."""
    out, start = [], True
    for part in re.split(r"(<[^>]+>)", fragment):
        if part.startswith("<"):
            out.append(part)
        else:
            t, start = title_case(part, start)
            out.append(t)
    return "".join(out)


def headings_tc(doc):
    doc = re.sub(r"(<(h[1-3])\b[^>]*>)(.*?)(</\2>)", lambda m: m.group(1) + tc_html(m.group(3)) + m.group(4), doc, flags=re.S)
    doc = re.sub(r'(<div class="big">)(.*?)(</div>)', lambda m: m.group(1) + tc_html(m.group(2)) + m.group(3), doc)
    doc = re.sub(r'(<div class="cta-box"><p>)(.*?)(<small>)', lambda m: m.group(1) + tc_html(m.group(2)) + m.group(3), doc)
    doc = re.sub(r'(<nav class="tabs".*?</nav>)', lambda m: re.sub(r'(<a href="#[^"]+">)(.*?)(</a>)', lambda a: a.group(1) + tc_html(a.group(2)) + a.group(3), m.group(1)), doc, flags=re.S)
    return doc


def esc(s):
    return html.escape(s, quote=True)


def cta(text, style="", link="reg"):
    cls = "btn" + (" btn-" + style if style else "")
    return (f'<a class="{cls}" href="{esc(AFF[link])}" target="_blank" '
            f'rel="nofollow sponsored">{esc(text)}</a>')


# Топ-игры: данные провайдеров (RTP — максимальная версия; оператор может использовать другую).
TOP_GAMES = [
    ("Gates of Olympus 1000", "Pragmatic Play", "Slot", "96.50%", "Alta", "15,000x"),
    ("Sugar Rush 1000", "Pragmatic Play", "Slot", "96.53%", "Alta", "25,000x"),
    ("Duck Hunters 2", "Nolimit City", "Slot", "96.00%", "Extrema", "40,000x"),
    ("Le Fisherman", "Hacksaw Gaming", "Slot", "96.33%", "Baja-media", "15,000x"),
    ("Crazy Time", "Evolution", "Concurso en vivo", "96.08%", "Variable", "20,000x"),
    ("Mines", "Originales de Stake", "Original", "99%", "Ajustable", "Según el riesgo"),
    ("Plinko", "Originales de Stake", "Original", "99%", "Ajustable", "Según el riesgo"),
    ("Dice", "Originales de Stake", "Original", "99%", "Ajustable", "Según el riesgo"),
]


def slugify(text):
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def game_img(name, prov, w=180, h=236):
    """<img> превью игры, если файл есть в src/assets/img/games/<slug>.webp."""
    slug = slugify(name)
    if not (SRC / "assets" / "img" / "games" / f"{slug}.webp").exists():
        return ""
    return (f'<img src="/assets/img/games/{slug}.webp" width="{w}" height="{h}" loading="lazy" decoding="async" '
            f'alt="{esc(name)} de {esc(prov)} en Stake">')


PHONES = {
    "home": ("Inicio de Stake en el celular", "Pantalla de inicio de Stake México en el navegador del celular"),
    "casino": ("Casino de Stake en el móvil", "Casino de Stake México en el celular con Originales y slots"),
    "sports": ("Apuestas deportivas en el móvil", "Sportsbook de Stake México en el celular con momios en pesos"),
    "live": ("Casino en vivo en el móvil", "Casino en vivo de Stake México en el celular con blackjack, ruleta y baccarat"),
    "promos": ("Promociones en el móvil", "Promociones de Stake México en el celular"),
}


def phones_html(keys):
    figs = []
    for k in [x.strip() for x in keys.split(",") if x.strip()]:
        cap, alt = PHONES[k]
        figs.append(f'<figure class="phone"><div class="phone-frame">'
                    f'<img src="/assets/img/app/stake-movil-{k}.jpg" width="517" height="1120" loading="lazy" decoding="async" alt="{esc(alt)}">'
                    f'</div><figcaption>{esc(cap)}</figcaption></figure>')
    cls = "phones" + (" single" if len(figs) == 1 else "")
    return f'<div class="{cls}" style="--n:{len(figs)}">' + "".join(figs) + "</div>"


def top_games_html():
    out = []
    for i, (name, prov, kind, rtp, vol, mx) in enumerate(TOP_GAMES):
        c1, c2 = GAME_COLORS[i % len(GAME_COLORS)]
        out.append(
            f'<article class="tg"><div class="art{" has-img" if game_img(name, prov) else ""}" style="--g1:{c1};--g2:{c2}">'
            f'{game_img(name, prov)}<span class="rank">#{i + 1}</span><b>{esc(name)}</b></div>'
            f'<div class="tg-body"><h3>{esc(name)}</h3><p class="prov">{esc(prov)} · {esc(kind)}</p>'
            f'<dl><div><dt>RTP</dt><dd>{rtp}</dd></div><div><dt>Volatilidad</dt><dd>{esc(vol)}</dd></div>'
            f'<div><dt>Ganancia máx.</dt><dd>{esc(mx)}</dd></div></dl></div></article>')
    return ('<div class="top-games">' + "".join(out) + '</div>'
            '<p class="fine-print">RTP de la versión con mayor retorno publicada por cada proveedor. '
            'El RTP y la ganancia máxima pueden variar: consulta la información dentro de cada juego en Stake.</p>')


def expand(body):
    """Шорткоды: {{cta:Текст|green|app}}, {{ctabox:Заголовок|Подпись|Кнопка|app}},
    последний параметр — тип ссылки: reg (по умолчанию) или app;
    {{games:Название/Провайдер;...}}, {{topgames}}, {{updated}}."""
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
            img = game_img(name, prov)
            out.append(f'<div class="game"><div class="art{" has-img" if img else ""}" style="--g1:{c1};--g2:{c2}">'
                       f'{img}<b>{esc(name)}</b></div><span>{esc(prov)}</span></div>')
        return '<div class="games">' + "".join(out) + "</div>"

    body = re.sub(r"\{\{cta:([^}]+)\}\}", _cta, body)
    body = re.sub(r"\{\{ctabox:([^}]+)\}\}", _box, body)
    body = re.sub(r"\{\{games:([^}]+)\}\}", _games, body)
    body = body.replace("{{topgames}}", top_games_html())
    body = re.sub(r"\{\{phones:([a-z,]+)\}\}", lambda m: phones_html(m.group(1)), body)
    body = re.sub(r"\{\{icon:([a-z]+)\}\}", lambda m: icon(m.group(1)), body)
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
  <div class="side-head">{LOGO}<button class="side-close" type="button" aria-label="Cerrar menú" data-close-menu>{icon("close")}</button></div>
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
  <div class="topbar-in">
    <button class="burger" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="sidebar">{icon("menu")}</button>
    <div class="topbar-logo">{LOGO}</div>
    {actions}
  </div>
</header>'''


def bottom_nav(current):
    items = [f'<li><button type="button" class="open-menu" aria-controls="sidebar">{icon("menu")}<span>Menú</span></button></li>']
    for href, label, ico in BOTTOM_NAV:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{href}"{cur}>{icon(ico)}<span>{label}</span></a></li>')
    return '<nav class="bottom-nav" aria-label="Navegación rápida"><ul>' + "".join(items) + "</ul></nav>"


# Соцсети Stake México — ссылки из футера stake.mx (20.10.2026)
SOCIAL = [
    ("X", "https://x.com/stake_mexico",
     '<path fill="currentColor" stroke="none" d="M17.75 3h3.07l-6.7 7.66L22 21h-6.17l-4.83-6.32L5.47 21H2.4l7.17-8.2L2 3h6.33l4.37 5.77zm-1.08 16.17h1.7L7.4 4.74H5.58z"/>'),
    ("Instagram", "https://www.instagram.com/stake.mexico/",
     '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>'),
    ("TikTok", "https://www.tiktok.com/@stakemexico",
     '<path fill="currentColor" stroke="none" d="M16.6 2h-3.3v13.2a2.9 2.9 0 1 1-2.9-2.9c.3 0 .6 0 .9.1V9a6.3 6.3 0 1 0 5.3 6.2V8.4a7.6 7.6 0 0 0 4.4 1.4V6.5a4.4 4.4 0 0 1-4.4-4.5z"/>'),
    ("Telegram", "https://t.me/stakemxsocial",
     '<path fill="currentColor" stroke="none" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm4.6 6.8-1.6 7.7c-.1.6-.5.7-1 .4l-2.6-1.9-1.3 1.2c-.1.1-.3.3-.6.3l.2-2.6 4.8-4.3c.2-.2 0-.3-.3-.1l-5.9 3.7-2.5-.8c-.6-.2-.6-.6.1-.8l9.8-3.8c.5-.2.9.1.9 1z"/>'),
]


def social_html():
    items = "".join(
        f'<li><a href="{url}" target="_blank" rel="nofollow noopener" aria-label="Stake México en {name}">'
        f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">{path}</svg></a></li>'
        for name, url, path in SOCIAL)
    return f'<nav class="social" aria-label="Redes sociales de Stake México"><ul>{items}</ul></nav>'


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
    {social_html()}
    <div class="disclaimer">
      <p>{SITE_NAME} es un sitio informativo independiente sobre Stake: no opera juegos ni acepta apuestas o pagos. Algunos enlaces son de afiliado: si te registras a través de ellos, el sitio puede recibir una comisión sin costo para ti.</p>
      <p>Stake en México es operado por Producciones Móviles S.A. de C.V., titular del permiso DGAJS/SCEVF/P-06/2005-TER expedido por la Secretaría de Gobernación, en unión de Unocapali La Paz Operadora, S.A. de C.V. Solo para mayores de 18 años. Juega con responsabilidad: si el juego deja de ser diversión, llama a la Línea de la Vida 800 911 2000.</p>
      <p>© 2026 {SITE_NAME}</p>
    </div>
  </div>
</footer>'''


def page_html(slug, meta, body):
    return headings_tc(_page_html(slug, meta, body))


def _page_html(slug, meta, body):
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
                      "name": SITE_NAME, "inLanguage": "es"})
        graph.append({"@type": "Organization", "@id": SITE + "/#org", "name": SITE_NAME,
                      "url": SITE + "/", "email": "contacto@stakes.com.mx"})

    graph.append({
        "@type": "WebPage" if kind == "legal" else "Article",
        "headline": meta["h1"],
        "description": meta["description"],
        "url": canonical,
        "inLanguage": "es",
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
        hero_side = (f'<aside class="offer-card"><span class="tag">{esc(o["tag"])}</span>'
                     f'<div class="offer-art" aria-hidden="true"><span></span><span></span><span></span></div>'
                     f'<div class="big">{esc(o["title"])}</div>'
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

    lead = f'<p class="lead">{esc(meta["lead"])}</p>' if meta.get("lead") else ""
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
    page_cls = "page"

    robots = meta.get("robots", "index, follow, max-image-preview:large")
    og_type = "website" if slug == "index" else "article"

    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta["title"])}</title>
<meta name="description" content="{esc(meta["description"])}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="es" href="{canonical}">
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
<link rel="stylesheet" href="/assets/style.css?v={asset_ver("style.css")}">
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
<script src="/assets/site.js?v={asset_ver("site.js")}" defer></script>
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
        meta["title"] = tc(meta["title"])
        meta.setdefault("crumb", meta["h1"])
        meta["h1"] = tc(meta["h1"])
        if meta.get("offer"):
            meta["offer"]["title"] = tc(meta["offer"]["title"])
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

    # Cloudflare (Workers static assets): кэш и заголовки безопасности
    (OUT / "_headers").write_text(
        "/*\n"
        "  X-Content-Type-Options: nosniff\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  X-Frame-Options: SAMEORIGIN\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
        "/assets/*\n"
        "  Cache-Control: public, max-age=31536000, immutable\n"
        "/sitemap.xml\n"
        "  Cache-Control: public, max-age=3600\n"
        "/robots.txt\n"
        "  Cache-Control: public, max-age=3600\n",
        encoding="utf-8")

    if errors:
        print("\nОШИБКИ:\n" + "\n".join(errors))
        sys.exit(1)
    print(f"\nГотово: {len(pages)} страниц → {OUT}")


if __name__ == "__main__":
    main()
