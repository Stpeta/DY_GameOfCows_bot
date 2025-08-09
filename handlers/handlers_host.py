from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from config_data.config import load_config
from database.base import async_session_maker
from lexicon.lexicon_en import LEXICON_EN
from keyboards.admin import admin_main_keyboard
from services.course_creation import create_course

config = load_config()
HOST_IDS = config.tg_bot.host_ids

host_router = Router()


class NewCourse(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_players = State()


@host_router.message(CommandStart(), F.from_user.id.in_(HOST_IDS))
async def host_start(message: Message) -> None:
    await message.answer(
        LEXICON_EN["host_menu_inactive"].format(count=0),
        reply_markup=admin_main_keyboard(),
    )


@host_router.callback_query(F.data == "new_course")
async def process_new_course(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_reply_markup()
    await callback.message.answer(LEXICON_EN["ask_course_name"])
    await state.set_state(NewCourse.waiting_for_name)


@host_router.message(NewCourse.waiting_for_name, F.text)
async def process_course_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(LEXICON_EN["ask_course_description"])
    await state.set_state(NewCourse.waiting_for_description)


@host_router.message(NewCourse.waiting_for_description, F.text)
async def process_course_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session_maker() as session:
        course = await create_course(
            session=session,
            host_id=message.from_user.id,
            name=data["name"],
            description=message.text,
        )
    await state.update_data(course_id=course.id, host_id=message.from_user.id)
    await state.set_state(NewCourse.waiting_for_players)
    await message.answer(
        LEXICON_EN["course_created"].format(
            name=course.name, code=course.registration_code
        )
    )
