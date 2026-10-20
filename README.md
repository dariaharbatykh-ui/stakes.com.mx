# stakes.com.mx

Статический сайт на чистом HTML/CSS о Stake México (stake.mx), на испанском (es-MX).

## Структура

| Путь | Что внутри |
|---|---|
| `src/pages/*.html` | контент страниц; сверху JSON с метаданными (`title`, `description`, `h1`, `lead`, `offer`, `type`) |
| `src/assets/` | `style.css`, `site.js` (мобильное меню), `favicon.svg` |
| `build.py` | собирает `public/`: шапка, меню, футер, хлебные крошки, оглавление, schema.org, `sitemap.xml`, `robots.txt`, `/go/stake/`; проверяет длину title ≤ 60 и description ≤ 160 и дубли |
| `public/` | готовый сайт, можно выкладывать как есть |
| `facts.md` | база фактов о бренде с официального сайта и источниками |
| `serve.mjs` | локальный сервер |

## Команды

```bash
python3 build.py
```

```bash
node serve.mjs 8080
```

Затем открыть http://localhost:8080.

## Шорткоды в контенте

- `{{cta:Текст|green}}` — партнёрская кнопка (`/go/stake/`, `target="_blank"`, `rel="nofollow sponsored"`)
- `{{ctabox:Заголовок|Подпись|Кнопка}}` — блок с кнопкой
- `{{games:Игра/Провайдер;...}}` — плитки игр
- `{{updated}}` — дата обновления

## Партнёрская ссылка

Все кнопки ведут на `/go/stake/` (noindex, закрыт в robots.txt). Сейчас редирект на `https://stake.mx/`. Чтобы поставить реальную ссылку, замените `AFF_URL` в `build.py` и пересоберите сайт.

## Страницы

Коммерческие: `/`, `/registro/`, `/iniciar-sesion/`, `/app/`, `/bono-de-bienvenida/`, `/codigo-promocional/`, `/metodos-de-pago/`, `/casino/`, `/apuestas-deportivas/`.
Служебные: `/sobre-nosotros/`, `/contacto/`, `/juego-responsable/`, `/aviso-de-privacidad/`, `/politica-de-cookies/`, `/terminos-y-condiciones/`, `/descargo-de-responsabilidad/`, `404.html`.
