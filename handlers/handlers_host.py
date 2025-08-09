from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from database.base import async_session_maker
from lexicon.lexicon_en import LEXICON_EN
from keyboards.admin import admin_main_keyboard
from services.game_creation import create_game
from filters.role_filter import RoleFilter

host_router = Router()
host_router.message.filter(RoleFilter("host"))
host_router.callback_query.filter(RoleFilter("host"))


class NewGame(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_players = State()


@host_router.message(CommandStart())
async def host_start(message: Message) -> None:
    await message.answer(
        LEXICON_EN["host_menu_inactive"].format(count=0),
        reply_markup=admin_main_keyboard(),
    )


@host_router.callback_query(F.data == "new_game")
async def process_new_game(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_reply_markup()
    await callback.message.answer(LEXICON_EN["ask_game_name"])
    await state.set_state(NewGame.waiting_for_name)


@host_router.message(NewGame.waiting_for_name, F.text)
async def process_game_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(LEXICON_EN["ask_game_description"])
    await state.set_state(NewGame.waiting_for_description)


@host_router.message(NewGame.waiting_for_description, F.text)
async def process_game_description(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session_maker() as session:
        game = await create_game(
            session=session,
            host_id=message.from_user.id,
            name=data["name"],
            description=message.text,
        )
    await state.update_data(game_id=game.id, host_id=message.from_user.id)
    await state.set_state(NewGame.waiting_for_players)
    await message.answer(
        LEXICON_EN["game_created"].format(
            name=game.name, code=game.registration_code
        )
    )
