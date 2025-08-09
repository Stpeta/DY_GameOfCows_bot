from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database.base import async_session_maker
from database.models import Game, Player
from lexicon.lexicon_en import LEXICON_EN
from keyboards.admin import (
    admin_main_keyboard,
    host_game_keyboard,
    waiting_players_keyboard,
)
from services.game_creation import create_game
from filters.role_filter import RoleFilter

host_router = Router()
host_router.message.filter(RoleFilter("host"))
host_router.callback_query.filter(RoleFilter("host"))


class NewGame(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_players = State()
    game_running = State()


waiting_messages: dict[int, tuple[int, int]] = {}


async def refresh_waiting_message(game_id: int, bot: Bot) -> None:
    """Update host's waiting message with current registered players."""
    data = waiting_messages.get(game_id)
    if not data:
        return
    host_id, msg_id = data
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.game_id == game_id))
        players = result.scalars().all()
    players_text = (
        "\n".join(player.name for player in players)
        if players
        else LEXICON_EN["no_players"]
    )
    await bot.edit_message_text(
        LEXICON_EN["waiting_for_players"].format(players=players_text),
        chat_id=host_id,
        message_id=msg_id,
        reply_markup=waiting_players_keyboard(),
    )


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
    await message.answer(
        LEXICON_EN["game_created"].format(
            name=game.name, code=game.registration_code
        )
    )
    waiting = await message.answer(
        LEXICON_EN["waiting_for_players"].format(
            players=LEXICON_EN["no_players"]
        ),
        reply_markup=waiting_players_keyboard(),
    )
    waiting_messages[game.id] = (message.from_user.id, waiting.message_id)
    await state.set_state(NewGame.waiting_for_players)


@host_router.callback_query(NewGame.waiting_for_players, F.data == "start_game")
async def start_game(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    game_id = data["game_id"]
    async with async_session_maker() as session:
        result = await session.execute(select(Player).where(Player.game_id == game_id))
        players = result.scalars().all()
    players_text = (
        "\n".join(f"{p.name}: {p.balance}" for p in players)
        if players
        else LEXICON_EN["no_players"]
    )
    await callback.message.edit_text(
        LEXICON_EN["host_main_menu"].format(players=players_text),
        reply_markup=host_game_keyboard(),
    )
    waiting_messages.pop(game_id, None)
    await state.set_state(NewGame.game_running)
    for player in players:
        await callback.bot.send_message(
            player.telegram_id,
            LEXICON_EN["player_main"].format(balance=player.balance),
        )


@host_router.callback_query(F.data == "finish_game")
async def finish_game(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    game_id = data.get("game_id")
    if game_id is not None:
        async with async_session_maker() as session:
            result = await session.execute(select(Game).where(Game.id == game_id))
            game = result.scalars().first()
            if game:
                game.is_active = False
                await session.commit()
    await callback.message.edit_text(LEXICON_EN["game_finished"])
    await state.clear()


@host_router.callback_query(NewGame.game_running, F.data == "start_day")
async def start_day(callback: CallbackQuery) -> None:
    await callback.answer("Day 1 started", show_alert=False)
