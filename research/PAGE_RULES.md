# Правила для новых страниц stakes.com.mx

Сайт: испанский (México), `lang="es"`, статический HTML. Одна страница = один файл `src/pages/<slug>.html`.
Образцы формата: `src/pages/casino.html`, `src/pages/apuestas-deportivas.html`, `src/pages/metodos-de-pago.html`.

## Формат файла

В начале — JSON в `<!--{ ... }-->`, ниже — HTML контента (без `<h1>`, H1 берётся из JSON).

```
<!--{
"title": "...",            // ≤ 60 символов, основной ключ в начале, год 2026 уместен
"description": "...",      // ≤ 160 символов, основной ключ, 1–2 факта, в конце призыв (Juega hoy / Apuesta hoy / Regístrate)
"lead": "...",             // абзац первого экрана: 2–3 предложения, самое важное, основной ключ внутри
"h1": "...",               // не дублирует title слово в слово
"crumb": "...",            // короткая подпись для хлебных крошек, обычный регистр
"priority": "0.8",
"offer": { "tag": "...", "title": "...", "button": "..." }   // карточка первого экрана: короткий заголовок и текст кнопки
}-->
```

Регистр заголовков (Title Case) сборка делает сама: пиши заголовки обычным регистром.

## Тело страницы

- 9–12 разделов: `<section><h2 id="kebab-id" data-tab="Коротко">Заголовок</h2> ... </section>`; `data-tab` — 1–3 слова для вкладок.
- Объём 1300–1900 слов. Абзацы до 3–4 предложений. Второе лицо к читателю («puedes», «tu cuenta»).
- О Stake — в третьем лице: «Stake», «el sitio», «la plataforma». Не «nosotros», не «él».
- Последний раздел — FAQ: `<section class="faq"><h2 id="faq">Preguntas frecuentes sobre …</h2>` + 4–6 блоков `<details><summary>Вопрос?</summary><div><p>Ответ.</p></div></details>`.

### Компоненты (только эти классы)

- Таблица: `<div class="table-wrap"><table><tr><th>…</th></tr><tr><td>…</td></tr></table></div>` (`class="facts"` для таблицы «параметр — значение»).
- Карточки: `<div class="cards"><div class="card"><span class="kicker">…</span><h3>…</h3><p>…</p></div>…</div>`.
- Шаги: `<ol class="steps"><li><strong>Шаг</strong>Пояснение.</li>…</ol>`.
- Инструкции-карточки: `<div class="howto"><div class="howto-card"><h3>{{icon:NAME}}Заголовок</h3><ol><li>…</li></ol></div>…</div>`; одна карточка — `<div class="howto single">`. Иконки: home, user, key, phone, gift, ticket, card, dice, ball, shield, info, mail, trophy, crown, tv, lock, chat, star, alert, heart.
- Заметка: `<div class="note"><p><strong>…</strong> …</p></div>`, предупреждение — `class="note warn"`.
- Список-плашки (провайдеры, лиги): `<ul class="chips"><li>…</li></ul>`.

### Шорткоды

- Плитки игр с превью: `{{games:Nombre exacto/Proveedor;Nombre/Proveedor;...}}` — названия ТОЧНО как в данных Stake (регистр и написание), 6–12 игр.
- Блок с партнёрской кнопкой: `{{ctabox:Заголовок|Подпись|Текст кнопки}}` (кнопка ведёт на регистрацию).
- Партнёрских кнопок на странице всего не больше 4, считая кнопку в `offer`. Обычно: offer + 2 ctabox. Кнопки не ставить в таблицы, FAQ, заголовки.

## Внутренние ссылки

- Только `<a href="/slug/">анкор</a>` внутри абзацев, не в заголовках, таблицах, FAQ, кнопках.
- На один URL — одна ссылка со страницы. На саму себя — нет.
- Анкор — ключ целевой страницы в нижнем регистре (кроме Stake и имён собственных): «registro en Stake», «métodos de pago en Stake», «app de Stake», «bonos de Stake», «casino de Stake», «apuestas deportivas en Stake».
- Существующие страницы: `/`, `/registro/`, `/iniciar-sesion/`, `/app/`, `/bono-de-bienvenida/`, `/codigo-promocional/`, `/metodos-de-pago/`, `/casino/`, `/apuestas-deportivas/`, `/juego-responsable/`.
- Новые страницы (можно ссылаться друг на друга): `/originales-de-stake/`, `/slots/`, `/casino-en-vivo/`, `/blackjack/`, `/apuestas-futbol/`, `/apuestas-tenis/`, `/apuestas-cricket/`, `/apuestas-hockey/`, `/apuestas-esports/`.
- 5–8 внутренних ссылок на страницу, включая хаб (`/casino/` или `/apuestas-deportivas/`).

## Факты — только из источников

1. `facts.md` — проверенная база (платежи, VIP, акции октября 2026, верификация, ответственная игра). Главный источник; при конфликте выигрывает он.
2. `research/stake-mx-2026-10-20/*.json` — снято со страниц Stake 20.10.2026: `header` (описание раздела), `list` (игры и провайдеры в порядке «Popular», «N jugando»), `guide` (гайд Stake по разделу), у спорта `text` (лиги, матчи, рынки). `policy-by-sport.json` — выдержки из правил ставок Stake по видам спорта.
3. Числа, проценты, суммы — дословно как в источнике. Нет факта — не пишем (никаких придуманных RTP, коэффициентов, минимальных ставок, количества игр).
4. Гайды Stake — маркетинговый текст: НЕ копировать предложения, пересказывать своими словами. Не переносить из гайдов утверждения, которые противоречат `facts.md` (например, «licencias internacionales» — у Stake México разрешение SEGOB; про бонусы — только то, что есть в `facts.md`).
5. Коэффициенты конкретных матчей и составы — не указывать (устаревают). Лиги и турниры — можно, как «en el sitio aparecen…» по состоянию на octubre de 2026.

## Запрещено

- Упоминать официальный сайт, домены stake.mx / stake.com / help.stake.mx, адреса поддержки Stake.
- «Ventajas/Desventajas», плюсы-минусы, рейтинги и оценки.
- Слова «editorial», «redacción», «nosotros».
- Обещания выигрыша, «el mejor», «garantizado», «100% seguro».
- Новые картинки и `<img>` вручную (превью игр подставит шорткод `{{games:...}}`).

## Обязательные разделы

**Страница игры/категории казино:** что это и как устроено у Stake; игры раздела ({{games}}); провайдеры (chips); как играть / правила; варианты/типы (таблица); бонусы и акции, которые подходят (из facts.md); как начать играть (ol.steps); как играть с телефона (howto или steps: браузер Chrome/Safari, добавить на экран, без APK); ответственная игра / советы; FAQ.

**Страница вида спорта:** что можно ставить на этот спорт в Stake (лиги/турниры из данных, chips); рынки и типы ставок (таблица); как liquidan apuestas — ключевые правила из policy простым языком; apuestas en vivo y Retirarse (из facts.md); акции, если есть для этого спорта в facts.md, иначе Club VIP (спорт считается x3); как сделать первую ставку (ol.steps); как ставить с телефона; советы; FAQ.

## Проверка

После записи файла запусти `python3 tools_check_page.py <slug>` из корня репозитория и исправляй, пока не будет `OK`. Не запускай `build.py`. Не трогай другие файлы.
