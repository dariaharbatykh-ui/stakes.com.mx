# stakes.com.mx

Статический сайт на чистом HTML/CSS о Stake México (stake.mx), на испанском (es-MX).

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
python3 build.py
```

```bash
node serve.mjs 8080
```

Затем открыть http://localhost:8080.

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
Служебные: `/sobre-nosotros/`, `/contacto/`, `/juego-responsable/`, `/aviso-de-privacidad/`, `/politica-de-cookies/`, `/terminos-y-condiciones/`, `/descargo-de-responsabilidad/`, `404.html`.
