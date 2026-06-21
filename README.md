# Telegram Lead Bot + Admin Panel 🤖📊

![CI](https://github.com/yusizer/telegram-lead-bot-admin/actions/workflows/ci.yml/badge.svg)

Telegram-бот, который через пошаговый диалог (FSM) собирает заявки (лиды) и
FastAPI-админку с дашбордом и управлением статусами заявок. Один процесс,
один Docker-контейнер — готово к деплою на Render.

> **Live demo (admin):** https://telegram-lead-bot-admin.onrender.com ·
> **Логин:** пароль `demo` ·
> **Бот:** _<добавь @username бота после заведения токена>_

## Возможности

- **Бот (aiogram 3):** `/start` → кнопка «Оставить заявку» → собирает имя,
  контакт, описание задачи → сохраняет заявку в БД → выдаёт номер заявки.
  Валидация на каждом шаге, FSM-состояния.
- **Админка (FastAPI):** вход по паролю (session-cookie), дашборд со статистикой
  (всего / за сегодня / новые / закрытые), таблица последних заявок, страница
  всех заявок с фильтром по статусу, смена статуса (`new` / `contacted` / `closed`).
- **БД:** SQLite через SQLAlchemy 2 (async) + aiosqlite.
- **Healthcheck:** `GET /health` для Render / uptime-мониторинга.

## Стек

| Слой        | Технология                                  |
|-------------|---------------------------------------------|
| Бот         | aiogram 3 (FSM, long-polling)               |
| Web/админка | FastAPI + Jinja2 + Bootstrap 5              |
| БД          | SQLAlchemy 2 (async) + aiosqlite (SQLite)   |
| Конфиг      | pydantic-settings (.env)                    |
| Деплой      | Render Blueprint (Python web) / Docker      |

## Структура

```
portfolio/telegram-bot-admin/
├── app/
│   ├── __main__.py     # entrypoint: бот + uvicorn в одном event loop
│   ├── config.py       # настройки из .env
│   ├── models.py       # модель Lead
│   ├── database.py     # async engine + init_db
│   ├── bot.py          # aiogram FSM-бот
│   ├── web.py          # FastAPI админка
│   └── templates/      # base / login / dashboard / leads (Jinja2)
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Локальный запуск

```bash
# 1. Установить зависимости
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Настроить окружение
cp .env.example .env   # Windows: copy .env.example .env
#   заполни TELEGRAM_BOT_TOKEN (от @BotFather)
#   придумай ADMIN_PASSWORD и SESSION_SECRET

# 3. Запустить (бот + админка одновременно)
python -m app
```

- Админка: http://localhost:8000  (логин: пароль из `ADMIN_PASSWORD`)
- Бот: напиши ему в Telegram `/start`

## Деплой на Render (one-click)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yusizer/telegram-lead-bot-admin)

1. Кликни кнопку выше (или открой
   `https://render.com/deploy?repo=https://github.com/yusizer/telegram-lead-bot-admin`).
2. Render прочитает `render.yaml` и создаст web-сервис `telegram-lead-bot-admin`
   (free, Python 3.12.6). `ADMIN_PASSWORD=demo`, `SESSION_SECRET` генерируется
   автоматически, `DATABASE_URL` — SQLite.
3. Сервис поднимет только FastAPI-админку (`uvicorn app.web:app`) — бот не
   запускается, т.к. токен-плейсхолдер. `seed_if_empty()` при старте наполняет
   демо-лидами, чтобы админка не выглядела пустой.
4. После деплоя открой `https://telegram-lead-bot-admin.onrender.com`, введи
   пароль `demo` — увидишь дашборд с заявками. `/health` — проверка, что сервис жив.

> ⚠️ SQLite хранится в файле внутри контейнера (Render free — диск эфемерный,
> сбрасывается при редеплое). Для демо-портфолио этого достаточно:
> `seed_if_empty()` каждый старт наполняет заново. Для прод-нагрузки подключи
> PostgreSQL (поменяй `DATABASE_URL` на `postgresql+asyncpg://...` и добавь
> `asyncpg` в requirements) и задай реальный `TELEGRAM_BOT_TOKEN`, чтобы
> запускался и бот (`python -m app`).

## Скриншоты

| Бот: приветствие и сбор заявки | Админка: дашборд |
|:---:|:---:|
| ![bot](docs/bot.png) | ![dashboard](docs/dashboard.png) |

_Положи скриншоты в `docs/` после запуска._

## Связь с услугой

Этот проект — готовая демонстрация связки «Telegram-бот + веб-админка со
статистикой», которую можно переиспользовать под разные ниши клиентов
(запись, заявки, опросы, лидогенерация).
