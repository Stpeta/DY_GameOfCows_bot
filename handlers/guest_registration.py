from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select

from database.base import async_session_maker
from database.models import Game, Player
from filters.role_filter import RoleFilter
from lexicon.lexicon_en import LEXICON_EN


guest_router = Router()
guest_router.message.filter(RoleFilter("guest"))


class Registration(StatesGroup):
    waiting_for_code = State()
    waiting_for_name = State()
    waiting_for_nickname = State()


@guest_router.message(CommandStart())
async def guest_start(message: Message, state: FSMContext) -> None:
    await message.answer(LEXICON_EN["ask_registration_code"])
    await state.set_state(Registration.waiting_for_code)


@guest_router.message(Registration.waiting_for_code, F.text)
async def process_code(message: Message, state: FSMContext) -> None:
    async with async_session_maker() as session:
        result = await session.execute(
            select(Game).where(Game.registration_code == message.text)
        )
        game = result.scalars().first()
    if not game:
        await message.answer(LEXICON_EN.get("invalid_registration_code", "Invalid code."))
        return
    await state.update_data(game_id=game.id, game_name=game.name)
    await message.answer(LEXICON_EN["ask_player_name"])
    await state.set_state(Registration.waiting_for_name)


@guest_router.message(Registration.waiting_for_name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(LEXICON_EN["ask_player_nickname"])
    await state.set_state(Registration.waiting_for_nickname)


@guest_router.message(Registration.waiting_for_nickname, F.text)
async def process_nickname(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session_maker() as session:
        player = Player(
            telegram_id=message.from_user.id,
            game_id=data["game_id"],
            registration_time=datetime.utcnow(),
            name=data["name"],
            nickname=message.text,
            is_registered=True,
        )
        session.add(player)
        await session.commit()
    await state.clear()
    await message.answer(
        LEXICON_EN["registration_success"].format(
            game=data["game_name"], name=data["name"]
        )
    )
