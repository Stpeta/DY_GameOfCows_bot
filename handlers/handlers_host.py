from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select

from database.base import async_session_maker
from database.models import FieldState, Game, Player, PlayerMove
from lexicon.lexicon_en import LEXICON_EN
from keyboards.admin import (
    admin_main_keyboard,
    host_game_keyboard,
    host_day_keyboard,
    waiting_players_keyboard,
)
from keyboards.player import hours_keyboard
from services.game_creation import create_game
from filters.role_filter import RoleFilter

host_router = Router()
host_router.message.filter(RoleFilter("host"))
host_router.callback_query.filter(RoleFilter("host"))


class NewGame(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_degradation = State()
    waiting_for_recovery = State()
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
    await state.update_data(description=message.text)
    await message.answer(LEXICON_EN["ask_degradation_coeff"])
    await state.set_state(NewGame.waiting_for_degradation)


@host_router.message(NewGame.waiting_for_degradation, F.text)
async def process_degradation(message: Message, state: FSMContext) -> None:
    await state.update_data(degradation=message.text)
    await message.answer(LEXICON_EN["ask_recovery_coeff"])
    await state.set_state(NewGame.waiting_for_recovery)


@host_router.message(NewGame.waiting_for_recovery, F.text)
async def process_recovery(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    async with async_session_maker() as session:
        game = await create_game(
            session=session,
            host_id=message.from_user.id,
            name=data["name"],
            description=data["description"],
            degradation_coeff=float(data["degradation"]),
            recovery_coeff=float(message.text),
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
async def start_day(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    game_id = data["game_id"]
    async with async_session_maker() as session:
        game = await session.get(Game, game_id)
        game.days_played = (game.days_played or 0) + 1
        day_number = game.days_played
        await session.commit()
        result = await session.execute(select(Player).where(Player.game_id == game_id))
        players = result.scalars().all()
    for player in players:
        await callback.bot.send_message(
            player.telegram_id,
            LEXICON_EN["choose_hours"],
            reply_markup=hours_keyboard(),
        )
    await callback.message.edit_text(
        LEXICON_EN["host_day_started"].format(day=day_number),
        reply_markup=host_day_keyboard(day_number),
    )


@host_router.callback_query(NewGame.game_running, F.data == "end_day")
async def end_day(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    game_id = data["game_id"]
    async with async_session_maker() as session:
        game = await session.get(Game, game_id)
        day_number = game.days_played or 0
        result = await session.execute(select(Player).where(Player.game_id == game_id))
        players = result.scalars().all()
        moves_result = await session.execute(
            select(PlayerMove).where(
                (PlayerMove.game_id == game_id)
                & (PlayerMove.day_number == day_number)
            )
        )
        moves = {move.player_id: move for move in moves_result.scalars().all()}
        total_hours = 0
        for player in players:
            move = moves.get(player.id)
            if not move:
                move = PlayerMove(
                    game_id=game_id,
                    day_number=day_number,
                    player_id=player.id,
                    hours=5,
                    coins=0,
                )
                session.add(move)
                moves[player.id] = move
            total_hours += move.hours
        avg_hours = total_hours / len(players) if players else 0
        result = await session.execute(
            select(FieldState)
            .where(FieldState.game_id == game_id)
            .order_by(FieldState.day_number.desc())
            .limit(1)
        )
        prev_state = result.scalars().first()
        prev_level = prev_state.field_level if prev_state else 100.0
        if avg_hours > 5:
            field_level = max(
                0.0, prev_level - game.degradation_coeff * (avg_hours - 5)
            )
        elif avg_hours < 5:
            field_level = min(
                100.0, prev_level + game.recovery_coeff * (5 - avg_hours)
            )
        else:
            field_level = prev_level
        session.add(
            FieldState(
                game_id=game_id,
                day_number=day_number,
                field_level=field_level,
                degradation_coeff=game.degradation_coeff,
                recovery_coeff=game.recovery_coeff,
            )
        )
        table_lines = []
        for player in players:
            move = moves[player.id]
            coins = int(move.hours * prev_level / 100)
            move.coins = coins
            player.balance += coins
            table_lines.append(f"{player.name}: {move.hours}h -> {coins}")
            await callback.bot.send_message(
                player.telegram_id,
                LEXICON_EN["day_results_player"].format(
                    day=day_number, hours=move.hours, coins=coins, field=field_level
                ),
            )
        table = "\n".join(table_lines)
        await session.commit()
    await callback.message.edit_text(
        LEXICON_EN["day_results_host"].format(
            day=day_number, table=table, avg=avg_hours, field=field_level
        ),
        reply_markup=host_game_keyboard(),
    )
