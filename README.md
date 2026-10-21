# stakes.com.mx

Статический сайт на чистом HTML/CSS о Stake México (stake.mx), на испанском (lang="es").

## Структура

| Путь | Что внутри |
|---|---|
| `src/pages/*.html` | контент страниц; сверху JSON с метаданными (`title`, `description`, `h1`, `lead`, `offer`, `type`) |
| `src/assets/` | `style.css` (дизайн в стиле Stake), `site.js` (меню, табы), `favicon.svg`, `fonts/` (Manrope, OFL) |
| `build.py` | собирает `public/`: шапка, меню, футер, хлебные крошки, оглавление, schema.org, `sitemap.xml`, `robots.txt`; проверяет длину title ≤ 60 и description ≤ 160 и дубли |
| `public/` | готовый сайт, можно выкладывать как есть |
| `facts.md` | база фактов о бренде с официального сайта и источниками |
| `serve.mjs` | локальный сервер |

## Команды

```bash
npm run build
```

```bash
npm run dev
```

Локально: http://localhost:8080.

## Cloudflare

Сайт отдаётся Cloudflare Workers как статические файлы из `public/` (`wrangler.toml`, без отдельного скрипта):

- `not_found_handling = "404-page"` — неизвестные адреса получают `404.html` с кодом 404;
- `html_handling = "auto-trailing-slash"` — `/registro` → `/registro/`;
- `public/_headers` (создаёт `build.py`) — кэш на год для `/assets/*` (у CSS/JS в ссылке `?v=хэш`, поэтому правки подхватываются сразу) и заголовки безопасности.

Аккаунт Cloudflare этого сайта: uzivggfem-977@get-emailxyz.eu (account ID 9e4a4001a16e0739b5680770f83dd7dc). Вход Wrangler для проекта хранится отдельно, в `.wrangler-home/` (не в git), поэтому не мешает другим проектам на этом компьютере.

Вход (один раз, в браузере откроется страница Cloudflare):

```bash
npm run login
```

Деплой:

```bash
npm run deploy
```

Сайт: https://stakes.com.mx (домен уже подключён к воркеру `stakes-com-mx` в панели Cloudflare; www.stakes.com.mx отдаёт 301 на основной домен). Технический адрес: https://stakes-com-mx.stakesmx.workers.dev (поддомен workers.dev — `stakesmx`; закрыт от индексации заголовком `X-Robots-Tag: noindex`). Обновление сайта: `npm run deploy` — домен при этом остаётся подключённым. Поддомен `scm.stakes.com.mx` (партнёрские ссылки) к воркеру не подключать.

## Шорткоды в контенте

- `{{cta:Текст|green|app}}` — партнёрская кнопка (`target="_blank"`, `rel="nofollow sponsored"`); последний параметр `reg` (по умолчанию) или `app`
- `{{ctabox:Заголовок|Подпись|Кнопка|app}}` — блок с кнопкой
- в JSON-шапке: `"hero_buttons": ["Текст|app", ...]`, `"offer": {"link": "app"}`
- `{{games:Игра/Провайдер;...}}` — плитки игр
- `{{updated}}` — дата обновления

## Партнёрская ссылка

Ссылки задаются в `AFF` в `build.py`:

- `reg` — регистрация: `https://scm.stakes.com.mx/?top=playeer` (все кнопки по умолчанию, шапка, плавающая кнопка на мобильном);
- `app` — приложение: `https://scm.stakes.com.mx/?top=playeer&max` (вторая кнопка на главной, первая кнопка и блок Android на `/app/`).

## Страницы

Коммерческие: `/`, `/registro/`, `/iniciar-sesion/`, `/app/`, `/bono-de-bienvenida/`, `/codigo-promocional/`, `/metodos-de-pago/`, `/casino/`, `/apuestas-deportivas/`.
Игры: `/originales-de-stake/`, `/slots/`, `/casino-en-vivo/`, `/blackjack/`.
Спорт: `/apuestas-futbol/`, `/apuestas-tenis/`, `/apuestas-cricket/`, `/apuestas-hockey/`, `/apuestas-esports/`.
Служебные: `/sobre-nosotros/`, `/contacto/`, `/juego-responsable/`, `/aviso-de-privacidad/`, `/politica-de-cookies/`, `/terminos-y-condiciones/`, `/descargo-de-responsabilidad/`, `404.html`.

## Новые страницы и данные

- `research/stake-mx-2026-10-20/` — данные со stake.mx на 20.10.2026 (описания разделов, списки игр, лиги, правила ставок по видам спорта, адреса обложек). Это источник фактов для страниц игр и спорта.
- `research/PAGE_RULES.md` — правила написания страниц (формат, компоненты, ссылки, запреты).
- `python3 tools_check_page.py <slug>` — проверка одной страницы: длина меты, запрещённые слова, разделы, FAQ, кнопки, ссылки.
- Превью игр: `src/assets/img/games/<slug-названия>.webp` подставляются в `{{games:...}}` автоматически по названию.
