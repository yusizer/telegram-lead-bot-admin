# Telegram Lead Bot + Admin Panel 🤖📊

Telegram-бот, который через пошаговый диалог (FSM) собирает заявки (лиды) и
FastAPI-админку с дашбордом и управлением статусами заявок. Один процесс,
один Docker-контейнер — готово к деплою на Railway.

> **Live demo:** _<добавь ссылку после деплоя на Railway>_ ·
> **Бот:** _<добавь @username бота>_

## Возможности

- **Бот (aiogram 3):** `/start` → кнопка «Оставить заявку» → собирает имя,
  контакт, описание задачи → сохраняет заявку в БД → выдаёт номер заявки.
  Валидация на каждом шаге, FSM-состояния.
- **Админка (FastAPI):** вход по паролю (session-cookie), дашборд со статистикой
  (всего / за сегодня / новые / закрытые), таблица последних заявок, страница
  всех заявок с фильтром по статусу, смена статуса (`new` / `contacted` / `closed`).
- **БД:** SQLite через SQLAlchemy 2 (async) + aiosqlite.
- **Healthcheck:** `GET /health` для Railway / uptime-мониторинга.

## Стек

| Слой        | Технология                                  |
|-------------|---------------------------------------------|
| Бот         | aiogram 3 (FSM, long-polling)               |
| Web/админка | FastAPI + Jinja2 + Bootstrap 5              |
| БД          | SQLAlchemy 2 (async) + aiosqlite (SQLite)   |
| Конфиг      | pydantic-settings (.env)                    |
| Деплой      | Docker → Railway (один web-сервис)          |

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

## Деплой на Railway

1. Залей репозиторий на GitHub.
2. На [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**.
3. Railway автоматически подхватит `Dockerfile`.
4. В **Variables** добавь:
   - `TELEGRAM_BOT_TOKEN`
   - `ADMIN_PASSWORD`
   - `SESSION_SECRET` (длинная случайная строка)
5. Railway выставит `PORT` сам — приложение его читает.
6. После деплоя открой публичный домен Railway — это и есть live demo админки.
   `/health` — для проверки, что сервис жив.

> ⚠️ SQLite хранится в файле внутри контейнера. Для демо-портфолио этого
> достаточно. Для прод-нагрузки подключи PostgreSQL (поменяй `DATABASE_URL`
> на `postgresql+asyncpg://...` и добавь `asyncpg` в requirements).

## Скриншоты

| Бот: приветствие и сбор заявки | Админка: дашборд |
|:---:|:---:|
| ![bot](docs/bot.png) | ![dashboard](docs/dashboard.png) |

_Положи скриншоты в `docs/` после запуска._

## Связь с услугой

Этот проект — готовая демонстрация связки «Telegram-бот + веб-админка со
статистикой», которую можно переиспользовать под разные ниши клиентов
(запись, заявки, опросы, лидогенерация).
