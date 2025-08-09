from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy import select

from database.base import async_session_maker
from database.models import Game, Player, PlayerMove
from filters.role_filter import RoleFilter
from lexicon.lexicon_en import LEXICON_EN

player_router = Router()
player_router.message.filter(RoleFilter("player"))
player_router.callback_query.filter(RoleFilter("player"))


@player_router.callback_query(F.data.startswith("hours_"))
async def process_hours(callback: CallbackQuery) -> None:
    hours = int(callback.data.split("_")[1])
    async with async_session_maker() as session:
        result = await session.execute(
            select(Player).where(Player.telegram_id == callback.from_user.id)
        )
        player = result.scalars().first()
        if not player:
            await callback.answer("Player not found", show_alert=True)
            return
        game = await session.get(Game, player.game_id)
        day_number = game.days_played or 0
        result = await session.execute(
            select(PlayerMove).where(
                (PlayerMove.game_id == game.id)
                & (PlayerMove.day_number == day_number)
                & (PlayerMove.player_id == player.id)
            )
        )
        move = result.scalars().first()
        if move:
            move.hours = hours
        else:
            session.add(
                PlayerMove(
                    game_id=game.id,
                    day_number=day_number,
                    player_id=player.id,
                    hours=hours,
                )
            )
        await session.commit()
    await callback.answer(
        LEXICON_EN["hours_received"].format(hours=hours), show_alert=True
    )
    await callback.message.delete()
