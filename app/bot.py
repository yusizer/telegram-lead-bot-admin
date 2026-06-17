"""Telegram bot: collects leads via a simple FSM conversation."""
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from .config import settings
from .database import SessionLocal
from .models import Lead

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


class LeadForm(StatesGroup):
    name = State()
    contact = State()
    task = State()


WELCOME = (
    "👋 Привет! Я помогу оформить заявку.\n\n"
    "Нажмите кнопку ниже, чтобы оставить заявку — "
    "бот соберёт имя, контакт и описание задачи."
)

WELCOME_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📝 Оставить заявку", callback_data="start_lead")]
    ]
)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME, reply_markup=WELCOME_KEYBOARD)


@dp.callback_query(F.data == "start_lead")
async def cb_start_lead(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(LeadForm.name)
    await callback.message.answer("Как вас зовут?")
    await callback.answer()


@dp.message(LeadForm.name)
async def step_name(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("Введите имя (минимум 2 символа):")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(LeadForm.contact)
    await message.answer(
        "Укажите контакт для связи:\n"
        "Telegram @username, email или телефон."
    )


@dp.message(LeadForm.contact)
async def step_contact(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("Контакт слишком короткий. Введите ещё раз:")
        return
    await state.update_data(contact=message.text.strip())
    await state.set_state(LeadForm.task)
    await message.answer("Опишите задачу в 1–2 предложениях:")


@dp.message(LeadForm.task)
async def step_task(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 5:
        await message.answer("Опишите задачу чуть подробнее (минимум 5 символов):")
        return
    data = await state.get_data()
    async with SessionLocal() as session:
        lead = Lead(
            name=data["name"],
            contact=data["contact"],
            task=message.text.strip(),
            status="new",
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)
    await state.clear()
    await message.answer(
        f"✅ Спасибо, {lead.name}! Заявка #{lead.id} принята.\n"
        "Мы свяжемся с вами в ближайшее время."
    )


async def start_bot() -> None:
    """Start long-polling. Run alongside the web server."""
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
