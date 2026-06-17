"""Async database engine and session factory."""
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import settings
from .models import Base, Lead

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Create tables if they don't exist yet."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_if_empty() -> None:
    """Populate sample leads so the demo admin never looks empty.

    Runs only when the table has zero rows — safe on every startup and after
    a container recycle (e.g. on Railway/Oracle), which is exactly when a
    visiting client would otherwise see a blank dashboard.
    """
    async with SessionLocal() as session:
        count = (await session.execute(select(func.count(Lead.id)))).scalar_one()
        if count:
            return

        now = datetime.now()
        samples = [
            ("Алиса", "@alice_dev", "Нужен Telegram-бот для записи клиентов на услуги", "new", 0),
            ("Bob", "bob@example.com", "Парсер цен конкурентов + дашборд с графиками", "new", 0),
            ('Студия "Лоза"', "+998 90 123-45-67", "Автоматизация: форма → Google Sheets → email", "contacted", 1),
            ("Дмитрий", "@dmitry_k", "Бот поддержки с базой знаний и админкой", "contacted", 2),
            ("Cafe Nord", "manager@cafenord.uz", "Сбор отзывов через QR-бота, статистика по дням", "closed", 4),
            ("Elena", "elena@mail.com", "REST API для мобильного приложения с JWT-авторизацией", "closed", 6),
            ("Max", "@maxbuilds", "Web-scraper каталога товаров + выгрузка в Excel", "new", 8),
            ("Olivia", "olivia@startup.io", "n8n-воркфлоу: лиды в CRM + уведомления в Telegram", "contacted", 10),
        ]
        session.add_all(
            Lead(
                name=name,
                contact=contact,
                task=task,
                status=status,
                created_at=now - timedelta(days=days_ago, hours=offset),
            )
            for (name, contact, task, status, days_ago), offset in zip(
                samples, range(0, len(samples) * 3, 3)
            )
        )
        await session.commit()

